# Module 6 – Infrastructure as Code (IaC) Automation with Python

## 1. Overview
Infrastructure as Code (IaC) enables engineers to define, manage, and deploy networks using code. This modern approach ensures repeatability, scalability, and automation for infrastructure configuration. In this module, learners will gain hands-on knowledge to implement IaC with Python, Git, YAML, Jinja2, Ansible, Terraform, Cisco pyATS, NetBox, and CI/CD tools.

---

## 2. What is Infrastructure as Code (IaC)?
IaC means treating infrastructure (network configuration, devices, topology) as source code. You write config instructions in files and use automation to apply them. IaC benefits:
- Version control
- Faster recovery
- Consistency across environments
- Automated rollback

---

## 3. Declarative vs Imperative IaC
- **Declarative**: You declare the desired state (e.g., `VLAN 10 exists`) — used by **Ansible**, **Terraform**, **Cisco NSO**.
- **Imperative**: You specify the steps (e.g., `ssh, run vlan command`) — used in raw Python/Netmiko scripts.

---

## 4. IaC Workflow with Python
Typical Python-based IaC involves:
- YAML file for device inventory and config
- Jinja2 templates for structured config
- Python to render templates and deploy
- Git for version control
- pyATS/ThousandEyes for validation

---

## 5. Using Jinja2 for Config Generation
Jinja2 is a templating engine. You define the structure of your config with placeholders, then populate it with actual data from YAML/JSON.

**Example – OSPF Template (jinja2):**
```jinja
router ospf {{ process_id }}
  network {{ network }} area {{ area }}
```

**YAML Input:**
```yaml
process_id: 1
network: 10.0.0.0 0.0.0.255
area: 0
```

**Python Code:**
```python
from jinja2 import Template
import yaml

with open('config.yaml') as f:
    data = yaml.safe_load(f)

with open('ospf_template.j2') as f:
    template = Template(f.read())

print(template.render(data))
```

---

## 6. NetBox as Source of Truth
**NetBox** is a network source of truth used to store:
- Devices, interfaces, IPs, VLANs
- Circuit information, racks, sites

Use NetBox API to:
- Query devices and IPs
- Build dynamic inventory
- Auto-render config with Jinja2

**Python Example:**
```python
import requests

url = "https://netbox.example.com/api/dcim/devices/"
headers = {"Authorization": "Token <API_TOKEN>"}

response = requests.get(url, headers=headers)
devices = response.json()["results"]
```

---

## 7. Version Control with Git
- Store all YAML, Jinja2, Python in Git
- Use `.gitignore` to exclude logs, `.venv`, etc.
- Use branches for dev/test/prod

---

## 8. Ansible in IaC
- **Playbooks** describe declarative network configs
- **Inventories** define device groups (static/dynamic)
- **Templates** use Jinja2
- Supports **idempotency** (re-run safe)

**Example:**
```yaml
- name: Configure hostname
  hosts: switches
  tasks:
    - name: Set hostname
      ios_config:
        lines:
          - hostname switch01
```

---

## 9. Terraform in IaC
**Terraform** is declarative and cloud/network agnostic. Cisco integrations include:
- Cisco ACI (terraform-provider-aci)
- Cisco Meraki (terraform-provider-meraki)
- NSO (experimental support)

**Terraform Example:**
```hcl
provider "aci" {
  username = "admin"
  password = var.password
}

resource "aci_tenant" "prod" {
  name = "Production"
}
```

---

## 10. Ansible vs Terraform
| Feature                 | Ansible                     | Terraform                  |
|------------------------|-----------------------------|----------------------------|
| Language               | YAML + Python modules       | HCL (HashiCorp Config Lang)|
| State tracking         | No (stateless)              | Yes                        |
| Use case               | Config mgmt (L2-L4)         | Infra provisioning (L1-L3) |
| Idempotent             | Yes                         | Yes                        |
| Agentless              | Yes                         | Yes                        |
| Cisco support          | IOS, NXOS, ACI, Meraki      | ACI, Meraki, NSO           |

---

## 11. pyATS for Post-Deployment Testing
Use pyATS to:
- Test OSPF/BGP interfaces
- Compare pre/post state (diff)
- Check SLA and logs

Example pyATS command:
```bash
genie learn ospf --testbed-file testbed.yaml --output pre_ospf
```

---

## 12. ThousandEyes for API-Driven Observability
- Validate app-to-app or site-to-cloud performance
- Use Python SDK to query probe results
- Trigger alerts when validation fails

---

## 13. Cisco NSO for Service-Oriented IaC
Cisco NSO enables model-driven service definition.
- Define YANG services
- Generate CLI/config mappings
- Use REST/NETCONF APIs
- Rollback, fast provisioning

---

## 14. CI/CD Pipeline with GitLab
To automate the end-to-end IaC process:

**Use GitLab CI/CD to:**
- Validate YAML and Python code
- Generate configs from templates
- Push config via Netmiko or Ansible
- Run pyATS for post-deploy testing

**.gitlab-ci.yml Example:**
```yaml
stages:
  - validate
  - generate
  - deploy
  - test

validate:
  stage: validate
  script:
    - yamllint inventory/
    - pylint scripts/*.py

generate:
  stage: generate
  script:
    - python3 scripts/generate_config.py

deploy:
  stage: deploy
  script:
    - python3 scripts/deploy_config.py

test:
  stage: test
  script:
    - python3 scripts/test_ospf.py
```

You can host your GitLab runner or use GitLab.com’s built-in runners.

---

## 15. Summary
- IaC transforms how networks are deployed and managed
- Git + YAML + Jinja2 + Python create a flexible pipeline
- NetBox offers centralized inventory
- pyATS and ThousandEyes validate behavior
- CI/CD (GitLab) ensures continuous compliance

---

