# Lab 4 – Automating BGP Configuration Using Paramiko

---

## 🎯 Objective
In this lab, you will learn to:
- Use **Paramiko** to SSH into multiple Cisco routers
- Send interactive configuration commands for **BGP setup**
- Backup and verify configurations
- Organize Python automation scripts using helper modules and YAML files
- Run everything inside **VSCode** with expected outputs

This lab builds your low-level SSH scripting skills to automate tasks that may require interaction (e.g., config mode).

---

## 🧰 Lab Environment Requirements

- **VSCode** with Python extension
- Two Cisco routers (physical or GNS3/CML)
- Python 3.8+ installed
- Devices must support SSH access

---

## 📁 Directory Structure
```bash
nasp-lab4/
├── devices.yaml
├── bgp_config.yaml
├── templates/
│   └── bgp_config.j2
├── scripts/
│   └── push_bgp.py
├── utils/
│   └── paramiko_helper.py
└── backups/
```

---

## 📄 devices.yaml
```yaml
- hostname: R1
  ip: 192.168.100.1
  username: cisco
  password: cisco123
- hostname: R2
  ip: 192.168.100.2
  username: cisco
  password: cisco123
```

## 📄 bgp_config.yaml
```yaml
R1:
  asn: 65001
  neighbors:
    - ip: 10.0.12.2
      remote_as: 65002

R2:
  asn: 65002
  neighbors:
    - ip: 10.0.12.1
      remote_as: 65001
```

---

## 🧾 Jinja2 Template: templates/bgp_config.j2
```jinja
router bgp {{ asn }}
{% for n in neighbors %}
 neighbor {{ n.ip }} remote-as {{ n.remote_as }}
{% endfor %}
```

---

## 🔧 Helper Script: utils/paramiko_helper.py
```python
import paramiko, time

def connect(device):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(device['ip'], username=device['username'], password=device['password'])
    return ssh

def run_shell(ssh, commands):
    chan = ssh.invoke_shell()
    output = ""
    for cmd in commands:
        chan.send(cmd + '\n')
        time.sleep(1)
        output += chan.recv(65535).decode()
    return output

def backup_config(ssh, hostname):
    output = run_shell(ssh, ['terminal length 0', 'show run'])
    with open(f"backups/{hostname}_config.txt", 'w') as f:
        f.write(output)
```

---

## 🚀 Main Script: scripts/push_bgp.py
```python
import yaml
from jinja2 import Environment, FileSystemLoader
from utils.paramiko_helper import connect, run_shell, backup_config

with open('../devices.yaml') as f:
    devices = yaml.safe_load(f)

with open('../bgp_config.yaml') as f:
    bgp_data = yaml.safe_load(f)

env = Environment(loader=FileSystemLoader('../templates'))
template = env.get_template('bgp_config.j2')

for device in devices:
    hostname = device['hostname']
    ssh = connect(device)
    backup_config(ssh, hostname)

    config = template.render(**bgp_data[hostname]).splitlines()
    commands = ['conf t'] + config + ['end', 'wr mem']
    result = run_shell(ssh, commands)
    print(f"[✓] Config pushed to {hostname} \n{result}")
    ssh.close()
```

---

## 🧪 Execution
In VSCode Terminal:
```bash
cd nasp-lab4/scripts
python push_bgp.py
```

### ✅ Expected Output
```
[✓] Config pushed to R1
router bgp 65001
 neighbor 10.0.12.2 remote-as 65002
...
[✓] Config pushed to R2
router bgp 65002
 neighbor 10.0.12.1 remote-as 65001
...
```

---

## 🔍 Validation on Router
Manually SSH or console to routers and verify:
```bash
show ip bgp summary
```
You should see BGP neighbors in **Established** state.

---

## 🧠 Takeaway Notes
- Paramiko allows you to emulate interactive CLI via `invoke_shell()`
- Use `Jinja2` and YAML for scalable configuration automation
- Back up device configs before pushing changes
- VSCode makes script navigation and execution easier
- Reuse helper modules and templates across many labs

---

## 🏡 Bonus Home Tasks

### 1. Modify the Template to Include a Description
- Add description for BGP neighbors in Jinja2

### 2. Use Paramiko to Remove BGP Config
- Create a YAML file `bgp_remove.yaml`
- Use a separate script to remove neighbors (e.g., `no router bgp ...`)

### 3. Add Error Handling in `paramiko_helper.py`
- Catch timeout and auth exceptions
- Retry connection once before failure

### 4. Extend `backup_config()` to Save `show ip bgp` output
```python
bgp_out = run_shell(ssh, ['terminal length 0', 'show ip bgp'])
with open(f"backups/{hostname}_bgp.txt", 'w') as f:
    f.write(bgp_out)
```

---

