import requests
from requests.auth import HTTPBasicAuth

def get_user_info(site_url, username, app_password):
    """Fetch WordPress user info using App Passwords"""
    endpoint = f"{site_url}/wp-json/wp/v2/users/me"
    response = requests.get(endpoint, auth=HTTPBasicAuth(username, app_password))
    return response
