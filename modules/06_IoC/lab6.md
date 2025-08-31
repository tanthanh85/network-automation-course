# Lab 6 – Infrastructure as Code with NETCONF, YAML, Jinja2 and pyATS

## Objective
In this advanced lab, learners will automate OSPF configuration on Cisco IOS XE devices using NETCONF. Instead of static XML, learners will use YAML + Jinja2 to dynamically generate the XML payload. The lab concludes with pyATS to validate the OSPF neighbor state.

> **Estimated Time**: 2–3 hours

---

## Prerequisites
- Cisco DevNet Sandbox: IOS XE on CSR1000v Always-On [sandbox](https://developer.cisco.com/site/sandbox/)
- Installed tools:
  - Python 3.9+
  - `ncclient`, `pyats`, `pyats.topology`, `pyats.aetest`, `jinja2`, `pyyaml`
  - VSCode

> 🔑 IOS XE Sandbox credentials:
```
Hostname: sandbox-iosxe-latest-1.cisco.com
NETCONF Port: 830
Username: developer
Password: C1sco12345
```

---

## Step-by-Step Guide

### Step 1: Setup Project Environment
```bash
git clone https://gitlab.com/<your-username>/netconf-iac-lab.git
cd netconf-iac-lab
python3 -m venv .venv
source .venv/bin/activate
pip install ncclient pyats jinja2 pyyaml
```

---

### Step 2: Define OSPF Data in YAML
Create a file `data/ospf_data.yaml`:
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

---

### Step 3: Create Jinja2 Template for XML
Create `templates/ospf_template.xml.j2`:
```jinja
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

---

### Step 4: Render XML and Push via NETCONF
Create `scripts/deploy_ospf_jinja.py`:
```python
import yaml
from jinja2 import Environment, FileSystemLoader
from ncclient import manager

# Load YAML
with open('data/ospf_data.yaml') as f:
    ospf_data = yaml.safe_load(f)

# Render XML from Jinja2
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('ospf_template.xml.j2')
rendered_xml = template.render(ospf=ospf_data['ospf'])

# Connect via NETCONF
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

Run it:
```bash
python3 scripts/deploy_ospf_jinja.py
```

✅ **Expected Output**: NETCONF `<ok/>` response

---

### Step 5: Validate OSPF with pyATS
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

Run pyATS:
```bash
genie learn ospf --testbed-file testbed.yaml --output ospf_state
cat ospf_state/ospf/ops/ospf/ospf.txt
```
✅ **Expected Output**: OSPF process, router ID, and neighbor info

---

## Homework Challenges
1. Add another OSPF area with 2 more networks
2. Include passive-interface config via Jinja2
3. Write a script to rollback OSPF config
4. Use `genie diff` to compare pre and post config
5. Try the same logic for BGP configuration using new YAML/template

---

## Takeaway Summary
✅ In this lab you learned:
- Using **YAML + Jinja2** to generate structured NETCONF payloads
- Configuring OSPF via **ncclient** to IOS XE
- Verifying neighbor state using **pyATS Genie**
- How data, templates, and testing integrate in an IaC workflow

