import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\.env")
 
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)
 
completion = client.chat.completions.create(
    model="openai/gpt-oss-120b:fireworks-ai",
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
)
 
print(completion.choices[0].message.content)