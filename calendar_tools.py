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
# utils.py
# calendar_tools.py



# import pytz
# import dateparser
# from datetime import datetime, timedelta
# from dateparser.search import search_dates
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError


# def create_service(creds):
#     return build("calendar", "v3", credentials=creds)


# def handle_calendar_command(user_input: str, creds):
#     service = create_service(creds)
#     now = datetime.utcnow().isoformat() + "Z"
#     lc_input = user_input.lower()

#     try:
#         # Booking intent
#         if any(k in lc_input for k in ["book", "schedule", "add", "create", "set up"]):
#             event = create_event_from_input(user_input)
#             if not event:
#                 return "❌ I couldn't understand the date/time for the event. Try including a specific time."

#             # Check for busy slots before booking
#             if is_time_slot_busy(service, event["start"]["dateTime"], event["end"]["dateTime"]):
#                 return f"❌ You're already busy during **{event['start']['dateTime']} to {event['end']['dateTime']} UTC**. Try a different time."

#             inserted = service.events().insert(calendarId='primary', body=event).execute()
#             return f"✅ Event **'{inserted.get('summary')}'** booked at **{inserted['start']['dateTime']} UTC**"

#         # Cancel intent
#         elif any(k in lc_input for k in ["cancel", "delete", "remove"]):
#             events = service.events().list(
#                 calendarId='primary',
#                 timeMin=now,
#                 maxResults=10,
#                 singleEvents=True,
#                 orderBy='startTime'
#             ).execute().get("items", [])

#             for event in events:
#                 if event['summary'].lower() in lc_input:
#                     service.events().delete(calendarId='primary', eventId=event['id']).execute()
#                     return f"🗑️ Event **'{event['summary']}'** canceled."
#             return "❌ Couldn't find a matching event to cancel in upcoming events."

#         # Availability intent
#         elif any(word in lc_input for word in ["free", "available", "busy"]):
#             time_min = datetime.now(pytz.timezone("Asia/Kolkata"))
#             time_max = time_min + timedelta(days=1)

#             body = {
#                 "timeMin": time_min.astimezone(pytz.utc).isoformat(),
#                 "timeMax": time_max.astimezone(pytz.utc).isoformat(),
#                 "timeZone": "UTC",
#                 "items": [{"id": "primary"}],
#             }

#             fb = service.freebusy().query(body=body).execute()
#             busy_slots = fb["calendars"]["primary"]["busy"]

#             if not busy_slots:
#                 return "🟢 You're free all day today!"
#             return "🟡 You're busy at:\n" + "\n".join(
#                 f"- {slot['start']} to {slot['end']}" for slot in busy_slots
#             )

#         # Unrecognized intent
#         return "🤖 I understood your message but couldn't match it to booking, canceling, or availability checking."

#     except HttpError as e:
#         return f"❌ Google Calendar API error: {e}"


# def create_event_from_input(user_input: str):
#     found = search_dates(
#         user_input,
#         languages=["en"],
#         settings={
#             "PREFER_DATES_FROM": "future",
#             "TIMEZONE": "Asia/Kolkata",
#             "RETURN_AS_TIMEZONE_AWARE": True
#         }
#     )

#     if not found or len(found) < 1:
#         return None

#     dt = found[0][1]  # Start time

#     if len(found) >= 2:
#         dt_end = found[1][1]
#     else:
#         dt_end = dt + timedelta(hours=1)

#     # Convert to UTC for Google Calendar API
#     dt_utc = dt.astimezone(pytz.utc)
#     dt_end_utc = dt_end.astimezone(pytz.utc)

#     summary = extract_summary(user_input)

#     return {
#         "summary": summary or "Untitled Event",
#         "start": {"dateTime": dt_utc.isoformat(), "timeZone": "UTC"},
#         "end": {"dateTime": dt_end_utc.isoformat(), "timeZone": "UTC"},
#     }


# def extract_summary(text: str):
#     for marker in ["called", "about", "titled", "named"]:
#         if marker in text:
#             after = text.split(marker, 1)[-1].strip()
#             return after[:100].capitalize()

#     # Fallback: extract meaningful tokens after keywords like "book", etc.
#     tokens = text.split()
#     for i, token in enumerate(tokens):
#         if token.lower() in ["book", "schedule", "add", "create"]:
#             return " ".join(tokens[i+1:i+6]).capitalize()
#     return "Meeting"


# def is_time_slot_busy(service, start_iso, end_iso):
#     """Check if there's any conflict in the given time range."""
#     body = {
#         "timeMin": start_iso,
#         "timeMax": end_iso,
#         "timeZone": "UTC",
#         "items": [{"id": "primary"}],
#     }

#     fb = service.freebusy().query(body=body).execute()
#     return bool(fb["calendars"]["primary"]["busy"])





from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
import re

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Natural language to intent parser
def parse_user_input(user_input):
    user_input = user_input.lower()
    if "cancel" in user_input:
        return "cancel"
    elif "book" in user_input or "schedule" in user_input:
        return "book"
    elif "availability" in user_input or "available" in user_input:
        return "check_availability"
    elif "free slot" in user_input:
        return "find_free_slots"
    elif "remind" in user_input:
        return "set_reminder"
    elif "schedule for" in user_input or "show my day" in user_input:
        return "daily_schedule"
    else:
        return "unknown"

# Extract datetime and details (simplified)
def extract_details(user_input):
    now = datetime.now(pytz.utc)
    match_time = re.search(r'at (\d{1,2})(:(\d{2}))?\s*(am|pm)?', user_input)
    match_day = re.search(r'(today|tomorrow)', user_input)
    hour = 10
    minute = 0

    if match_time:
        hour = int(match_time.group(1))
        minute = int(match_time.group(3)) if match_time.group(3) else 0
        ampm = match_time.group(4)
        if ampm == 'pm' and hour < 12:
            hour += 12

    if match_day:
        if match_day.group(1) == 'tomorrow':
            now += timedelta(days=1)

    event_start = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    event_end = event_start + timedelta(hours=1)

    summary = "Meeting"
    summary_match = re.search(r'with (\w+)', user_input)
    if summary_match:
        summary = f"Meeting with {summary_match.group(1).capitalize()}"

    return summary, event_start.isoformat(), event_end.isoformat()

# Book an event
def book_event(service, summary, start, end):
    event = {
        'summary': summary,
        'start': {'dateTime': start, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end, 'timeZone': 'Asia/Kolkata'},
    }

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start,
        timeMax=end,
        singleEvents=True
    ).execute()

    if events_result.get('items'):
        return "Conflict: You already have an event during that time."

    service.events().insert(calendarId='primary', body=event).execute()
    return f"Event '{summary}' booked from {start} to {end}."

# Cancel event (based on title)
def cancel_event(service, user_input):
    events_result = service.events().list(
        calendarId='primary',
        timeMin=datetime.utcnow().isoformat() + 'Z',
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    for event in events:
        if user_input.lower() in event['summary'].lower():
            service.events().delete(calendarId='primary', eventId=event['id']).execute()
            return f"Event '{event['summary']}' has been canceled."
    return "No matching event found to cancel."

# Check availability now
def check_availability(service):
    now = datetime.utcnow().isoformat() + 'Z'
    in_one_hour = (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'
    events = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=in_one_hour,
        singleEvents=True
    ).execute()
    if events.get('items'):
        return "You are busy right now."
    return "You are free now."

# Daily schedule
def check_daily_schedule(service):
    now = datetime.utcnow()
    start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=pytz.utc)
    end_of_day = start_of_day + timedelta(days=1)

    events = service.events().list(
        calendarId='primary',
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    event_list = events.get('items', [])
    if not event_list:
        return "You have no events scheduled today."
    response = "Today's schedule:\n"
    for event in event_list:
        start = event['start'].get('dateTime', event['start'].get('date'))
        response += f"- {event['summary']} at {start}\n"
    return response

# Find free slots today
def find_free_slots(service):
    now = datetime.now(pytz.utc)
    end_of_day = now.replace(hour=23, minute=59)
    events = service.events().list(
        calendarId='primary',
        timeMin=now.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    busy_times = [(datetime.fromisoformat(e['start']['dateTime']), datetime.fromisoformat(e['end']['dateTime']))
                  for e in events.get('items', []) if 'dateTime' in e['start']]

    free_slots = []
    current = now
    for start, end in busy_times:
        if current < start:
            free_slots.append((current, start))
        current = max(current, end)

    if current < end_of_day:
        free_slots.append((current, end_of_day))

    if not free_slots:
        return "No free slots today."

    reply = "Free slots today:\n"
    for s, e in free_slots:
        reply += f"- {s.strftime('%H:%M')} to {e.strftime('%H:%M')}\n"
    return reply

# Set reminder (event in calendar)
def set_reminder(service, user_input):
    summary, start, end = extract_details(user_input)
    event = {
        'summary': summary,
        'start': {'dateTime': start, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end, 'timeZone': 'Asia/Kolkata'},
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 10}
            ]
        }
    }
    service.events().insert(calendarId='primary', body=event).execute()
    return f"Reminder set: {summary} at {start}."

# Entry point
def handle_calendar_command(user_input, creds):
    service = build('calendar', 'v3', credentials=creds)
    intent = parse_user_input(user_input)

    if intent == "book":
        summary, start, end = extract_details(user_input)
        return book_event(service, summary, start, end)
    elif intent == "cancel":
        return cancel_event(service, user_input)
    elif intent == "check_availability":
        return check_availability(service)
    elif intent == "find_free_slots":
        return find_free_slots(service)
    elif intent == "set_reminder":
        return set_reminder(service, user_input)
    elif intent == "daily_schedule":
        return check_daily_schedule(service)
    else:
        return "Sorry, I couldn't understand your request."

