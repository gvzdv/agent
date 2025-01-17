import os
import openai
import os
from dotenv import load_dotenv
from tools import get_weather, add_diary_entry

# from tools import add_event, get_events, get_mail
import json
import backoff
from prompt import PROMPT

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

LATITUDE = 45.486842
LONGITUDE = -73.563944

FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather forecast.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_diary_entry",
            "description": "Add a diary entry in Notion.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "User's diary entry text.",
                    }
                },
                "required": ["content"],
            },
        },
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
]

HISTORY = [{"role": "developer", "content": PROMPT}]


@backoff.on_exception(backoff.expo, openai.RateLimitError)
def process_user_message(user_message):
    global HISTORY
    HISTORY.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=HISTORY,
        tools=FUNCTIONS,
    )

    print(response)

    message = response.choices[0].message
    tool_call = message.tool_calls

    if tool_call is not None:
        fn_name = tool_call[0].function.name

        # Call the relevant tool
        if fn_name == "get_weather":
            result = get_weather(LATITUDE, LONGITUDE)
            # right now lat/lon are hardcoded, so we don't parse them from the function call
            # args = json.loads(tool_call[0].function.arguments)
        elif fn_name == "add_diary_entry":
            args = json.loads(tool_call[0].function.arguments)
            entry_text = args["content"]
            result = add_diary_entry(entry_text)
        # elif fn_name == "add_event":
        #     result = add_event(**args)
        # elif fn_name == "get_events":
        #     result = get_events(**args)
        # elif fn_name == "get_mail":
        #     result = get_mail()
        else:
            result = "Couldn't find a suitable function."
        HISTORY.append({"role": "assistant", "content": result})
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
        HISTORY.append({"role": "assistant", "content": assistant_answer})
        return assistant_answer
