import json
import boto3
import pdfplumber
import io
from boto3.dynamodb.conditions import Key, Attr

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Constants
BUCKET_NAME = "cammi"
USERS_TABLE = "Users"

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

    # Upload extracted text to S3
    s3_key = f"url_parsing/{project_id}/{user_id}/pdf_extraction.txt"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=all_text.encode("utf-8"),
        ContentType="text/plain"
    )

    # Use S3 URI format
    s3_url = f"s3://{BUCKET_NAME}/{s3_key}"

    # Return success response
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "PDF text extracted and uploaded successfully",
            "url": s3_url
        })
    }
