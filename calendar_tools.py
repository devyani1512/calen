from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dateparser import parse
import json
import datetime

TIMEZONE = "Asia/Kolkata"
CALENDAR_ID = "primary"

def get_service(user):
    info = json.loads(user.auth_info)
    creds = Credentials.from_authorized_user_info(info, scopes=["https://www.googleapis.com/auth/calendar"])
    return build("calendar", "v3", credentials=creds)

def list_events_for_date(date_str, user):
    service = get_service(user)
    start = parse(f"{date_str} 00:00").astimezone()
    end = start + datetime.timedelta(days=1)
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute().get("items", [])
    return events

def check_availability(date_str, start_time, end_time, user):
    events = list_events_for_date(date_str, user)
    if not events:
        return "✅ You're free all day."
    for e in events:
        s = e['start'].get('dateTime', e['start'].get('date'))
        e_end = e['end'].get('dateTime', e['end'].get('date'))
        if not (e_end <= parse(f"{date_str} {start_time}") or s >= parse(f"{date_str} {end_time}")):
            return f"❌ Busy during {start_time}-{end_time}: {e['summary']}"
    return f"✅ Free during {start_time}-{end_time}."

def find_free_slots(date_str, duration_min, user):
    events = list_events_for_date(date_str, user)
    start = parse(f"{date_str} 00:00")
    end = start + datetime.timedelta(days=1)
    busy = []
    for e in events:
        s = parse(e['start'].get('dateTime', e['start'].get('date')))
        e_end = parse(e['end'].get('dateTime', e['end'].get('date')))
        busy.append((s, e_end))
    busy.sort()
    free = []
    cursor = start
    for s, e_end in busy:
        diff = (s - cursor).total_seconds() / 60
        if diff >= duration_min:
            free.append(f"{cursor.time()}–{s.time()}")
        cursor = max(cursor, e_end)
    if (end - cursor).total_seconds()/60 >= duration_min:
        free.append(f"{cursor.time()}–{end.time()}")
    return "\n".join(free) if free else "⚠️ No free slots."

def book_event(date_str, start_time, end_time, summary, reminder_min, user):
    service = get_service(user)
    start = parse(f"{date_str} {start_time}")
    end = parse(f"{date_str} {end_time}")
    body = {
        "summary": summary,
        "start": {"dateTime": start.isoformat(), "timeZone": TIMEZONE},
        "end": {"dateTime": end.isoformat(), "timeZone": TIMEZONE},
        "reminders": {"useDefault": False, "overrides": [{"method":"popup", "minutes": reminder_min}]}
    }
    event = service.events().insert(calendarId=CALENDAR_ID, body=body).execute()
    return f"✅ Created: {event.get('htmlLink')}"




