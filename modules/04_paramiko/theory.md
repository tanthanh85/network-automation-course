# Module 4 – Automating Network Devices with Paramiko (SSH Library)

---

## 🎯 Objective
This module introduces learners to **Paramiko**, a Python library that provides low-level access to network devices over SSH. Unlike Netmiko (which is built on top of Paramiko), this module teaches learners to:

- Understand how SSH works at the socket and channel level
- Use Paramiko for custom network automation scripts
- Transfer files with SFTP
- Design scripts for device access, command execution, and data extraction
- Use Paramiko when Netmiko isn't available or when fine-grained control is needed

---

## 🔍 Why Learn Paramiko?

Netmiko is great for high-level CLI automation, but:
- You may need more control over the SSH session (prompt handling, delay tuning)
- Some devices or platforms do not support Netmiko
- You want to upload/download files via SFTP (e.g., send backup configs)

Paramiko gives you access to:
- Full SSH client behavior (connect, authenticate, execute)
- Interactive channels (like a terminal session)
- File transfers using **SFTP**

> Think of Paramiko as your "Swiss Army Knife" for low-level SSH and SFTP.

---

## 🧱 How SSH Works (Behind the Scenes)

When you connect to a network device using SSH:
- A **transport layer** is established with encryption (using AES, etc.)
- A **channel** is created (like a terminal)
- Commands are sent through that channel
- The output is received as bytes
- You must manually decode, process, and handle the CLI output

With Paramiko:
- You create the transport and authentication manually
- You must send and receive commands and handle CLI prompts (if needed)

---

## 📦 Installing Paramiko
```bash
pip install paramiko
```

Optional (for SFTP file uploads/downloads):
```bash
pip install scp
```

---

## 📘 Basic Usage: Connect and Run Command
```python
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.1.10', username='admin', password='cisco123')

stdin, stdout, stderr = ssh.exec_command('show version')
print(stdout.read().decode())
ssh.close()
```

### 🔍 Breakdown:
- `set_missing_host_key_policy`: Auto-accepts unknown devices
- `exec_command`: Opens a new channel, sends the command
- Output is read as bytes; use `.decode()` to get readable string

---

## 🖥️ Interactive Channel (Like Terminal Access)
Useful for commands that require multiple prompts or interactive behavior.
```python
chan = ssh.invoke_shell()
chan.send('enable\n')
chan.send('cisco123\n')
chan.send('terminal length 0\n')
chan.send('show run\n')
time.sleep(2)
output = chan.recv(65535).decode()
print(output)
```

---

## 📂 Uploading/Downloading Files with SFTP
```python
ftp = ssh.open_sftp()
ftp.get('/etc/config.txt', 'backup/config.txt')   # Download
ftp.put('my_script.py', '/tmp/my_script.py')      # Upload
ftp.close()
```

---

## 🧪 Use Cases in Network Automation

| Use Case                        | Benefit                                                                 |
|--------------------------------|-------------------------------------------------------------------------|
| Backup configuration           | Run `show run` and save to file                                         |
| Upload script to router        | Use SFTP to upload Python/CLI/TCL script                                |
| Execute interactive sequence   | Enable, configure terminal, show interfaces                             |
| Send TCL or diagnostic scripts | Useful for NPE/NPD troubleshooting on Cisco devices                    |
| Devices not supported by Netmiko| Low-level SSH fallback with full control                               |

---

## 🧩 Designing Paramiko Automation Projects

Recommended layout:
```
nasp-lab4/
├── devices.yaml
├── utils/
│   └── paramiko_helper.py
├── main_backup.py        # Collect and store config
├── main_diag.py          # Send commands and extract interface stats
└── requirements.txt
```

### Helper Module Example (`paramiko_helper.py`):
```python
import paramiko, time

def connect(dev):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(dev['ip'], username=dev['username'], password=dev['password'])
    return ssh

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode()

def run_shell(ssh, commands):
    chan = ssh.invoke_shell()
    output = ""
    for cmd in commands:
        chan.send(cmd + '\n')
        time.sleep(1)
        output += chan.recv(65535).decode()
    return output

def backup_config(ssh, hostname):
    out = run_command(ssh, 'show running-config')
    with open(f"backups/{hostname}_config.txt", 'w') as f:
        f.write(out)
```

---

## 🛠️ Error Handling Tips

| Error                           | Cause                                          | Fix                                  |
|--------------------------------|------------------------------------------------|---------------------------------------|
| `SSHException`                 | Wrong IP, port blocked, SSH not enabled       | Check IP, SSH settings               |
| `AuthenticationException`      | Wrong user/password                           | Verify credentials                   |
| `TimeoutError`                 | Device not reachable                          | Use `timeout=5` in `connect()`       |
| Output returns blank           | You forgot `terminal length 0`                | Send `terminal length 0` via shell   |

---

## 🧠 Best Practices

- Always use `invoke_shell()` when working with multiple interactive CLI commands
- Use `terminal length 0` to avoid pagination issues
- Clean up SSH and SFTP connections properly
- Store inventory and config data in YAML
- Create reusable helper modules (not copy/paste)

---

## 🏗️ When to Use Paramiko vs Netmiko

| Scenario                          | Use Paramiko | Use Netmiko |
|----------------------------------|--------------|-------------|
| Full control over SSH flow       | ✅           |             |
| Interactive command sequences    | ✅           | ✅ (some)    |
| Multi-vendor high-level support  |              | ✅           |
| Easier for beginners             |              | ✅           |
| Upload/download files            | ✅           |             |

---

## 🏁 Summary
Paramiko empowers network engineers with direct SSH control for:
- Interactive command sessions
- Backup and diagnostics
- Uploading and downloading scripts

It is a must-have in your toolkit when working with SSH-based devices or when you need fine-grained CLI access.

👉 In the next lab, learners will implement these concepts in a hands-on way.

Would you like me to proceed with **Lab 4: Automating Backups and Diagnostics with Paramiko** next?

