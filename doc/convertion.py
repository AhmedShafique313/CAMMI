import requests, json, base64, os
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\.env")

# Your API secret key from ConvertAPI dashboard
CONVERTAPI_KEY = os.getenv("CONVERTAPI_KEY")

url = "https://v2.convertapi.com/convert/docx/to/pdf?Secret=" + CONVERTAPI_KEY

files = {"File": open(r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\doc\gtm.docx", "rb")}
response = requests.post(url, files=files)
result = response.json()

if "Files" in result and "FileData" in result["Files"][0]:
    base64_pdf = result["Files"][0]["FileData"]
    print(base64_pdf)
else:
    print("Invalid document")