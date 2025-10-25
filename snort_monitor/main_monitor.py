import time
import os
from notifier import send_telegram_alert, send_sms_alert

ALERT_LOG = "/var/log/snort/snort.alert.fast"  # path to snort alerts
PRIORITY_THRESHOLD = 2  # example: only alert for priority >= 2

def tail_f(filename):
    """Generator to read new lines in a file like 'tail -f'"""
    with open(filename, "r") as f:
        f.seek(0, os.SEEK_END)  # move to the end
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            yield line.strip()

def parse_alert_line(line: str):
    """Basic parser: extract priority and message"""
    if "[Priority:" in line:
        try:
            priority_part = line.split("[Priority:")[1].split("]")[0].strip()
            priority = int(priority_part)
            return {"priority": priority, "msg": line}
        except:
            return {"priority": 0, "msg": line}
    else:
        return {"priority": 0, "msg": line}

def main():
    print("[ARAN] Snort Monitor Started!")
    for line in tail_f(ALERT_LOG):
        alert = parse_alert_line(line)
        print(f"[DEBUG] New line: {alert['msg']}")

        if alert["priority"] >= PRIORITY_THRESHOLD:
            send_telegram_alert(alert["msg"])
            send_sms_alert(alert["msg"])

if __name__ == "__main__":
    main()

