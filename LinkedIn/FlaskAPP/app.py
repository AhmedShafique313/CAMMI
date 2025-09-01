import os
import requests
from flask import Flask, redirect, request, session, url_for, render_template_string
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta, timezone

load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\.env")

app = Flask(__name__)
app.secret_key = "super_secret_key"  # change for production

# LinkedIn App credentials
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

from dotenv import load_dotenv
import os

# Load .env file
load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FLASK_SECRET = os.getenv("FLASK_SECRET")
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")

print("Supabase URL:", SUPABASE_URL)   # Debug
print("Supabase Key exists:", SUPABASE_KEY is not None)  # Debug



import os
import requests
from flask import Flask, redirect, request, session, url_for, render_template_string
from supabase import create_client, Client
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load env variables
load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\.env")

# Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# LinkedIn App credentials
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# OAuth endpoints
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
PROFILE_URL = "https://api.linkedin.com/v2/me"
EMAIL_URL = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"


@app.route("/")
def home():
    return '<a href="/login">Login with LinkedIn</a>'


@app.route("/login")
def login():
    auth_link = (
        f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=r_liteprofile r_emailaddress w_member_social"
    )
    return redirect(auth_link)


@app.route("/callback")
def callback():
    code = request.args.get("code")

    # Exchange code for access token
    token_res = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()

    access_token = token_res.get("access_token")
    expires_in = token_res.get("expires_in", 0)
    expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))

    # Fetch profile info
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get(PROFILE_URL, headers=headers).json()
    email_data = requests.get(EMAIL_URL, headers=headers).json()
    email = email_data["elements"][0]["handle~"]["emailAddress"]

    linkedin_id = profile.get("id")
    first_name = profile.get("localizedFirstName", "")
    last_name = profile.get("localizedLastName", "")

    # Save to Supabase
    data = {
        "linkedin_id": linkedin_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "access_token": access_token,
        "expires_at": expires_at.isoformat(),  # ✅ fix for Supabase date field
    }

    insert_res = supabase.table("linkedin_tokens").insert(data).execute()
    print("Inserted:", insert_res)

    # Store session
    session["user"] = data

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect("/")

    html = f"""
    <h2>Welcome {user['first_name']} {user['last_name']}</h2>
    <p>Email: {user['email']}</p>
    <p>LinkedIn ID: {user['linkedin_id']}</p>
    <p>Access Token Expires At: {user['expires_at']}</p>
    <a href="/schedule">Schedule a Post</a>
    """
    return render_template_string(html)


@app.route("/schedule")
def schedule():
    return """
    <h2>Schedule a LinkedIn Post</h2>
    <form method="post" action="/schedule_post">
        <textarea name="content" rows="4" cols="50" placeholder="Write your post..."></textarea><br><br>
        <input type="datetime-local" name="schedule_time"><br><br>
        <button type="submit">Schedule</button>
    </form>
    """


@app.route("/schedule_post", methods=["POST"])
def schedule_post():
    content = request.form["content"]
    schedule_time = request.form["schedule_time"]

    user = session.get("user")
    if not user:
        return redirect("/")

    # Save scheduled post to Supabase
    data = {
        "linkedin_id": user["linkedin_id"],
        "content": content,
        "schedule_time": schedule_time,
    }

    res = supabase.table("scheduled_posts").insert(data).execute()
    print("Scheduled:", res)

    return "<h3>Post Scheduled Successfully!</h3><a href='/dashboard'>Back to Dashboard</a>"


if __name__ == "__main__":
    app.run(debug=True)
