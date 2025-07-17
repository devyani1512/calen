import os
import json
from openai import OpenAI
from flask import session
from calendar_tools import handle_calendar_command

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(message):
    try:
        system_prompt = (
            "You are a helpful assistant that manages a user's Google Calendar. "
            "Always use the tool to handle any calendar-related query like booking, checking, or canceling events. "
            "Otherwise, respond casually."
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "handle_calendar_command",
                    "description": "Handles Google Calendar commands like booking or checking availability",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_input": {
                                "type": "string",
                                "description": "The user's original calendar command"
                            }
                        },
                        "required": ["user_input"]
                    }
                }
            }
        ]

        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            tools=tools,
            tool_choice="auto"
        )

        response_message = chat_response.choices[0].message

        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)
            user_input_arg = arguments["user_input"]
            return handle_calendar_command(user_input_arg, session.get("user_id"))
        else:
            return response_message.content

    except Exception as e:
        return f"❌ Assistant error: {str(e)}"


