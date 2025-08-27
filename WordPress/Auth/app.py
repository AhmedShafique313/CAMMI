import streamlit as st

st.set_page_config(page_title="WordPress Connector", page_icon="🌍")

st.title("🌍 Connect Your WordPress Website")

st.markdown("""
Choose how you want to connect your WordPress site:

1. **OAuth 2.0 (Recommended)**  
   - Requires OAuth plugin installed on your site  
   - Redirect login like Google Auth

2. **Application Passwords**  
   - Works with WordPress 5.6+  
   - Generate an App Password in WP profile and paste it here
""")

st.page_link("pages/Connect_Oauth.py", label="🔑 Connect via OAuth 2.0")
st.page_link("pages/Connect_AppPW.py", label="🔑 Connect via Application Passwords")

# Once connected, show publish option
if "wp_connected" in st.session_state and st.session_state["wp_connected"]:
    st.page_link("pages/Publish_Post.py", label="✍️ Publish a Blog Post")
