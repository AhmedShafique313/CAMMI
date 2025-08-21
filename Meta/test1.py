import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\.env")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={ACCESS_TOKEN}"
res = requests.get(url).json()
print(res)
