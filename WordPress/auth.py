import requests
from requests.auth import HTTPBasicAuth

site_url = "https://playground.wordpress.net"
username = "admin"
app_password = "vnoY lJrz pDiy CFKf IftD cYkw"

endpoint = f"{site_url}/wp-json/wp/v2/users/me"
response = requests.get(endpoint, auth=HTTPBasicAuth(username, app_password))

print("Status Code:", response.status_code)
print("Response:", response.text)
