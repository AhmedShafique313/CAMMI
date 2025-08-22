from flask import Flask, redirect, url_for, session, request, render_template_string
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import os, json

app = Flask(__name__)
app.secret_key = "supersecret"   # change this in production

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

CLIENT_SECRETS_FILE = r"C:\Users\Kavtech AI Engineer\Documents\CAMMI\client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# ---------- HTML TEMPLATE ----------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Google Calendar Integration</title>
    <link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.css" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.js"></script>
</head>
<body style="font-family: Arial; margin:20px;">
    <h1>📅 Google Calendar Integration (Flask)</h1>

    {% if not session.get('credentials') %}
        <a href="{{ url_for('authorize') }}">🔑 Sign in with Google</a>
    {% else %}
        <form method="post" action="{{ url_for('create_event') }}">
            <h3>➕ Create New Event</h3>
            <label>Event Title:</label><br>
            <input type="text" name="title" required><br><br>

            <label>Event Date:</label>
            <input type="date" name="date" required><br><br>

            <label>Start Time:</label>
            <input type="time" name="start_time" required><br><br>

            <label>End Time:</label>
            <input type="time" name="end_time" required><br><br>

            <button type="submit">✅ Create Event</button>
        </form>

        <h3>🗓️ Calendar View</h3>
        <div id="calendar"></div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                var calendarEl = document.getElementById('calendar');
                var calendar = new FullCalendar.Calendar(calendarEl, {
                    initialView: 'dayGridMonth',
                    headerToolbar: {
                        left: 'prev,next today',
                        center: 'title',
                        right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
                    },
                    events: {{ events|safe }},
                    editable: false,
                    selectable: false
                });
                calendar.render();
            });
        </script>
        <style>
            #calendar {
                max-width: 900px;
                margin: 20px auto;
            }
        </style>
    {% endif %}
</body>
</html>
"""

# ---------- ROUTES ----------

@app.route("/")
def index():
    events = "[]"
    if "credentials" in session:
        creds = Credentials.from_authorized_user_info(session["credentials"], SCOPES)
        service = build("calendar", "v3", credentials=creds)

        events_result = service.events().list(
            calendarId="primary",
            timeMin=datetime.utcnow().isoformat() + "Z",
            maxResults=50,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        items = events_result.get("items", [])
        data = []
        for e in items:
            start = e["start"].get("dateTime", e["start"].get("date"))
            end = e["end"].get("dateTime", e["end"].get("date"))

            if len(start) == 10:  # all-day event
                start += "T00:00:00"
                end += "T23:59:59"

            data.append({
                "id": e.get("id"),
                "title": e.get("summary", "No Title"),
                "start": start,
                "end": end
            })

        events = json.dumps(data)

    return render_template_string(HTML_TEMPLATE, events=events, session=session)

@app.route("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return redirect(auth_url)

@app.route("/oauth2callback")
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session["credentials"] = json.loads(creds.to_json())
    return redirect(url_for("index"))

@app.route("/create_event", methods=["POST"])
def create_event():
    if "credentials" not in session:
        return redirect(url_for("index"))

    creds = Credentials.from_authorized_user_info(session["credentials"], SCOPES)
    service = build("calendar", "v3", credentials=creds)

    title = request.form["title"]
    date = request.form["date"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]

    start_dt = datetime.fromisoformat(f"{date}T{start_time}")
    end_dt = datetime.fromisoformat(f"{date}T{end_time}")

    event = {
        "summary": title,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"}
    }

    service.events().insert(calendarId="primary", body=event).execute()
    return redirect(url_for("index"))

# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(port=5000, debug=True)
