import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_openai(message, user):
    chat_history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": message}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
    )
    return response.choices[0].message["content"].strip()
