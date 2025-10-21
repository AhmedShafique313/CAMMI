import json, base64, boto3
from google.oauth2.service_account import Credentials
from google import genai
from boto3.dynamodb.conditions import Key

def normalize_private_key(pk: str) -> str:
    if pk is None:
        return None
    pk = pk.strip()
    if (pk.startswith('"') and pk.endswith('"')) or (pk.startswith("'") and pk.endswith("'")):
        pk = pk[1:-1]
    return pk.replace("\\n", "\n")

def build_client():
    service_account_info = {
        "type": "xx",
        "project_id": "xxxx",
        "private_key_id": "xx",
        "private_key": "xx",
        "client_email": "xx",
        "client_id": "xx",
        "auth_uri": "xx",
        "token_uri": "xx",
        "auth_provider_x509_cert_url": "xx",
        "client_x509_cert_url": "xx",
        "universe_domain": "xx"
    }

    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)

    return genai.Client(
        vertexai=True,
        project=service_account_info["project_id"],
        location="us-central1",
        credentials=creds,
    )

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table("Users")

def get_user_by_session(session_id: str):
    response = users_table.query(
        IndexName="session_id-index",
        KeyConditionExpression=Key("session_id").eq(session_id)
    )
    if not response["Items"]:
        return None
    return response["Items"][0]

def update_user_credits(email: str, new_credits: int):
    users_table.update_item(
        Key={"email": email},
        UpdateExpression="SET total_credits = :val",
        ExpressionAttributeValues={":val": new_credits}
    )

def is_unsafe_prompt(prompt: str) -> bool:
    prompt = prompt.lower()
    adult_keywords = [
        "nude", "naked", "sex", "sexual", "porn", "erotic", "nsfw", "boobs",
        "breasts", "genitals", "vagina", "penis", "nipple", "fetish", "explicit",
        "lingerie", "underwear", "xxx", "adult", "sensual", "provocative"
    ]

    return any(word in prompt for word in adult_keywords)

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    session_id = body.get("session_id")
    prompt = body.get("prompt", "")

    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }

    if not session_id:
        return {
            "statusCode": 400,
            "headers": cors_headers,
            "body": json.dumps({"error": "Missing session_id"})
        }

    user = get_user_by_session(session_id)
    if not user:
        return {
            "statusCode": 400,
            "headers": cors_headers,
            "body": "Unknown User"
        }
    
    email = user["email"]
    total_credits = int(user.get("total_credits", 0))

    if is_unsafe_prompt(prompt):
        return {
            "statusCode": 400,
            "headers": cors_headers,
            "body": json.dumps({
                "session_id": session_id,
                "error": "Prompt contains restricted or unsafe content"
            })
        }

    if total_credits < 2:
        return {
            "statusCode": 402,
            "headers": cors_headers,
            "body": json.dumps({
                "session_id": session_id,
                "error": "Insufficient credits",
                "total_credits": total_credits
            })
        }

    new_credits = total_credits - 2
    update_user_credits(email, new_credits)

    client = build_client()
    
    
    result = client.models.generate_images(
            model="publishers/google/models/imagen-4.0-ultra-generate-001",
            prompt=prompt
    )

    image_bytes = result.images[0].image_bytes
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response = {
        "session_id": session_id,
        "remaining_credits": new_credits,
        "image_base64": image_base64
    }

    return {
        "statusCode": 200,
        "headers": cors_headers,
        # "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response)
    }