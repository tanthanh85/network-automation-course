# Lab 3 – Automating Network Devices with Netmiko

---

## 🎯 Lab Objectives
By the end of this lab, learners will:

- Create a Python project to automate CLI tasks with Netmiko
- Connect to multiple Cisco routers using YAML inventory
- Push loopback and OSPF configurations via Jinja2 template
- Use TextFSM to parse `show ip interface brief` command output
- Backup `show running-config` to local files
- Practice script modularization and reusability

> 💡 **Prerequisite**: Learners must have completed Lab 1 and Lab 2 (virtual environment, VSCode, YAML handling, and concurrency).

---

## 🧰 Files & Directory Structure
```
nasp-lab3/
├── devices.yaml                 # Inventory of routers
├── templates/
│   └── ospf.j2                  # Jinja2 template for loopback + OSPF
├── backups/                    # Folder to store running-config
├── main.py                     # Entrypoint script
├── utils/
│   ├── netmiko_helper.py       # Custom connection wrapper
│   └── jinja_renderer.py       # Template rendering logic
└── requirements.txt            # Netmiko, PyYAML, Jinja2
```

---

## 🧪 Step-by-Step Lab Instructions

### ✅ Step 1 – Setup Your Project

1. Create the folder structure above using VSCode.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Linux/macOS
   venv\Scripts\activate         # On Windows
   ```
3. Install the required libraries:
   ```bash
   pip install netmiko PyYAML jinja2
   pip install ntc_templates
   ```
4. Set NTC Template environment variable (Linux/macOS):
   ```bash
   git clone https://github.com/networktocode/ntc-templates.git
   export NET_TEXTFSM=$PWD/ntc-templates/templates
   ```
   On Windows:
   ```powershell
   $env:NET_TEXTFSM = "$PWD\ntc-templates\templates"
   ```

5. Save the packages to `requirements.txt`:
   ```bash
   pip freeze > requirements.txt
   ```

### ✅ Step 2 – Create Your Device Inventory

**File: `devices.yaml`**
```yaml
- hostname: R1
  ip: 192.168.1.10
  username: admin
  password: cisco123
  secret: enable123
  loopbacks:
    - { id: 1, ip: 10.1.1.1, mask: 255.255.255.255 }
  ospf:
    process_id: 1
    networks:
      - { network: 10.0.0.0, wildcard: 0.255.255.255, area: 0 }

- hostname: R2
  ip: 192.168.1.11
  username: admin
  password: cisco123
  secret: enable123
  loopbacks:
    - { id: 2, ip: 10.2.2.2, mask: 255.255.255.255 }
  ospf:
    process_id: 1
    networks:
      - { network: 10.0.0.0, wildcard: 0.255.255.255, area: 0 }
```

### ✅ Step 3 – Write the OSPF Template

**File: `templates/ospf.j2`**
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

### ✅ Step 4 – Create the `jinja_renderer.py` Helper

**File: `utils/jinja_renderer.py`**
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))

def render_config(data, template_name):
    template = env.get_template(template_name)
    return template.render(**data).splitlines()
```

### ✅ Step 5 – Create the `netmiko_helper.py` Module

**File: `utils/netmiko_helper.py`**
```python
from netmiko import ConnectHandler
import os

os.environ['NET_TEXTFSM'] = './ntc-templates/templates'

def connect_device(dev):
    conn = ConnectHandler(
        device_type='cisco_ios',
        ip=dev['ip'],
        username=dev['username'],
        password=dev['password'],
        secret=dev['secret']
    )
    conn.enable()
    return conn

def send_commands(conn, config):
    return conn.send_config_set(config)

def backup_config(conn, hostname):
    output = conn.send_command("show running-config")
    with open(f"backups/{hostname}_config.txt", 'w') as f:
        f.write(output)

def parse_interfaces(conn):
    return conn.send_command("show ip interface brief", use_textfsm=True)
```

### ✅ Step 6 – Main Execution Script

**File: `main.py`**
```python
import yaml
from utils.jinja_renderer import render_config
from utils.netmiko_helper import connect_device, send_commands, backup_config, parse_interfaces

with open("devices.yaml") as f:
    devices = yaml.safe_load(f)

for dev in devices:
    print(f"Connecting to {dev['hostname']}...")
    conn = connect_device(dev)

    print("Generating config...")
    config = render_config(dev, "ospf.j2")
    send_commands(conn, config)

    print("Backing up config...")
    backup_config(conn, dev['hostname'])

    print("Parsing interfaces...")
    interfaces = parse_interfaces(conn)
    print(interfaces)
    conn.disconnect()
```

### ✅ Step 7 – Run Your Script

In VSCode Terminal:
```bash
python main.py
```

### ✅ Expected Results

- OSPF and Loopback interfaces are configured on both routers
- Text files are saved under `backups/` folder
- Interface status printed as list of dictionaries:
```python
[
  {'intf': 'GigabitEthernet0/0', 'ipaddr': '192.168.1.10', 'status': 'up', 'protocol': 'up'},
  {'intf': 'Loopback1', 'ipaddr': '10.1.1.1', 'status': 'up', 'protocol': 'up'}
]
```

---

## 🧠 Takeaway Notes
- Netmiko simplifies CLI automation and works across vendors
- Use YAML to define inventory and config data
- Use Jinja2 to generate scalable CLI from data
- TextFSM helps convert unstructured output into structured Python objects
- Always modularize your logic into helper files for maintainability

---

## 🏡 Home Practice

1. Add more loopbacks and verify OSPF routes are exchanged
2. Write a second template to configure hostname, banner, and NTP
3. Add try/except blocks for connection errors
4. Try creating a Python package out of `utils/` to reuse across projects
5. Commit your lab folder to GitHub with a README

