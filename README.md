# 🛡️ Project Aran — Real-Time Threat Alert System

       db             88888888ba              db             888b      88  
      d88b            88      "8b            d88b            8888b     88  
     d8'`8b           88      ,8P           d8'`8b           88 `8b    88  
    d8'  `8b          88aaaaaa8P'          d8'  `8b          88  `8b   88  
   d8YaaaaY8b         88""""88'           d8YaaaaY8b         88   `8b  88  
  d8""""""""8b        88    `8b          d8""""""""8b        88    `8b 88  
 d8'        `8b       88     `8b        d8'        `8b       88     `8888  
d8'          `8b      88      `8b      d8'          `8b      88      `888  
                                                                           
                                                                          
## 📖 Overview
**Project Aran** (Automated Real-time Alert Network) is a cybersecurity monitoring system designed to detect and respond to network-based threats in real-time.  
It leverages **Snort IDS** for intrusion detection and integrates **multi-channel alerting mechanisms** (Telegram, Email, and SMS via Twilio) along with a **Flask-based dashboard** for visualizing live alerts.

This project is part of the **BSc (Hons) in Cyber Security** final-year research titled  
**“Development of a Real-Time Threat Alert System for Website Security Using Intrusion Detection and Automated Notifications.”**

---

## ⚙️ System Architecture

    [Network Traffic]
            │
     ┌──────▼──────┐
     │   SNORT IDS │
     └──────┬──────┘
            │
     [Snort Alert Logs]
            │
    ┌───────▼────────┐
    │  Python Monitor│  ← (main_monitor.py)
    └───────┬────────┘
            │
────────────┼─────────────────────────────────────────────────────────┐
│                 │             │
▼                 ▼             ▼                                     ▼
[Dashboard] [Telegram Bot] [Twilio SMS]                 (Flask + MySQL) (SMS Alerts)



---

## 🧩 Features

✅ **Real-time Intrusion Detection** — powered by Snort IDS  
✅ **Instant Multi-Channel Notifications** — alerts via Telegram, Email, and SMS  
✅ **Flask Dashboard** — live monitoring of threats with auto-refresh and severity indicators  
✅ **MySQL Database Integration** — stores alert history for analytics and reporting  
✅ **Modular Design** — monitor and dashboard components work independently or together  

---

## 🖥️ Tech Stack
|------------------------------------------------------------------------|
| Component           | Technology                                       |
|---------------------|--------------------------------------------------|
| **IDS Engine**      | Snort 2.x / 3.x                                  |
| **Backend**         | Python 3 (Flask, threading, dotenv)              |
| **Database**        | MySQL                                            |
| **Alert Channels**  | Telegram Bot API, Twilio API (SMS), SMTP (Email) |
| **Dashboard**       | HTML, CSS, JavaScript (Flask Templates)          |
| **Platform**        | Linux (Kali / Ubuntu)                            |
|------------------------------------------------------------------------|

## 🚀 Setup Guide

### 1️⃣ Clone the Repository
```
git clone https://github.com/itsmecavi/aran-ids.git
cd aran-ids
```

###  2️⃣ Install Dependencies
```
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables

Create a .env file inside the snort-monitor folder with the following:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TWILIO_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE=+1xxxx
RECEIVER_PHONE=+94xxxx
EMAIL_USER=youremail@gmail.com
EMAIL_PASS=yourpassword
```
### 4️⃣ Start Snort IDS
``` sudo snort -A fast -i <interface> -c /etc/snort/snort.conf ```

5️⃣ Run the Real-Time Monitor
```python3 main_monitor.py```

6️⃣ Launch the Flask Dashboard
```
cd ../Dashboard
python3 dashboard.py
```
Then open:
👉 http://127.0.0.1:5000/
