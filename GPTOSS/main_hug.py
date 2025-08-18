import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\.env")
 
client = InferenceClient(
    provider="fireworks-ai",
    api_key=os.environ["HF_TOKEN"],
)
 
completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
)
 
print(completion.choices[0].message.content)