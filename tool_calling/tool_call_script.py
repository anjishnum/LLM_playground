from dotenv import load_dotenv
import os
from openai import OpenAI
import json

def multiply(a, b):
    return a * b

tool_definition = {
    "type": "function",
    "function": {
        "name": "multiply",
        "description": "Multiplies two numbers together.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "The first number to multiply."
                },
                "b": {
                    "type": "number",
                    "description": "The second number to multiply."
                }
            },
            "required": ["a", "b"]
        }
    }
}

def main():
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(api_key=openai_api_key)

    messages = []

    system_prompt = "You are a helpful assistant that can perform mathematical operations using the provided tools. dont show any latex or math symbols in your response. respond in plain text only."

    messages.append({"role": "system", "content": system_prompt})

    user_input = input()

    messages.append({"role": "user", "content": user_input})

    first_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[tool_definition]
    )

    messages.append(first_response.choices[0].message)
    
    if first_response.choices[0].message.tool_calls:
        tool_call = first_response.choices[0].message.tool_calls[0]
        tool_id = tool_call.id
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        if tool_name == "multiply":
            a = tool_args["a"]
            b = tool_args["b"]
            result = multiply(a, b)

            messages.append({"role": "tool", "content": f"{result}", "tool_call_id": tool_id})

            second_response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=[tool_definition]
            )

            print(second_response.choices[0].message.content)

        else:
            print("Unknown tool called.")
    
    else:
        print(first_response.choices[0].message.content)



if __name__ == "__main__":
    main()