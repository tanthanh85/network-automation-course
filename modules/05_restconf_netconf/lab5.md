# Lab 5 – Automating Network Monitoring with RESTCONF & NETCONF

---

## 🎯 Objective
In this lab, you will:
- Connect to Cisco DevNet Sandbox (IOS XE)
- Retrieve interface and device health data via **RESTCONF**
- Pull hostname and BGP status via **NETCONF**
- Use **YAML inventory**, **Jinja2**, and **helper modules** to organize your scripts
- Learn how to build NETCONF payloads and locate RESTCONF API endpoints using official docs or Postman

By the end, you will be able to monitor a router using model-driven APIs programmatically.

---

## 🧰 Prerequisites
- Python 3.8+ and VSCode installed
- Installed: `requests`, `xmltodict`, `ncclient`, `PyYAML`
```bash
pip install requests xmltodict ncclient pyyaml
```

---

## 🧪 Step 1 — Connect to Cisco IOS XE Sandbox
Use the always-on sandbox:

🔗 https://developer.cisco.com/site/ios-xe/

| Field        | Value                    |
|--------------|--------------------------|
| Host         | sandbox-iosxe-latest-1.cisco.com |
| RESTCONF Port| 443                      |
| NETCONF Port | 830                      |
| Username     | developer                |
| Password     | C1sco12345               |

---

## 🧪 Step 2 — Project Folder Layout
Create this structure in your VSCode workspace:

```
nasp-lab5/
├── inventory.yaml
├── restconf/
│   └── get_interfaces.py
├── netconf/
│   └── get_hostname.py
├── utils/
│   ├── restconf_helper.py
│   └── netconf_helper.py
```

---

## 🧪 Step 3 — Define Inventory
**inventory.yaml**
```yaml
devices:
  - name: iosxe1
    ip: sandbox-iosxe-latest-1.cisco.com
    port: 443
    netconf_port: 830
    username: developer
    password: C1sco12345
```

---

## 🧪 Step 4 — RESTCONF Helper Module
**utils/restconf_helper.py**
```python
import requests, yaml
from requests.auth import HTTPBasicAuth

with open("../inventory.yaml") as f:
    device = yaml.safe_load(f)['devices'][0]

BASE_URL = f"https://{device['ip']}:{device['port']}"
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

requests.packages.urllib3.disable_warnings()

def get_restconf(path):
    url = BASE_URL + path
    try:
        resp = requests.get(url, auth=HTTPBasicAuth(device['username'], device['password']),
                            headers=HEADERS, verify=False)
        return resp.json()
    except Exception as e:
        print("❌ RESTCONF Error:", e)
```

---

## 🧪 Step 5 — Retrieve Interfaces via RESTCONF
**restconf/get_interfaces.py**
```python
from utils.restconf_helper import get_restconf

path = "/data/ietf-interfaces:interfaces"
data = get_restconf(path)

interfaces = data['ietf-interfaces:interfaces']['interface']
for intf in interfaces:
    print(f"{intf['name']} ➡️ Enabled: {intf['enabled']}, Type: {intf['type']}")
```

✅ **Run:**
```bash
python restconf/get_interfaces.py
```

🟢 **Expected Output:**
```
GigabitEthernet1 ➡️ Enabled: True, Type: iana-if-type:ethernetCsmacd
Loopback0 ➡️ Enabled: True, Type: iana-if-type:softwareLoopback
```

---

## 🧪 Step 6 — NETCONF Helper Module
**utils/netconf_helper.py**
```python
from ncclient import manager
import yaml

with open("../inventory.yaml") as f:
    device = yaml.safe_load(f)['devices'][0]

def netconf_connect():
    return manager.connect(
        host=device['ip'],
        port=device['netconf_port'],
        username=device['username'],
        password=device['password'],
        hostkey_verify=False,
        device_params={'name': 'csr'},
        look_for_keys=False,
        allow_agent=False
    )
```

---

## 🧪 Step 7 — Get Hostname via NETCONF
**netconf/get_hostname.py**
```python
from utils.netconf_helper import netconf_connect
import xmltodict

m = netconf_connect()
filter = """
<filter>
  <native xmlns='http://cisco.com/ns/yang/Cisco-IOS-XE-native'>
    <hostname></hostname>
  </native>
</filter>
"""
response = m.get(filter)
data = xmltodict.parse(response.xml)
host = data['rpc-reply']['data']['native']['hostname']
print("🔎 Hostname:", host)
m.close_session()
```

✅ **Run:**
```bash
python netconf/get_hostname.py
```
🟢 **Expected Output:**
```
🔎 Hostname: ios-xe-mgmt.cisco.com
```

---

## 🔎 How to Build NETCONF Filters
- Use `xmltodict` to help parse XML output
- Always refer to YANG models: https://github.com/YangModels/yang
- Wrap payload inside `<filter>...</filter>`
- Use correct namespaces (e.g., `http://cisco.com/ns/yang/Cisco-IOS-XE-native`)

---

## 🌐 How to Explore RESTCONF API Paths
Use Cisco API documentation:
- https://developer.cisco.com/docs/ios-xe/

Or use Postman to explore live:
1. Open **Postman**
2. Set method to **GET**
3. URL:
```
https://sandbox-iosxe-latest-1.cisco.com/restconf/data/ietf-interfaces:interfaces
```
4. Add Headers:
```
Accept: application/yang-data+json
Content-Type: application/yang-data+json
```
5. Use **Basic Auth** with `developer` / `C1sco12345`
6. Click **Send** and view JSON structure

Postman helps you:
- Discover full API paths
- Understand response format
- Troubleshoot before writing Python

---

## 🧪 Bonus Tasks (Optional)
- Create another script to pull CPU utilization via RESTCONF from:
  `/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization`
- Retrieve BGP neighbors via NETCONF using appropriate YANG filter

---

## 📌 Troubleshooting Tips
| Issue             | Check                                   |
|------------------|------------------------------------------|
| 401 Unauthorized | Username/password mismatch               |
| Timeout Error     | Wrong IP, firewall, VPN issues           |
| XML parse error   | Check indentation and YANG filter syntax |
| JSON decode error | RESTCONF path invalid or empty response  |

---

## ✅ Takeaway Notes
- RESTCONF is excellent for RESTful access to YANG-modeled data
- NETCONF provides structured and reliable config/state retrieval
- YAML inventory keeps things organized
- Postman is your best friend when starting RESTCONF automation
- Building NETCONF filters manually requires namespace and structure awareness
- These skills are foundational for DevNet certifications and real-world network monitoring

