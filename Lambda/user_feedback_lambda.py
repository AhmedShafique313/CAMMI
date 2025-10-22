import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

USERS_TABLE = "Users"
FEEDBACK_TABLE = "user_feedback"

def lambda_handler(event, context):
    if "body" not in event or not event["body"]:
        return build_response(400, {"error": "Missing request body."})

    body = json.loads(event["body"])

    session_id = body.get("session_id")
    question = body.get("question")
    answer = body.get("answer")

    if not session_id or not question or not answer:
        return build_response(400, {"error": "Missing one or more required fields: session_id, question, answer"})

    users_table = dynamodb.Table(USERS_TABLE)
    response = users_table.query(
        IndexName="session_id-index",  
        KeyConditionExpression=Key("session_id").eq(session_id)
    )

    if not response.get("Items"):
        return build_response(404, {"error": f"No user found for session_id: {session_id}"})

    user_item = response["Items"][0]
    user_id = user_item.get("id")
    email = user_item.get("email")

    if not user_id:
        return build_response(400, {"error": "User record found, but 'id' field missing."})

    feedback_table = dynamodb.Table(FEEDBACK_TABLE)
    feedback_table.put_item(
        Item={
            "user_id": user_id,      # partition key
            "question": question,    # sort key
            "answer": answer,
            "session_id": session_id
        }
    )

    return build_response(200, {
        "message": "Feedback successfully stored.",
        "user_id": user_id,
        "email": email,
        "question": question
    })


def build_response(status_code, body_dict):
    """Formats response with CORS headers."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(body_dict)
    }
