import requests

BASE_TELEGRAM_URL = "https://api.telegram.org/bot"

def send_message(token, chat_id, text):
    url = f"{BASE_TELEGRAM_URL}{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    resp = requests.post(url, json=payload)
    return resp.json()

def get_file(token, file_id):
    url = f"{BASE_TELEGRAM_URL}{token}/getFile"
    payload = {"file_id": file_id}
    resp = requests.post(url, json=payload)
    return resp.json()

def download_file(token, file_path):
    # Download .ogg from Telegram
    file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    local_filename = file_path.split("/")[-1]
    resp = requests.get(file_url)
    with open(local_filename, "wb") as f:
        f.write(resp.content)
    return local_filename