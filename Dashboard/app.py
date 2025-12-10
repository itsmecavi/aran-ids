from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = "aran-secret-key"  # Required for sessions

# Default login credentials
USERNAME = "admin"
PASSWORD = "admin123"

# Paths
DB_PATH = "/home/cavin/Desktop/Project-Aran/snort_monitor/alerts.db"
JSON_PATH = "/home/cavin/Desktop/Project-Aran/snort_monitor/alerts.json"

# ------------------- LOGIN LOGIC --------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USERNAME and password == PASSWORD:
            session["user"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- DASHBOARD LOGIC -------------------

# Custom filter
@app.template_filter('datetimeformat')
def datetimeformat(value):
    try:
        return datetime.datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(value)

@app.route("/")
def index():

    # Require login
    if "user" not in session:
        return redirect(url_for("login"))

    priority = request.args.get("priority")
    classification = request.args.get("classification")
    alerts = []

    # Load from DB
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, classification, priority, protocol, src_ip, dest_ip, message
                FROM alerts ORDER BY id DESC LIMIT 50
            """)
            alerts = cursor.fetchall()
            conn.close()
        except Exception as e:
            print(f"[!] Database read error: {e}")

    # Load from JSON backup
    if not alerts and os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r") as f:
                data = json.load(f)
                alerts = [
                    (d.get("timestamp"), d.get("classification"), d.get("priority"),
                     d.get("protocol"), d.get("src_ip"), d.get("dest_ip"),
                     d.get("message"))
                    for d in data
                ]
        except:
            alerts = []

    # Filters
    if priority:
        alerts = [a for a in alerts if str(a[2]) == priority]
    if classification:
        alerts = [a for a in alerts if classification.lower() in str(a[1]).lower()]

    return render_template("index.html", alerts=alerts)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

