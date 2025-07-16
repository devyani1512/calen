# utils.py

from openai import OpenAI
import json
from calendar_tools import handle_calendar_command

client = OpenAI()

def ask_openai(user_input, user):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "handle_calendar_command",
                "description": "Handle flexible calendar requests like booking or checking events",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "A natural language calendar request, like 'Book a meeting tomorrow at 3 PM'"
                        }
                    },
                    "required": ["command"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": "You are a helpful assistant that can access the user's calendar to check availability, find free slots, and book events. If a message is a calendar request, call the tool provided."},
        {"role": "user", "content": user_input}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Or "gpt-4-turbo" or "gpt-3.5-turbo"
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # Check if a tool was called
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.function.name == "handle_calendar_command":
                arguments = json.loads(tool_call.function.arguments)
                command_text = arguments["command"]
                return handle_calendar_command(command_text, user)
    else:
        return message.content

