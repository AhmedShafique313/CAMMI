import json, uuid
import boto3
import requests
import cachecontrol
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests

# ------------------------
# Config
# ------------------------
CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = "callback api"

ZOHO_EMAIL = "info@cammi.ai"
ZOHO_APP_PASSWORD = ""
USERS_TABLE = "google_oauth_table"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST"
}

# ------------------------
# DynamoDB setup
# ------------------------
dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table(USERS_TABLE)

# ------------------------
# OAuth flow
# ------------------------
flow = Flow.from_client_config(
    {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [REDIRECT_URI],
        }
    },
    scopes=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    redirect_uri=REDIRECT_URI,
)

# ------------------------
# Send welcome email
# ------------------------
def send_welcome_email(user_info):
    subject = "Welcome to CAMMI - Your AI-Powered Marketing Co-Pilot!"
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height:1.6; color:#333;">
        <h2>👋 Hello {user_info['name']},</h2>
        <p>Welcome to <b>CAMMI</b>! We're thrilled to have you on board.</p>
        <p>CAMMI simplifies your marketing workflow — strategy, content creation, scheduling, and tracking.</p>
        <h3>🚀 To get started:</h3>
        <ol>
          <li>Upload your brand collateral.</li>
          <li>Chat with CAMMI for strategies or content.</li>
          <li>Approve outputs before posting.</li>
        </ol>
        <p>💡 Need help? Email us at <a href="mailto:info@cammi.ai">info@cammi.ai</a></p>
        <p style="margin-top:20px;">Cheers,<br><b>The CAMMI Team</b></p>
      </body>
    </html>
    """
    msg = MIMEMultipart("alternative")
    msg["From"] = f"CAMMI Team <{ZOHO_EMAIL}>"
    msg["To"] = user_info["email"]
    msg["Subject"] = subject
    msg.attach(MIMEText("Welcome to CAMMI!", "plain"))
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP_SSL("smtp.zoho.com", 465) as server:
        server.login(ZOHO_EMAIL, ZOHO_APP_PASSWORD)
        server.sendmail(ZOHO_EMAIL, user_info["email"], msg.as_string())

# ------------------------
# Login handler
# ------------------------
def login_lambda(event, context):
    try:
        authorization_url, state = flow.authorization_url()
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "login_url": authorization_url,
                "state": state,
                "event": event
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }

# ------------------------
# Callback handler
# ------------------------
def callback_lambda(event, context):
    try:
        # Get query parameters or JSON body
        query_params = event.get("queryStringParameters", {}) or {}
        if event.get("body"):
            try:
                body_data = json.loads(event["body"])
                query_params.update(body_data)
            except Exception as e:
                print("Failed to parse body:", str(e))

        # Construct authorization_response (URL-encoded)
        from urllib.parse import urlencode
        authorization_response = REDIRECT_URI + "?" + urlencode(query_params)

        # Exchange code for tokens
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        # Prepare request to verify ID token
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)

        # Verify token and get user info
        id_info = id_token.verify_oauth2_token(
            id_token=credentials.id_token,
            request=token_request,
            audience=CLIENT_ID,
        )
        session_id = str(uuid.uuid4())

        # Build user info
        user_info = {
            "sub": id_info.get("sub"),
            "name": id_info.get("name"),
            "email": id_info.get("email"),
            "picture": id_info.get("picture"),
            "locale": id_info.get("locale"),
            "access_token": credentials.token,
            "expiry": str(credentials.expiry),
            "session_id": str(session_id),
            "onboarding_status": "true"
        }

        # Save to DynamoDB
        users_table.put_item(Item=user_info)
        send_welcome_email(user_info)

        # redirect to the dashboard
        # dashboard_url = "https://yourdomain.com/dashboard"

        # return {
        #     "statusCode": 302,
        #     "headers": {
        #         "Location": dashboard_url,
        #         **CORS_HEADERS
        #     },
        #     "body": ""
        # }
        # Return success message
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": "Login successful",
                "user": user_info
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e), "event": event})
        }

# ------------------------
# Main Lambda handler
# ------------------------
def lambda_handler(event, context):
    # Use path, handle API Gateway stage (/test)
    path = event.get("requestContext", {}).get("http", {}).get("path", "") \
        or event.get("path", "")

    # Debugging
    print("EVENT PATH:", path)

    # Use endswith to handle stage prefix
    if path.endswith("/login"):
        return login_lambda(event, context)
    elif path.endswith("/callback"):
        return callback_lambda(event, context)
    else:
        return {
            "statusCode": 404,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "Not found"})
        }
