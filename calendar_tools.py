
import pytz
import dateparser
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json



CALENDAR_ID = "primary"  # Using 'primary' for user's default calendar
TIMEZONE = "Asia/Kolkata" 

def parse_date_time(date_str, time_str):
    """Parses a date and time string into a timezone-aware datetime object."""
    combined_str = f"{date_str} {time_str}"
    parsed_dt = dateparser.parse(
        combined_str,
        settings={"TIMEZONE": TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True}
    )
    if parsed_dt and not parsed_dt.tzinfo:
        # If dateparser doesn't make it timezone aware,we assume the set TIMEZONE
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
        
        hours = "".join(filter(str.isdigit, hours_str))
        if hours:
            reminders.append(int(hours) * 60)
            if len(parts) > 1: 
                reminder_str = parts[1] 
        else: # Handle cases like "an hour" or "1 hour" where digit extraction might fail for "an"
            if "an " in hours_str or "one " in hours_str:
                reminders.append(60)
                if len(parts) > 1:
                    reminder_str = parts[1]


   
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
    
    
    return sorted(list(set(reminders)))




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
            return f" Event **'{inserted.get('summary')}'** booked on **{start_dt.strftime('%A, %B %d, %Y')}** from **{start_dt.strftime('%I:%M %p')}** to **{end_dt.strftime('%I:%M %p')}** with reminders: {mins_str}."

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
                    return f" Canceled event: **'{event['summary']}'** on {date}."
            return f"⚠ No event titled **'{summary}'** found on {date}."

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

            return " You are free during that time." if not events else " You have events during that time."

        elif intent == "check_schedule":
            date = params.get("date")

            if not date:
                return "❌ Please provide a date to check the schedule."

            start_of_day = parse_date_time(date, "00:00")
            end_of_day = parse_date_time(date, "23:59")

            if not start_of_day or not end_of_day:
                return " Couldn't parse date for schedule check."

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
                return f" No events scheduled for {date}."

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
                return " Please provide a date to find free slots."

            start_of_day = parse_date_time(date, "00:00")
            end_of_day = parse_date_time(date, "23:59")

            if not start_of_day or not end_of_day:
                return " Couldn't parse date for finding free slots."
            
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

            return "\n".join(free_slots) if free_slots else f" No free {duration_minutes}-minute slots on {date}."


        # Default or unrecognized intent
        return " I understood your message but couldn't match it to a known calendar command. Please provide structured intent and parameters."

    except HttpError as e:
        return f" Google Calendar API error: {e}"
    except Exception as e:
        return f" An unexpected error occurred: {e}"

