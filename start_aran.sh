#!/usr/bin/env bash

# 1) Start Snort (adjust command if you use snort3 or different service name)
echo "[ARAN-IDS] Starting Snort..."
sudo systemctl start snort

# Optional: show status
sudo systemctl is-active --quiet snort
if [ $? -ne 0 ]; then
  echo "[ARAN-IDS] Snort failed to start. Check: sudo systemctl status snort"
  exit 1
fi

# 2) Start main monitor
echo "[ARAN-IDS] Starting main monitor..."
cd "$(dirname "$0")/snort_monitor"
python3 main_monitor2.py &

# 3) Start Flask dashboard
echo "[ARAN-IDS] Starting dashboard..."
cd "$(dirname "$0")/Dashboard"
python3 app.py &

echo "[ARAN-IDS] All components started."
echo " - Snort service (systemd)"
echo " - main_monitor2.py (background)"
echo " - Flask dashboard (background)"
