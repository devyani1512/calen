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
                            "description": "The user's natural language calendar query, e.g. 'Schedule meeting at 4pm tomorrow with Rahul'."
                        }
                    },
                    "required": ["user_input"]
                }
            }
        }
    ]

    messages = [{"role": "user", "content": query}]

    # Initial model call
    response = client.chat.completions.create(
        model="gpt-4o",  # Changed to gpt-4o to avoid 403 error
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
            args = json.loads(call.function.arguments)

            if call.function.name == "handle_calendar_command":
                result = handle_calendar_command(args["user_input"], creds)
            else:
                result = f"Tool `{call.function.name}` not recognized."

            tool_messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "name": call.function.name,
                "content": result
            })

        messages += tool_messages

        # Second model call for follow-up after tool execution
        followup = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        return followup.choices[0].message.content

    # No tool called, just return direct response
    return choice.message.content




