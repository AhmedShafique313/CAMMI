import os, pathlib, requests, base64, json
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token, credentials as google_credentials
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from google.oauth2 import service_account

app = Flask("Google Login App")
app.secret_key = "CodeSpecialist.com"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "334771385468-n1oc9t8relolp47904b4hojsfosglcek.apps.googleusercontent.com" #fake id
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

# scopes for permissions ok we need these permissions to work on Google Cloud Console

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", 
            "https://www.googleapis.com/auth/userinfo.email", 
            "openid",
            "https://www.googleapis.com/auth/gmail.send"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


# @app.route("/login")
# def login():
#     authorization_url, state = flow.authorization_url()
#     session["state"] = state
#     return redirect(authorization_url)


# @app.route("/callback")
# def callback():
#     flow.fetch_token(authorization_response=request.url)

#     if not session["state"] == request.args["state"]:
#         abort(500)

#     credentials = flow.credentials
#     request_session = requests.session()
#     cached_session = cachecontrol.CacheControl(request_session)
#     token_request = google.auth.transport.requests.Request(session=cached_session)

#     id_info = id_token.verify_oauth2_token(
#         id_token=credentials._id_token,
#         request=token_request,
#         audience=GOOGLE_CLIENT_ID
#     )

#     # Save user info
#     session["google_id"] = id_info.get("sub")
#     session["name"] = id_info.get("name")
#     session["email"] = id_info.get("email")

#     # ✅ Save credentials for Gmail API
#     session["credentials"] = {
#         "token": credentials.token,
#         "refresh_token": credentials.refresh_token,
#         "token_uri": credentials.token_uri,
#         "client_id": credentials.client_id,
#         "client_secret": credentials.client_secret,
#         "scopes": credentials.scopes
#     }

#     return redirect("/userinfo")



# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/")


# @app.route("/")
# def index():
#     return "Hello World <a href='/login'><button>Login</button></a>"


# @app.route("/userinfo")
# def userinfo():
#     if "google_id" not in session:
#         return redirect("/login")
    
#     return f"""
#     <h1>User Info</h1>
#     <p><b>Name:</b> {session['name']}</p>
#     <p><b>Email:</b> {session['email']}</p>
#     <p><b>Google ID:</b> {session['google_id']}</p>
#     <a href='/send_email'><button>Send Welcome Email</button></a>
#     <br><br>
#     <a href='/logout'><button>Logout</button></a>
#     """

# # helper for raw email message
# def create_message(sender, to, subject, message_text):
#     from email.mime.text import MIMEText
#     import base64

#     message = MIMEText(message_text, "plain", "utf-8")
#     message["to"] = to
#     message["from"] = sender
#     message["subject"] = subject

#     raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
#     return {"raw": raw_message}


# @app.route("/send_email")
# def send_email():
#     if "credentials" not in session:
#         return redirect("/login")

#     try:
#         from google.oauth2 import credentials as google_credentials
#         from googleapiclient.discovery import build

#         creds = google_credentials.Credentials(**session["credentials"])
#         service = build("gmail", "v1", credentials=creds)

#         sender = session["email"]
#         to = "hamadnasir008@gmail.com"   # change to test email
#         subject = "Welcome!"
#         body = f"Hello {session['name']}, this is a test email sent using the Gmail API."

#         message = create_message(sender, to, subject, body)

#         # Send email
#         send_message = service.users().messages().send(userId="me", body=message).execute()
#         print("📩 Email sent successfully:", send_message)

#         return f"✅ Email sent to {to}!<br>Message ID: {send_message['id']}<br><a href='/userinfo'>Back</a>"

#     except Exception as e:
#         import traceback
#         error_details = traceback.format_exc()
#         print("❌ Error sending email:", error_details)
#         return f"❌ Failed to send email:<br><pre>{error_details}</pre>"


# helper for Gmail API message
def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text, "plain", "utf-8")
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return {"raw": raw_message}

@app.route("/")
def index():
    return "Welcome to CAMMI! <a href='/login'><button>Sign in with Google</button></a>"


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    # store user info
    user_info = {
        "google_id": id_info.get("sub"),
        "name": id_info.get("name"),
        "email": id_info.get("email")
    }

    with open("userinfo.json", "w", encoding="utf-8") as f:
        json.dump(user_info, f, indent=4)

    # send email from info@cammi.ai
    try:
        SERVICE_ACCOUNT_FILE = os.path.join(pathlib.Path(__file__).parent, "service_account.json")
        SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        # IMPORTANT: domain-wide delegation must be enabled for info@cammi.ai
        delegated_creds = creds.with_subject("info@cammi.ai")

        service = build("gmail", "v1", credentials=delegated_creds)

        subject = "Welcome to CAMMI!"
        body = f"Hello {user_info['name']},\n\nThanks for signing in to CAMMI! 🚀"

        message = create_message("info@cammi.ai", user_info["email"], subject, body)
        service.users().messages().send(userId="me", body=message).execute()

        return f"✅ Welcome email sent to {user_info['email']} and user info saved."

    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"
    
# till here
if __name__ == "__main__":
    app.run(debug=True)