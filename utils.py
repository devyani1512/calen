from openai import OpenAI
import os
from calendar_tools import handle_calendar_command

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(query, creds):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "handle_calendar_command",
                "description": "Handle calendar queries like availability, booking, cancelation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_input": {
                            "type": "string",
                            "description": "The user's natural language request"
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

    response_message = response.choices[0].message

    if response_message.tool_calls:
        tool_call = response_message.tool_calls[0]
        function_name = tool_call.function.name
        arguments = eval(tool_call.function.arguments)  # parse JSON string to dict
        if function_name == "handle_calendar_command":
            tool_result = handle_calendar_command(arguments["user_input"], creds)
            # Return original message + tool result
            messages.append(response_message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_result
            })

            final_response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            return final_response.choices[0].message.content
    else:
        return response_message.content


