# from openai import OpenAI
# import os
# import json
# from calendar_tools import handle_calendar_command

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def ask_openai(query: str, creds):
#     tools = [
#         {
#             "type": "function",
#             "function": {
#                 "name": "handle_calendar_command",
#                 "description": "Handles natural language calendar requests (book, cancel, check availability).",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "user_input": {
#                             "type": "string",
#                             "description": "The user's natural language calendar query, e.g. 'Schedule meeting at 4pm tomorrow with Rahul'."
#                         }
#                     },
#                     "required": ["user_input"]
#                 }
#             }
#         }
#     ]

#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are a helpful calendar assistant. If the user asks anything related to calendar tasks—"
#                 "such as booking, canceling, checking availability, rescheduling, or anything about dates, times, "
#                 "or events—**always** call the tool `handle_calendar_command` with the raw user input. "
#                 "Do not attempt to answer such queries directly yourself. Always rely on the tool."
#             )
#         },
#         {"role": "user", "content": query}
#     ]

#     # Initial model call
#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=messages,
#         tools=tools,
#         tool_choice="auto"
#     )

#     choice = response.choices[0]
#     tool_calls = choice.message.tool_calls

#     # If a tool is called
#     if tool_calls:
#         tool_messages = [choice.message]

#         for call in tool_calls:
#             args = json.loads(call.function.arguments)

#             if call.function.name == "handle_calendar_command":
#                 result = handle_calendar_command(args["user_input"], creds)
#             else:
#                 result = f"Tool `{call.function.name}` not recognized."

#             tool_messages.append({
#                 "role": "tool",
#                 "tool_call_id": call.id,
#                 "name": call.function.name,
#                 "content": result
#             })

#         messages += tool_messages

#         # Second model call for follow-up after tool execution
#         followup = client.chat.completions.create(
#             model="gpt-4o",
#             messages=messages
#         )

#         return followup.choices[0].message.content

#     # No tool called, just return direct response
#     return choice.message.content


# utils.py
from openai import OpenAI
import os
import json
from calendar_tools import handle_calendar_command # Make sure this import is correct

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(query: str, creds):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "handle_calendar_command",
                "description": "Handles various calendar requests like booking, canceling, checking availability, checking schedules, and finding free slots.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "description": "The specific calendar action requested by the user.",
                            "enum": ["book_event", "cancel_event", "check_availability", "check_schedule", "find_free_slots"]
                        },
                        "parameters": {
                            "type": "object",
                            "description": "A dictionary of parameters required for the specific intent.",
                            "properties": {
                                "date": {"type": "string", "description": "The date for the event/query (e.g., 'tomorrow', 'next Monday', 'July 25th')."},
                                "start_time": {"type": "string", "description": "The start time for the event/query (e.g., '10 AM', '14:30')."},
                                "end_time": {"type": "string", "description": "The end time for the event/query (e.g., '11 AM', '15:30')."},
                                "summary": {"type": "string", "description": "The title or summary of the event (e.g., 'Team Meeting', 'Dentist Appointment')."},
                                "reminder": {"type": "string", "description": "Natural language description of reminder duration (e.g., '15 minutes', '1 hour', '30 min before')."},
                                "duration_minutes": {"type": "integer", "description": "The duration in minutes for finding free slots (e.g., 60 for an hour)."}
                            },
                            # Make relevant parameters required for specific intents if desired,
                            # or handle missing parameters within handle_calendar_command
                            # For example, for book_event: "required": ["date", "start_time", "end_time", "summary"]
                        }
                    },
                    "required": ["intent", "parameters"]
                }
            }
        }
    ]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful calendar assistant. Your primary function is to interpret user requests "
                "for calendar management (booking, canceling, checking availability, schedules, or finding free slots) "
                "and translate them into structured calls to the `handle_calendar_command` tool. "
                "Extract all relevant information such as intent, dates, times, summaries, and reminders "
                "and provide them as parameters to the tool. "
                "Always call the tool `handle_calendar_command` for any calendar-related query. "
                "Do not attempt to answer such queries directly yourself. Always rely on the tool."
                "Current date and time for context: " + datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S %Z%z")
            )
        },
        {"role": "user", "content": query}
    ]

    # Initial model call
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    choice = response.choices[0]
    tool_calls = choice.message.tool_calls

    # If a tool is called
    if tool_calls:
        tool_messages = [choice.message]

        for call in tool_calls:
            # `args` will now be the dictionary with 'intent' and 'parameters'
            args = json.loads(call.function.arguments)

            print(f"DEBUG: Function Name: {call.function.name}")
            print(f"DEBUG: Arguments from OpenAI: {args}") # This will show the structured dict

            if call.function.name == "handle_calendar_command":
                # Pass the entire 'args' dictionary directly
                result = handle_calendar_command(args, creds)
            else:
                result = f"Tool `{call.function.name}` not recognized."

            tool_messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "name": call.function.name,
                "content": result
            })

        messages.extend(tool_messages) # Use extend for list of dicts

        # Second model call for follow-up after tool execution
        followup = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        return followup.choices[0].message.content

    # No tool called, just return direct response
    return choice.message.content





