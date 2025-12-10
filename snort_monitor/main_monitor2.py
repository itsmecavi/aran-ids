#!/usr/bin/env python3
import os
import time
import sqlite3
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

# NEW: import email notifier
from notifier import send_email_alert  # adjust path if needed

# ====================== BANNER ======================
from rich.console import Console
from rich.panel import Panel
from rich import box
from pyfiglet import Figlet

os.system("")
console = Console()

f = Figlet(font="big", width=200)
console.print(f"[bold blue]{f.renderText('ARAN-IDS')}[/]")

console.print(Panel(
    "[bold cyan]ARAN-IDS: Active Network Defense[/]\n\n"
    "[green]• Real-time Snort alert monitoring[/]\n"
    "[green]• Telegram + Email incident notifications[/]\n"
    "[green]• Centralised SQLite alert logging[/]\n"
    "[green]• Lightweight, auditable Python stack[/]\n\n"
    "[bold white on green]        SECURITY MONITORING ONLINE        [/]",
    title="[bold white on blue] ARAN-IDS v1.0 [/]",
    subtitle="[bold bright_cyan]Enterprise Network Threat Monitoring[/]",
    border_style="bright_blue",
    box=box.HEAVY,
    padding=(1, 8),
    width=90
))

console.print("\n[bold blue]╔[/][white]══════════════════════════════════════════════════════════[/][bold blue]╗[/]")
console.print("   [bold green]                 STATUS: Monitoring active[/]")
console.print("[bold blue]╚[/][white]══════════════════════════════════════════════════════════[/][bold blue]╝[/]\n")

# ====================== CONFIG ======================
load_dotenv()

ALERT_FILE = "/var/log/snort/snort.alert.fast"
DB_PATH    = "/home/cavin/Desktop/Project-Aran/snort_monitor/alerts.db"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")
TWILIO_SID         = os.getenv("TWILIO_SID")
TWILIO_TOKEN       = os.getenv("TWILIO_TOKEN")
TWILIO_FROM        = os.getenv("TWILIO_FROM")
TWILIO_TO          = os.getenv("TWILIO_TO")

# serious alert policy
SERIOUS_PRIORITIES = [1, 2]      # only these get SMS + EMAIL

# SMS protection
SMS_DAILY_LIMIT = 5              # tune for Twilio trial
_sms_daily_count = 0
_sms_cache = {}                  # {hash(msg): last_sent_time}

# ====================== DATABASE ======================
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, classification TEXT, priority INTEGER,
            protocol TEXT, src_ip TEXT, dest_ip TEXT, message TEXT)''')

# ====================== SAVE ALERT ======================
def save_to_db(alert):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''INSERT INTO alerts
                (timestamp, classification, priority, protocol, src_ip, dest_ip, message)
                VALUES (?,?,?,?,?,?,?)''',
                (alert["timestamp"], alert["classification"], alert["priority"],
                 alert["protocol"], alert["src_ip"], alert["dest_ip"], alert["message"]))
    except Exception as e:
        console.print(f"[red]DB ERROR:[/] {e}")

# ====================== NOTIFICATIONS ======================
def send_telegram(msg):
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=8
        )
    except:
        pass

def can_send_sms(msg: str) -> bool:
    """
    Protect Twilio trial:
    - de-duplicate same message for 1 hour
    - enforce per-process daily cap
    """
    global _sms_daily_count, _sms_cache

    now = datetime.now()

    # simple "day" bucket: reset counter when date changes in this process
    current_day = now.strftime("%Y-%m-%d")
    cache_day = _sms_cache.get("_day")
    if cache_day != current_day:
        _sms_daily_count = 0
        _sms_cache = {"_day": current_day}

    if _sms_daily_count >= SMS_DAILY_LIMIT:
        console.print("[yellow][SMS] Daily limit reached, skipping.[/]")
        return False

    h = hash(msg)
    last = _sms_cache.get(h)
    if last and (now - last) < timedelta(hours=1):
        console.print("[yellow][SMS] Duplicate within 1 hour, skipping.[/]")
        return False

    _sms_daily_count += 1
    _sms_cache[h] = now
    return True

def send_sms(msg):
    if not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, TWILIO_TO]):
        return
    if not can_send_sms(msg):
        return
    try:
        from twilio.rest import Client
        Client(TWILIO_SID, TWILIO_TOKEN).messages.create(
            to=TWILIO_TO, from_=TWILIO_FROM, body=msg[:1590])
        console.print("[green][SMS] Sent serious alert.[/]")
    except:
        pass

# ====================== PARSE ALERT ======================
def parse_alert(line):
    try:
        priority = int(line.split("[Priority:")[1].split("]")[0]) if "[Priority:" in line else 3
        protocol = line.split("{")[1].split("}")[0] if "{" in line and "}" in line else "UNKNOWN"
        ip_part = line.split("}")[1].strip() if "}" in line else ""
        src_ip, dest_ip = ip_part.split(" -> ") if " -> " in ip_part else ("?", "?")
        classification = line.split("[**]")[1].strip() if len(line.split("[**]")) > 1 else "Alert"

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "classification": classification,
            "priority": priority,
            "protocol": protocol,
            "src_ip": src_ip.strip(),
            "dest_ip": dest_ip.strip(),
            "message": line.strip()
        }
    except:
        return None

# ====================== MAIN LOOP ======================
def monitor_alerts():
    if not os.path.exists(ALERT_FILE):
        console.print(f"[bold red][!] Snort alert file not found:[/] {ALERT_FILE}")
        return

    console.print("[bold green][+] Monitoring started — waiting for threats…[/]\n")

    with open(ALERT_FILE, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.3)
                continue
            if "[**]" in line and "->" in line:
                alert = parse_alert(line)
                if alert:
                    color = "bright_red" if alert["priority"] == 1 else "yellow" if alert["priority"] == 2 else "white"
                    console.print(f"[{color}]ALERT[/] {alert['message']}")
                    save_to_db(alert)

                    severity = (
                        "CRITICAL" if alert["priority"] == 1
                        else "HIGH" if alert["priority"] == 2
                        else "MEDIUM"
                    )

                    msg = (
                        f"<b>ARAN-IDS Alert</b>\n"
                        f"<code>{alert['timestamp']}</code>\n"
                        f"<b>Severity:</b> {severity} (P{alert['priority']})\n"
                        f"<b>Event:</b> {alert['classification']}\n"
                        f"<b>Source:</b> {alert['src_ip']}  →  "
                        f"<b>Destination:</b> {alert['dest_ip']}\n"
                        f"<b>Protocol:</b> {alert['protocol']}"
                    )

                    # Telegram always
                    send_telegram(msg)

                    # Serious only → SMS + EMAIL
                    if alert["priority"] in SERIOUS_PRIORITIES:
                        send_sms(msg)
                        send_email_alert(alert)  # HTML email using template

if __name__ == "__main__":
    init_db()
    try:
        monitor_alerts()
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]ARAN-IDS v1.0 monitoring stopped by operator. stopped. Network exposed.[/]")
        
        console.print("[bold cyan]Remember to restart monitoring after maintenance.[/]")

