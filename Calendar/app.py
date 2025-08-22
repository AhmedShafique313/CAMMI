# import streamlit as st
# from google_auth_oauthlib.flow import Flow
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials
# import os, json
# from datetime import datetime, timedelta

# st.set_page_config(page_title="Google Calendar Integration", page_icon="📅")

# # Required for local dev (since we're not using HTTPS)
# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# # Your existing JSON file path (don’t change it)
# CLIENT_SECRETS_FILE = r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\client_secret.json"

# SCOPES = ["https://www.googleapis.com/auth/calendar"]

# st.title("📅 Google Calendar Integration")

# # Step 1: Ask user to login
# if "credentials" not in st.session_state:
#     if st.button("🔑 Sign in with Google"):
#         flow = Flow.from_client_secrets_file(
#             CLIENT_SECRETS_FILE,
#             scopes=SCOPES,
#             redirect_uri="http://localhost:8501/oauth2callback"
#         )
#         auth_url, _ = flow.authorization_url(
#             access_type="offline",
#             include_granted_scopes="true",
#             prompt="consent"
#         )
#         st.markdown(f"[👉 Click here to authenticate with Google]({auth_url})")

# # Step 2: Handle redirect after login
# if "code" in st.query_params:  # Google appends ?code=... in redirect
#     code = st.query_params["code"]
#     flow = Flow.from_client_secrets_file(
#         CLIENT_SECRETS_FILE,
#         scopes=SCOPES,
#         redirect_uri="http://localhost:8501/oauth2callback"
#     )
#     flow.fetch_token(code=code)
#     creds = flow.credentials
#     st.session_state["credentials"] = json.loads(creds.to_json())
#     st.success("✅ Logged in successfully! Please reload the page.")

# # # Step 3: Use the Calendar API
# # if "credentials" in st.session_state:
# #     creds = Credentials.from_authorized_user_info(st.session_state["credentials"])
# #     service = build("calendar", "v3", credentials=creds)

# #     st.subheader("📌 Your Upcoming Events")
# #     events_result = service.events().list(
# #         calendarId="primary", maxResults=5, singleEvents=True,
# #         orderBy="startTime"
# #     ).execute()
# #     events = events_result.get("items", [])

# #     if not events:
# #         st.info("No upcoming events found.")
# #     else:
# #         for event in events:
# #             start = event["start"].get("dateTime", event["start"].get("date"))
# #             st.write(f"🔹 {event.get('summary', 'No Title')} — {start}")


# # Step 3: Use the Calendar API
# if "credentials" in st.session_state:
#     creds = Credentials.from_authorized_user_info(st.session_state["credentials"])
#     service = build("calendar", "v3", credentials=creds)

#     # --- Event creation form ---
#     with st.expander("➕ Create New Event"):
#         with st.form("event_form"):
#             title = st.text_input("Event Title")

#             # Split datetime into date + time inputs
#             col1, col2 = st.columns(2)
#             with col1:
#                 event_date = st.date_input("Event Date", value=datetime.now().date())
#             with col2:
#                 start_time = st.time_input("Start Time", value=(datetime.now() + timedelta(hours=1)).time())

#             end_time = st.time_input("End Time", value=(datetime.now() + timedelta(hours=2)).time())

#             submit = st.form_submit_button("✅ Create Event")

#         if submit:
#             start_dt = datetime.combine(event_date, start_time)
#             end_dt = datetime.combine(event_date, end_time)

#             event = {
#                 "summary": title,
#                 "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
#                 "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
#             }
#             service.events().insert(calendarId="primary", body=event).execute()
#             st.success(f"✅ Event '{title}' created! Please refresh below to see it.")

#     # --- Refresh Button ---
#     if st.button("🔄 Refresh Events"):
#         st.experimental_rerun()

#     # --- Fetch events ---
#     st.subheader("📌 Your Upcoming Events")
#     events_result = service.events().list(
#         calendarId="primary",
#         timeMin=datetime.utcnow().isoformat() + "Z",
#         maxResults=50,
#         singleEvents=True,
#         orderBy="startTime"
#     ).execute()
#     events = events_result.get("items", [])

#     # Convert to FullCalendar format
#     event_data = []
#     for event in events:
#         start = event["start"].get("dateTime", event["start"].get("date"))
#         end = event["end"].get("dateTime", event["end"].get("date"))

#         # If all-day event (date only), convert to full-day ISO
#         if len(start) == 10:  # "YYYY-MM-DD"
#             start = start + "T00:00:00"
#             end = end + "T23:59:59"

#         event_data.append({
#             "title": event.get("summary", "No Title"),
#             "start": start,
#             "end": end
#         })

#     # --- FullCalendar UI ---
#     st.markdown("### 🗓️ Calendar View")
#     calendar_events = json.dumps(event_data)

#     st.components.v1.html(f"""
#         <link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.css" rel="stylesheet" />
#         <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.js"></script>
#         <div id='calendar'></div>
#         <script>
#           document.addEventListener('DOMContentLoaded', function() {{
#             var calendarEl = document.getElementById('calendar');
#             var calendar = new FullCalendar.Calendar(calendarEl, {{
#               initialView: 'dayGridMonth',
#               headerToolbar: {{
#                 left: 'prev,next today',
#                 center: 'title',
#                 right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
#               }},
#               events: {calendar_events},
#               selectable: false,
#               editable: false
#             }});
#             calendar.render();
#           }});
#         </script>
#         <style>
#             #calendar {{
#                 max-width: 100%;
#                 margin: 20px auto;
#             }}
#         </style>
#     """, height=700)

import streamlit as st
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os, json
from datetime import datetime, timedelta

st.set_page_config(page_title="Google Calendar Integration", page_icon="📅")

# Allow local dev (no HTTPS)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

CLIENT_SECRETS_FILE = r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\client_secret.json"
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

st.title("📅 Google Calendar Integration")

# --- Check if already logged in ---
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build("calendar", "v3", credentials=creds)

    # --- Event creation form ---
    with st.expander("➕ Create New Event"):
        with st.form("event_form"):
            title = st.text_input("Event Title")

            col1, col2 = st.columns(2)
            with col1:
                event_date = st.date_input("Event Date", value=datetime.now().date())
            with col2:
                start_time = st.time_input("Start Time", value=(datetime.now() + timedelta(hours=1)).time())

            end_time = st.time_input("End Time", value=(datetime.now() + timedelta(hours=2)).time())

            submit = st.form_submit_button("✅ Create Event")

        if submit:
            start_dt = datetime.combine(event_date, start_time)
            end_dt = datetime.combine(event_date, end_time)

            event = {
                "summary": title,
                "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
                "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
            }
            service.events().insert(calendarId="primary", body=event).execute()
            st.success(f"✅ Event '{title}' created!")

    # --- Fetch events ---
    st.subheader("📌 Your Upcoming Events")
    events_result = service.events().list(
        calendarId="primary",
        timeMin=datetime.utcnow().isoformat() + "Z",
        maxResults=50,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])

    if not events:
        st.info("No upcoming events found.")
    else:
        event_data = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))

            if len(start) == 10:
                start = start + "T00:00:00"
                end = end + "T23:59:59"

            event_data.append({
                "title": event.get("summary", "No Title"),
                "start": start,
                "end": end
            })

        # --- FullCalendar UI ---
        import json
        calendar_events = json.dumps(event_data)
        st.markdown("### 🗓️ Calendar View")

        st.components.v1.html(f"""
            <link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.css" rel="stylesheet" />
            <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.js"></script>
            <div id='calendar'></div>
            <script>
              document.addEventListener('DOMContentLoaded', function() {{
                var calendarEl = document.getElementById('calendar');
                var calendar = new FullCalendar.Calendar(calendarEl, {{
                  initialView: 'dayGridMonth',
                  headerToolbar: {{
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
                  }},
                  events: {calendar_events},
                }});
                calendar.render();
              }});
            </script>
            <style>
                #calendar {{
                    max-width: 100%;
                    margin: 20px auto;
                }}
            </style>
        """, height=700)

else:
    st.warning("⚠️ You are not signed in.")
    st.write("👉 Please go to the [OAuth Callback Page](http://localhost:8501/oauth_callback) to log in.")
