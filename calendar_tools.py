# calendar_tools.py
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dateparser import parse
from datetime import timedelta
import json

TIMEZONE = "Asia/Kolkata"  # adjust as needed

def get_service(user):
    info = json.loads(user.auth_info)
    creds = Credentials.from_authorized_user_info(info, scopes=["https://www.googleapis.com/auth/calendar"])
    return build("calendar", "v3", credentials=creds)

def check_availability(date, start_time, end_time, user):
    service = get_service(user)
    start = parse(f"{date} {start_time}", settings={"TIMEZONE": TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True})
    end = parse(f"{date} {end_time}", settings={"TIMEZONE": TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True})
    body = {"timeMin": start.isoformat(), "timeMax": end.isoformat(), "timeZone": TIMEZONE, "items": [{"id": "primary"}]}
    resp = service.freebusy().query(body=body).execute()
    busy = resp["calendars"]["primary"].get("busy", [])
    return "free" if not busy else "busy"

def find_free_slots(date, duration_minutes, user):
    service = get_service(user)
    start_of_day = parse(f"{date} 00:00", settings={"TIMEZONE": TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True})
    end_of_day = start_of_day + timedelta(hours=24)
    body = {"timeMin": start_of_day.isoformat(), "timeMax": end_of_day.isoformat(),
            "timeZone": TIMEZONE, "items":[{"id":"primary"}]}
    events = service.freebusy().query(body=body).execute()["calendars"]["primary"].get("busy", [])
    slots = []
    cursor = start_of_day
    for busy in events:
        busy_start = parse(busy["start"])
        if (busy_start - cursor).total_seconds() >= duration_minutes*60:
            slots.append((cursor, busy_start))
        cursor = max(cursor, parse(busy["end"]))
    if (end_of_day - cursor).total_seconds() >= duration_minutes*60:
        slots.append((cursor, end_of_day))
    return slots

def book_event(date, start_time, end_time, summary, user):
    service = get_service(user)
    start = parse(f"{date} {start_time}", settings={"TIMEZONE": TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True})
    end = parse(f"{date} {end_time}", settings={"TIMEZONE": TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True})
    if start >= end:
        return "❌ Start time must be before end time."
    
    event = {"summary": summary,
             "start": {"dateTime": start.isoformat(), "timeZone": TIMEZONE},
             "end":   {"dateTime": end.isoformat(),   "timeZone": TIMEZONE}}
    service.events().insert(calendarId="primary", body=event).execute()
    return f"✅ Event booked: {summary} on {date} from {start_time} to {end_time}."

def handle_calendar_command(command, user):
    cmd = command.lower()
    if "book" in cmd:
        parts = command.split()
        # Expected: book on DATE from TIME to TIME title TITLE
        try:
            date = parts[parts.index("on")+1]
            start = parts[parts.index("from")+1]
            end = parts[parts.index("to")+1]
            title = " ".join(parts[parts.index("title")+1:])
            return book_event(date, start, end, title, user)
        except Exception:
            return "❌ Format error. Use: book on YYYY-MM-DD from HH:MM to HH:MM title MyEvent"
    
    if "availability" in cmd:
        # Example: check availability on DATE from TIME to TIME
        parts = command.split()
        try:
            date = parts[parts.index("on")+1]
            start = parts[parts.index("from")+1]
            end = parts[parts.index("to")+1]
            state = check_availability(date, start, end, user)
            return f"You are *{state}* on {date} between {start} and {end}."
        except Exception:
            return "❌ Format error. Use: check availability on YYYY-MM-DD from HH:MM to HH:MM"

    if "free slots" in cmd:
        # Example: find free slots on DATE duration MINUTES
        parts = command.split()
        try:
            date = parts[parts.index("on")+1]
            dur = int(parts[parts.index("duration")+1])
            slots = find_free_slots(date, dur, user)
            if not slots:
                return f"No {dur}-minute free slots on {date}."
            resp = "Free slots:\n"
            for s,e in slots:
                resp += f"{s.strftime('%H:%M')}–{e.strftime('%H:%M')}\n"
            return resp
        except Exception:
            return "❌ Format: free slots on YYYY-MM-DD duration MINUTES"
    
    return "❓ Sorry, I didn't understand. Try: book / availability / free slots."




