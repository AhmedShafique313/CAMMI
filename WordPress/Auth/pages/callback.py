import streamlit as st
import requests

APP_DOMAIN = "http://localhost:8501"

st.title("🔄 OAuth2 Callback from WordPress")

query_params = st.query_params
auth_code = query_params.get("code", [None])[0]
state = query_params.get("state", [None])[0]

if not auth_code:
    st.error("No authorization code received.")
else:
    st.success("Authorization code received!")

    site_url = st.session_state.get("site_url", "")
    token_url = f"{site_url}/oauth/token"

    response = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": f"{APP_DOMAIN}/pages/callback",
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET"
    })

    if response.status_code == 200:
        token_data = response.json()
        st.session_state["wp_token"] = token_data
        st.session_state["wp_connected"] = True
        st.success("✅ Connected to WordPress successfully!")
        st.json(token_data)
    else:
        st.error("Failed to fetch access token")
        st.text(response.text)
