# Module 1: Foundations of Python for Network Automation

This foundational module introduces Python programming within the context of network automation. You’ll learn why Python is ideal for automating networking tasks, how to manage your development environment, how to structure scripts for scalability, and how to work with various data types and formats (JSON, YAML, XML).

---

## 1. Why Learn Python for Network Automation?

Python is the most popular language for network automation due to:

1. **Simple Syntax**: Python is readable and beginner-friendly.
2. **Powerful Libraries**: Like Netmiko, NAPALM, pyATS, requests, and more.
3. **Multivendor Support**: Used across Cisco, Juniper, Arista, and open platforms.
4. **Versatility**: Automates configuration, monitoring, log parsing, API calls, etc.
5. **Strong Community**: Abundant resources, DevNet labs, GitHub repos, and documentation.

**Examples**:
- Backup configs across 100 routers
- Pull device status via REST API
- Detect and remediate outages automatically

---

## 2. Managing Your Python Environment

### 2.1 Using Git for Version Control
Git allows you to track changes, collaborate, and back up your scripts.

```bash
git init                  # Initialize a Git repo
git add .                # Stage changes
git commit -m "message"  # Commit changes
git remote add origin <url>  # Link to GitHub
git push -u origin main      # Push to remote
```

**Best Practices**:
- Commit often with meaningful messages.
- Use branches for experiments.
- Use `.gitignore` to exclude unwanted files.

### 2.2 Creating a Virtual Environment
Isolate Python packages per project.

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

Use `requirements.txt` to manage dependencies:
```bash
pip freeze > requirements.txt
```

---

## 3. Python Data Types and Data Structures

### 3.1 Scalar Types
| Type  | Example    |
|-------|------------|
| int   | `10`       |
| float | `3.14`     |
| bool  | `True`     |
| str   | `'router1'`|

### 3.2 Collection Types
| Type   | Description                  | Example                          |
|--------|------------------------------|----------------------------------|
| list   | Ordered, mutable             | `[1, 2, 3]`                      |
| tuple  | Ordered, immutable           | `(1, 2, 3)`                      |
| dict   | Key-value store              | `{'ip': '10.1.1.1'}`             |
| set    | Unordered, unique values     | `{'router1', 'router2'}`         |

**Access & Manipulation**:
```python
interfaces = ['Gig0/0', 'Gig0/1']
print(interfaces[0])
interfaces.append('Gig0/2')

config = {'hostname': 'r1', 'bgp': True}
print(config['hostname'])
```

---

## 4. Data Representation: JSON, YAML, XML

### 4.1 JSON
JavaScript Object Notation: structured, widely used in APIs.
```json
{
  "hostname": "r1",
  "interfaces": ["Gig0/0", "Gig0/1"]
}
```
```python
import json
with open("data.json") as f:
    data = json.load(f)
```

### 4.2 YAML
More human-friendly than JSON.
```yaml
hostname: r1
interfaces:
  - Gig0/0
  - Gig0/1
```
```python
import yaml
with open("data.yaml") as f:
    data = yaml.safe_load(f)
```

### 4.3 XML
Often used in legacy systems or NETCONF.
```xml
<device>
  <hostname>r1</hostname>
</device>
```
```python
import xml.etree.ElementTree as ET
root = ET.parse("device.xml").getroot()
print(root.find("hostname").text)
```

---

## 5. Python Control Structures

### 5.1 If-Else Logic
```python
cpu = 75
if cpu > 80:
    print("High CPU")
else:
    print("CPU OK")
```

### 5.2 Loops

#### `for` Loop
```python
for interface in interfaces:
    print("Check", interface)
```

#### `while` Loop
```python
retry = 0
while retry < 3:
    print("Retrying...")
    retry += 1
```

---

## 6. Functions and Script Structuring

### 6.1 Functions
Encapsulate logic for reuse and clarity.
```python
def connect_to_device(ip):
    print(f"Connecting to {ip}")
```

### 6.2 When to Modularize
Split logic when:
- Script >100 lines
- Multiple logical stages (e.g., parsing, connecting, backing up)
- Functions are reused across scripts

### 6.3 Project Structure
```
project/
├── main.py
├── helpers.py
└── data/
    └── devices.yaml
```

---

## 7. Naming Conventions (PEP8)

| Element    | Convention     | Example              |
|------------|----------------|----------------------|
| Variables  | `snake_case`   | `device_name`        |
| Functions  | `snake_case`   | `get_uptime()`       |
| Classes    | `CamelCase`    | `RouterDevice`       |
| Constants  | `UPPER_CASE`   | `MAX_RETRY`          |
| Files      | `lowercase.py` | `main.py`, `api.py`  |

---

## 8. Error Handling in Python
Use `try`/`except` to catch runtime problems.
```python
try:
    with open("config.txt") as f:
        data = f.read()
except FileNotFoundError:
    print("File not found")
```

Use specific exceptions for clarity:
- `FileNotFoundError`
- `ValueError`
- `TimeoutError`

---

## 9. Procedural vs Object-Oriented Python

### 9.1 Procedural Example
```python
def reboot(ip):
    print(f"Rebooting {ip}")
reboot("10.0.0.1")
```

### 9.2 OOP Example
```python
class Device:
    def __init__(self, ip):
        self.ip = ip
    def reboot(self):
        print("Rebooting", self.ip)

r1 = Device("10.0.0.1")
r1.reboot()
```

**Use OOP when**:
- You have many devices with shared behaviors
- You want reusable components

---

## 10. Summary

By the end of this module, you should:
- Understand Python syntax and data types
- Work with JSON, YAML, XML
- Use loops and functions
- Understand modular design
- Follow Python best practices
- Compare procedural vs OOP design
- Manage scripts using Git and virtual environments

👉 Next: [Lab Guide – Module 1](lab1.md)

