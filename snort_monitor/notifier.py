import os
import requests
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv
from mailjet_rest import Client as MailjetClient
import datetime

load_dotenv()  # loads .env file

# ------------------- TELEGRAM ------------------- #
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] Missing bot token or chat ID")
        return

    try:
        session = requests.Session()
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}

        response = session.post(url, data=payload, timeout=8)
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
    """
    This is called only for serious alerts (priority 1 or 2).
    Upstream logic (monitor script) already handles de-dup and daily caps.
    """
    if not all([TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, TWILIO_TO]):
        print("[SMS] Missing Twilio credentials")
        return

    try:
        client = TwilioClient(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=message[:1590], from_=TWILIO_FROM, to=TWILIO_TO)
        print(f"[SMS] Sent: {message}")
    except Exception as e:
        print(f"[SMS] Failed: {e}")


# ------------------- EMAIL (SMTP + HTML template) ------------------- #
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM")
SMTP_TO   = os.getenv("SMTP_TO")

# path: Project-Aran/templates/alert_email.html
TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__),
    "templates",
    "alert_email.html",
)

def _load_html_template():
    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[Email] Failed to load template: {e}")
        return ""

HTML_TEMPLATE = _load_html_template()

def _render_alert_html(alert_dict: dict) -> str:
    """
    Replace placeholders in alert_email.html using keys from alert_dict.
    Your HTML should contain placeholders like:
    {{signature}}, {{src_ip}}, {{dest_ip}}, {{protocol}},
    {{priority_label}}, {{timestamp}}
    """
    html = HTML_TEMPLATE
    replacements = {
        "{{signature}}":      alert_dict.get("signature", ""),
        "{{src_ip}}":        alert_dict.get("src_ip", ""),
        "{{dest_ip}}":       alert_dict.get("dest_ip", ""),
        "{{protocol}}":      alert_dict.get("protocol", ""),
        "{{priority_label}}": alert_dict.get("priority_label", ""),
        "{{timestamp}}":     alert_dict.get("timestamp", ""),
    }
    for key, value in replacements.items():
        html = html.replace(key, str(value))
    return html

def send_email_alert(alert: dict):
    """
    Send serious alert email via SMTP using the HTML template.
    Call this only for priority 1 or 2 alerts in your monitor.
    """
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_TO]):
        print("[Email] Missing SMTP configuration")
        return

    body_html = _render_alert_html(alert)

    msg = MIMEMultipart("alternative")
    subject_prefix = alert.get("priority_label", "Security Alert")
    msg["Subject"] = f"[{subject_prefix}] {alert.get('signature', 'Snort Alert')}"
    msg["From"] = SMTP_FROM
    msg["To"] = SMTP_TO

    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, [SMTP_TO], msg.as_string())
        print("[Email] Alert email sent successfully")
    except Exception as e:
        print(f"[Email] Failed: {e}")

