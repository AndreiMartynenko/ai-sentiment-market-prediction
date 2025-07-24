
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # or use PUBLIC_CHAT_ID

def send_telegram_message(message: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        raise ValueError("Missing TELEGRAM_TOKEN or CHAT_ID in .env")

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, data=payload)
    
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
    else:
        print("Message sent to Telegram!")

# Example usage
if __name__ == "__main__":
    send_telegram_message("Test signal from AI Sentiment Bot")