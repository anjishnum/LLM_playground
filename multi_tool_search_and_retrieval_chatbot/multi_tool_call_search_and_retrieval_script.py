"""
A simple multi-tool agent that can search the web, convert temperature between Celsius and Fahrenheit, and calculate the area of a rectangle. It uses OpenAI's API to handle user queries and tool calls.
This script takes the user prompt, sends to the model, and if the model decides to call a tool, it executes the tool and sends the result back to the model for a final response.
"""

from tavily import TavilyClient
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import time


def celsius_fahrenheit_converter_function(temperature: float, unit: str) -> float:
    """
    Convert temperature between Celsius and Fahrenheit.

    Args:
        temperature (float): The temperature value to convert.
        unit (str): The unit of the input temperature ('C' for Celsius, 'F' for Fahrenheit).

    Returns:
        float: The converted temperature value.
    """
    if unit.upper() == 'C':
        return (temperature * 9/5) + 32  # Convert Celsius to Fahrenheit
    elif unit.upper() == 'F':
        return (temperature - 32) * 5/9  # Convert Fahrenheit to Celsius
    else:
        raise ValueError("Unit must be 'C' for Celsius or 'F' for Fahrenheit.")

celsius_fahrenheit_converter_definition = {
    "type": "function",
    "function": {
        "name": "celsius_fahrenheit_converter_function",
        "description": "Convert temperature between Celsius and Fahrenheit.",
        "parameters": {
            "type": "object",
            "properties": {
                "temperature": {
                    "type": "number",
                    "description": "The temperature value to convert."
                },
                "unit": {
                    "type": "string",
                    "description": "The unit of the input temperature ('C' for Celsius, 'F' for Fahrenheit)."
                }
            },
            "required": ["temperature", "unit"]
        }
    }
}


def area_calculator_function(length: float, width: float) -> float:
    """
    Calculate the area of a rectangle.

    Args:
        length (float): The length of the rectangle.
        width (float): The width of the rectangle.

    Returns:
        float: The area of the rectangle.
    """
    return length * width

area_calculator_definition = {
    "type": "function",
    "function": {
        "name": "area_calculator_function",
        "description": "Calculate the area of a rectangle.",
        "parameters": {
            "type": "object",
            "properties": {
                "length": {
                    "type": "number",
                    "description": "The length of the rectangle."
                },
                "width": {
                    "type": "number",
                    "description": "The width of the rectangle."
                }
            },
            "required": ["length", "width"]
        }
    }
}

def web_search_function(query: str) -> str:
    """
    Perform a web search using Tavily's API.

    Args:
        query (str): The search query.

    Returns:
        str: The search results.
    """
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    search_results = tavily_client.search(
        query=query,
        include_answer="basic",
        search_depth="advanced"
    )

    final_results = [{'url': r["url"], 'content': r["content"]} for r in search_results["results"]]
    return json.dumps(final_results)

web_search_tool_definition = {
    "type": "function",
    "function": {
        "name": "web_search_function",
        "description": "Perform web search using Tavily's API. Use this tool to search the web for recent information or to find answers to questions that require up-to-date knowledge.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query for the web search"
                }
            },
            "required": ["query"]
        }
    }
}

TOOL = {
    "celsius_fahrenheit_converter_function": celsius_fahrenheit_converter_function,
    "area_calculator_function": area_calculator_function,
    "web_search_function": web_search_function
}



def ask_model(client, messages):
    """Ask the model for a response."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=[
            celsius_fahrenheit_converter_definition,
            area_calculator_definition,
            web_search_tool_definition
        ]
    )

    return response.choices[0].message

def execute_tool(tool_call):
    """Execute the tool call and return the result."""
    tool_id = tool_call.id
    tool_name = tool_call.function.name
    arguments = tool_call.function.arguments
    if type(arguments) == str:
        arguments = json.loads(arguments)
    if tool_name in TOOL:
        try:
            result = TOOL[tool_name](**arguments)
        except Exception as e:
            print(f"Error occurred while executing tool {tool_name}: {e}")
            return {
                "role": "tool",
                "content": f"Error occurred while executing tool {tool_name}: {e}",
                "tool_call_id": tool_id
            }
    else:
        print(f"Tool {tool_name} not found.")
        return {
            "role": "tool",
            "content": f"Tool {tool_name} not found.",
            "tool_call_id": tool_id
        }
    
    return {
        "role": "tool",
        "content": f"Result from tool: {round(result, 2) if isinstance(result, float) else result}",
        "tool_call_id": tool_id
    }



def main():

    # --- Set up the OpenAI client and load environment variables --- 
    load_dotenv()

    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # --- ----


    # --- Initialize the conversation with a system prompt and get user input ---
    messages = []

    messages.append({
        "role": "system",
        "content": "You are a helpful assistant. Any numbers should be passed as text and not as latex or code blocks."
    })

    user_prompt = input('Enter your question: ')

    start_time = time.time()

    messages.append({
        "role": "user",
        "content": user_prompt
    })
    # --- ----


    # --- Ask the model for a response and handle tool calls; repeat until no more tool calls ---
    model_response = ask_model(openai_client, messages)

    while True:
        if model_response.tool_calls:
            messages.append(model_response)
            for tool_call in model_response.tool_calls:
                print('Tool called: ', tool_call.function.name)
                message_from_tool_call_response = execute_tool(tool_call)
                messages.append(message_from_tool_call_response)

            model_response = ask_model(openai_client, messages)

        else:
            print('\n',model_response.content,'\n')
            break
    # --- ----


    end_time = time.time()

    print(f"Total time taken: {round(end_time - start_time, 2)} seconds")

if __name__ == "__main__":
    main()