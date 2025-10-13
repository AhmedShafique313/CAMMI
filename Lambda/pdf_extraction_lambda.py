import json
import boto3
import pdfplumber
import io
from boto3.dynamodb.conditions import Key, Attr

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

# Constants
BUCKET_NAME = "cammi"
USERS_TABLE = "Users"

# 🧠 Bedrock LLM call
def llm_calling(prompt, model_id, session_id="default-session"):
    """Call AWS Bedrock LLM. (No try/except — errors will propagate for visibility.)"""
    conversation = [
        {
            "role": "user",
            "content": [{"text": str(prompt)}]
        }
    ]

    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={
            # No strict max token limitation
            "temperature": 0.7,
            "topP": 0.9
        },
        requestMetadata={
            "sessionId": session_id
        }
    )

    response_text = response["output"]["message"]["content"][0]["text"]
    return response_text.strip()

# 🧾 Prompt builder for business profile extraction
def call_llm_extract_profile(all_content: str) -> str:
    """
    Sends the extracted PDF text to the Bedrock model with your exact prompt,
    returns the model's formatted business profile text.
    """
    prompt_relevancy = f"""
You are an expert business and marketing analyst specializing in B2B brand strategy.
 
You are given structured company information (scraped and pre-organized in JSON or markdown):
{str(all_content)}
 
Your task:
1. Extract all key information relevant to building a detailed and personalized business profile.
2. Use only factual data found in the input. Do not infer or invent data.
3. Return the response in the exact format below using the same headings and order.
4. If any field cannot be determined confidently, leave it blank (do not make assumptions).
 
Return your answer in this format exactly:
 
Business Name:
Industry / Sector:
Mission:
Vision:
Objective / Purpose Statement:
Business Concept:
Products or Services Offered:
Target Market:
Who They Currently Sell To:
Value Proposition:
Top Business Goals:
Challenges:
Company Overview / About Summary:
Core Values / Brand Personality:
Unique Selling Points (USPs):
Competitive Advantage / What Sets Them Apart:
Market Positioning Statement:
Customer Segments:
Proof Points / Case Studies / Testimonials Summary:
Key Differentiators:
Tone of Voice / Brand Personality Keywords:
Core Features / Capabilities:
Business Model:
Technology Stack / Tools / Platform:
Geographic Presence:
Leadership / Founder Info:
Company Values / Culture:
Strategic Initiatives / Future Plans:
Awards / Recognition / Partnerships:
Press Mentions or Achievements:
Client or Industry Verticals Served:
 
Notes:
- Keep responses concise and factual.
- Avoid any assumptions or generation of new data.
- Use sentence form, not bullet lists, except where lists are explicitly more natural.
    """.strip()

    return llm_calling(prompt_relevancy, model_id="us.anthropic.claude-sonnet-4-20250514-v1:0")  # You can swap the model ID if needed


def lambda_handler(event, context):
    # Parse JSON body
    body = json.loads(event.get("body", "{}"))
    session_id = body.get("session_id")
    project_id = body.get("project_id")

    # Validate input
    if not session_id or not project_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing session_id or project_id"})
        }

    # Find PDF in S3
    prefix = f"pdf_files/{session_id}/"
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

    if "Contents" not in response or len(response["Contents"]) == 0:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": f"No PDF found for session_id {session_id}"})
        }

    # Pick the first .pdf file in the folder
    pdf_key = next(
        (obj["Key"] for obj in response["Contents"] if obj["Key"].lower().endswith(".pdf")),
        None
    )

    if not pdf_key:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": f"No PDF file found in {prefix}"})
        }

    # Fetch PDF file from S3
    pdf_obj = s3.get_object(Bucket=BUCKET_NAME, Key=pdf_key)
    pdf_bytes = pdf_obj["Body"].read()

    print(f"Reading file from S3: {pdf_key}")
    print(f"File size: {len(pdf_bytes)} bytes")

    # ✅ Extract text from PDF (optimized for Lambda)
    all_text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            print(f"Extracting page {i + 1} ...")
            text = page.extract_text()
            if text:
                all_text += text + "\n" + "-" * 80 + "\n"

    # 🧠 Call Bedrock LLM to extract structured business profile
    print("Calling Bedrock LLM to generate structured business profile...")
    parsed_profile = call_llm_extract_profile(all_text)
    print("LLM processing completed.")

    # ✅ Get user_id from DynamoDB (Users table)
    table = dynamodb.Table(USERS_TABLE)

    # --- Option 1: (Recommended) Query using GSI "session_id-index"
    try:
        response = table.query(
            IndexName="session_id-index",
            KeyConditionExpression=Key("session_id").eq(session_id)
        )
        if not response.get("Items"):
            return {
                "statusCode": 404,
                "body": json.dumps({"message": f"No user found for session_id {session_id}"})
            }
        user_id = response["Items"][0]["id"]
        print(f"User found via GSI: {user_id}")
    except Exception as e:
        print(f"GSI not found or query failed, fallback to scan: {e}")

        # --- Option 2: (Fallback) Scan entire table by session_id
        response = table.scan(
            FilterExpression=Attr("session_id").eq(session_id)
        )
        if not response.get("Items"):
            return {
                "statusCode": 404,
                "body": json.dumps({"message": f"No user found for session_id {session_id}"})
            }
        user_id = response["Items"][0]["id"]
        print(f"User found via scan: {user_id}")

    # ✅ Upload extracted + parsed text to S3 (Append if file exists)
    s3_key = f"url_parsing/{project_id}/{user_id}/pdf_extraction.txt"

    try:
        # Check if file exists
        existing_obj = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        existing_content = existing_obj["Body"].read().decode("utf-8")
        print("Existing file found. Appending new content...")
    except s3.exceptions.NoSuchKey:
        existing_content = ""
        print("No existing file found. Creating a new one...")

    # Append parsed content
    final_output = (
        existing_content + "\n\n--- NEW PDF EXTRACT ---\n\n" + parsed_profile
        if existing_content
        else parsed_profile
    )

    # Upload updated content
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=final_output.encode("utf-8"),
        ContentType="text/plain"
    )

    # Use S3 URI format
    s3_url = f"s3://{BUCKET_NAME}/{s3_key}"

    # Return success response
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "PDF text extracted, processed by Bedrock LLM, and uploaded successfully (appended if existing)",
            "url": s3_url
        })
    }
