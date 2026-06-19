from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)

messages = []

system_prompt = "you are a jovial and helpful assistant that answers questions and provides information in a friendly manner."

messages.append({'role': 'system', 'content': system_prompt})

while(True):
    
    print("\n")
    user_input = input()

    if user_input.lower() == "exit" or user_input.lower() == "quit":
        break

    messages.append({'role': 'user', 'content': user_input})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    messages.append({'role': 'assistant', 'content': response.choices[0].message.content})

    print(response.choices[0].message.content)

