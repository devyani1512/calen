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


import pytz
import dateparser
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json

# --- START: Utilities adopted from Code 1 ---
# Note: For production, GOOGLE_CREDENTIALS_JSON should be set as an environment variable
# For testing here, you might need to set it directly or provide a placeholder for the structure.
# Example: os.environ["GOOGLE_CREDENTIALS_JSON"] = json.dumps({"type": "service_account", ...})

# Placeholder for service object setup as per original code 1's setup section
# Assuming 'creds' passed to create_service will handle this from an external source
# creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
# info = json.loads(creds_json)
# credentials = service_account.Credentials.from_service_account_info(
#     info, scopes=["https://www.googleapis.com/auth/calendar"]
# )
# service = build("calendar", "v3", credentials=credentials)

CALENDAR_ID = "primary"  # Using 'primary' for user's default calendar as in original code 2
TIMEZONE = "Asia/Kolkata" # Keeping timezone consistent with original code 1 setup

def parse_date_time(date_str, time_str):
    """Parses a date and time string into a timezone-aware datetime object."""
    combined_str = f"{date_str} {time_str}"
    parsed_dt = dateparser.parse(
        combined_str,
        settings={"TIMEZONE": TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True}
    )
    if parsed_dt and not parsed_dt.tzinfo:
        # If dateparser doesn't make it timezone aware, assume the set TIMEZONE
        local_tz = pytz.timezone(TIMEZONE)
        parsed_dt = local_tz.localize(parsed_dt)
    return parsed_dt

def parse_reminder_string(reminder_str: str) -> list[int]:
    """
    Parse strings like '1 hour and 15 minutes' → [60, 15] (minutes before).
    """
    if not reminder_str:
        return [15] # Default reminder
    reminder_str = reminder_str.lower()
    reminders = []
    
    # Handle hours
    if "hour" in reminder_str:
        parts = reminder_str.split("hour")
        hours_str = parts[0].strip()
        # Extract digits before "hour"
        hours = "".join(filter(str.isdigit, hours_str))
        if hours:
            reminders.append(int(hours) * 60)
            if len(parts) > 1: # Check if there's more after "hour"
                reminder_str = parts[1] # Continue parsing for minutes
        else: # Handle cases like "an hour" or "1 hour" where digit extraction might fail for "an"
            if "an " in hours_str or "one " in hours_str:
                reminders.append(60)
                if len(parts) > 1:
                    reminder_str = parts[1]


    # Handle minutes
    if "minute" in reminder_str:
        if "and" in reminder_str:
            minutes = reminder_str.split("and")[-1]
        else:
            minutes = reminder_str.split("minute")[0]
        minutes = "".join(filter(str.isdigit, minutes))
        if minutes:
            reminders.append(int(minutes))

    if not reminders:
        reminders = [15] # Default if nothing is parsed
    
    # Ensure no duplicates and sort for consistency, though not strictly necessary for overrides
    return sorted(list(set(reminders)))

# --- END: Utilities adopted from Code 1 ---


def create_service(creds):
    """Builds and returns the Google Calendar API service object."""
    return build("calendar", "v3", credentials=creds)

def is_time_slot_busy(service, start_iso, end_iso):
    """Check if there's any conflict in the given time range."""
    body = {
        "timeMin": start_iso,
        "timeMax": end_iso,
        "timeZone": "UTC", # Free/busy API expects UTC
        "items": [{"id": CALENDAR_ID}],
    }

    try:
        fb = service.freebusy().query(body=body).execute()
        return bool(fb["calendars"][CALENDAR_ID]["busy"])
    except HttpError as e:
        print(f"Error checking free/busy: {e}")
        return False # Assume not busy or handle error upstream

def handle_calendar_command(user_command: dict, creds):
    """
    Handles calendar commands based on a structured dictionary input,
    interpreting intents and parameters.

    Args:
        user_command (dict): A dictionary containing 'intent' and 'parameters'.
                             Example:
                             {
                                 "intent": "book_event",
                                 "parameters": {
                                     "date": "tomorrow",
                                     "start_time": "10:00 AM",
                                     "end_time": "11:00 AM",
                                     "summary": "Project Sync",
                                     "reminder": "15 minutes"
                                 }
                             }
                             or
                             {
                                 "intent": "cancel_event",
                                 "parameters": {
                                     "summary": "Dentist Appointment",
                                     "date": "next Tuesday"
                                 }
                             }
                             or
                             {
                                 "intent": "check_availability",
                                 "parameters": {
                                     "date": "today",
                                     "start_time": "9 AM",
                                     "end_time": "5 PM"
                                 }
                             }
                             or
                             {
                                 "intent": "check_schedule",
                                 "parameters": {
                                     "date": "Friday"
                                 }
                             }
                             or
                             {
                                 "intent": "find_free_slots",
                                 "parameters": {
                                     "date": "tomorrow",
                                     "duration_minutes": 90
                                 }
                             }
        creds: Google API credentials.

    Returns:
        str: A message indicating the result of the calendar command.
    """
    service = create_service(creds)
    params = user_command.get("parameters", {})
    intent = user_command.get("intent")

    try:
        if intent == "book_event":
            date = params.get("date")
            start_time = params.get("start_time")
            end_time = params.get("end_time")
            summary = params.get("summary", "Meeting")
            reminder = params.get("reminder")

            if not all([date, start_time, end_time]):
                return "❌ Please provide a date, start time, and end time to book an event."

            start_dt = parse_date_time(date, start_time)
            end_dt = parse_date_time(date, end_time)

            if not start_dt or not end_dt or start_dt >= end_dt:
                return "❌ Invalid or unclear time range for booking."

            # Convert to UTC for Google Calendar API
            start_dt_utc = start_dt.astimezone(pytz.utc)
            end_dt_utc = end_dt.astimezone(pytz.utc)

            if is_time_slot_busy(service, start_dt_utc.isoformat(), end_dt_utc.isoformat()):
                return f"❌ You're already busy during **{start_dt.strftime('%I:%M %p')} to {end_dt.strftime('%I:%M %p')}** on {date}. Try a different time."

            reminder_minutes_list = parse_reminder_string(reminder)
            overrides = [{"method": "popup", "minutes": m} for m in reminder_minutes_list]

            body = {
                "summary": summary,
                "start": {"dateTime": start_dt_utc.isoformat(), "timeZone": "UTC"},
                "end": {"dateTime": end_dt_utc.isoformat(), "timeZone": "UTC"},
                "reminders": {
                    "useDefault": False,
                    "overrides": overrides
                }
            }

            inserted = service.events().insert(calendarId=CALENDAR_ID, body=body).execute()
            mins_str = ", ".join([f"{m} min" for m in reminder_minutes_list])
            return f"✅ Event **'{inserted.get('summary')}'** booked on **{start_dt.strftime('%A, %B %d, %Y')}** from **{start_dt.strftime('%I:%M %p')}** to **{end_dt.strftime('%I:%M %p')}** with reminders: {mins_str}."

        elif intent == "cancel_event":
            summary = params.get("summary")
            date = params.get("date")

            if not all([summary, date]):
                return "❌ Please provide the event summary and date to cancel an event."

            start_of_day = parse_date_time(date, "00:00")
            end_of_day = parse_date_time(date, "23:59")

            if not start_of_day or not end_of_day:
                return "❌ Couldn't parse date for cancellation."

            # Convert to UTC for Google Calendar API
            start_of_day_utc = start_of_day.astimezone(pytz.utc)
            end_of_day_utc = end_of_day.astimezone(pytz.utc)

            events_result = service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=start_of_day_utc.isoformat(),
                timeMax=end_of_day_utc.isoformat(),
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            events = events_result.get("items", [])

            for event in events:
                if event.get("summary", "").lower() == summary.lower():
                    service.events().delete(calendarId=CALENDAR_ID, eventId=event["id"]).execute()
                    return f"🗑️ Canceled event: **'{event['summary']}'** on {date}."
            return f"⚠️ No event titled **'{summary}'** found on {date}."

        elif intent == "check_availability":
            date = params.get("date")
            start_time = params.get("start_time")
            end_time = params.get("end_time")

            if not all([date, start_time, end_time]):
                return "❌ Please provide a date, start time, and end time to check availability."

            start_dt = parse_date_time(date, start_time)
            end_dt = parse_date_time(date, end_time)

            if not start_dt or not end_dt:
                return "❌ Couldn't parse time range for availability check."

            # Convert to UTC for Google Calendar API
            start_dt_utc = start_dt.astimezone(pytz.utc)
            end_dt_utc = end_dt.astimezone(pytz.utc)

            events_result = service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=start_dt_utc.isoformat(),
                timeMax=end_dt_utc.isoformat(),
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            events = events_result.get("items", [])

            return "✅ You are free during that time." if not events else "🗓️ You have events during that time."

        elif intent == "check_schedule":
            date = params.get("date")

            if not date:
                return "❌ Please provide a date to check the schedule."

            start_of_day = parse_date_time(date, "00:00")
            end_of_day = parse_date_time(date, "23:59")

            if not start_of_day or not end_of_day:
                return "❌ Couldn't parse date for schedule check."

            # Convert to UTC for Google Calendar API
            start_of_day_utc = start_of_day.astimezone(pytz.utc)
            end_of_day_utc = end_of_day.astimezone(pytz.utc)

            events_result = service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=start_of_day_utc.isoformat(),
                timeMax=end_of_day_utc.isoformat(),
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            events = events_result.get("items", [])

            if not events:
                return f"✅ No events scheduled for {date}."

            schedule_list = []
            for event in events:
                start = dateparser.parse(event['start']['dateTime']).astimezone(pytz.timezone(TIMEZONE))
                end = dateparser.parse(event['end']['dateTime']).astimezone(pytz.timezone(TIMEZONE))
                schedule_list.append(
                    f"- **{event['summary']}** from {start.strftime('%I:%M %p')} to {end.strftime('%I:%M %p')}"
                )
            return f"🗓️ Here's your schedule for {date}:\n" + "\n".join(schedule_list)

        elif intent == "find_free_slots":
            date = params.get("date")
            duration_minutes = params.get("duration_minutes", 60) # Default to 60 minutes

            if not date:
                return "❌ Please provide a date to find free slots."

            start_of_day = parse_date_time(date, "00:00")
            end_of_day = parse_date_time(date, "23:59")

            if not start_of_day or not end_of_day:
                return "❌ Couldn't parse date for finding free slots."
            
            # Convert to UTC for Google Calendar API
            start_of_day_utc = start_of_day.astimezone(pytz.utc)
            end_of_day_utc = end_of_day.astimezone(pytz.utc)

            events_result = service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=start_of_day_utc.isoformat(),
                timeMax=end_of_day_utc.isoformat(),
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            events = events_result.get("items", [])

            # Convert event times back to local timezone for logic
            busy_times = []
            for e in events:
                start_local = dateparser.parse(e["start"]["dateTime"]).astimezone(pytz.timezone(TIMEZONE))
                end_local = dateparser.parse(e["end"]["dateTime"]).astimezone(pytz.timezone(TIMEZONE))
                busy_times.append((start_local, end_local))
            
            busy_times.sort()

            current = start_of_day
            free_slots = []

            for start, end in busy_times:
                if (start - current).total_seconds() >= duration_minutes * 60:
                    free_slots.append(f"{current.strftime('%I:%M %p')} to {start.strftime('%I:%M %p')}")
                current = max(current, end)

            if (end_of_day - current).total_seconds() >= duration_minutes * 60:
                free_slots.append(f"{current.strftime('%I:%M %p')} to {end_of_day.strftime('%I:%M %p')}")

            return "\n".join(free_slots) if free_slots else f"❌ No free {duration_minutes}-minute slots on {date}."


        # Default or unrecognized intent
        return "🤖 I understood your message but couldn't match it to a known calendar command. Please provide structured intent and parameters."

    except HttpError as e:
        return f"❌ Google Calendar API error: {e}"
    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"


# --- How to use this modified handle_calendar_command ---
# This version expects a pre-parsed 'user_command' dictionary.
# You would need an *external* component (like an NLU/NLP model)
# to take raw user input (e.g., "Book a meeting tomorrow from 10 to 11 AM about Project X")
# and convert it into the structured 'user_command' dictionary.

# Example Usage (assuming you have 'creds' object from an OAuth flow)
# You would replace `your_creds_object` with the actual credentials.

# from google.oauth2.credentials import Credentials # Example import for credentials

# # --- Mock Credentials for demonstration if running directly ---
# # In a real scenario, these would come from an OAuth flow or service account file.
# # For demonstration, you might load a dummy structure or use actual ones if available.
# # For a service account:
# # import google.auth
# # import google.oauth2.service_account
# # creds_info = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
# # mock_creds = google.oauth2.service_account.Credentials.from_service_account_info(
# #    creds_info, scopes=["https://www.googleapis.com/auth/calendar"]
# # )

# # For user credentials (OAuth 2.0 flow):
# # You would typically get this from a web flow.
# # Here's a placeholder:
# # from google.auth.transport.requests import Request
# # from google.oauth2.credentials import Credentials
# # if os.path.exists('token.json'):
# #     mock_creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar'])
# # else:
# #     mock_creds = None # You'd trigger an OAuth flow here


# # --- DEMO USAGE ---
# # To make this runnable for demonstration, let's create a dummy creds object
# # In a real app, this would be proper authenticated credentials.
# class MockCredentials:
#     def __init__(self, token='mock_token'):
#         self.token = token
#     def apply(self, headers):
#         headers['Authorization'] = f'Bearer {self.token}'
#     def refresh(self, request):
#         pass # Not implemented for mock
#     def to_json(self):
#         return json.dumps({"token": self.token})

# mock_creds = MockCredentials()

# # 1. Book an event
# book_command = {
#     "intent": "book_event",
#     "parameters": {
#         "date": "21st July 2025",
#         "start_time": "10:00 AM",
#         "end_time": "11:00 AM",
#         "summary": "Team Standup",
#         "reminder": "15 minutes"
#     }
# }
# print(handle_calendar_command(book_command, mock_creds))

# # 2. Check schedule
# schedule_command = {
#     "intent": "check_schedule",
#     "parameters": {
#         "date": "21st July 2025"
#     }
# }
# print(handle_calendar_command(schedule_command, mock_creds))

# # 3. Check availability for a specific time
# availability_command = {
#     "intent": "check_availability",
#     "parameters": {
#         "date": "21st July 2025",
#         "start_time": "10:30 AM",
#         "end_time": "11:30 AM"
#     }
# }
# print(handle_calendar_command(availability_command, mock_creds))

# # 4. Find free slots
# free_slots_command = {
#     "intent": "find_free_slots",
#     "parameters": {
#         "date": "21st July 2025",
#         "duration_minutes": 30
#     }
# }
# print(handle_calendar_command(free_slots_command, mock_creds))

# # 5. Cancel an event
# cancel_command = {
#     "intent": "cancel_event",
#     "parameters": {
#         "summary": "Team Standup",
#         "date": "21st July 2025"
#     }
# }
# print(handle_calendar_command(cancel_command, mock_creds))
