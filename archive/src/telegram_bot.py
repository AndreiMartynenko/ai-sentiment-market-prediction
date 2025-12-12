# src/send_telegram.py

import os
import logging
import requests
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Can be user ID or public group ID

def send_telegram_message(message: str) -> bool:
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logging.error("TELEGRAM_TOKEN or CHAT_ID is missing in .env")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logging.info("Message sent to Telegram.")
        return True
    except requests.RequestException as e:
        logging.error(f"Failed to send message: {e}")
        return False

# Example usage
if __name__ == "__main__":
    send_telegram_message("*Test signal* from AI Sentiment Bot")