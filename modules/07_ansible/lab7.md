# Lab 7: Ansible for Multi-Device Configuration and NTP Verification

## 🎯 Lab Objectives
In this lab, learners will use Ansible to:

1. Connect to Cisco IOS XE sandbox routers.
2. Verify NTP configuration and synchronization status.
3. Create 10 Loopback interfaces with unique IP addresses.
4. Use structured inventory and Jinja2 templating for configuration.

This lab emphasizes Ansible's power to scale configurations across multiple devices.

---

## 🧰 Prerequisites
- Python 3, Ansible installed (`pip install ansible`)
- Ansible Cisco collections: `ansible-galaxy collection install cisco.ios`
- Cisco IOS XE sandbox credentials:
  - IP: `sandbox-iosxe-latest-1.cisco.com`
  - Port: `22`
  - Username: `admin`
  - Password: `C1sco12345`

---

## 🗂 Directory Structure
```
lab7/
├── inventory.yaml
├── group_vars/
│   └── all.yaml
├── templates/
│   └── loopbacks.j2
├── playbooks/
│   └── configure_loopbacks.yml
│   └── check_ntp.yml
```

---

## 📁 Step 1: Create the Inventory
Create `inventory.yaml`:
```yaml
all:
  children:
    cisco:
      hosts:
        iosxe1:
          ansible_host: sandbox-iosxe-latest-1.cisco.com
          ansible_port: 22
          ansible_user: admin
          ansible_password: C1sco12345
          ansible_network_os: ios
          ansible_connection: network_cli
```

---

## 📁 Step 2: Create Variables
Create `group_vars/all.yaml`:
```yaml
loopbacks:
  - { id: 0, ip: 10.10.0.1, mask: 255.255.255.255 }
  - { id: 1, ip: 10.10.1.1, mask: 255.255.255.255 }
  - { id: 2, ip: 10.10.2.1, mask: 255.255.255.255 }
  - { id: 3, ip: 10.10.3.1, mask: 255.255.255.255 }
  - { id: 4, ip: 10.10.4.1, mask: 255.255.255.255 }
  - { id: 5, ip: 10.10.5.1, mask: 255.255.255.255 }
  - { id: 6, ip: 10.10.6.1, mask: 255.255.255.255 }
  - { id: 7, ip: 10.10.7.1, mask: 255.255.255.255 }
  - { id: 8, ip: 10.10.8.1, mask: 255.255.255.255 }
  - { id: 9, ip: 10.10.9.1, mask: 255.255.255.255 }
```

---

## 🧩 Step 3: Jinja2 Template
Create `templates/loopbacks.j2`:
```jinja
{% for int in loopbacks %}
interface Loopback{{ int.id }}
 ip address {{ int.ip }} {{ int.mask }}
{% endfor %}
```

---

## 🚀 Step 4: Playbook to Configure Loopbacks
Create `playbooks/configure_loopbacks.yml`:
```yaml
- name: Create 10 Loopback Interfaces on Cisco IOS XE
  hosts: cisco
  gather_facts: no
  connection: network_cli
  tasks:
    - name: Render Jinja2 template
      template:
        src: ../templates/loopbacks.j2
        dest: /tmp/loopbacks.cfg

    - name: Apply loopback configuration
      ios_config:
        src: /tmp/loopbacks.cfg
```

---

## 🔎 Step 5: Playbook to Check NTP Status
Create `playbooks/check_ntp.yml`:
```yaml
- name: Verify NTP status on IOS XE
  hosts: cisco
  gather_facts: no
  connection: network_cli
  tasks:
    - name: Run "show ntp status"
      ios_command:
        commands:
          - show ntp status
      register: ntp_output

    - name: Display NTP Output
      debug:
        var: ntp_output.stdout_lines
```

---

## ▶️ Step 6: Run the Playbooks
From the `lab7/` directory:

```bash
ansible-playbook -i inventory.yaml playbooks/check_ntp.yml
```
Expected Output:
```
"show ntp status" results:
Clock is synchronized, stratum 3, reference is 192.168.1.1
```

Then run:
```bash
ansible-playbook -i inventory.yaml playbooks/configure_loopbacks.yml
```
Expected Output:
```
PLAY [Create 10 Loopback Interfaces on Cisco IOS XE]
TASK [Apply loopback configuration] => changed=1
```

To verify manually:
```bash
ssh admin@sandbox-iosxe-latest-1.cisco.com
show ip interface brief | include Loopback
```

---

## 🧠 Troubleshooting
- `Connection timeout`: Check sandbox availability and port
- `Authentication failed`: Reconfirm credentials
- `Module not found`: Run `ansible-galaxy collection install cisco.ios`
- Missing output? Add `debug:` to view variables

---

## 📌 Takeaways
- Used **Ansible inventory and Jinja2** to deploy configs
- Queried real-time **NTP sync status**
- Created and verified **10 Loopback interfaces**
- Demonstrated **multi-device scalability** via Ansible

