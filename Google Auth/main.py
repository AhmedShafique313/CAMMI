import os, pathlib, base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from email.mime.text import MIMEText

# Path to your client_secret.json from Google Cloud Console
CLIENT_SECRET_FILE = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

# Scopes: profile info + email + Gmail send
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
    "https://www.googleapis.com/auth/gmail.send"
]

def create_message(sender, to, subject, message_text):
    """Create a raw email message."""
    message = MIMEText(message_text, "plain", "utf-8")
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return {"raw": raw_message}

def get_credentials(token_file):
    """Load or request OAuth credentials and save them into a file."""
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    return creds

def get_user_info():
    """Ask the user to log in and return their Google profile info."""
    creds = get_credentials("user_token.json")   # user’s token
    service = build("oauth2", "v2", credentials=creds)
    user_info = service.userinfo().get().execute()
    return user_info   # contains email, name, id, etc.

# def send_from_fixed_account(to_email, user_name):
#     """Sends email always from ahmed.kavtech@gmail.com."""
#     creds = get_credentials("sender_token.json")   # sender’s token
#     service = build("gmail", "v1", credentials=creds)

#     sender = "ahmed.kavtech@gmail.com"   # fixed sender account
#     subject = "Welcome to CAMMI!"
#     body = f"Hello {user_name},\n\nYou are successfully authenticated with Google! 🎉\n\n– The CAMMI Team"

#     message = create_message(sender, to_email, subject, body)
#     send_message = service.users().messages().send(userId="me", body=message).execute()
#     print("📩 Email sent successfully:", send_message["id"])

def main():
    # Step 1: User logs in with Google (e.g. ahmed.shafique.professional@gmail.com)
    user_info = get_user_info()
    print(f"✅ Logged in user: {user_info['email']} ({user_info['name']})")

    # Step 2: Send them a welcome email from fixed account
    # send_from_fixed_account(user_info["email"], user_info["name"])

if __name__ == "__main__":
    main()
