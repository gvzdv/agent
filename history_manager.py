from collections import defaultdict
import os
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY", "")

CONVERSATION_STORE = defaultdict(list)
MAX_MESSAGES = 20  # keep last 20 messages in raw form

def get_conversation_history(chat_id):
    return CONVERSATION_STORE[chat_id]

def append_user_message(chat_id, user_text):
    conversation = CONVERSATION_STORE[chat_id]
    conversation.append({"role": "user", "content": user_text})
    manage_history(chat_id)

def manage_history(chat_id):
    """
    If conversation goes beyond MAX_MESSAGES, summarize older messages
    and store them as a single 'assistant' or 'system' message.
    """
    conversation = CONVERSATION_STORE[chat_id]
    
    if len(conversation) > MAX_MESSAGES:
        # separate old portion
        old_section = conversation[:-MAX_MESSAGES]
        new_section = conversation[-MAX_MESSAGES:]
        
        # summarize old_section
        summary = summarize_conversation(old_section)
        
        # store the summary as a system message
        # you could store it as a special role "system" or "assistant"
        summarized_msg = {
            "role": "assistant",
            "content": f"Summary of older messages: {summary}"
        }
        
        # reset conversation to [summarized_msg + last MAX_MESSAGES]
        CONVERSATION_STORE[chat_id] = [summarized_msg] + new_section

def summarize_conversation(messages):
    """
    Use GPT-4 to summarize older conversation messages. 
    Keep it short, focusing on key points.
    """
    content_str = ""
    for msg in messages:
        role = msg["role"]
        text = msg["content"]
        content_str += f"{role.upper()}: {text}\n\n"
    
    # Simple summarization call
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that summarizes chat logs succinctly."
            },
            {
                "role": "user",
                "content": content_str
            }
        ],
        max_tokens=150,
        temperature=0.5
    )
    
    return response["choices"][0]["message"]["content"]