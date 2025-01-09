# tools.py
import requests
import json
from datetime import datetime
import pytz

def get_weather(lat, lon):
    # 1. YR requires HTTP headers including a User-Agent
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/complete?lat={lat}&lon={lon}"
    headers = {
        "User-Agent": "PersonalAgentApp/0.01 https://github.com/gvzdv/agent"
    }
    resp = requests.get(url, headers=headers)
    data = resp.json()
    forecast = process_forecast(data)
    return forecast 

def process_forecast(weather_json):
    weather = json.dumps(weather_json)

    # Load the JSON data
    data = json.loads(weather)

    # Convert UTC time to Montreal local time
    def convert_to_local_time(utc_time):
        utc_time = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%SZ")
        montreal_tz = pytz.timezone("America/Montreal")
        return utc_time.replace(tzinfo=pytz.utc).astimezone(montreal_tz)

    # Extract timeseries data
    timeseries = data["properties"]["timeseries"]

    # Initialize variables for high, low, and current temperature
    current_temp = timeseries[0]["data"]["instant"]["details"]["air_temperature"]
    high_temp = float('-inf')
    low_temp = float('inf')
    high_temp_time = None
    low_temp_time = None
    weather_summary = ""

    # Extract weather summary from the first entry
    weather_summary = ""
    if "next_12_hours" in timeseries[0]["data"]:
        weather_summary = timeseries[0]["data"]["next_12_hours"]["summary"]["symbol_code"]

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
    return {"unread_important": 2, "messages": ["Important: Meeting tomorrow", "Important: Check invoice"]}

def add_diary_entry(entry_text, storage_option):
    """
    Add a diary entry to Notion.
    """
    return {"status": f"Diary entry stored in Notion", "entry_preview": entry_text[:50]}
