import os
from openai import OpenAI
import os
from dotenv import load_dotenv
from tools import get_weather
# from tools import add_event, get_events
# from tools import get_mail
# from tools import add_diary_entry
import json

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

LATITUDE=45.486842
LONGITUDE=-73.563944

FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather forecast.",
            "parameters": {
                "type": "object",
                "properties": {
                },
            }
        }
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "add_event",
    #         "description": "Add an event to Google Calendar.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "summary": {"type": "string"},
    #                 "start_time": {"type": "string"},
    #                 "end_time": {"type": "string"}
    #             },
    #             "required": ["summary", "start_time", "end_time"]
    #         }
    #     }
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "get_events",
    #         "description": "Retrieve events for a given date from Google Calendar.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "date": {"type": "string"}
    #             },
    #             "required": ["date"]
    #         }
    #     }
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "get_mail",
    #         "description": "Retrieve unread Gmail messages, focusing on importance."
    #     }
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "add_diary_entry",
    #         "description": "Add a diary entry in Notion.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "title": {"type": "string"},
    #                 "content": {"type": "string"}
    #             },
    #             "required": ["title", "content"]
    #         }
    #     }
    # }
]

def process_user_message(chat_id, history):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=history,
        tools=FUNCTIONS,
    )
    
    message = response.choices[0].message
    # print(message)
    # print('--------')
    # print(message.tool_calls[0].function.name)
    
    tool_call = message.tool_calls

    if tool_call is not None:
        # print('Tool call in message')
        fn_name = tool_call[0].function.name
        # right now lat/lon are hardcoded, so we don't parse them from the function call
        # args = json.loads(tool_call[0].function.arguments)
        # print(fn_name, args)
        
        # Call the relevant tool
        if fn_name == "get_weather":
            result = get_weather(LATITUDE, LONGITUDE)
        # elif fn_name == "add_event":
        #     result = add_event(**args)
        # elif fn_name == "get_events":
        #     result = get_events(**args)
        # elif fn_name == "get_mail":
        #     result = get_mail()
        # elif fn_name == "add_diary_entry":
        #     result = add_diary_entry(**args)
        else:
            result = {"error": "No such function."}
        history.append({"role": "assistant", "content": result})
        print(result)
        return result
        
        # Provide result to GPT-4 to finalize response.
        # For now, I skip this part and return the answer directly from the function.
        # second_response = client.chat.completions.create(
        #     model="gpt-4o",
        #     messages=history + [
        #         {
        #             "role": "function",
        #             "name": fn_name,
        #             "content": json.dumps(result)
        #         }
        #     ]
        # )
        # final_message = second_response.choices[0].message.content
        # history.append({"role": "assistant", "content": final_message})
        # return final_message
    else:
        # Direct textual answer
        assistant_answer = message.content
        history.append({"role": "assistant", "content": assistant_answer})
        print(assistant_answer)
        return assistant_answer
    
test_history = [
  {
      "role": "system",
      "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user."
  },
  {
      "role": "user",
      "content": "what's the weather today?"
  }
]

process_user_message(1, test_history)