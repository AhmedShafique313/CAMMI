import json
import stripe
import boto3

# -------------------------
# Environment Configuration
# -------------------------
stripe.api_key = ""
FRONTEND_DOMAIN = ""

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
stripe_table = dynamodb.Table("stripe_table")

# -------------------------
# Plan Mapping (lookup_key → plan_name, credits)
# -------------------------
PLAN_CREDITS = {
    # Monthly subscription plans
    "explorer_monthly": {"plan_name": "Explorer", "credits": 500},
    "starter_monthly": {"plan_name": "Starter", "credits": 5000},
    "growth_monthly": {"plan_name": "Growth", "credits": 20000},
    "pro_monthly": {"plan_name": "Pro", "credits": 50000},
    "scale_enterprise_monthly": {"plan_name": "Scale/Enterprise", "credits": 150000},

    # Custom / one-time plan
    "agency_custom": {"plan_name": "Agency/Custom", "credits": 1000},
}



# -------------------------
# Lambda Handler
# -------------------------
def lambda_handler(event, context):
    path = event.get("path", "")
    method = event.get("httpMethod", "GET")

    # ------------------------
    # 1️⃣ Create Checkout Session
    # ------------------------
    if path.endswith("/checkout-plans") and method == "POST":
        body = parse_body(event)
        lookup_key = body.get("lookup_key")

        if not lookup_key:
            return response_json({"error": "lookup_key required"}, 400)

        prices = stripe.Price.list(lookup_keys=[lookup_key], expand=["data.product"])
        if not prices.data:
            return response_json({"error": "Invalid lookup_key"}, 400)

        checkout_session = stripe.checkout.Session.create(
            line_items=[{"price": prices.data[0].id, "quantity": 1}],
            mode="subscription",
            success_url=f"{FRONTEND_DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_DOMAIN}/cancel",
            metadata={"lookup_key": lookup_key},  # store lookup_key for webhook
        )

        return response_json({"checkout_url": checkout_session.url})

    # ------------------------
    # 2️⃣ Create Customer Portal
    # ------------------------
    elif path.endswith("/create-portal-session") and method == "POST":
        body = parse_body(event)
        session_id = body.get("session_id")

        if not session_id:
            return response_json({"error": "session_id required"}, 400)

        checkout_session = stripe.checkout.Session.retrieve(session_id)
        if not checkout_session.customer:
            return response_json({"error": "No customer found for this session"}, 400)

        portal_session = stripe.billing_portal.Session.create(
            customer=checkout_session.customer,
            return_url=FRONTEND_DOMAIN,
        )

        return response_json({"portal_url": portal_session.url})

    # ------------------------
    # 3️⃣ Handle Webhook (Stripe → Lambda)
    # ------------------------
    elif path.endswith("/payments") and method == "POST":
        webhook_secret = ""
        payload = event.get("body", "")
        sig_header = event["headers"].get("Stripe-Signature")

        # Verify Stripe webhook
        try:
            stripe_event = stripe.Webhook.construct_event(
                payload=payload, sig_header=sig_header, secret=webhook_secret
            )
        except Exception as e:
            return response_json({"error": f"Invalid webhook signature: {str(e)}"}, 400)

        event_type = stripe_event["type"]
        data = stripe_event["data"]["object"]

        # ✅ Handle successful payments or subscriptions
        if event_type in ("checkout.session.completed", "payment_intent.succeeded"):
            customer_email = (
                data.get("customer_details", {}).get("email")
                or data.get("receipt_email")
                or data.get("metadata", {}).get("email")
            )

            if not customer_email:
                return response_json({"error": "No email in webhook payload"}, 400)

            # Detect lookup_key (from metadata or price)
            lookup_key = None
            if data.get("metadata") and "lookup_key" in data["metadata"]:
                lookup_key = data["metadata"]["lookup_key"]
            elif data.get("subscription"):
                try:
                    subscription = stripe.Subscription.retrieve(data["subscription"])
                    if subscription["items"]["data"]:
                        lookup_key = subscription["items"]["data"][0]["price"].get("lookup_key")
                except Exception:
                    lookup_key = None

            # Fallback if lookup_key not found
            plan_info = PLAN_CREDITS.get(lookup_key, {"plan_name": "Agency/Custom", "credits": 1000})

            # Build DynamoDB item
            db_item = {
                "email": customer_email,   # partition key
                "delivery_status": "success",
                "stripe_event_type": event_type,
                "payment_id": stripe_event.get("id"),
                "payment_at": data.get("created"),
                "amount_subtotal": data.get("amount_subtotal"),
                "amount_total": data.get("amount_total"),
                "currency": data.get("currency"),
                "customer_id": data.get("customer"),
                "country": data.get("customer_details", {}).get("address", {}).get("country") if data.get("customer_details") else None,
                "business_name": data.get("customer_details", {}).get("business_name") if data.get("customer_details") else None,
                "name": data.get("customer_details", {}).get("name") if data.get("customer_details") else None,
                "phone": data.get("customer_details", {}).get("phone") if data.get("customer_details") else None,
                "invoice_id": data.get("invoice"),
                "package_mode": data.get("mode"),
                "payment_status": data.get("payment_status", "succeeded"),
                "subscription_id": data.get("subscription"),
                "success_url": f"{FRONTEND_DOMAIN}/success?session_id={data.get('id')}",
                "plan_name": plan_info["plan_name"],
                "credits": plan_info["credits"],
                "body": payload,
            }

            # ✅ Write to DynamoDB
            stripe_table.put_item(Item=db_item)

        # ------------------------
        # Return Success
        # ------------------------
        return response_json({"status": "success", "event_type": event_type})

    # ------------------------
    # 4️⃣ Fallback for unknown routes
    # ------------------------
    return response_json({"error": f"Route {path} not found"}, 404)


# ------------------------
# Helper Functions
# ------------------------
def parse_body(event):
    """Parse JSON body from API Gateway event"""
    if event.get("body"):
        try:
            return json.loads(event["body"])
        except json.JSONDecodeError:
            return {}
    return {}

def response_json(body, status=200):
    """Return JSON response with CORS headers"""
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": FRONTEND_DOMAIN,
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body),
    }
