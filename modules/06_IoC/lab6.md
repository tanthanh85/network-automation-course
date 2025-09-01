# Lab 6 – Infrastructure as Code with NETCONF, YAML, Jinja2, Git, and pyATS

## 🎯 Objective

In this advanced lab, learners will automate OSPF configuration on Cisco IOS XE devices using NETCONF. Instead of static XML, learners will use YAML + Jinja2 to dynamically generate the XML payload. The lab concludes with **pyATS** to validate the OSPF neighbor state and includes Git-based version control and **a rollback script** to remove the OSPF configuration if necessary.

⏱ Estimated Time: 2–3 hours

---

## 📋 Prerequisites

- Cisco DevNet Sandbox: IOS XE on CSR1000v Always-On sandbox
- Tools installed:
  - Python 3.9+
  - `ncclient`, `pyats`, `pyats.topology`, `pyats.aetest`, `jinja2`, `pyyaml`
  - Git CLI
  - VSCode

🔑 IOS XE Sandbox credentials:

- Hostname: `sandbox-iosxe-latest-1.cisco.com`
- NETCONF Port: `830`
- Username: `developer`
- Password: `C1sco12345`

---

## Step-by-Step Guide

### 🧱 Step 1: Setup Project Environment

```bash
git clone https://gitlab.com/<your-username>/netconf-iac-lab.git
cd netconf-iac-lab
python3 -m venv .venv
source .venv/bin/activate
pip install ncclient pyats jinja2 pyyaml
```

Create a `.gitignore` file to ignore unnecessary files:
```bash
echo -e ".venv/\n__pycache__/\n*.log\n*.pyc\noutput/" > .gitignore
```

### 📄 Step 2: Define OSPF Data in YAML

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

### 🧩 Step 3: Create Jinja2 Template for XML

Create `templates/ospf_template.xml.j2`:

```
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

### ⚙️ Step 4: Render XML and Push via NETCONF

Create `scripts/deploy_ospf_jinja.py`:

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

Run the script:

```bash
python3 scripts/deploy_ospf_jinja.py
```

✅ **Expected Output**:

```xml
<ok/>
```

---

### 🧪 Step 5: Validate OSPF with pyATS

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

Run validation:

```bash
genie learn ospf --testbed-file testbed.yaml --output ospf_state
cat ospf_state/ospf/ops/ospf/ospf.txt
```

✅ **Expected Output**:

- OSPF process ID
- Router ID: `1.1.1.1`
- Neighbor information from each area

---

### 🔄 Step 6: Rollback OSPF Configuration

Create `scripts/rollback_ospf_jinja.py`:

```python
from ncclient import manager

rollback_xml = """
<config>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <router>
      <ospf operation="delete"/>
    </router>
  </native>
</config>
"""

with manager.connect(
    host="sandbox-iosxe-latest-1.cisco.com",
    port=830,
    username="developer",
    password="C1sco12345",
    hostkey_verify=False,
    device_params={"name": "csr"},
) as m:
    response = m.edit_config(target="running", config=rollback_xml)
    print(response)
```

Run the rollback:

```bash
python3 scripts/rollback_ospf_jinja.py
```

✅ **Expected Output**:

```xml
<ok/>
```

Verify OSPF is removed:

```bash
show ip ospf
```

Should return:

```txt
% OSPF not running
```

---

## 📚 Homework Challenges

1. ✅ Add another OSPF area with 2 more networks
2. ✅ Include `passive-interface` config via Jinja2
3. ✅ Write a script to **rollback OSPF config** (already done!)
4. ✅ Use `genie diff` to compare pre and post state
5. ✅ Try configuring **BGP** using new YAML + Jinja2

---

## 🧠 Takeaway Summary

- YAML + Jinja2 enables dynamic NETCONF payload generation
- Git stores your IaC code for collaboration and rollback
- NETCONF allows precise network config control
- pyATS verifies post-deploy network behavior
- You’ve practiced **real IaC DevOps flow for networking**