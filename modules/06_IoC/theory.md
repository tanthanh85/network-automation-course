# Module 6 – Infrastructure as Code (IaC) Automation with Python

## 1. Overview
Infrastructure as Code (IaC) enables engineers to define, manage, and deploy networks using code. This modern approach ensures repeatability, scalability, and automation for infrastructure configuration. In this module, learners will gain hands-on knowledge to implement IaC with Python, Git, YAML, Jinja2, Ansible, Terraform, Cisco pyATS, NetBox, and CI/CD tools.

## 2. What is Infrastructure as Code (IaC)?
IaC means treating infrastructure (network configuration, devices, topology) as source code. You write config instructions in files and use automation to apply them. IaC benefits:

- Version control
- Faster recovery
- Consistency across environments
- Automated rollback

## 3. Declarative vs Imperative IaC
- **Declarative**: You declare the desired state (e.g., VLAN 10 exists) — used by Ansible, Terraform.
- **Imperative**: You specify the steps (e.g., ssh, run vlan command) — used in raw Python/Netmiko scripts.

## 4. IaC Workflow with Python
Typical Python-based IaC involves:
- YAML file for device inventory and config
- Jinja2 templates for structured config
- Python to render templates and deploy
- Git for version control
- pyATS/ThousandEyes for validation

## 5. Using Jinja2 for Config Generation
Jinja2 is a templating engine. You define the structure of your config with placeholders, then populate it with actual data from YAML/JSON.

**Example – OSPF Template (jinja2):**
```jinja2
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

## 6. NetBox as Source of Truth
NetBox is a network source of truth used to store:
- Devices, interfaces, IPs, VLANs
- Circuit information, racks, sites

**Use NetBox API to:**
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

## 7. Version Control with Git

Version control is critical in modern network automation workflows. It ensures your configurations, templates, and scripts are tracked, auditable, and easily reversible.

### 7.1 Why Git Matters for IaC
Git allows teams to:
- Track changes to YAML files, Python scripts, and Jinja2 templates
- Collaborate on automation projects
- Revert to known-good versions
- Maintain development, test, and production branches
- Enable CI/CD workflows (e.g., GitLab pipelines)

### 7.2 Repository Structure Example
```
network-automation/
├── inventory/
│   ├── dev.yaml
│   ├── prod.yaml
├── templates/
│   ├── ospf_template.j2
│   └── bgp_template.j2
├── configs/
│   └── generated/
├── scripts/
│   ├── generate_config.py
│   ├── deploy_config.py
├── testbed/
│   └── testbed.yaml
├── .gitignore
└── README.md
```

### 7.3 Using `.gitignore`
```gitignore
__pycache__/
.venv/
logs/
*.log
*.pyc
*.swp
.env
```

### 7.4 Common Git Operations

| Task                  | Command                                  |
|-----------------------|-------------------------------------------|
| Initialize repo       | `git init`                                |
| Add files             | `git add .`                               |
| Commit                | `git commit -m "Initial commit"`          |
| Check status          | `git status`                              |
| View history          | `git log --oneline`                       |
| Create branch         | `git checkout -b dev`                     |
| Switch branch         | `git checkout main`                       |
| Merge branch          | `git merge dev`                           |
| Push to remote        | `git push origin dev`                     |
| Pull from remote      | `git pull`                                |
| Fetch changes         | `git fetch`                               |
| Rebase                | `git rebase main`                         |
| View diff             | `git diff`                                |
| Resolve conflicts     | Manual + `git add` + `git commit`         |
| Roll back commit      | `git reset --hard HEAD~1`                 |
| Tag release           | `git tag v1.0`                            |

### 7.5 Sample Workflow
```bash
git clone https://gitlab.com/team/network-automation.git
cd network-automation
git checkout -b feature/ospf-config
vim templates/ospf_template.j2
git add templates/ospf_template.j2
git commit -m "Add OSPF template"
git push origin feature/ospf-config
```

### 7.6 Git Branching Model
- `main`
- `dev`
- `feature/<name>`
- `hotfix/<issue>`
- `release/v1.0`

### 7.7 Best Practices
- Use `.gitignore` wisely
- Keep secrets out of Git
- Use merge requests
- Tag stable versions

### 7.8 Troubleshooting Git
| Issue                        | Fix                                  |
|-----------------------------|---------------------------------------|
| Merge conflict               | Edit file, `git add`, then `commit`  |
| SSH error                   | Add SSH key to GitLab/GitHub         |

## 8. Ansible in IaC
Example:
```yaml
- name: Configure hostname
  hosts: switches
  tasks:
    - name: Set hostname
      ios_config:
        lines:
          - hostname switch01
```

## 9. Terraform in IaC
Example:
```hcl
provider "aci" {
  username = "admin"
  password = var.password
}

resource "aci_tenant" "prod" {
  name = "Production"
}
```

## 10. Ansible vs Terraform
| Feature       | Ansible        | Terraform       |
|---------------|----------------|-----------------|
| Language      | YAML           | HCL             |
| Cisco Support | IOS, NXOS      | ACI, Meraki     |
| Use Case      | Config mgmt    | Infra deploy    |

## 11. pyATS for Post-Deploy Testing
```bash
genie learn ospf --testbed-file testbed.yaml --output pre_ospf
```

## 12. ThousandEyes for Observability
Use API or SDK to validate reachability and app performance.

## 13. CI/CD with GitLab

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

## 14. Summary
IaC transforms how networks are managed. Combining Git, YAML, Python, Ansible, pyATS, NetBox and GitLab CI/CD enables reliable and scalable infrastructure automation.