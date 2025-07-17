import os
from openai import OpenAI
from calendar_tools import handle_calendar_command

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(message, session_id=None):
    try:
        system_prompt = (
            "You are a helpful assistant that helps users manage their Google Calendar. "
            "You MUST always respond in JSON format using one of the tools if it's about booking or checking events. "
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
                user_input_arg = eval(tool_call.function.arguments)["user_input"]
                return handle_calendar_command(user_input_arg)
        else:
            return response_message.content

    except Exception as e:
        return f"❌ Assistant error: {str(e)}"

