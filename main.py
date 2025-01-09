from fastapi import FastAPI, Request
import uvicorn
import os
import json
import requests

# from telegram_api import send_message, get_file, download_file
from gpt_integration import process_user_message
from history_manager import get_conversation_history, append_user_message

import os
from dotenv import load_dotenv

app = FastAPI()

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

@app.post("/webhook")
async def telegram_webhook(update: dict):
    """
    This endpoint is called by Telegram via webhook whenever there's a new message.
    """
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        
        # If voice, transcribe
        # if "voice" in message:
        #     file_id = message["voice"]["file_id"]
        #     file_info = get_file(TELEGRAM_BOT_TOKEN, file_id)
        #     file_path = file_info["result"]["file_path"]
        #     local_file_path = download_file(TELEGRAM_BOT_TOKEN, file_path)
            
        #     # Transcribe
        #     transcribed_text = transcribe_audio(local_file_path, OPENAI_API_KEY)
        #     user_text = transcribed_text
        # else:
        #     # If text
        #     user_text = message.get("text", "")
        
        # Append user message to history (will handle summarization if needed)
        conversation_history = get_conversation_history(chat_id)
        append_user_message(chat_id, user_text)
        
        # Process user message with GPT-4
        response_text = process_user_message(chat_id, conversation_history)
        
        # Send final response
        send_message(TELEGRAM_BOT_TOKEN, chat_id, response_text)
    
    return {"status": "ok"}

# def transcribe_audio(local_file_path: str, openai_api_key: str) -> str:
#     """
#     Example function using OpenAI Whisper API
#     """
#     import requests
    
#     url = "https://api.openai.com/v1/audio/transcriptions"
#     headers = {
#         "Authorization": f"Bearer {openai_api_key}"
#     }
#     files = {
#         "file": open(local_file_path, "rb"),
#         "model": (None, "whisper-1")  # or whichever model is appropriate
#     }
#     response = requests.post(url, headers=headers, files=files)
    
#     if response.status_code == 200:
#         return response.json().get("text", "")
#     else:
#         return "[Transcription Error]"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)