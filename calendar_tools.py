from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dateparser import parse
import json
import datetime

TIMEZONE = "Asia/Kolkata"  # change as needed

def get_service(user):
    info = json.loads(user.auth_info)
    creds = Credentials.from_authorized_user_info(info, scopes=["https://www.googleapis.com/auth/calendar"])
    return build("calendar", "v3", credentials=creds)

def check_availability(user, start_dt, end_dt):
    service = get_service(user)
    body = {
      "timeMin": start_dt.isoformat(),
      "timeMax": end_dt.isoformat(),
      "timeZone": TIMEZONE,
      "items": [{"id": "primary"}]
    }
    resp = service.freebusy().query(body=body).execute()
    busy = resp["calendars"]["primary"].get("busy", [])
    return busy

def find_free_slots(user, date_str, duration_min=60):
    # build datetime range for the date
    start_day = parse(f"{date_str} 00:00", settings={"TIMEZONE": TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True})
    end_day = start_day + datetime.timedelta(days=1)
    busy = check_availability(user, start_day, end_day)
    slots = []
    cursor = start_day
    for b in busy:
        bstart = parse(b["start"])
        bend = parse(b["end"])
        if (bstart - cursor).total_seconds() >= duration_min * 60:
            slots.append((cursor, bstart))
        cursor = max(cursor, bend)
    if (end_day - cursor).total_seconds() >= duration_min * 60:
        slots.append((cursor, end_day))
    formatted = [f"{s.strftime('%H:%M')}–{e.strftime('%H:%M')}" for s, e in slots]
    return formatted or ["No free slots for that duration"]

def book_event(user, date_str, start_time, end_time, summary="Meeting", reminder_mins=15):
    service = get_service(user)
    start_dt = parse(f"{date_str} {start_time}", settings={"TIMEZONE": TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True})
    end_dt = parse(f"{date_str} {end_time}", settings={"TIMEZONE": TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True})
    if not start_dt or not end_dt or end_dt <= start_dt:
        return "❌ Invalid dates/times."
    busy = check_availability(user, start_dt, end_dt)
    if busy:
        return "⚠️ You’re busy during that time."
    event = {
        "summary": summary,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": TIMEZONE},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": TIMEZONE},
        "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": reminder_mins}]}
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    return f"✅ Event booked: {created.get('htmlLink')}"

# Handler combining parsing and actions
def handle_calendar_command(command, user):
    cmd = command.lower()
    if "free slots" in cmd:
        # expecting something like: "free slots on July 20 for 60"
        parts = command.split()
        date_part = parts[3]
        dur = int(parts[-1])
        slots = find_free_slots(user, date_part, dur)
        return "🕒 Free slots:\n" + "\n".join(slots)

    elif "availability" in cmd:
        # expecting: "availability from July 20 10:00 to July 20 11:00"
        parts = command.split()
        start = parse(f"{parts[2]} {parts[3]}", settings={"TIMEZONE": TIMEZONE})
        end = parse(f"{parts[4]} {parts[5]}", settings={"TIMEZONE": TIMEZONE})
        busy = check_availability(user, start, end)
        if busy:
            return "You're busy then:\n" + "\n".join([f"{b['start']} to {b['end']}" for b in busy])
        return "✅ You’re free in that range."

    elif "book" in cmd:
        # expecting "book meeting on July 20 from 10:00 to 11:00 title fuel"
        parts = command.split()
        date = parts[3]
        start = parts[5]
        end = parts[7]
        title = command.split("title", 1)[1].strip() if "title" in cmd else "Meeting"
        return book_event(user, date, start, end, summary=title)

    else:
        return "❓ I didn't understand. Try ‘free slots’, ‘availability’, or ‘book’."



