import json
import stripe
import boto3

# Stripe API key
stripe.api_key = ""

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
stripe_table = dynamodb.Table("stripe_table")

# Frontend domain
FRONTEND_DOMAIN = ""

# Plan mapping (lookup_key → {plan_name, credits})
PLAN_CREDITS = {
    "starter_lite": {"plan_name": "Starter/Lite", "credits": 100},
    "pro_monthly": {"plan_name": "Pro", "credits": 180},
    "growth_monthly": {"plan_name": "Growth", "credits": 300},
    "scale_enterprise": {"plan_name": "Scale/Enterprise", "credits": 700},
}

def lambda_handler(event, context):
    path = event.get("path", "")
    method = event.get("httpMethod", "GET")

    # ------------------------
    # Create Checkout Session
    # ------------------------
    if path.endswith("/checkout-plans") and method == "POST":
        body = parse_body(event)
        lookup_key = body.get("lookup_key")

        if not lookup_key:
            return response_json({"error": "lookup_key required", "event": event}, 400)

        prices = stripe.Price.list(
            lookup_keys=[lookup_key],
            expand=["data.product"]
        )

        if not prices.data:
            return response_json({"error": "Invalid lookup_key", "event": event}, 400)

        checkout_session = stripe.checkout.Session.create(
            line_items=[{"price": prices.data[0].id, "quantity": 1}],
            mode="subscription",
            success_url=f"{FRONTEND_DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_DOMAIN}/cancel",
        )

        return response_json({
            "checkout_url": checkout_session.url,
            "event": event
        })

    # ------------------------
    # Customer Portal
    # ------------------------
    elif path.endswith("/create-portal-session") and method == "POST":
        body = parse_body(event)
        checkout_session_id = body.get("session_id")

        if not checkout_session_id:
            return response_json({"error": "session_id required", "event": event}, 400)

        checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)

        if not checkout_session.customer:
            return response_json(
                {"error": "No customer found for this session", "event": event}, 400
            )

        portal_session = stripe.billing_portal.Session.create(
            customer=checkout_session.customer,
            return_url=FRONTEND_DOMAIN,
        )

        return response_json({
            "portal_url": portal_session.url,
            "event": event
        })

    # ------------------------
    # Webhook
    # ------------------------
    elif path.endswith("/payments") and method == "POST":
        webhook_secret = ""
        payload = event.get("body", "")
        sig_header = event["headers"].get("Stripe-Signature")

        # Verify Stripe webhook
        stripe_event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=webhook_secret
        )

        event_type = stripe_event["type"]
        data = stripe_event["data"]["object"]

        if event_type == "checkout.session.completed":
            customer_email = data.get("customer_details", {}).get("email")
            if not customer_email:
                return response_json({"error": "No email in webhook payload"}, 400)

            # Get lookup_key from session data (if set in Checkout Session metadata/price)
            lookup_key = None
            if data.get("metadata") and "lookup_key" in data["metadata"]:
                lookup_key = data["metadata"]["lookup_key"]
            elif data.get("display_items"):
                # legacy case if display_items was used
                lookup_key = data["display_items"][0]["price"]["lookup_key"]
            elif data.get("subscription"):
                # retrieve subscription to get lookup_key
                subscription = stripe.Subscription.retrieve(data["subscription"])
                if subscription["items"]["data"]:
                    lookup_key = subscription["items"]["data"][0]["price"].get("lookup_key")

            # Fallback if lookup_key not found
            plan_info = PLAN_CREDITS.get(lookup_key, {"plan_name": "Unknown", "credits": 0})

            # Prepare item for stripe_table (email = partition key)
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
                "country": data.get("customer_details", {}).get("address", {}).get("country"),
                "business_name": data.get("customer_details", {}).get("business_name"),
                "name": data.get("customer_details", {}).get("name"),
                "phone": data.get("customer_details", {}).get("phone"),
                "invoice_id": data.get("invoice"),
                "package_mode": data.get("mode"),
                "payment_status": data.get("payment_status"),
                "subscription_id": data.get("subscription"),
                "success_url": f"{FRONTEND_DOMAIN}/success?session_id={data['id']}",
                "body": payload,
                "plan_name": plan_info["plan_name"],
                "credits": plan_info["credits"]
            }

            stripe_table.put_item(Item=db_item)

        return response_json({
            "status": "success",
            "event_type": event_type
        })

    # ------------------------
    # Unknown Route
    # ------------------------
    return response_json({"error": f"Route {path} not found", "event": event}, 404)


# ------------------------
# Helpers
# ------------------------
def parse_body(event):
    """Parse JSON body from API Gateway event"""
    if event.get("body"):
        return json.loads(event["body"])
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
