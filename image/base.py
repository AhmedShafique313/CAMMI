import base64

def main():
    with open("base64.txt", "r", encoding="utf-8") as f:
        image_base64 = f.read().strip()

    if image_base64.startswith("data:image"):
        image_base64 = image_base64.split(",")[1]

    image_bytes = base64.b64decode(image_base64)
    with open("output.png", "wb") as f:
        f.write(image_bytes)

    print("✅ Image saved as output.png")

if __name__ == "__main__":
    main()
