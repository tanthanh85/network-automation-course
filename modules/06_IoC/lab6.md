# Lab 6 – Infrastructure as Code with Netmiko, YAML, Jinja2, Git and pyATS

## Objective
In this advanced lab, learners will automate OSPF configuration on Cisco IOS XE devices using **Netmiko** instead of NETCONF. Configuration will be dynamically generated using **YAML** and **Jinja2**. Learners will also use **Git** for version control and **pyATS** for validation. In case of error or rollback scenario, a script will be provided to remove the OSPF configuration.

---

## Estimated Time: 2–3 hours

### Prerequisites

- Cisco DevNet Sandbox: IOS XE on CSR1000v Always-On sandbox
- Installed tools:
  - Python 3.9+
  - netmiko, pyats, jinja2, pyyaml
- VSCode

🔑 IOS XE Sandbox credentials:

- Hostname: `sandbox-iosxe-latest-1.cisco.com`
- SSH Port: `22`
- Username: `developer`
- Password: `C1sco12345`

---

## Step-by-Step Guide

### Step 1: Setup Project Environment

```bash
git clone https://gitlab.com/<your-username>/netmiko-iac-lab.git
cd netmiko-iac-lab
python3 -m venv .venv
source .venv/bin/activate
pip install netmiko jinja2 pyyaml pyats
```

### Step 2: Define OSPF Data in YAML

Create `data/ospf_data.yaml`:

```yaml
ospf:
  process_id: 1
  router_id: 1.1.1.1
  networks:
    - ip: 192.168.0.0 0.0.255.255 area 0
    - ip: 10.10.10.0 0.0.0.255 area 1
```

### Step 3: Create Jinja2 Template for CLI

Create `templates/ospf_template.j2`:

```jinja2
router ospf {{ ospf.process_id }}
 router-id {{ ospf.router_id }}
{% for net in ospf.networks %}
 network {{ net }}
{% endfor %}
```

### Step 4: Render Template and Send via Netmiko

Create `scripts/deploy_ospf_netmiko.py`:

```python
import yaml
from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler

# Load YAML
with open('data/ospf_data.yaml') as f:
    ospf_data = yaml.safe_load(f)

# Render template
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('ospf_template.j2')
config = template.render(ospf=ospf_data['ospf']).splitlines()

# Connect to device
device = {
    'device_type': 'cisco_ios',
    'host': 'sandbox-iosxe-latest-1.cisco.com',
    'username': 'developer',
    'password': 'C1sco12345',
}

with ConnectHandler(**device) as conn:
    output = conn.send_config_set(config)
    print(output)
```

✅ **Expected Result**: Output of `send_config_set()` with successful OSPF commands applied

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

Run:

```bash
genie learn ospf --testbed-file testbed.yaml --output ospf_state
cat ospf_state/ospf/ops/ospf/ospf.txt
```

✅ **Expected Result**: OSPF process, router ID, and neighbor info

### Step 6: Rollback Script

Create `scripts/rollback_ospf_netmiko.py`:

```python
from netmiko import ConnectHandler

device = {
    'device_type': 'cisco_ios',
    'host': 'sandbox-iosxe-latest-1.cisco.com',
    'username': 'developer',
    'password': 'C1sco12345',
}

commands = [
    'no router ospf 1'
]

with ConnectHandler(**device) as conn:
    output = conn.send_config_set(commands)
    print(output)
```

✅ **Expected Result**: `no router ospf 1` successfully executed

---

## Homework Challenges

- Add 2 more networks in a new OSPF area in the YAML file
- Extend Jinja2 to include passive-interface command
- Test BGP deployment using same IaC pattern
- Use pyATS `genie diff` to compare `pre` and `post` OSPF

---

## GitLab CI/CD (Optional)

You can use GitLab CI/CD pipeline to:

- Validate YAML and Jinja2 templates
- Render configuration files
- Push OSPF config using Netmiko
- Run pyATS verification

Example `.gitlab-ci.yml`:

```yaml
stages:
  - validate
  - deploy
  - test

validate:
  stage: validate
  script:
    - yamllint data/
    - python3 -m py_compile scripts/*.py

deploy:
  stage: deploy
  script:
    - python3 scripts/deploy_ospf_netmiko.py

test:
  stage: test
  script:
    - genie learn ospf --testbed-file testbed.yaml --output ospf_state
```

---

## Takeaway Summary

✅ You have learned:

- Netmiko-based CLI automation for IOS XE
- YAML + Jinja2 for structured configuration
- Version control integration with Git
- Post-deployment validation using pyATS
- GitLab CI/CD overview for network automation workflows