import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()  # this reads .env in current working directory

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ------------------- TELEGRAM ------------------- #
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] Missing bot token or chat ID")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"[Telegram] Sent: {message}")
        else:
            print(f"[Telegram] Failed: {response.text}")
    except Exception as e:
        print(f"[Telegram] Exception: {e}")

# ------------------- SMS (Twilio) ------------------- #
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_TO = os.getenv("TWILIO_TO")

def send_sms_alert(message: str):
    if not all([TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, TWILIO_TO]):
        print("[SMS] Missing Twilio credentials")
        return

    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=TWILIO_FROM, to=TWILIO_TO)
        print(f"[SMS] Sent: {message}")
    except Exception as e:
        print(f"[SMS] Failed: {e}")

