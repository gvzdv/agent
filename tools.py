import requests
import json
from datetime import datetime, timezone
import pytz
from dotenv import load_dotenv
import os

load_dotenv()

NOTION_DB_ID = os.getenv("NOTION_DB_ID")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

# Helper function: Convert UTC time to Montreal local time
def convert_to_local_time(utc_time):
    utc_time = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%SZ")
    montreal_tz = pytz.timezone("America/Montreal")
    return utc_time.replace(tzinfo=pytz.utc).astimezone(montreal_tz)


def get_weather(lat, lon):
    """
    Retrieve weather forecast from The Norwegian Meteorological Institute.
    """
    # 1. YR requires HTTP headers including a User-Agent
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/complete?lat={lat}&lon={lon}"
    headers = {"User-Agent": "PersonalAgentApp/0.01 https://github.com/gvzdv/agent"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    forecast = process_forecast(data)
    return forecast


def process_forecast(weather_json):
    """
    Process weather forecast data.
    """
    weather = json.dumps(weather_json)

    # Load the JSON data
    data = json.loads(weather)

    # Extract timeseries data
    timeseries = data["properties"]["timeseries"]

    # Initialize variables for high, low, and current temperature
    current_temp = timeseries[0]["data"]["instant"]["details"]["air_temperature"]
    high_temp = float("-inf")
    low_temp = float("inf")
    high_temp_time = None
    low_temp_time = None
    weather_summary = ""

    # Extract weather summary from the first entry
    weather_summary = ""
    if "next_12_hours" in timeseries[0]["data"]:
        weather_summary = timeseries[0]["data"]["next_12_hours"]["summary"][
            "symbol_code"
        ]

    # Iterate over the next 12 hours (assume timeseries is ordered by time)
    for entry in timeseries[:12]:
        time = entry["time"]
        temp = entry["data"]["instant"]["details"]["air_temperature"]

        if temp > high_temp:
            high_temp = temp
            high_temp_time = time

        if temp < low_temp:
            low_temp = temp
            low_temp_time = time

    # Convert high/low temperature times to local time
    high_temp_time_local = convert_to_local_time(high_temp_time).strftime("%H:%M")
    low_temp_time_local = convert_to_local_time(low_temp_time).strftime("%H:%M")

    # Generate the summary
    forecast = (
        f"Today's weather:\n"
        f"Currently: {current_temp}°C\n"
        f"High: {high_temp}°C (at {high_temp_time_local})\n"
        f"Low: {low_temp}°C (at {low_temp_time_local})\n"
        f"Stuff in the sky: {weather_summary.replace('_', ' ')}"
    )

    return forecast


def add_diary_entry(entry_text):
    """
    Add a diary entry to Notion.
    """
    # Notion API endpoint for creating a new page
    url = "https://api.notion.com/v1/pages"
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"  
    }
    
    # 1. Get the current UTC time
    now_utc = datetime.now(timezone.utc)
    # 2. Convert it to a string in the format "YYYY-MM-DDTHH:MM:SSZ"
    now_utc_str = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    # 3. Convert that UTC string to local Montreal time
    local_now = convert_to_local_time(now_utc_str)
    # 4. Format local_now as an ISO8601 string (e.g., "2025-01-16T14:30:00-05:00")
    local_now_str = local_now.isoformat()

    # Notion will store the local time with the correct offset.
    
    # Construct the request payload.
    payload = {
        "parent": {
            "database_id": NOTION_DB_ID
        },
        "properties": {
            # Title property (often named 'Name' or 'Title')
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": f"Diary entry: {local_now.strftime('%d/%m')}"
                        }
                    }
                ]
            },
            # Date property
            "Date": {
                "date": {
                    "start": local_now_str
                }
            }
        },
        # Add the text as a paragraph block
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": entry_text
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    # Make the POST request to create the page
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return f"Diary entry saved in Notion, entry preview: {entry_text[:50]}"
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


def add_event(summary, start_time, end_time):
    """
    Insert event into Google Calendar
    """
    # use googleapiclient or direct REST call with credentials
    # return success status or event info
    return {"status": "Event added", "summary": summary}


def get_events(date):
    """
    Retrieve events for a date from Google Calendar
    """
    # return list of events
    return {"events": ["Event 1 at 10:00", "Event 2 at 15:00"]}


def get_mail():
    """
    Retrieve unread mail from Gmail, focusing on importance
    """
    # return important unread messages
    return {
        "unread_important": 2,
        "messages": ["Important: Meeting tomorrow", "Important: Check invoice"],
    }
