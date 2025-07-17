# calendar_tools.py

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dateparser import parse
from datetime import datetime, timedelta
import json

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = "Asia/Kolkata"

def get_service(user):
    info = json.loads(user.auth_info)
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("calendar", "v3", credentials=creds)

def handle_calendar_command(command: str, user):
    svc = get_service(user)

    command_lower = command.lower()

    # Detect schedule query
    if "schedule" in command_lower or "what do i have" in command_lower:
        target_date = parse(command)
        if not target_date:
            return "❌ Couldn't understand the date in your request."

        start_dt = datetime.combine(target_date.date(), datetime.min.time())
        end_dt = datetime.combine(target_date.date(), datetime.max.time())

        events = svc.events().list(
            calendarId="primary",
            timeMin=start_dt.isoformat() + "Z",
            timeMax=end_dt.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime"
        ).execute().get("items", [])

        if not events:
            return f"📅 You're free on {target_date.strftime('%A, %d %B')}!"

        reply = f"🗓️ Your schedule for {target_date.strftime('%A, %d %B')}:\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            start_time = parse(start).strftime("%H:%M")
            summary = event.get("summary", "No Title")
            reply += f"• {start_time} – {summary}\n"

        return reply

    # Detect free slot query
    elif "free" in command_lower or "available" in command_lower:
        target_date = parse(command)
        if not target_date:
            return "❌ Couldn't understand the date in your request."
        return "\n".join(find_free_slots(target_date.strftime("%Y-%m-%d"), 30, user))

    # Default to booking if "book", "schedule", "add event", etc.
    elif any(word in command_lower for word in ["book", "add", "schedule meeting"]):
        # Fallback logic – customize further with NLP
        date = parse(command)
        if not date:
            return "❌ Couldn't understand the date/time."
        start = date.strftime("%H:%M")
        end = (date + timedelta(hours=1)).strftime("%H:%M")
        return book_event(date.strftime("%Y-%m-%d"), start, end, "Event", user)

    else:
        return "🤖 Sorry, I couldn't understand your request. Try saying something like:\n- 'What’s my schedule on Friday?'\n- 'Book a meeting tomorrow at 3pm'"


