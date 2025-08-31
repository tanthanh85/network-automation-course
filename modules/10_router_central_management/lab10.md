# Lab 10 — Centralized Router Management Console

## 🎯 Objective
Design and deploy a **web-based centralized management platform** to monitor and interact with Cisco routers using Flask and Netmiko.

This lab teaches how to:
- Build a web UI with Flask
- Read router inventory from YAML
- Collect interface status and configuration backups
- Display results via dynamic HTML templates
- Extend automation logic via modular scripts

Tested against Cisco DevNet Sandbox IOS XE device.

---

## 🧰 Prerequisites
- **Python 3.9+** installed
- **VS Code** with Python extension
- Cisco IOS XE DevNet sandbox access
  - Host: `sandbox-iosxe-latest-1.cisco.com`
  - Port: `22`
  - Username: `developer`
  - Password: `C1sco12345`

---

## 🗂 Folder Structure
```bash
lab10_central_console/
├── app.py
├── inventory.yaml
├── requirements.txt
├── templates/
│   ├── index.html
│   ├── status.html
│   └── backup.html
├── static/
│   └── style.css
├── utils/
│   ├── fetch_status.py
│   └── backup_config.py
└── logs/
    └── router_logs.txt
```

---

## 🔧 Step-by-Step Instructions

### ✅ Step 1: Create Virtual Environment and Install Dependencies
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install flask netmiko pyyaml jinja2
```
Create `requirements.txt`:
```text
flask
netmiko
pyyaml
jinja2
```

### ✅ Step 2: Define Your Router Inventory (inventory.yaml)
```yaml
routers:
  - name: IOSXE_R1
    ip: sandbox-iosxe-latest-1.cisco.com
    port: 22
    username: developer
    password: C1sco12345
    device_type: cisco_ios
```

### ✅ Step 3: Create Flask Application (app.py)
```python
from flask import Flask, render_template
from utils import fetch_status, backup_config

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    data = fetch_status.run()
    return render_template('status.html', data=data)

@app.route('/backup')
def backup():
    logs = backup_config.run()
    return render_template('backup.html', logs=logs)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

### ✅ Step 4: Status Collector (utils/fetch_status.py)
```python
from netmiko import ConnectHandler
import yaml

def run():
    with open("inventory.yaml") as f:
        routers = yaml.safe_load(f)["routers"]

    results = []
    for r in routers:
        conn = ConnectHandler(**r)
        output = conn.send_command("show ip interface brief")
        results.append({"name": r["name"], "output": output})
        conn.disconnect()
    return results
```

### ✅ Step 5: Configuration Backup Script (utils/backup_config.py)
```python
from netmiko import ConnectHandler
import yaml
from datetime import datetime

def run():
    with open("inventory.yaml") as f:
        routers = yaml.safe_load(f)["routers"]

    results = []
    for r in routers:
        conn = ConnectHandler(**r)
        config = conn.send_command("show running-config")
        filename = f"logs/{r['name']}_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(filename, 'w') as f:
            f.write(config)
        conn.disconnect()
        results.append(f"Backed up {r['name']} to {filename}")
    return results
```

### ✅ Step 6: Create HTML Templates

#### 🔹 templates/index.html
```html
<h1>Network Router Console</h1>
<a href="/status">🔍 Check Interface Status</a><br>
<a href="/backup">💾 Backup Running Configuration</a>
```

#### 🔹 templates/status.html
```html
<h2>Interface Status Summary</h2>
{% for device in data %}
<h3>{{ device.name }}</h3>
<pre>{{ device.output }}</pre>
{% endfor %}
```

#### 🔹 templates/backup.html
```html
<h2>Backup Summary</h2>
<ul>
{% for log in logs %}
  <li>{{ log }}</li>
{% endfor %}
</ul>
```

### ✅ Step 7: Launch Flask Application
```bash
flask run --port 5000
```
Then open browser: `http://127.0.0.1:5000`

---

## ✅ Expected Results

### 🔸 Web Homepage
- Navigation links for: Status and Backup

### 🔸 /status Page
- Output of `show ip interface brief` for each router

### 🔸 /backup Page
- Confirmation of saved configuration per router in `/logs`
- Filenames timestamped for easy auditing

---

## 📝 Takeaway Notes
- Flask + Netmiko enables lightweight router automation portals
- Templates (Jinja2) make UI extensible and readable
- Using `utils/` folder makes code modular and reusable
- `inventory.yaml` scales easily for 100+ routers
- This app can be dockerized or hosted on an NGINX server in production

