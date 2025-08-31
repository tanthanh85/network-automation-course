# Module 9 — Creating Management Console for Cisco Switches using Python

## 🧭 Objective
In this module, learners will understand how to build a **management console** for Cisco switches using Python. The goal is to create a single tool or script that allows users to remotely manage **VLANs**, **Spanning Tree Protocol (STP)**, and **EtherChannel** configurations. The module introduces design patterns for building CLI-based management tools and explains how to build reusable logic and interactive menus.

This module connects prior topics (Netmiko, Paramiko, YAML, Jinja2) and builds toward a **modular, scalable, and operator-friendly** console.

---

## 🧱 Why Build a Python Console for Switches?

- Standard CLI is powerful but lacks integration
- GUIs (e.g., DNAC) may not be accessible in all environments
- A custom Python console allows:
  - Rapid access to status/configs
  - Batch configuration of multiple switches
  - Integration with YAML, JSON, and templates
  - Better error-handling and logging

---

## 📚 Key Features to Include

| Feature | Description |
|--------|-------------|
| VLAN Management | Add, remove, and display VLANs |
| STP Management | View spanning-tree status, root bridges |
| EtherChannel | Create Port-Channels with templates |
| Logging | Save logs to file (per device) |
| Menu System | Interactive prompt or CLI args |
| Device Inventory | YAML-based inventory file |
| Extensibility | Easy to add features like NTP, SNMP, etc. |

---

## 🧩 Design Architecture

```
console_manager/
├── inventory.yaml            # List of switches and credentials
├── main.py                   # Entry point: menu or args
├── vlan.py                   # Add/Delete/Show VLANs
├── stp.py                    # STP status display
├── etherchannel.py           # EtherChannel config
├── templates/                # Jinja2 configs for Port-Channels
└── utils.py                  # Shared Netmiko functions
```

---

## 🧾 YAML Inventory Example
```yaml
switches:
  - name: dist1
    ip: 10.10.10.10
    username: cisco
    password: C1sco12345
  - name: access1
    ip: 10.10.10.20
    username: cisco
    password: C1sco12345
```

---

## 🖥️ Interactive Console Example
```bash
$ python main.py

[1] Configure VLAN
[2] Show VLANs
[3] Configure EtherChannel
[4] Show STP
[5] Exit

Choice: 1
→ Enter VLAN ID: 100
→ Enter VLAN Name: MGMT
→ Apply to which switch? dist1
✅ VLAN 100 created on dist1
```

---

## 🧠 VLAN Logic Example
```python
# vlan.py
from netmiko import ConnectHandler

def create_vlan(device, vlan_id, vlan_name):
    net_connect = ConnectHandler(**device)
    commands = [
        f"vlan {vlan_id}",
        f"name {vlan_name}"
    ]
    output = net_connect.send_config_set(commands)
    return output
```

---

## 🧵 STP Info Example
```python
# stp.py

def show_stp(device):
    net_connect = ConnectHandler(**device)
    output = net_connect.send_command("show spanning-tree root")
    return output
```

---

## 🌐 EtherChannel with Template
**`etherchannel.j2`**
```jinja
interface Port-channel{{ po_id }}
 description {{ desc }}
 switchport
 switchport mode trunk
```

**etherchannel.py**
```python
from jinja2 import Template

with open('templates/etherchannel.j2') as f:
    tmpl = Template(f.read())

config = tmpl.render(po_id=2, desc='Trunk to dist2')
commands = config.strip().split('\n')
output = net_connect.send_config_set(commands)
```

---

## 🛠️ Logging Best Practice
```python
import logging

logging.basicConfig(filename=f"logs/{device['name']}.log", level=logging.INFO)
logging.info("VLAN 100 created")
```

---

## ✅ Expected Output for Operators
- Clear CLI feedback (`✅ VLAN created on dist1`)
- Logs per operation per switch
- Consistent YAML → CLI behavior
- Easy extensibility for NTP, SNMP, syslog, etc.

---

## 🧠 Takeaway Notes
- Python enables building operator-friendly tools that scale
- Menus and modular design keep scripts readable and usable
- YAML + Jinja2 templates bring config repeatability
- Real-time CLI interaction allows fast validation
- Netmiko and error handling must be robust for production use

