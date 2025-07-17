# utils.py

import os
import json
from openai import OpenAI
from calendar_tool import handle_calendar_command

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(messages, functions=None, function_call="auto"):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        functions=functions,
        function_call=function_call
    )
    return response

