from flask import Flask, render_template, request
import json
import os
import datetime

app = Flask(__name__)
DASHBOARD_JSON = "../snort_monitor/alerts.json"

@app.template_filter('datetimeformat')
def datetimeformat(value):
    return datetime.datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

@app.route("/")
def index():
    priority = request.args.get("priority")
    classification = request.args.get("classification")
    alerts = []
    if os.path.exists(DASHBOARD_JSON):
        with open(DASHBOARD_JSON, "r") as f:
            try:
                alerts = json.load(f)
            except:
                alerts = []

    if priority:
        alerts = [a for a in alerts if str(a["priority"]) == priority]
    if classification:
        alerts = [a for a in alerts if classification.lower() in a["classification"].lower()]

    return render_template("index.html", alerts=alerts)

if __name__ == "__main__":
    app.run(debug=True)
