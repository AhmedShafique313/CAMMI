import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

st.title("🔑 Connect WordPress via Application Password")

site_url = st.text_input("WordPress Site URL", placeholder="https://example.com")
username = st.text_input("WordPress Username")
app_password = st.text_input("WordPress Application Password", type="password")

if st.button("Connect with App Password"):
    if site_url and username and app_password:
        endpoint = f"{site_url}/wp-json/wp/v2/users/me"
        response = requests.get(endpoint, auth=HTTPBasicAuth(username, app_password))

        if response.status_code == 200:
            user_data = response.json()
            st.session_state["wp_user"] = user_data
            st.session_state["wp_auth"] = (username, app_password)
            st.session_state["site_url"] = site_url
            st.session_state["wp_connected"] = True
            st.success("✅ Connected to WordPress successfully!")
            st.json(user_data)
        else:
            st.error("❌ Connection failed")
            st.text(response.text)
    else:
        st.error("Please fill all fields.")
