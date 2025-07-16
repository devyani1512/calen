# calendar_tools.py
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dateparser import parse
import json, datetime

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = "Asia/Kolkata"

def get_service(user):
    info = json.loads(user.auth_info)
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("calendar", "v3", credentials=creds)

def check_availability(date, start, end, user):
    svc = get_service(user)
    start_dt = parse(f"{date} {start}")
    end_dt = parse(f"{date} {end}")
    events = svc.events().list(
        calendarId="primary",
        timeMin=start_dt.isoformat(),
        timeMax=end_dt.isoformat(),
        singleEvents=True
    ).execute().get("items", [])
    return "✅ Free" if not events else "🚫 Busy"

def find_free_slots(date, duration_min, user):
    svc = get_service(user)
    start_dt = parse(f"{date} 00:00")
    end_dt = parse(f"{date} 23:59")
    fb = svc.freebusy().query(body={
        "timeMin": start_dt.isoformat(),
        "timeMax": end_dt.isoformat(),
        "timeZone": TIMEZONE,
        "items":[{"id":"primary"}]
    }).execute()
    busy = fb["calendars"]["primary"]["busy"]
    slots, cur = [], start_dt
    for b in busy:
        bstart = parse(b["start"]); bend = parse(b["end"])
        if (bstart - cur).total_seconds() >= duration_min*60:
            slots.append(f"{cur.strftime('%H:%M')}–{bstart.strftime('%H:%M')}")
        cur = max(cur, bend)
    if (end_dt - cur).total_seconds() >= duration_min*60:
        slots.append(f"{cur.strftime('%H:%M')}–23:59")
    return slots or ["No free slots"]

def book_event(date, start, end, summary, user):
    svc = get_service(user)
    start_dt = parse(f"{date} {start}")
    end_dt = parse(f"{date} {end}")
    event = {
        "summary": summary,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": TIMEZONE},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": TIMEZONE}
    }
    svc.events().insert(calendarId="primary", body=event).execute()
    return f"✅ Booked \"{summary}\" on {date} from {start} to {end}"
