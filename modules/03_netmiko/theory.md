# Module 3 – Network Device Automation using Netmiko

---

## 🧠 Why Use Netmiko for Network Automation?
In the world of network automation, most engineers face a common challenge: how to interact with legacy devices that still rely heavily on CLI-based configuration. Python’s built-in `paramiko` library supports raw SSH, but managing device prompts, interactive sessions, and vendor-specific quirks is extremely time-consuming and error-prone.

This is where **Netmiko** becomes a powerful tool. Netmiko is a high-level SSH library tailored specifically for **network engineers**. It simplifies interactions with CLI-based network devices from vendors like:

- Cisco IOS, NX-OS
- Juniper JunOS
- Arista EOS
- HP ProCurve
- Palo Alto, Fortinet, Mikrotik, Huawei, and more

Netmiko abstracts the complexity of CLI session handling and gives you a **clean, Pythonic interface** to send commands and retrieve output.

---

## 🚀 Key Features of Netmiko

| Feature | Description |
|--------|-------------|
| `send_command()` | Send show/exec-level commands |
| `send_config_set()` | Send global config/line-by-line changes |
| Prompt detection | Automatically manages `enable` and `config` modes |
| Output buffering | Handles output sizes properly without hanging |
| Delay tuning | Uses `delay_factor`, `read_timeout` for slow devices |
| Secure connection | Based on `paramiko`, supports SSH only |
| Multivendor support | Automatically adapts to different platforms |

---

## 🔍 Netmiko Connection Workflow

### 1. Define the Device Dictionary
```python
cisco_ios = {
    'device_type': 'cisco_ios',
    'ip': '192.168.100.1',
    'username': 'admin',
    'password': 'cisco123',
    'secret': 'enablepass',   # Optional: for entering enable mode
}
```

### 2. Establish SSH Connection
```python
from netmiko import ConnectHandler

net_connect = ConnectHandler(**cisco_ios)
net_connect.enable()  # Enter privileged EXEC mode (if needed)
```

### 3. Run Show Commands
```python
output = net_connect.send_command("show ip interface brief")
print(output)
```

### 4. Run Configuration Changes
```python
config = [
    "hostname Core-R1",
    "interface loopback0",
    "ip address 10.0.0.1 255.255.255.255"
]
net_connect.send_config_set(config)
```

### 5. Save the Configuration
```python
net_connect.send_command("write memory")
```

### 6. Disconnect
```python
net_connect.disconnect()
```

---

## 🧪 Use Cases for Netmiko in the Field

| Scenario | Application |
|----------|-------------|
| Bulk configuration | Apply VLANs, banners, or ACLs to all edge switches |
| Configuration backup | Retrieve `show run` and store in versioned text files |
| Health check | Automate `show version`, `show interfaces`, etc. for NOC scripts |
| Troubleshooting toolkit | Build CLI-driven tool to check interface, BGP, OSPF status |
| Compliance auditing | Check for non-compliant hostname, NTP, SNMP configs |
| Credential rotation | Automate change of local admin passwords monthly |

---

## 📊 Parsing Return Output: Regex vs TextFSM vs NTC Templates

### ❗ The Problem
Most CLI output is **unstructured** text. If you run:
```python
net_connect.send_command("show ip interface brief")
```
you get back a multiline string. It's hard to work with this in Python unless it's parsed into structured data (lists, dicts).

---

### ✅ Option 1: Manual Regex Parsing
You can use Python's built-in `re` module:
```python
import re
output = net_connect.send_command("show ip interface brief")

interfaces = re.findall(r"(\S+)\s+(\S+)\s+YES.*?(up|down|administratively down)\s+(up|down)", output)
print(interfaces)
```

✅ Pros:
- Flexible and works with any vendor CLI

❌ Cons:
- Hard to maintain
- Fragile if output format changes
- Requires deep regex knowledge

---

### ✅ Option 2: TextFSM (Recommended)
Netmiko supports **TextFSM parsing** out of the box:
```python
output = net_connect.send_command("show ip interface brief", use_textfsm=True)
print(output)
```
Returns:
```python
[
  {'intf': 'GigabitEthernet0/0', 'ipaddr': '192.168.1.1', 'status': 'up', 'protocol': 'up'},
  {'intf': 'Loopback0', 'ipaddr': '10.1.1.1', 'status': 'up', 'protocol': 'up'}
]
```

✅ Pros:
- Clean JSON-like output
- Easy to loop through, convert to CSV, JSON, etc.

❌ Cons:
- Relies on correct TextFSM template
- May not support every command

---

### ✅ Option 3: NTC Templates (TextFSM-powered)
NTC Templates is a community-driven repo of prebuilt TextFSM templates.

**Installation:**
```bash
git clone https://github.com/networktocode/ntc-templates.git
export NET_TEXTFSM=/path/to/ntc-templates/templates
```

**In Python:**
```python
import os
os.environ['NET_TEXTFSM'] = '/path/to/ntc-templates/templates'
output = net_connect.send_command("show version", use_textfsm=True)
```

---

## 🧱 Script Structuring and Modular Design

### Recommended Project Layout
```bash
nasp-project/
├── main.py                # Entrypoint to call functions from tasks
├── devices.yaml           # Structured device inventory
├── .env                   # Store credentials (via python-dotenv)
├── tasks/
│   ├── backup.py
│   ├── vlan.py
│   ├── banner.py
│   └── config_push.py
└── lib/
    └── netmiko_helper.py
```

---

## 📦 Introduction to Jinja2 Templates for CLI Automation

Jinja2 is a powerful templating engine for Python, commonly used in automation to generate device configurations from structured data. Instead of hardcoding interface and protocol configurations, you use **templates + YAML** to dynamically generate CLI.

### 🔧 Example: Automating OSPF Configuration

#### Step 1: Inventory - `devices.yaml`
```yaml
- hostname: R1
  ip: 192.168.10.1
  username: admin
  password: cisco123
  secret: enablepass
  loopbacks:
    - { id: 1, ip: 10.1.1.1, mask: 255.255.255.255 }
    - { id: 2, ip: 10.2.2.2, mask: 255.255.255.255 }
  ospf:
    process_id: 1
    networks:
      - { network: 10.0.0.0, wildcard: 0.255.255.255, area: 0 }
```

#### Step 2: OSPF Jinja Template - `templates/ospf.j2`
```jinja
hostname {{ hostname }}
router ospf {{ ospf.process_id }}
{% for net in ospf.networks %}
 network {{ net.network }} {{ net.wildcard }} area {{ net.area }}
{% endfor %}
{% for lo in loopbacks %}
interface Loopback{{ lo.id }}
 ip address {{ lo.ip }} {{ lo.mask }}
{% endfor %}
```

#### Step 3: Python Script to Render and Push
```python
from jinja2 import Environment, FileSystemLoader
import yaml
from netmiko import ConnectHandler

# Load data
with open('devices.yaml') as f:
    devices = yaml.safe_load(f)

# Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('ospf.j2')

for dev in devices:
    config = template.render(**dev).splitlines()
    conn = ConnectHandler(
        device_type='cisco_ios',
        ip=dev['ip'],
        username=dev['username'],
        password=dev['password'],
        secret=dev['secret']
    )
    conn.enable()
    conn.send_config_set(config)
    conn.save_config()
    conn.disconnect()
```

---

## ✅ Summary: What You Should Know Now
By completing this module, you should be able to:

- Understand the role of Netmiko in network CLI automation
- Connect securely to Cisco/Arista/Juniper devices
- Send commands, retrieve output, and save configs
- Parse CLI output using regex or TextFSM/NTC Templates
- Build reusable Python scripts and organize projects
- Use Jinja2 + YAML for scalable CLI generation
- Iterate over inventories and handle exceptions


