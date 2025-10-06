import boto3

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table("Users")

def lambda_handler(event, context):
    updated_users = []

    for record in event.get("Records", []):
        if record["eventName"] not in ("INSERT", "MODIFY"):
            continue  # only process new items

        new_item = record["dynamodb"].get("NewImage", {})
        if not new_item:
            continue

        # Extract values
        email = new_item.get("email", {}).get("S")
        amount_total = new_item.get("amount_total", {}).get("N")
        plan_name = new_item.get("plan_name", {}).get("S")
        payment_status = new_item.get("payment_status", {}).get("S")
        credits = new_item.get("credits", {}).get("N")
        country = new_item.get("country", {}).get("S")
        currency = new_item.get("currency", {}).get("S")
        payment_at = new_item.get("payment_at", {}).get("N")

        if not email:
            continue

        # Update only these four fields, keep all others intact
        update_expr = []
        expr_values = {}

        if amount_total is not None:
            update_expr.append("amount_total = :amount_total")
            expr_values[":amount_total"] = int(amount_total)

        if plan_name is not None:
            update_expr.append("plan_name = :plan_name")
            expr_values[":plan_name"] = plan_name

        if payment_status is not None:
            update_expr.append("payment_status = :payment_status")
            expr_values[":payment_status"] = payment_status

        if credits is not None:
            update_expr.append("credits = :credits")
            expr_values[":credits"] = int(credits)
        
        if country is not None:
            update_expr.append("country = :country")
            expr_values[":country"] = country
        
        if currency is not None:
            update_expr.append("currency = :currency")
            expr_values[":currency"] = currency

        if payment_at is not None:
            update_expr.append("payment_at = :payment_at")
            expr_values[":payment_at"] = int(payment_at)

        if update_expr:  # only run if we actually have something to update
            users_table.update_item(
                Key={"email": email},
                UpdateExpression="SET " + ", ".join(update_expr),
                ExpressionAttributeValues=expr_values
            )

            updated_users.append({
                "email": email,
                "amount_total": amount_total,
                "plan_name": plan_name,
                "payment_status": payment_status,
                "credits": credits,
                "country": country,
                "currency": currency,
                "payment_at": payment_at
            })

    return {
        "statusCode": 200,
        "body": f"Updated {len(updated_users)} user(s)",
        "updated_users": updated_users
    }
