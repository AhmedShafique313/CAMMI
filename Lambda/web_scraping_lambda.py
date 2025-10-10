import json, boto3
from boto3.dynamodb.conditions import Attr
from hyperbrowser import Hyperbrowser
from hyperbrowser.models import StartScrapeJobParams, ScrapeOptions
from huggingface_hub import InferenceClient

# AWS clients
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
BUCKET_NAME = "cammi"
# DynamoDB table
users_table = dynamodb.Table("Users")

# Hyperbrowser + Hugging Face clients
client_scraper = Hyperbrowser(api_key="")
client = InferenceClient(provider="fireworks-ai", api_key="")


# ---------- SCRAPING ----------
def scrape_links(url):
    """Scrape all links from the website."""
    result = client_scraper.scrape.start_and_wait(
        StartScrapeJobParams(
            url=url,
            scrape_options=ScrapeOptions(formats=["links"], only_main_content=True)
        )
    )
    return result.data.links


def scrape_page_content(url):
    """Scrape markdown content from a given URL."""
    result = client_scraper.scrape.start_and_wait(
        StartScrapeJobParams(
            url=url,
            scrape_options=ScrapeOptions(formats=["markdown"], only_main_content=True)
        )
    )
    return result.data.markdown or ""


# ---------- LLM ----------
def llm_calling(prompt):
    """Call the Fireworks/Groq model using HuggingFace client."""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": str(prompt)}]
    )
    return response.choices[0].message.content.strip()


# ---------- MAIN LAMBDA HANDLER ----------
def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return build_response(200, {"message": "CORS preflight OK"})

    # Parse input
    body = json.loads(event.get("body", "{}"))
    session_id = body.get("session_id")
    website = body.get("website")

    if not session_id or not website:
        return build_response(400, {"error": "Missing required fields: session_id or website"})

    # ---- 1. Fetch user info using session_id ----
    user_resp = users_table.scan(
        FilterExpression=Attr("session_id").eq(session_id)
    )
    user_items = user_resp.get("Items", [])
    if not user_items:
        return build_response(404, {"error": "User not found"})

    user = user_items[0]
    email = user.get("email")
    user_id = user.get("id")
    org_id = user.get("org_id")
    project_id = user.get("project_id")
    org_name = user.get("organization_name")
    project_name = user.get("project_name")

    # ---- 2. Scrape website ----
    links = scrape_links(website)
    links = [link for link in links if link.startswith(website)]

    all_content = ""
    for idx, link in enumerate(links, start=1):
        page_content = scrape_page_content(link)
        all_content += f"\n\n--- Page: {link} ---\n{page_content}"

    # ---- 3. Structure data ----
    prompt_structuring = f"""
    You are an expert information architect.
    Convert the following unstructured data into a structured format without losing any details.
    {all_content}
    """
    structured_info = llm_calling(prompt_structuring)

    # ---- 4. Create business profile ----
    prompt_profile = f"""
    You are an expert business analyst.
    Using the structured information below, create a professional company profile.

    {structured_info}

    Return the output using these exact headings:
    Business Name:
    Industry / Sector:
    Mission:
    Vision:
    Products or Services Offered:
    Target Market:
    Value Proposition:
    Company Overview:
    """
    structured_profile = llm_calling(prompt_profile)

    # ---- 5. Save profile to S3 ----
    s3_key = f"{org_id}/{project_id}/{user_id}/web_scraping.txt"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=structured_profile.encode("utf-8"),
        ContentType="text/plain"
    )

    s3_url = f"s3://{BUCKET_NAME}/{s3_key}"

    # ---- 6. Return response ----
    response_body = {
        "website": website,
        "organization_name": org_name,
        "project_name": project_name,
        "org_id": org_id,
        "project_id": project_id,
        "user_id": user_id,
        "email": email,
        "s3_url": s3_url,
        "structured_profile": structured_profile
    }

    return build_response(200, response_body)


# ---------- HELPER ----------
def build_response(status, body):
    """Helper to build API Gateway compatible response."""
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body)
    }
