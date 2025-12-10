import os
from dotenv import load_dotenv
from notifier import send_email_alert  # uses your HTML template + SMTP

load_dotenv()

def main():
    # Fake alert dict to fill the placeholders
    alert = {
        "signature": "Test Attack: SYN Flood",
        "src_ip": "10.0.0.123",
        "dest_ip": "192.168.116.130",
        "protocol": "TCP",
        "priority_label": "HIGH",
        "timestamp": "2025-12-04 22:50:00",
    }
    send_email_alert(alert)

if __name__ == "__main__":
    main()

