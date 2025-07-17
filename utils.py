# utils.py

import json
import os
from openai import OpenAI
from calendar_tools import handle_calendar_command

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(message: str):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful calendar assistant."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content.strip()

def handle_user_query(user_input: str, user_token_info: dict):
    try:
        return handle_calendar_command(user_token_info, user_input)
    except Exception as e:
        return f"Error: {str(e)}"

