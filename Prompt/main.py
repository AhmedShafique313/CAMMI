import boto3
import json
from botocore.exceptions import ClientError
from openai import OpenAI

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key="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",
)
 
# ---------- Bedrock Call ----------
def invoke_bedrock(prompt: str, session_id: str) -> str:
    instruction = """ou are a senior prompt engineer. Your task is to take user inputs and rewrite them as powerful, clear prompts "
    "that get the best results which focuses on clarity, specificity, and alignment with business objectives. "
    "Just give the refined prompt only as output.Do not provide output in double quotation
    Note: You are generating document-ready text so don't add your additional response."""
 
    conversation = [  
        {
            "role": "user",
            "content": [{"text": str(instruction)}]
        },
        {
            "role": "user",
            "content": [{"text": str(prompt.strip())}]
        }
    ]
 
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:fireworks-ai",
    messages=conversation
    )
 
    return response.choices[0].message.content.strip()
 
# ---------- Lambda Handler ----------
def lambda_handler(event, context):
    try:
        # ✅ Validate request body
        if not event.get("body"):
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"error": "Empty body received"})
            }
 
        body = json.loads(event["body"])
        prompt = body.get("prompt", "").strip()
        session_id = body.get("session_id", "")
 
        if not prompt:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"error": "Missing 'prompt' in request body"})
            }
 
        # ✅ Invoke Bedrock
        bedrock_response = invoke_bedrock(prompt, session_id)
 
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Response generated successfully",
                "session_id": session_id,
                "bedrock_response": bedrock_response
            })
        }
 
    except (ClientError, Exception) as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }