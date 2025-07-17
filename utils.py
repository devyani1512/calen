import os
import json
from openai import OpenAI
from calendar_tools import handle_calendar_command

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(message, session_id=None, user_id=None):
    try:
        system_prompt = (
            "You are a helpful assistant that helps users manage their Google Calendar. "
            "You MUST always respond in JSON format using the tool if it's about booking or checking events. "
            "If it's a casual message, respond normally."
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "handle_calendar_command",
                    "description": "Book or check Google Calendar based on natural language input",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_input": {
                                "type": "string",
                                "description": "The user's original natural language request",
                            },
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user (used to fetch credentials)",
                            }
                        },
                        "required": ["user_input", "user_id"],
                    },
                },
            }
        ]

        chat_response = client.chat.completions.create(
            model="gpt-4o",  # or gpt-3.5-turbo
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
            args = json.loads(tool_call.function.arguments)
            return handle_calendar_command(
                user_input=args["user_input"],
                user_id=args["user_id"]
            )
        else:
            return response_message.content

    except Exception as e:
        return f"❌ Assistant error: {str(e)}"


