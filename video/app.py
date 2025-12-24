import time,requests
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load the .env (optional, still good for other variables)
load_dotenv(dotenv_path=r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\.env")

# Explicitly set the credentials path in code
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\video\secrets\gcp-veo-secrets.json"

# Initialize client
client = genai.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    vertexai=True
)

prompt = """
A professional white woman standing in a modern office environment, speaking directly to the camera.
She is confident, friendly, and enthusiastic. She explains: 
'Hi! I’m here to introduce you to CAMMI, the AI platform that helps you generate content, ideas, and videos in seconds.
With CAMMI, you can streamline your creative workflow and bring your ideas to life faster than ever.'
She gestures naturally while speaking, maintaining eye contact with the viewer.
The background is bright and clean, resembling a corporate tech office.
"""

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
)

while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)


generated_video = operation.response.generated_videos[0].video
generated_video.save("dialogue_example.mp4")
print("Generated video saved to dialogue_example.mp4")