from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dateparser import parse
import json, datetime, re

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
        "items": [{"id": "primary"}]
    }).execute()
    busy = fb["calendars"]["primary"]["busy"]
    slots, cur = [], start_dt
    for b in busy:
        bstart = parse(b["start"])
        bend = parse(b["end"])
        if (bstart - cur).total_seconds() >= duration_min * 60:
            slots.append(f"{cur.strftime('%H:%M')}–{bstart.strftime('%H:%M')}")
        cur = max(cur, bend)
    if (end_dt - cur).total_seconds() >= duration_min * 60:
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

# NEW: Flexible command handling
def handle_calendar_command(command, user):
    command = command.lower()

    # Try to detect intent
    if "free" in command or "available" in command:
        # Try to extract time range
        date = extract_date(command) or "today"
        start, end = extract_time_range(command) or ("09:00", "10:00")
        return check_availability(date, start, end, user)

    elif "slot" in command or "free time" in command or "find time" in command:
        date = extract_date(command) or "today"
        duration = extract_duration(command) or 30
        slots = find_free_slots(date, duration, user)
        return f"🕓 Free slots for {date} ({duration} min):\n" + "\n".join(slots)

    elif "book" in command or "schedule" in command or "add" in command:
        date = extract_date(command) or "today"
        start, end = extract_time_range(command) or ("15:00", "16:00")
        summary = extract_summary(command) or "Event"
        return book_event(date, start, end, summary, user)

    else:
        return "❓ Sorry, I couldn't understand your request."

# --- Helpers below ---
def extract_date(text):
    parsed = parse(text)
    if parsed:
        return parsed.strftime("%Y-%m-%d")
    return None

def extract_time_range(text):
    # Match time ranges like "from 2 to 3", "2pm to 3pm", "at 5"
    range_match = re.search(r"(?:from )?(\d{1,2})(?::\d{2})?\s?(am|pm)?\s?(to|-)\s?(\d{1,2})(?::\d{2})?\s?(am|pm)?", text)
    if range_match:
        start_hour = f"{range_match.group(1)} {range_match.group(2) or ''}".strip()
        end_hour = f"{range_match.group(4)} {range_match.group(5) or ''}".strip()
        start = parse(start_hour).strftime("%H:%M")
        end = parse(end_hour).strftime("%H:%M")
        return (start, end)

    single_match = re.search(r"(?:at|around)?\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
    if single_match:
        hour = single_match.group(1)
        minute = single_match.group(2) or "00"
        period = single_match.group(3) or ""
        dt = parse(f"{hour}:{minute} {period}")
        start = dt.strftime("%H:%M")
        end_dt = dt + datetime.timedelta(hours=1)
        end = end_dt.strftime("%H:%M")
        return (start, end)
    return None

def extract_duration(text):
    match = re.search(r"(\d{1,3})\s?(minutes|min|mins)", text)
    if match:
        return int(match.group(1))
    return None

def extract_summary(text):
    # Naively extract quoted text or keywords
    quote = re.search(r'"([^"]+)"', text)
    if quote:
        return quote.group(1)
    if "meeting" in text:
        return "Meeting"
    if "call" in text:
        return "Call"
    if "event" in text:
        return "Event"
    return "Event"

