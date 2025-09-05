from flask import Flask, request, render_template_string, redirect
import requests

app = Flask(__name__)

# 🔧 Replace these with your LinkedIn credentials
ACCESS_TOKEN = "AQXpFiYRfVUF9WuofEaqSqIIGkOcZHbuSkkUK5BMYndWY-5t6YwlmgWYA1nYjWo-Xn7ESTbn4SpP4ImDBR6T0JXFks7r18clXWd5aNiFtfRAPEt3mdzpEGUsTpx-VwBJZ8F0KuVLVL8gNH9in0-MiERyx0cQ45tOD4pntdRjvAlHY33lCY43jqPAOwC7KnhO0pD6jzFlH8XcNQzK8il5QxXlexzgdDWs5Us9uLIeIhyRTSK-y-Xg808gi5Sx_RnYhrkHWjO8WM7Et_9VbJ5LfpNTME2hm8VNgO9wYiw7IsFQ89NM6SIfrHm7NrUZ8rS0Nb9FF70Td-N12iWY4s9z8i8ctbGQ_Q"
PERSON_SUB = "BiXLFEGlD6"  # e.g. BiXLFEGlD6

# Simple HTML UI
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>LinkedIn Image Poster</title>
</head>
<body style="font-family: Arial; margin: 50px;">
    <h2>Post Image to LinkedIn</h2>
    <form method="POST" enctype="multipart/form-data" action="/post">
        <label>Message:</label><br>
        <textarea name="message" rows="4" cols="50" required></textarea><br><br>
        
        <label>Select Image:</label><br>
        <input type="file" name="image" accept="image/*" required><br><br>
        
        <button type="submit">Upload & Post</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_FORM)


@app.route("/post", methods=["POST"])
def post_to_linkedin():
    message = request.form.get("message")
    file = request.files["image"]

    if not file:
        return "No file uploaded", 400

    # Step 1: Register upload
    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": f"urn:li:person:{PERSON_SUB}",
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }
    reg_res = requests.post(register_url, headers=headers, json=payload)
    if reg_res.status_code != 200:
        return f"Register upload failed: {reg_res.text}", 400

    reg_data = reg_res.json()
    upload_url = reg_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset = reg_data["value"]["asset"]

    # Step 2: Upload binary image
    upload_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": file.mimetype
    }
    upload_res = requests.put(upload_url, headers=upload_headers, data=file.read())
    if upload_res.status_code not in [200, 201]:
        return f"Image upload failed: {upload_res.text}", 400

    # Step 3: Create UGC post
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    post_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    post_payload = {
        "author": f"urn:li:person:{PERSON_SUB}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": message},
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "media": asset,
                        "description": {"text": "Uploaded via Flask app"},
                        "title": {"text": "Flask Upload"}
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    post_res = requests.post(post_url, headers=post_headers, json=post_payload)
    if post_res.status_code not in [200, 201]:
        return f"Post creation failed: {post_res.text}", 400

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
