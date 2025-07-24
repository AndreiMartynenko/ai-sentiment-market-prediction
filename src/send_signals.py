import os
import requests

# Load env vars
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SIGNALS_FILE = "data/processed/trading_signals.txt"

def send_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    return response.status_code == 200

# Read signals and send
if os.path.exists(SIGNALS_FILE):
    with open(SIGNALS_FILE, "r") as f:
        lines = f.readlines()

    for line in lines:
        formatted = f"📡 *Signal:* {line.strip()}\n\n*Not financial advice — for research only.*"
        send_message(formatted)
    print("All signals sent to Telegram!")
else:
    print("No signal file found.")