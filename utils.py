# utils.py
import os
import json
from openai import OpenAI
from calendar_tools import handle_calendar_command
from models import get_user_credentials  # Assumes this is in models.py or similar

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(message, user_id):
    try:
        system_prompt = (
            "You are a helpful assistant that helps users manage their Google Calendar. "
            "If the user message is about booking/checking/cancelling events, call the calendar tool."
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "handle_calendar_command",
                    "description": "Book/check Google Calendar based on natural language",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_input": {
                                "type": "string",
                                "description": "The user's original message",
                            }
                        },
                        "required": ["user_input"],
                    },
                },
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
            if tool_call.function.name == "handle_calendar_command":
                user_input_arg = json.loads(tool_call.function.arguments)["user_input"]
                creds = get_user_credentials(user_id)
                return handle_calendar_command(user_input_arg, creds)
        else:
            return response_message.content

    except Exception as e:
        return f"❌ Assistant error: {str(e)}"

