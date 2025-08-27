import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

st.title("✍️ Publish a Blog Post to WordPress")

if "wp_connected" not in st.session_state or not st.session_state["wp_connected"]:
    st.error("⚠️ Please connect your WordPress site first.")
    st.stop()

site_url = st.session_state["site_url"]

title = st.text_input("Post Title")
content = st.text_area("Post Content")
publish_btn = st.button("🚀 Publish Post")

if publish_btn:
    if not title or not content:
        st.error("Please provide both title and content.")
    else:
        headers = {"Content-Type": "application/json"}

        # Case 1: OAuth2
        if "wp_token" in st.session_state:
            token = st.session_state["wp_token"]["access_token"]
            headers["Authorization"] = f"Bearer {token}"
            response = requests.post(
                f"{site_url}/wp-json/wp/v2/posts",
                headers=headers,
                json={"title": title, "content": content, "status": "publish"}
            )

        # Case 2: App Password
        elif "wp_auth" in st.session_state:
            username, app_password = st.session_state["wp_auth"]
            response = requests.post(
                f"{site_url}/wp-json/wp/v2/posts",
                auth=HTTPBasicAuth(username, app_password),
                headers=headers,
                json={"title": title, "content": content, "status": "publish"}
            )

        if response.status_code in [200, 201]:
            st.success("✅ Post published successfully!")
            st.json(response.json())
        else:
            st.error("❌ Failed to publish post")
            st.text(response.text)
