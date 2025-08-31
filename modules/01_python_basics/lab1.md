# Lab 1 – Python Foundations for Network Automation

> **Lab Duration**: 2 hours  
> **Objective**: Equip learners with hands-on experience in Python fundamentals, version control using Git, environment isolation using virtual environments, and structured data parsing (JSON, YAML, XML). Learners will practice modular design, error handling, and OOP concepts for scalable network automation scripting.

---

## 🧰 Environment Preparation

### Step 1: Create a Working Directory
```bash
mkdir netauto-lab1 && cd netauto-lab1
```

### Step 2: Initialize Git Repository
```bash
git init
```

### Step 3: Create `.gitignore`
```bash
echo ".venv/\n__pycache__/\n*.log\n*.pyc" > .gitignore
```
> ✅ This ensures sensitive, unnecessary, or auto-generated files are not committed.

### Step 4: Set Up Virtual Environment
```bash
python3 -m venv .venv
```
Activate:
- macOS/Linux:
```bash
source .venv/bin/activate
```
- Windows:
```bash
.venv\Scripts\activate
```
Install required packages:
```bash
pip install pyyaml xmltodict
pip freeze > requirements.txt
```
> ✅ This creates an isolated Python environment and locks dependencies.

To switch between environments later:
```bash
# Activate again (Linux/macOS):
source .venv/bin/activate
# Or deactivate when done:
deactivate
```

---

## 🔣 Core Python Concepts in Action

### Step 5: Python Data Types and Access

**Create `types_demo.py`**
```python
hostname = "R1"
ip_address = "192.168.10.1"
is_active = True
interfaces = ["Gig0/0", "Gig0/1"]
metrics = (12.3, 0.2)
device = {
    "hostname": hostname,
    "ip": ip_address,
    "interfaces": interfaces,
    "active": is_active
}

print(device['hostname'])
print(f"First Interface: {device['interfaces'][0]}")

# Type checking
types = [hostname, ip_address, is_active, interfaces, metrics, device]
for val in types:
    print(type(val))
```
**Run the script:**
```bash
python types_demo.py
```
**Expected Output:**
```
R1
First Interface: Gig0/0
<class 'str'>
<class 'str'>
<class 'bool'>
<class 'list'>
<class 'tuple'>
<class 'dict'>
```

> 💡 **Troubleshooting Tips:**
- If you see `ModuleNotFoundError` → Make sure you’re in the virtual environment.
- If you see `SyntaxError` → Check for missing colons `:` or unmatched quotes.

---

### Step 6: Iteration with For/While
**Create `loop_demo.py`**
```python
devices = [
    {"hostname": "R1", "ip": "10.0.0.1"},
    {"hostname": "R2", "ip": "10.0.0.2"},
    {"hostname": "R3", "ip": "10.0.0.3"}
]

print("For Loop:")
for dev in devices:
    print(dev['hostname'])

print("\nWhile Loop:")
i = 0
while i < len(devices):
    print(devices[i]['ip'])
    i += 1
```
**Run:**
```bash
python loop_demo.py
```
**Expected Output:**
```
For Loop:
R1
R2
R3

While Loop:
10.0.0.1
10.0.0.2
10.0.0.3
```

> 💡 **Troubleshooting Tips:**
- `IndexError: list index out of range` → Make sure loop counter is correct.
- `KeyError: 'hostname'` → Ensure key names match exactly.

---

## 📂 Structured Data Handling

### Step 7: Parse JSON
**Create `device.json`**
```json
{
  "hostname": "R1",
  "ip": "192.168.1.1",
  "location": "Datacenter"
}
```
**Create `json_demo.py`**
```python
import json
with open("device.json") as f:
    dev = json.load(f)
print(f"{dev['hostname']} at {dev['location']}")
```
**Run:**
```bash
python json_demo.py
```
**Expected Output:**
```
R1 at Datacenter
```
> 💡 **Fixes:**
- JSON format requires double quotes, not single quotes.
- `json.decoder.JSONDecodeError` → Check for trailing commas.

---

### Step 8: Parse YAML
**Create `devices.yaml`**
```yaml
- hostname: R1
  ip: 10.0.0.1
- hostname: R2
  ip: 10.0.0.2
```
**Create `yaml_demo.py`**
```python
import yaml
with open("devices.yaml") as f:
    data = yaml.safe_load(f)
for d in data:
    print(f"{d['hostname']} - {d['ip']}")
```
**Run:**
```bash
python yaml_demo.py
```
**Expected Output:**
```
R1 - 10.0.0.1
R2 - 10.0.0.2
```
> 💡 Make sure YAML uses spaces, not tabs.

---

### Step 9: Parse XML
**Create `device.xml`**
```xml
<device>
  <hostname>R1</hostname>
  <ip>10.0.0.1</ip>
</device>
```
**Create `xml_demo.py`**
```python
import xmltodict
with open("device.xml") as f:
    doc = xmltodict.parse(f.read())
print(doc['device']['hostname'])
```
**Run:**
```bash
python xml_demo.py
```
**Expected Output:**
```
R1
```
> 💡 XML must be properly closed; indentation helps with readability.

---

## 🧩 Python Functions and Modular Design

### Step 10: Define Functions
**Create `func_demo.py`**
```python
def device_summary(name, ip):
    print(f"Device: {name} - IP: {ip}")

device_summary("R1", "192.168.1.1")
```
**Run:**
```bash
python func_demo.py
```
**Expected Output:**
```
Device: R1 - IP: 192.168.1.1
```

---

### Step 11: Create a Module
**Create `utils.py`**
```python
def greet(msg):
    print(f"[INFO] {msg}")
```
**Create `main_module.py`**
```python
from utils import greet
greet("Welcome to Network Automation")
```
**Run:**
```bash
python main_module.py
```
**Expected Output:**
```
[INFO] Welcome to Network Automation
```
> 💡 Ensure both files are in the same directory.

---

## 🛡️ Error Handling
**Create `error_demo.py`**
```python
device = {"ip": "10.0.0.1"}
try:
    print(device['hostname'])
except KeyError as e:
    print("Missing key:", e)
```
**Run:**
```bash
python error_demo.py
```
**Expected Output:**
```
Missing key: 'hostname'
```

---

## 🧱 Object-Oriented Basics
**Create `oop_demo.py`**
```python
class Device:
    def __init__(self, hostname, ip):
        self.hostname = hostname
        self.ip = ip
    def summary(self):
        print(f"{self.hostname} - {self.ip}")

r1 = Device("R1", "10.0.0.1")
r1.summary()
```
**Run:**
```bash
python oop_demo.py
```
**Expected Output:**
```
R1 - 10.0.0.1
```
> 💡 Check for correct use of `self` and indentation inside the class.

---

✅ Takeaway Notes and extended home assignments are in the next section.

Would you like me to expand the Git collaboration and module packaging sections next?

