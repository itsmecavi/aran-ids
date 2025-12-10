import os
import time
import sqlite3
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables (Telegram, Twilio, etc.)
load_dotenv()

# === Configuration ===
ALERT_FILE = "/var/log/snort/snort.alert.fast"
DB_PATH = "/home/cavin/Desktop/Project-Aran/snort_monitor/alerts.db"

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Twilio (optional)
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_TO = os.getenv("TWILIO_TO")

# === Database Setup ===
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        classification TEXT,
        priority INTEGER,
        protocol TEXT,
        src_ip TEXT,
        dest_ip TEXT,
        message TEXT
    )''')
    conn.commit()
    conn.close()

# === Save Alert to Database ===
def save_to_db(alert):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO alerts (timestamp, classification, priority, protocol, src_ip, dest_ip, message)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (alert["timestamp"], alert["classification"], alert["priority"],
                        alert["protocol"], alert["src_ip"], alert["dest_ip"], alert["message"]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] {e}")

# === Telegram Notification ===
def send_telegram(alert_msg):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": alert_msg}
            requests.post(url, data=payload, timeout=10)
        except Exception as e:
            print(f"[Telegram ERROR] {e}")

# === Twilio Notification ===
def send_sms(alert_msg):
    if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM and TWILIO_TO):
        return
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(to=TWILIO_TO, from_=TWILIO_FROM, body=alert_msg)
    except Exception as e:
        print(f"[SMS ERROR] {e}")

# === Parse Snort Alert Line ===
def parse_alert(line):
    # Example alert format:
    # [**] [1:1000001:0] ICMP test detected [**] [Priority: 2] {ICMP} 192.168.1.10 -> 192.168.1.20
    try:
        parts = line.strip().split(" ")
        classification = " ".join(parts[2:5]).replace("[**]", "").strip()
        priority = 2
        protocol = "UNKNOWN"
        src_ip = dest_ip = "N/A"

        # Priority
        if "[Priority:" in line:
            priority = int(line.split("[Priority:")[1].split("]")[0].strip())

        # Protocol and IPs
        if "->" in line:
            proto_section = line.split("{")[1].split("}")[0]
            protocol = proto_section.strip()
            ip_part = line.split("}")[1].strip()
            src_ip, dest_ip = ip_part.split(" -> ")

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "classification": classification,
            "priority": priority,
            "protocol": protocol,
            "src_ip": src_ip,
            "dest_ip": dest_ip,
            "message": line.strip()
        }
    except Exception:
        return None

# === Main Monitor ===
def monitor_alerts():
    print("[+] Monitoring Snort alerts...")
    with open(ALERT_FILE, "r") as f:
        f.seek(0, os.SEEK_END)  # Move to end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue

            if "[**]" in line and "->" in line:
                alert = parse_alert(line)
                if alert:
                    print(f"[ALERT] {alert['message']}")
                    save_to_db(alert)
                    msg = (f"🚨 Snort Alert 🚨\n"
                           f"Type: {alert['classification']}\n"
                           f"Priority: {alert['priority']}\n"
                           f"Protocol: {alert['protocol']}\n"
                           f"Src: {alert['src_ip']}\n"
                           f"Dst: {alert['dest_ip']}\n"
                           f"Time: {alert['timestamp']}")
                    send_telegram(msg)
                    send_sms(msg)

if __name__ == "__main__":
    init_db()
    monitor_alerts()

