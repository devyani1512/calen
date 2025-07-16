# calendar_tools.py

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dateparser import parse
from datetime import timedelta
import json

TIME_ZONE = "Asia/Kolkata"  # adjust if needed

def get_service(user):
    print("🔍 user.auth_info =", user.auth_info)
    info = json.loads(user.auth_info)
    creds = Credentials.from_authorized_user_info(
        info, scopes=["https://www.googleapis.com/auth/calendar"]
    )
    return build("calendar", "v3", credentials=creds)

def handle_calendar_command(command: str, user):
    service = get_service(user)

    # Expecting command like: "book meeting on July 20 at 3pm about Project"
    import re
    pattern = r"on\s+(.*?)\s+at\s+(.*?)\s+about\s+(.+)"
    m = re.search(pattern, command, re.IGNORECASE)
    if not m:
        return ("❌ Could not parse. Use format: "
                "'on [date] at [time] about [subject]'")

    date_str, time_str, summary = m.groups()
    dt = parse(f"{date_str} {time_str}", settings={"TIMEZONE": TIME_ZONE})
    if not dt:
        return ("❌ Invalid date/time — try something like: "
                "'on July 20 at 3pm about Team Sync'")

    # Default duration 1 hour
    end_dt = dt + timedelta(hours=1)

    event = {
        "summary": summary.strip(),
        "start": {"dateTime": dt.isoformat(), "timeZone": TIME_ZONE},
        "end":   {"dateTime": end_dt.isoformat(), "timeZone": TIME_ZONE},
    }

    try:
        created = service.events().insert(calendarId="primary", body=event).execute()
        link = created.get("htmlLink")
        return (f"✅ Meeting created: **{summary.strip()}** on "
                f"{dt.strftime('%b %d, %Y at %I:%M %p')} — [View on Google Calendar]({link})")
    except Exception as e:
        return f"❌ Failed to create event: {e}"

