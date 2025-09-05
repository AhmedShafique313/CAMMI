import json
from groq import Groq
import os
 
client = Groq(api_key="")
 
def invoke_groq(prompt: str):
    instruction = (
        "You are a senior prompt engineer. "
        "Your task is to take user inputs and rewrite them as powerful, clear prompts "
        "that get the best results which focus on clarity, specificity, and alignment with business objectives. "
        "Just give the refined prompt only as output. Do not provide output in double quotation. "
        "Note: You are generating document-ready text so don't add your additional response."
    )
 
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt.strip()},
        ],
    )
 
    return response.choices[0].message.content.strip()
 
def lambda_handler(event, context):
    if not event.get("body"):
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": "Empty body received"}),
        }
 
    body = json.loads(event["body"])
    prompt = body.get("prompt", "").strip()
    # session_id = body.get("session_id", "")
 
    if not prompt:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": "Missing 'prompt' in request body"}),
        }
 
    groq_response = invoke_groq(prompt)
 
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps(
            {
                "message": "Response generated successfully",
                # "session_id": session_id,
                "groq_response": groq_response,
            }
        ),
    }