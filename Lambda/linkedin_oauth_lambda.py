import json
import urllib3, boto3
from urllib.parse import urlencode
 
http = urllib3.PoolManager()
 
CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = "https://o3uzr46ro5.execute-api.us-east-1.amazonaws.com/cammi-dev/callback"
 
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"

dynamodb = boto3.resource("dynamodb")
user_table = dynamodb.Table("linkedin_user_table")
 
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization"
}
  
def lambda_handler(event, context):
    """Main Lambda handler for LinkedIn OAuth via API Gateway"""
    path = event.get("path")
    query = event.get("queryStringParameters") or {}

    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": ""
        }
 
    if path == "/":
        return response_html("""
            <h2>Login with LinkedIn</h2>
            <a href="/login"><button>Login with LinkedIn</button></a>
        """)
 
    elif path == "/linkedinlogin":
        params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": "openid profile email w_member_social",
        }
        login_url = f"{AUTH_URL}?{urlencode(params)}"
        return {
            "statusCode": 200,
            "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
            "body": json.dumps({"login_url": login_url})
        }
 
    elif path == "/callback":
        code = query.get("code")
        if not code:
            return response_html("<h3>Error: No code provided</h3>", 400)
 
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        encoded_data = urlencode(token_data)
 
        token_res = http.request(
            "POST",
            TOKEN_URL,
            body=encoded_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_json = json.loads(token_res.data.decode("utf-8"))
        access_token = token_json.get("access_token")
 
        if not access_token:
            return response_html(f"<h3>Error getting token: {token_json}</h3>", 400)
 
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_res = http.request("GET", USERINFO_URL, headers=headers)
        userinfo = json.loads(userinfo_res.data.decode("utf-8"))

        item = {"sub": userinfo.get("sub"), "access_token": access_token}
        optional_fields = ["name", "given_name", "family_name", "picture", "locale", "email", "email_verified"]
        for field in optional_fields:
            if userinfo.get(field) is not None:
                item[field] = userinfo[field]
 
        user_table.put_item(Item=item)

        html_snippet = f"""
            <h2>Welcome {userinfo.get('name', '')}</h2>
            <p><b>LinkedIn ID:</b> {userinfo.get('sub')}</p>
            <p><b>Email:</b> {userinfo.get('email', 'N/A')}</p>
            <img src="{userinfo.get('picture', '')}" alt="Profile Picture" width="120">
            <p><b>Access Token:</b> {access_token}</p>
        """

        # redirect_url = f"https://cammi-yot6.vercel.app/dashboard?sub={userinfo.get('sub')}"
        redirect_url = f"http://localhost:3000/dashboard/scheduler/linkedin?sub={userinfo.get('sub')}"
        return {
            "statusCode": 302,
            "headers": {
                **CORS_HEADERS,
                "Location": redirect_url
            },
            "body": ""
        }
 
    return response_html("<h3>Not Found</h3>", 404)

def response_html(html, status=200):
    """Helper to return JSON responses with HTML content in 'body' field"""
    return {
        "statusCode": status,
        "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
        "body": json.dumps({"html": html})
    }