import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")

def send_message(chat_id, text):
    send_message_url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(send_message_url, json=payload)
    if response.status_code == 200:
        app.logger.debug("Message sent successfully")
    else:
        app.logger.error(f"Failed to send message: {response.text}")

# Later: add voice file processing

# def get_file(token, file_id):
#     url = f"{BASE_TELEGRAM_URL}{token}/getFile"
#     payload = {"file_id": file_id}
#     resp = requests.post(url, json=payload)
#     return resp.json()

# def download_file(token, file_path):
#     # Download .ogg from Telegram
#     file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
#     local_filename = file_path.split("/")[-1]
#     resp = requests.get(file_url)
#     with open(local_filename, "wb") as f:
#         f.write(resp.content)
#     return local_filename