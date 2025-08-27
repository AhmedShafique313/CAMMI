import streamlit as st
import webbrowser
import uuid

APP_DOMAIN = "http://localhost:8501"   # Replace with deployed app URL

st.title("🔑 Connect WordPress via OAuth 2.0")

site_url = st.text_input("Enter your WordPress site URL", placeholder="https://example.com")

if st.button("Connect with OAuth 2.0"):
    if not site_url:
        st.error("Please enter your WordPress site URL")
    else:
        # Unique state
        state = str(uuid.uuid4())
        st.session_state["oauth_state"] = state
        st.session_state["site_url"] = site_url

        # Example OAuth plugin path
        auth_url = f"{site_url}/oauth/authorize" \
                   f"?response_type=code&client_id=YOUR_CLIENT_ID" \
                   f"&redirect_uri={APP_DOMAIN}/pages/callback" \
                   f"&state={state}"

        st.info("Opening login in a new tab...")
        webbrowser.open_new_tab(auth_url)
