import os
import requests
from flask import Flask, redirect, request, session, url_for, render_template_string
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\.env")

app = Flask(__name__)
app.secret_key = "super_secret_key"  # change for production

# LinkedIn App credentials
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"

# LinkedIn OAuth URLs
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"


@app.route("/")
def home():
    return render_template_string('''
        <h2>Login with LinkedIn</h2>
        <a href="{{ url_for('login') }}">
            <button>Login with LinkedIn</button>
        </a>
    ''')


@app.route("/login")
def login():
    # Redirect user to LinkedIn OAuth
    auth_url = (
        f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=openid%20profile%20email%20w_member_social"
    )
    return redirect(auth_url)


@app.route("/callback")
def callback():
    # Get authorization code from LinkedIn
    code = request.args.get("code")
    if not code:
        return "No code provided", 400

    # Exchange code for access token
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(
        TOKEN_URL,
        data=token_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response_json = response.json()

    access_token = response_json.get("access_token")
    if not access_token:
        return f"Error getting token: {response_json}", 400

    session["access_token"] = access_token
    headers = {"Authorization": f"Bearer {access_token}"}

    # Fetch user profile via OpenID Connect
    userinfo = requests.get(USERINFO_URL, headers=headers).json()

    return render_template_string('''
        <h2>Welcome {{userinfo.get("name")}}</h2>
        <p><b>LinkedIn ID:</b> {{userinfo.get("sub")}}</p>
        <p><b>Email:</b> {{userinfo.get("email")}}</p>
        <img src="{{userinfo.get("picture")}}" alt="Profile Picture" width="120">
        <p><b>Access Token:</b> {{token}}</p>
    ''', userinfo=userinfo, token=access_token)


if __name__ == "__main__":
    app.run(debug=True)
