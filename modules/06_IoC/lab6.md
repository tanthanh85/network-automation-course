
# Lab 6 – Infrastructure as Code with NETCONF, YAML, Jinja2, pyATS and Git

## 🎯 Objective

In this advanced lab, learners will automate OSPF configuration on Cisco IOS XE devices using NETCONF. Instead of static XML, learners will use **YAML + Jinja2** to dynamically generate the XML payload. The lab includes:

- Using **Git** to version-control automation code and templates.
- Applying **NETCONF** to push config to devices.
- Validating the results using **pyATS**.
- Using **Git-based rollback** in case post-deployment validation fails.

> 🕒 Estimated Time: 3–4 hours

---

## 🔧 Prerequisites

- Cisco DevNet Sandbox: IOS XE on CSR1000v Always-On
- Python 3.9+
- VSCode
- Installed Python packages:
  ```bash
  pip install ncclient pyats jinja2 pyyaml
  ```

- IOS XE Credentials:
  ```text
  Host: sandbox-iosxe-latest-1.cisco.com
  Port: 830 (NETCONF), 22 (SSH)
  Username: developer
  Password: C1sco12345
  ```

---

## 🧪 Step-by-Step Guide

### Step 1: Git Project Setup

```bash
git clone https://gitlab.com/<your-username>/netconf-iac-lab.git
cd netconf-iac-lab
python3 -m venv .venv
source .venv/bin/activate
pip install ncclient pyats jinja2 pyyaml

git init
echo ".venv/
__pycache__/
*.log" > .gitignore
git add .
git commit -m "Initial OSPF automation project"
```

> ✅ Expected: Clean Git repo with only necessary files tracked.

---

### Step 2: Define OSPF Data in YAML

Create `data/ospf_data.yaml`:

```yaml
ospf:
  process_id: 1
  router_id: 1.1.1.1
  networks:
    - ip: 192.168.0.0
      wildcard: 0.0.255.255
      area: 0
    - ip: 10.10.10.0
      wildcard: 0.0.0.255
      area: 1
```

> ✅ Expected: Structured OSPF input data

Commit changes:

```bash
git add data/ospf_data.yaml
git commit -m "Add initial OSPF YAML config"
```

---

### Step 3: Jinja2 Template for NETCONF Payload

Create `templates/ospf_template.xml.j2`:

```jinja2
<config>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <router>
      <ospf>
        <id>{{ ospf.process_id }}</id>
        <router-id>{{ ospf.router_id }}</router-id>
        {% for net in ospf.networks %}
        <network>
          <ip>{{ net.ip }}</ip>
          <wildcard>{{ net.wildcard }}</wildcard>
          <area>{{ net.area }}</area>
        </network>
        {% endfor %}
      </ospf>
    </router>
  </native>
</config>
```

Commit:

```bash
git add templates/
git commit -m "Add Jinja2 template for OSPF XML"
```

---

### Step 4: Render and Deploy via NETCONF

Create `scripts/deploy_ospf.py`:

```python
import yaml
from jinja2 import Environment, FileSystemLoader
from ncclient import manager

with open('data/ospf_data.yaml') as f:
    ospf_data = yaml.safe_load(f)

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('ospf_template.xml.j2')
rendered_xml = template.render(ospf=ospf_data['ospf'])

with manager.connect(
    host="sandbox-iosxe-latest-1.cisco.com",
    port=830,
    username="developer",
    password="C1sco12345",
    hostkey_verify=False,
    device_params={'name': 'csr'}
) as m:
    response = m.edit_config(target="running", config=rendered_xml)
    print(response)
```

Run:

```bash
python3 scripts/deploy_ospf.py
```

> ✅ Expected: `<ok/>` NETCONF success response

Commit:

```bash
git add scripts/
git commit -m "Deploy OSPF with dynamic NETCONF payload"
```

---

### Step 5: Validate with pyATS

Create `testbed.yaml`:

```yaml
devices:
  iosxe:
    os: iosxe
    type: router
    connections:
      cli:
        protocol: ssh
        ip: sandbox-iosxe-latest-1.cisco.com
        port: 22
    credentials:
      default:
        username: developer
        password: C1sco12345
```

Run:

```bash
genie learn ospf --testbed-file testbed.yaml --output ospf_state
cat ospf_state/ospf/ops/ospf/ospf.txt
```

> ✅ Expected Output:
```
Process ID: 1
Router ID: 1.1.1.1
Neighbors: 1 or more established
```

---

### Step 6: Git Rollback if Validation Fails

Simulate validation failure. Then rollback:

```bash
git log  # Get previous commit hash
git revert <commit-hash>  # OR
git checkout <previous-commit> -- data/ospf_data.yaml
```

Re-run deployment:

```bash
python3 scripts/deploy_ospf.py
```

> ✅ Expected: Device reverts to previous config.

---

## 🏡 Homework Challenges

1. Add a 3rd area to the YAML and push config.
2. Introduce a deliberate error in YAML and practice rollback.
3. Use `git branch` to create staging/prod branches.
4. Use `genie diff` to compare `ospf_state` with previous state.
5. Write `scripts/rollback.py` to revert via NETCONF.

---

## ✅ Takeaway Summary

- Learned Git workflow in automation projects
- Used YAML + Jinja2 to build NETCONF payload
- Deployed dynamic config via NETCONF
- Validated via pyATS Genie
- Practiced rollback and change tracking via Git

