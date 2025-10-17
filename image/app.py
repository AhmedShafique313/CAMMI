import os
from google import genai

# Point to your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\image\service-account.json"

# Initialize the client
client = genai.Client(
    vertexai=True,
    project="lyrical-marker-474614-s5",
    location="us-central1",
)

# --- List available models ---
print("🔍 Available models in your project:")
try:
    models = client.models.list()
    for m in models:
        print(" -", m.name)
except Exception as e:
    print("⚠️ Could not list models:", e)

# --- Generate image with Imagen 4.0 ---
print("\n🎨 Generating image with Imagen 4.0...")
try:
    result = client.models.generate_images(
        model="publishers/google/models/imagen-4.0-ultra-generate-preview-06-06",
        prompt="A fantasy landscape, moonlit, with a castle on a hill, in cinematic style",
    )

    # Save single image
    output_path = "output.png"
    with open(output_path, "wb") as f:
        f.write(result.images[0].image_bytes)

    print(f"✅ Image saved as {output_path}")

except Exception as e:
    print("❌ Image generation failed:", e)
