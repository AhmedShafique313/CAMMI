import json
import boto3
import requests
import cachecontrol
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests

# ✅ Hardcoded configs
GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""
ZOHO_EMAIL = "info@cammi.ai"  # fake
ZOHO_APP_PASSWORD = ""
USERS_TABLE = ""

# DynamoDB client
dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table(USERS_TABLE)

# Common CORS headers
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST"
}

# OAuth flow
flow = Flow.from_client_secrets_file(
    "client_secret.json",
    scopes=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    redirect_uri="https://your-api-gateway-url.com/callback",  # fake
)

def send_welcome_email(user_info):
    subject = "Welcome to CAMMI - Your AI-Powered Marketing Co-Pilot!"

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height:1.6; color:#333;">
        <h2>👋 Hello {user_info['name']},</h2>
        <p>Welcome to <b>CAMMI</b>! We're thrilled to have you on board.</p>
        <p>
          CAMMI is designed to simplify your marketing workflow —
          from <b>strategy</b> and <b>content creation</b> 
          to <b>scheduling</b> and <b>performance tracking</b>,
          all in one intelligent, conversational platform.
        </p>
        <h3>🚀 To get started:</h3>
        <ol>
          <li>Upload your brand collateral so CAMMI can learn your unique voice.</li>
          <li>Ask away - Request a GTM strategy, generate content, or schedule posts—just chat with CAMMI like a teammate.</li>
          <li>Approve with confidence - Every output is reviewed by you before anything goes live.</li>
        </ol>
        <p>
          💡 Need help? Our support team is just a message away at 
          <a href="mailto:info@cammi.ai">info@cammi.ai</a>
        </p>
        <p style="margin-top:20px;">Cheers,<br><b>The CAMMI Team</b></p>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = f"CAMMI Team <{ZOHO_EMAIL}>"
    msg["To"] = user_info["email"]
    msg["Subject"] = subject

    msg.attach(MIMEText("Welcome to CAMMI! Please use an email client that supports HTML.", "plain"))
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP_SSL("smtp.zoho.com", 465) as server:
        server.login(ZOHO_EMAIL, ZOHO_APP_PASSWORD)
        server.sendmail(ZOHO_EMAIL, user_info["email"], msg.as_string())


# ------------------------
# Lambda for /login
# ------------------------
def login_lambda(event, context):
    authorization_url, state = flow.authorization_url()

    return {
        "statusCode": 200,
        "headers": CORS_HEADERS,
        "body": json.dumps({
            "login_url": authorization_url,
            "state": state,
            "event": event  # ✅ Always include input event
        })
    }


# ------------------------
# Lambda for /callback
# ------------------------
def callback_lambda(event, context):
    # Collect query params + body data
    query_params = event.get("queryStringParameters", {}) or {}
    if event.get("body"):
        body_data = json.loads(event["body"])
        query_params.update(body_data)

    # Build Google authorization response
    authorization_response = "https://your-api-gateway-url.com/callback?" + "&".join(
        [f"{k}={v}" for k, v in query_params.items()]
    )

    # Exchange code for tokens
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    # Verify token
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID,
    )

    # Build user info
    user_info = {
        "sub": id_info.get("sub"),
        "name": id_info.get("name"),
        "email": id_info.get("email"),
        "picture": id_info.get("picture"),
        "locale": id_info.get("locale"),
        "access_token": credentials.token,
        "expiry": str(credentials.expiry),
    }

    # Save in DynamoDB (partition key = email)
    users_table.put_item(Item=user_info)

    # Send welcome email
    send_welcome_email(user_info)

    # ✅ Return user info and original event
    return {
        "statusCode": 200,
        "headers": CORS_HEADERS,
        "body": json.dumps({
            "message": "Login successful",
            "user": user_info,
            "event": event
        })
    }
