# src/send_signals.py

import os
import requests
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SIGNALS_FILE = "data/processed/trading_signals.txt"

def send_message(message: str) -> bool:
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
        if response.status_code == 200:
            logging.info("Message sent to Telegram")
            return True
        else:
            logging.warning(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Telegram API request failed: {e}")
        return False

def main():
    if not os.path.exists(SIGNALS_FILE):
        logging.warning("No signal file found.")
        return

    with open(SIGNALS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        message = f"*Signal:* {line.strip()}\n\n*Not financial advice — for research only.*"
        send_message(message)

if __name__ == "__main__":
    main()