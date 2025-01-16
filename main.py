from flask import Flask, request, jsonify
import os
import requests
import logging
from dotenv import load_dotenv
from gpt_integration import process_user_message, HISTORY

# Initiate app
app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET")

# Load secrets
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
WEBHOOK_URL = os.getenv("SERVICE_URL") + f"/webhook/{BOT_TOKEN}"
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
FILE_API_URL = f'https://api.telegram.org/file/bot{BOT_TOKEN}'


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

@app.route('/webhook/<token>', methods=['POST'])
def webhook(token):
    if token == BOT_TOKEN:
        try:
            update = request.get_json()
            app.logger.debug(f"Received update: {update}")

            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']

                if chat_id != USER_ID:
                    app.logger.warning(f"Unauthorized access attempt by user ID: {chat_id}")
                    return jsonify({'status': 'unauthorized'}), 403

                if 'text' in message:
                    user_text = message['text']
                    print(f"Received message: {user_text}")
                    
                    # Append user message to history and process user message with GPT-4o
                    response_text = process_user_message(user_text)
                    app.logger.debug(f"Response: {response_text}")
                    app.logger.debug(f"Conversation history: {HISTORY}")
                    
                    # Send final response
                    send_message(chat_id, response_text)
                    return jsonify({'status': 'ok'}), 200
                
        except Exception as e:
            app.logger.error(f"Error in webhook function: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        app.logger.error("Unauthorized access attempt")
        return jsonify({'status': 'unauthorized'}), 401

# @app.post("/webhook")
# async def telegram_webhook(update: dict):
#     """
#     This endpoint is called by Telegram via webhook whenever there's a new message.
#     """
#     if "message" in update:
#         message = update["message"]
#         chat_id = message["chat"]["id"]
        
#         # If voice, transcribe
#         # if "voice" in message:
#         #     file_id = message["voice"]["file_id"]
#         #     file_info = get_file(TELEGRAM_BOT_TOKEN, file_id)
#         #     file_path = file_info["result"]["file_path"]
#         #     local_file_path = download_file(TELEGRAM_BOT_TOKEN, file_path)
            
#         #     # Transcribe
#         #     transcribed_text = transcribe_audio(local_file_path, OPENAI_API_KEY)
#         #     user_text = transcribed_text
#         # else:
#         #     # If text
#         #     user_text = message.get("text", "")
        
#         # Append user message to history (will handle summarization if needed)
#         conversation_history = get_conversation_history(chat_id)
#         append_user_message(chat_id, user_text)
        
#         # Process user message with GPT-4
#         response_text = process_user_message(chat_id, conversation_history)
        
#         # Send final response
#         send_message(TELEGRAM_BOT_TOKEN, chat_id, response_text)
    
#     return {"status": "ok"}

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)