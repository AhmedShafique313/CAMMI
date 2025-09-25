import requests, json, base64

# Your API secret key from ConvertAPI dashboard
API_KEY = ""

url = "https://v2.convertapi.com/convert/docx/to/pdf?Secret=" + API_KEY

files = {"File": open(r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\doc\gtm.docx", "rb")}
response = requests.post(url, files=files)
result = response.json()

print(json.dumps(result, indent=2))

if "Files" in result:
    file_info = result["Files"][0]

    if "Url" in file_info:
        # Case 1: API returns a hosted URL
        print("PDF available at:", file_info["Url"])

    elif "FileData" in file_info:
        # Case 2: API returned the Base64 file
        pdf_bytes = base64.b64decode(file_info["FileData"])
        with open("output.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("PDF saved locally as output.pdf")

    else:
        print("Unexpected file response:", file_info)

else:
    print("Error:", result)