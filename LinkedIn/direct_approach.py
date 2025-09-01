import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\.env")

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"  # Can be any redirect URI you've registered

# -------------------------------
# Step 1: Generate authorization URL
# -------------------------------
SCOPES = ["openid", "profile", "email", "w_member_social", "r_events", "rw_events"]
auth_params = {
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": " ".join(SCOPES)
}
auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"

print("Go to this URL in your browser and authorize the app:")
print(auth_url)

# -------------------------------
# Step 2: Get authorization code from user
# -------------------------------
auth_code = input("Paste the authorization code here: ").strip()

# -------------------------------
# Step 3: Exchange code for access token
# -------------------------------
token_data = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": REDIRECT_URI,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}
token_res = requests.post(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data=token_data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
).json()

access_token = token_res.get("access_token")
if not access_token:
    raise Exception(f"Error getting access token: {token_res}")

print("✅ Access Token acquired!")
print(access_token)

# -------------------------------
# Step 4: Fetch user profile & email
# -------------------------------
headers = {"Authorization": f"Bearer {access_token}"}

profile = requests.get("https://api.linkedin.com/v2/me", headers=headers).json()
email_resp = requests.get(
    "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
    headers=headers
).json()

linkedin_id = profile.get("id")
first_name = profile.get("localizedFirstName")
last_name = profile.get("localizedLastName")
email = email_resp.get("elements")[0]["handle~"]["emailAddress"]

print(f"LinkedIn ID: {linkedin_id}")
print(f"Name: {first_name} {last_name}")
print(f"Email: {email}")

# -------------------------------
# Step 5: Create a post
# -------------------------------
post_text = input("Enter the post text: ").strip()

post_payload = {
    "author": f"urn:li:person:{linkedin_id}",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": post_text},
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
}

post_res = requests.post(
    "https://api.linkedin.com/v2/ugcPosts",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    },
    json=post_payload
)

if post_res.status_code == 201:
    print("✅ Post published successfully!")
    print(post_res.json())
else:
    print("❌ Failed to post")
    print(post_res.status_code, post_res.text)
