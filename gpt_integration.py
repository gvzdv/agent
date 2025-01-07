import os
import openai
import json
from tools.weather import get_weather
from tools.calendar_api import add_event, get_events
from tools.gmail_api import get_mail
from tools.notion_diary import add_diary_entry

openai.api_key = os.environ.get("OPENAI_API_KEY", "")

FUNCTIONS = [
    {
        "name": "get_weather",
        "description": "Get the weather for a location using YR.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"}
            },
            "required": ["lat", "lon"]
        }
    },
    {
        "name": "add_event",
        "description": "Add an event to Google Calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "start_time": {"type": "string"},
                "end_time": {"type": "string"}
            },
            "required": ["summary", "start_time", "end_time"]
        }
    },
    {
        "name": "get_events",
        "description": "Retrieve events for a given date from Google Calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string"}
            },
            "required": ["date"]
        }
    },
    {
        "name": "get_mail",
        "description": "Retrieve unread Gmail messages, focusing on importance."
    },
    {
        "name": "add_diary_entry",
        "description": "Add a diary entry in Notion.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["title", "content"]
        }
    }
]

def process_user_message(chat_id, history):
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=history,
        functions=FUNCTIONS,
        function_call="auto"
    )
    
    message = response["choices"][0]["message"]
    
    if "function_call" in message:
        fn_name = message["function_call"]["name"]
        args_json = message["function_call"].get("arguments", "{}")
        args = json.loads(args_json)
        
        # Call the relevant tool
        if fn_name == "get_weather":
            result = get_weather(**args)
        elif fn_name == "add_event":
            result = add_event(**args)
        elif fn_name == "get_events":
            result = get_events(**args)
        elif fn_name == "get_mail":
            result = get_mail()
        elif fn_name == "add_diary_entry":
            result = add_diary_entry(**args)
        else:
            result = {"error": "No such function."}
        
        # Provide result to GPT-4 to finalize response
        second_response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=history + [
                {
                    "role": "function",
                    "name": fn_name,
                    "content": json.dumps(result)
                }
            ]
        )
        final_message = second_response["choices"][0]["message"]["content"]
        history.append({"role": "assistant", "content": final_message})
        return final_message
    else:
        # Direct textual answer
        assistant_answer = message["content"]
        history.append({"role": "assistant", "content": assistant_answer})
        return assistant_answer