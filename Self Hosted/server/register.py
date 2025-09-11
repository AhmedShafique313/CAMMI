import json
import uuid
import boto3
from botocore.exceptions import ClientError

# DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("WordPressSites")

import json
import uuid
import boto3

# DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("WordPressSites")

def lambda_handler(event, context):
    # Add CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }

    # Parse input body
    if "body" in event:
        body = json.loads(event["body"])
    else:
        body = event  # for testing directly

    sitename = body.get("sitename")
    baseurl = body.get("baseurl")
    username = body.get("username")
    app_password = body.get("app_password")

    # Validate required fields
    if not all([sitename, baseurl, username, app_password]):
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Missing required fields"})
        }

    # Create unique ID
    site_id = str(uuid.uuid4())

    # Save to DynamoDB
    item = {
        "sitename": sitename,   # partition key
        "id": site_id,
        "base_url": baseurl.rstrip("/"),
        "username": username,
        "app_password": app_password
    }
    table.put_item(Item=item)

    # Success response
    return {
        "statusCode": 201,
        "headers": headers,
        "body": json.dumps({
            "message": "✅ Site registered successfully!",
            "id": site_id,
            "sitename": sitename
        })
    }