import json
from groq import Groq
import os

client = Groq(api_key="")

def invoke_groq(prompt: str, session_id: str) -> str:
    instruction = (
        """
    You are a senior business strategist.
    Your task is to refine the user’s response into a clear, professional, and business-aligned statement.
    You will be given both the question and the user’s answer.
    Use the question to understand the context, and then refine only the answer.
    Focus on clarity, structure, and alignment with business or strategic language.
    Do not ask questions, give advice, or include suggestions to the user.
    Output only the refined statement."""
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
    session_id = body.get("session_id", "")

    if not prompt:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": "Missing 'prompt' in request body"}),
        }

    groq_response = invoke_groq(prompt, session_id)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps(
            {
                "message": "Response generated successfully",
                "session_id": session_id,
                "groq_response": groq_response,
            }
        ),
    }
