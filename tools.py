# tools.py
import requests

def get_weather(lat, lon):
    """
    Basic integration with YR Weather:
    https://developer.yr.no/doc/GettingStarted/
    """
    # Pseudo-code
    # 1. YR requires HTTP headers including a User-Agent
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    headers = {
        "User-Agent": "MyWeatherApp/1.0 contact@example.com"
    }
    resp = requests.get(url, headers=headers)
    data = resp.json()
    # parse data
    # Return a short textual forecast
    return {"forecast": "It might be sunny, data from YR: ..."}  

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
    Add a diary entry. storage_option could be 'firestore', 'cloud_storage', etc.
    """
    # For now, just pretend we store it
    return {"status": f"Diary entry stored in {storage_option}", "entry_preview": entry_text[:50]}