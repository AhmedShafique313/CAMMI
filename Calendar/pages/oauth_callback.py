import streamlit as st
from google_auth_oauthlib.flow import Flow
import os, json

CLIENT_SECRETS_FILE = r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\client_secret.json"
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

st.set_page_config(page_title="Google OAuth Callback", page_icon="🔑")
st.title("🔑 Google Login")

if "code" not in st.query_params:
    # Step 1: Create login link
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8501/oauth_callback"
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    st.markdown(f"[👉 Click here to sign in with Google]({auth_url})")

else:
    # Step 2: Handle redirect (Google appends ?code=... here)
    code = st.query_params["code"]

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8501/oauth_callback"
    )
    flow.fetch_token(code=code)
    creds = flow.credentials

    # Save token.json for reuse
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    st.success("✅ Login successful!")
    st.write("Now go back to the [main app](http://localhost:8501/) to use Google Calendar.")
