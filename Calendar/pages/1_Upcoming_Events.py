import streamlit as st
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
from datetime import datetime
import json

st.set_page_config(page_title="📅 Upcoming Events", page_icon="🗓️")

TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

st.title("📅 Your Upcoming Google Calendar Events")

# --- Check if logged in ---
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build("calendar", "v3", credentials=creds)

    # --- Fetch events ---
    st.subheader("📌 Event List")
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

            if len(start) == 10:  # All-day event
                start = start + "T00:00:00"
                end = end + "T23:59:59"

            event_data.append({
                "title": event.get("summary", "No Title"),
                "start": start,
                "end": end
            })

        # Show as list
        for ev in event_data:
            st.write(f"📍 **{ev['title']}** — {ev['start']} → {ev['end']}")

        # --- FullCalendar UI ---
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
    st.write("👉 Please log in first from the **main page** (`app.py`).")
