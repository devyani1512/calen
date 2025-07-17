# import os
# import json
# import pytz
# import dateparser
# from datetime import datetime, timedelta
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials

# # Get Google Calendar service
# def get_calendar_service(user_info: dict):
#     creds = Credentials.from_authorized_user_info(user_info, scopes=["https://www.googleapis.com/auth/calendar"])
#     return build("calendar", "v3", credentials=creds)

# # Book an event using natural language input
# def book_event_natural(user_info: dict, description: str):
#     event_time = dateparser.parse(
#         description,
#         settings={
#             'PREFER_DATES_FROM': 'future',
#             'RELATIVE_BASE': datetime.now(),
#             'RETURN_AS_TIMEZONE_AWARE': False
#         }
#     )

#     if not event_time:
#         return {"success": False, "message": "❌ Couldn't understand the date/time. Try something like 'meeting tomorrow at 3pm for 1 hour'"}

#     # Default duration = 1 hour
#     duration = timedelta(hours=1)
#     desc_lower = description.lower()

#     if "30 minutes" in desc_lower or "half an hour" in desc_lower:
#         duration = timedelta(minutes=30)
#     elif "15 minutes" in desc_lower or "quarter" in desc_lower:
#         duration = timedelta(minutes=15)
#     elif "2 hours" in desc_lower or "two hours" in desc_lower:
#         duration = timedelta(hours=2)
#     elif "1.5 hours" in desc_lower or "hour and a half" in desc_lower:
#         duration = timedelta(minutes=90)

#     start = event_time
#     end = start + duration
#     timezone = 'Asia/Kolkata'

#     event = {
#         "summary": "Event",
#         "description": description,
#         "start": {"dateTime": start.isoformat(), "timeZone": timezone},
#         "end": {"dateTime": end.isoformat(), "timeZone": timezone},
#     }

#     try:
#         service = get_calendar_service(user_info)
#         service.events().insert(calendarId="primary", body=event).execute()
#         return {
#             "success": True,
#             "message": f"✅ Booked event on {start.strftime('%A, %d %b')} from {start.strftime('%I:%M %p')} to {end.strftime('%I:%M %p')}."
#         }
#     except Exception as e:
#         return {"success": False, "message": f"❌ Failed to create event: {str(e)}"}

# # Get schedule for a specific day
# def check_schedule_day(user_info: dict, day: str):
#     parsed_day = dateparser.parse(day, settings={'PREFER_DATES_FROM': 'future'})
#     if not parsed_day:
#         return {"success": False, "message": "❌ Couldn't understand the day. Try 'today', 'next Tuesday', '5th August' etc."}

#     start = datetime.combine(parsed_day.date(), datetime.min.time())
#     end = start + timedelta(days=1)
#     timezone = 'Asia/Kolkata'
#     service = get_calendar_service(user_info)

#     try:
#         events = service.events().list(
#             calendarId='primary',
#             timeMin=start.isoformat() + 'Z',
#             timeMax=end.isoformat() + 'Z',
#             singleEvents=True,
#             orderBy='startTime'
#         ).execute().get('items', [])

#         if not events:
#             return {"success": True, "message": f"🗓 No events found on {parsed_day.strftime('%A, %d %b')}."}

#         schedule = f"📅 Your schedule on {parsed_day.strftime('%A, %d %b')}:\n"
#         for event in events:
#             start_time = event['start'].get('dateTime', event['start'].get('date'))
#             summary = event.get('summary', 'No Title')
#             start_local = dateparser.parse(start_time).strftime('%I:%M %p')
#             schedule += f"• {summary} at {start_local}\n"
#         return {"success": True, "message": schedule}
#     except Exception as e:
#         return {"success": False, "message": f"❌ Failed to fetch schedule: {str(e)}"}

# # Check free slots on a given day
# def find_free_slots(user_info: dict, day: str):
#     parsed_day = dateparser.parse(day, settings={'PREFER_DATES_FROM': 'future'})
#     if not parsed_day:
#         return {"success": False, "message": "❌ Couldn't understand the day. Try 'tomorrow', 'next Friday', etc."}

#     timezone = pytz.timezone('Asia/Kolkata')
#     start_day = timezone.localize(datetime.combine(parsed_day.date(), datetime.min.time()))
#     work_start = start_day.replace(hour=9)
#     work_end = start_day.replace(hour=18)

#     service = get_calendar_service(user_info)
#     try:
#         busy_times = service.freebusy().query(body={
#             "timeMin": work_start.isoformat(),
#             "timeMax": work_end.isoformat(),
#             "timeZone": "Asia/Kolkata",
#             "items": [{"id": "primary"}]
#         }).execute()

#         busy_periods = busy_times['calendars']['primary'].get('busy', [])
#         free_slots = []
#         current = work_start

#         for period in busy_periods:
#             busy_start = dateparser.parse(period['start'])
#             busy_end = dateparser.parse(period['end'])
#             if current < busy_start:
#                 free_slots.append((current, busy_start))
#             current = max(current, busy_end)

#         if current < work_end:
#             free_slots.append((current, work_end))

#         if not free_slots:
#             return {"success": True, "message": "🟡 No free time slots available in working hours."}

#         slot_msg = "🟢 Free time slots:\n"
#         for slot_start, slot_end in free_slots:
#             slot_msg += f"• {slot_start.strftime('%I:%M %p')} – {slot_end.strftime('%I:%M %p')}\n"
#         return {"success": True, "message": slot_msg}
#     except Exception as e:
#         return {"success": False, "message": f"❌ Failed to find free slots: {str(e)}"}

# # ✅ Add this to fix your import error!
# def handle_calendar_command(command: str, user_info: dict):
#     command_lower = command.lower()

#     if "schedule" in command_lower or "what do i have" in command_lower:
#         return check_schedule_day(user_info, command)
#     elif "free" in command_lower or "available" in command_lower:
#         return find_free_slots(user_info, command)
#     elif "book" in command_lower or "add event" in command_lower or "schedule a meeting" in command_lower:
#         return book_event_natural(user_info, command)
#     else:
#         return {"success": False, "message": "🤖 Sorry, I couldn't understand the calendar command."}
# calendar_tools.py

# calendar_tools.py

# calendar_tool.py
# calendar_tool.py

# calendar_tool.py
import os
import json
import pytz
from datetime import datetime, timedelta
from dateparser import parse as parse_date
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from models import db, User  # Make sure models.py has User with credentials_json

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service(user_id):
    user = User.query.get(user_id)
    if not user or not user.credentials_json:
        raise Exception("User credentials not found. Please log in.")

    creds_dict = json.loads(user.credentials_json)
    creds = Credentials.from_authorized_user_info(info=creds_dict, scopes=SCOPES)
    service = build("calendar", "v3", credentials=creds)
    return service

def book_event_natural(text, user_id):
    event_time = parse_date(text, settings={"PREFER_DATES_FROM": "future"})
    if not event_time:
        return "⚠️ Couldn't understand the event time."

    start_time = event_time.replace(tzinfo=pytz.UTC)
    end_time = start_time + timedelta(hours=1)

    event = {
        "summary": text,
        "start": {"dateTime": start_time.isoformat()},
        "end": {"dateTime": end_time.isoformat()},
    }

    service = get_calendar_service(user_id)
    event = service.events().insert(calendarId="primary", body=event).execute()
    return f"✅ Event created: {event.get('htmlLink')}"

def check_schedule_day(user_id, date=None):
    service = get_calendar_service(user_id)
    now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    if date:
        start = parse_date(date).replace(tzinfo=pytz.UTC)
    else:
        start = now

    end = start + timedelta(days=1)
    events_result = service.events().list(
        calendarId="primary", timeMin=start.isoformat(), timeMax=end.isoformat(),
        singleEvents=True, orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    if not events:
        return "📅 No events scheduled for the day."

    schedule = "\n".join(
        f"- {e['summary']} at {e['start'].get('dateTime', e['start'].get('date'))}"
        for e in events
    )
    return f"📅 Your events:\n{schedule}"

def handle_calendar_command(user_input, user_id):
    text = user_input.lower()
    if "book" in text or "schedule" in text or "add event" in text:
        return book_event_natural(text, user_id)
    elif "what" in text or "check" in text or "today" in text or "events" in text:
        return check_schedule_day(user_id)
    else:
        return "🤖 Sorry, I couldn't understand. Please rephrase your request."
