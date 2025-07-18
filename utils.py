from openai import OpenAI
import os
import json
from calendar_tools import handle_calendar_command

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(query: str, creds):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "handle_calendar_command",
                "description": "Handles natural language calendar requests (book, cancel, check availability).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_input": {
                            "type": "string",
                            "description": "The natural language request (e.g., 'Book meeting tomorrow at 3pm called Team Sync')"
                        }
                    },
                    "required": ["user_input"]
                }
            }
        }
    ]

    messages = [{"role": "user", "content": query}]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    choice = response.choices[0]
    tool_calls = choice.message.tool_calls

    if tool_calls:
        call = tool_calls[0]
        arguments = json.loads(call.function.arguments)
        result = handle_calendar_command(arguments["user_input"], creds)

        messages += [
            choice.message,
            {
                "role": "tool",
                "tool_call_id": call.id,
                "name": call.function.name,
                "content": result
            }
        ]

        followup = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        return followup.choices[0].message.content

    return choice.message.content



