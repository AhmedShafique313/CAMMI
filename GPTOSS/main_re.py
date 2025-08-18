import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\.env")
 
API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
}
 
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()
 
response = query({
    "messages": [
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
    "model": "openai/gpt-oss-120b:fireworks-ai"
})
 
print(response["choices"][0]["message"]["content"])