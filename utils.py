import os
import json
from openai import OpenAI
from calendar_tool import handle_calendar_command

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(user_input, user_obj):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "handle_calendar_command",
                "description": "Process calendar requests like booking, availability checking, or finding free slots in natural language.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "A natural language calendar instruction, e.g., 'Book a meeting tomorrow at 3pm for 1 hour'"
                        }
                    },
                    "required": ["command"]
                },
            }
        }
    ]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that can access the user's calendar to check availability, "
                "book meetings, and find free time. If the user message is a calendar-related instruction, "
                "use the calendar function tool to execute it."
            )
        },
        {"role": "user", "content": user_input}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.function.name == "handle_calendar_command":
                try:
                    args = json.loads(tool_call.function.arguments)
                    return handle_calendar_command(args["command"], user_obj)
                except Exception as e:
                    return f"❌ Error processing calendar request: {str(e)}"
    else:
        return message.content
