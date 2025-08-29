import os
import pathlib
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRET_FILE = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

def main():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=8080)  # Opens browser once for login

    with open("sender_token.json", "w") as token:
        token.write(creds.to_json())

    print("✅ sender_token.json created successfully for ahmed.kavtech@gmail.com")

if __name__ == "__main__":
    main()
