# Lab 9 — Python-Based Management Console for Cisco Nexus Switches

## 🎯 Objective
Build and operate a Python-based **Management Console** that connects to Cisco **Nexus switches** (via Netmiko) and allows:
- Verification of **VLAN** and **STP** status
- Creation of new VLANs and Port-Channels (EtherChannel)
- Modular and menu-driven structure with reusable functions

We’ll use:
- Cisco Nexus sandbox switches
- `Netmiko`, `Jinja2`, and `PyYAML`

---

## 🧰 Prerequisites
- Python 3.8+ installed
- VSCode with Python extension
- Virtual environment setup
- Required packages:
  ```bash
  pip install netmiko pyyaml jinja2
  ```
- Cisco Nexus sandbox credentials (IP, username, password)

---

## 🗂️ Project Structure
```
lab09_switch_console/
├── inventory.yaml
├── main.py
├── vlan.py
├── stp.py
├── etherchannel.py
├── utils.py
└── templates/
    └── etherchannel.j2
```

---

## 📁 Step 1 — Define the Device Inventory
**inventory.yaml**
```yaml
switches:
  - name: nexus1
    ip: sandbox-nexus1.cisco.com
    username: developer
    password: C1sco12345
    device_type: cisco_nxos
  - name: nexus2
    ip: sandbox-nexus2.cisco.com
    username: developer
    password: C1sco12345
    device_type: cisco_nxos
```

### ✅ Expected Result
Inventory file should load successfully when you run:
```python
from utils import get_device
print(get_device("nexus1"))
```
Output:
```python
{'name': 'nexus1', 'ip': 'sandbox-nexus1.cisco.com', ...}
```

---

## 🧠 Step 2 — Create Utility Function
**utils.py**
```python
from netmiko import ConnectHandler
import yaml

# Load inventory
with open("inventory.yaml") as f:
    inventory = yaml.safe_load(f)

# Find device by name
def get_device(name):
    for d in inventory['switches']:
        if d['name'] == name:
            return d
    return None
```

### ✅ Expected Result
Importing and calling `get_device('nexus1')` should return the full device dictionary.

---

## 🧱 Step 3 — VLAN Module
**vlan.py**
```python
from netmiko import ConnectHandler

def create_vlan(device, vlan_id, vlan_name):
    net_connect = ConnectHandler(**device)
    commands = [
        f"vlan {vlan_id}",
        f"name {vlan_name}"
    ]
    output = net_connect.send_config_set(commands)
    print(output)
    net_connect.disconnect()
```

### ✅ Expected Result
After choosing VLAN creation from `main.py`, you should see output like:
```text
config terminal
vlan 200
name DMZ
exit
```
And on the switch CLI:
```bash
show vlan id 200
```
Should confirm VLAN creation.

---

## 🌉 Step 4 — EtherChannel Template & Script
**templates/etherchannel.j2**
```jinja
interface port-channel{{ po_id }}
 description {{ desc }}
 switchport
 switchport mode trunk
```

**etherchannel.py**
```python
from netmiko import ConnectHandler
from jinja2 import Template


def configure_port_channel(device, po_id, desc):
    with open('templates/etherchannel.j2') as f:
        template = Template(f.read())
    rendered = template.render(po_id=po_id, desc=desc)
    commands = rendered.strip().split('\n')

    net_connect = ConnectHandler(**device)
    output = net_connect.send_config_set(commands)
    print(output)
    net_connect.disconnect()
```

### ✅ Expected Result
```text
interface port-channel10
 description Uplink to Core
 switchport
 switchport mode trunk
```
And verify on Nexus switch:
```bash
show interface port-channel10
```

---

## 🧵 Step 5 — STP Display Module
**stp.py**
```python
from netmiko import ConnectHandler

def show_stp(device):
    net_connect = ConnectHandler(**device)
    output = net_connect.send_command("show spanning-tree root")
    print(output)
    net_connect.disconnect()
```

### ✅ Expected Result
When selected in `main.py`, this will print:
```text
VLAN0001
  Root ID    Priority    32769
             Address     aabb.cc00.0200
```

---

## 📟 Step 6 — Main Console Script
**main.py**
```python
from utils import get_device
from vlan import create_vlan
from stp import show_stp
from etherchannel import configure_port_channel

print("Select Device: nexus1 / nexus2")
dev = input("Device: ")
device = get_device(dev)

print("""
1. Create VLAN
2. Show STP Status
3. Configure EtherChannel
""")

choice = input("Your choice: ")
if choice == "1":
    vlan_id = input("Enter VLAN ID: ")
    vlan_name = input("Enter VLAN Name: ")
    create_vlan(device, vlan_id, vlan_name)

elif choice == "2":
    show_stp(device)

elif choice == "3":
    po_id = input("Enter Port-Channel ID: ")
    desc = input("Enter Description: ")
    configure_port_channel(device, po_id, desc)
```

### ✅ Expected Result
Menu should prompt the user clearly. Example run:
```bash
Device: nexus1
1. Create VLAN
2. Show STP Status
3. Configure EtherChannel
Your choice: 1
Enter VLAN ID: 300
Enter VLAN Name: MGMT
```

Output will show successful config being sent to the switch.

---

## 🧠 Takeaway Notes
- Use `cisco_nxos` device type for Nexus devices
- Modular scripts enable CLI-like management tools
- Netmiko + Jinja2 make it fast to deploy changes
- Can expand console with NTP, SNMP, Port-security tasks

