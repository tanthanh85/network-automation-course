# Module 10 — Creating Centralized Configuration Management Console for Cisco Routers

## 🎯 Objective
By the end of this module, learners will have designed and deployed a **Python Flask-based centralized web console** for managing multiple Cisco routers. The solution provides a web interface to:

- Display live router status
- Trigger configuration backups
- Push configuration snippets
- Monitor logs and interface status
- Send notifications (Email, Slack, Telegram)
- Serve as a foundation for full-blown NMS solutions

---

## 🌐 Why Flask?
Flask is a minimal yet powerful web framework written in Python, ideal for:

- Embedding automation logic into web dashboards
- Prototyping operational tools for NOC/SOC teams
- Integrating router automation workflows into UI-driven systems

Unlike Django or FastAPI, Flask is lightweight, fast to deploy, and simple to customize. It’s especially suited for engineers transitioning from CLI scripts to web-based automation tools.

---

## 🧱 Architecture Overview
```
┌──────────────┐      ┌──────────────────────┐      ┌────────────────────────┐
│ Web Browser  │◄────► Flask Web Interface  │◄────► Python Automation Logic │
└──────────────┘      └──────────────────────┘      └────────────────────────┘
                                              │
                               ┌──────────────┴──────────────┐
                               │ Router 1 │ Router 2 │ ...   │
                               └─────────────────────────────┘
```

---

## 🗂️ Project Directory Structure
```
router_console/
├── app.py                      # Flask entry point
├── templates/                 
│   └── index.html             # UI with buttons and tables
├── static/
│   └── style.css              # Optional styling
├── inventory.yaml             # Device list and auth
├── utils/
│   ├── fetch_status.py        # Show interface brief, version
│   ├── backup_config.py       # Run backups and diff
│   ├── push_config.py         # Send snippets or templates
│   └── notify.py              # Slack/Email alerts
├── config_snippets/
│   └── ntp.cfg                # Example push
└── logs/
    └── router1_run.txt        # Saved output per device
```

---

## 📘 inventory.yaml
```yaml
routers:
  - name: R1
    ip: sandbox-iosxe-latest-1.cisco.com
    username: developer
    password: C1sco12345
    device_type: cisco_ios

  - name: R2
    ip: sandbox-iosxe-restricted-1.cisco.com
    username: developer
    password: C1sco12345
    device_type: cisco_ios
```

---

## 🧠 Flask Concepts for Automation

### 1. Routing
```python
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/status')
def status():
    return render_template("status.html", data=fetch_status.run())
```

### 2. Template (index.html)
```html
<!DOCTYPE html>
<html>
<head><title>Router Console</title></head>
<body>
<h2>Router Control Panel</h2>
<a href="/status">Status</a> | <a href="/backup">Backup</a>
</body>
</html>
```

---

## 🔧 Sample Automation Backend: `fetch_status.py`
```python
from netmiko import ConnectHandler
import yaml

def run():
    with open("inventory.yaml") as f:
        devices = yaml.safe_load(f)['routers']

    result = []
    for dev in devices:
        conn = ConnectHandler(**dev)
        status = conn.send_command("show ip interface brief")
        result.append({"name": dev['name'], "output": status})
        conn.disconnect()
    return result
```

---

## 📤 push_config.py Example
```python
from netmiko import ConnectHandler
import yaml

def run(snippet_path):
    with open("inventory.yaml") as f:
        devices = yaml.safe_load(f)['routers']

    with open(snippet_path) as cfg:
        commands = cfg.read().splitlines()

    for dev in devices:
        conn = ConnectHandler(**dev)
        conn.send_config_set(commands)
        conn.disconnect()
```

---

## 🔔 Slack Notification Example
```python
# notify.py
import requests

def send_slack(msg):
    url = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
    requests.post(url, json={"text": msg})
```

---

## 🧪 Use Case Examples

### 🔹 Use Case 1 — Configuration Backup
1. NOC engineer clicks `Backup` on UI
2. All router configurations (`show run`) saved into logs folder
3. Slack/Email alert confirms backup success

### 🔹 Use Case 2 — Push Config to All Devices
1. Template saved in `config_snippets/ntp.cfg`
2. Engineer clicks `Apply NTP Config`
3. Script logs into all routers, applies config
4. Console shows which routers were updated successfully

### 🔹 Use Case 3 — Health Dashboard
- Shows hostname, uptime, last reboot, interface status
- Highlights devices that are unreachable
- Can include CPU, memory, or OSPF state

---

## 🔐 Flask Deployment Best Practices
- Use `.env` or Vault for secrets
- Run Flask via Gunicorn with NGINX proxy
- Protect routes with `Flask-Login`
- Use HTTPS
- Limit commands to allowlist (avoid arbitrary command injection)

---

## 🚀 Extension Ideas
- Role-Based Access Control (RBAC)
- Dynamic device discovery via NetBox API
- Compare startup vs running configs
- Schedule periodic backups with `cron`
- Database logging with SQLite/PostgreSQL


---

## 📦 Technologies Used
- Python 3.10+
- Flask (Web Framework)
- Netmiko (Device connection)
- PyYAML (Inventory)
- Slack/Email APIs (Alerting)
- Bootstrap CSS (Frontend styling)

---
