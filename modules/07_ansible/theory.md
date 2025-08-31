# Module 7: Ansible Workflows for Network Automation

## Overview

Ansible is one of the most widely adopted tools for network automation, built on a simple, agentless architecture. It allows engineers to automate the configuration, deployment, and management of network devices through declarative YAML-based playbooks. In this module, you will learn how to use Ansible for managing network infrastructure, compare it with Python libraries like Netmiko, and integrate it with tools such as NetBox, Jinja2, and CI/CD pipelines.

---

## Why Ansible for Network Automation?
- **Agentless**: No need to install software on network devices.
- **Declarative Language (YAML)**: Makes playbooks human-readable and easy to maintain.
- **Scalable**: Manage hundreds of devices using inventory files.
- **Idempotent**: Ensures predictable, repeatable state.
- **Rich Ecosystem**: Thousands of ready-to-use modules, including those for Cisco, Juniper, and Arista.

---

## Key Components

### 1. Inventory (YAML Format)
Ansible inventory defines the devices (hosts) to be managed. You can use static or dynamic inventory. YAML format is cleaner and preferred for structured inventories.

**Example `inventory.yaml`:**
```yaml
all:
  children:
    cisco:
      hosts:
        csr1000v1:
          ansible_host: 192.0.2.1
          ansible_user: admin
          ansible_password: admin
          ansible_network_os: ios
        csr1000v2:
          ansible_host: 192.0.2.2
          ansible_user: admin
          ansible_password: admin
          ansible_network_os: ios
        csr1000v3:
          ansible_host: 192.0.2.3
          ansible_user: admin
          ansible_password: admin
          ansible_network_os: ios
```

To use it:
```bash
ansible-playbook -i inventory.yaml configure_vlan.yml
```

### 2. Playbook
Playbooks are YAML files that describe tasks to be run.

**Example `configure_vlan.yml`:**
```yaml
- name: Configure VLAN on Cisco devices
  hosts: cisco
  gather_facts: no
  connection: network_cli
  tasks:
    - name: Create VLAN 100
      ios_config:
        lines:
          - vlan 100
          - name PROD_VLAN
```

### 3. Running the Playbook
Make sure you are in the same directory as the inventory and playbook files. Run the command:

```bash
ansible-playbook -i inventory.yaml configure_vlan.yml
```

#### Expected Output:
```
PLAY [Configure VLAN on Cisco devices] **************************************************

TASK [Create VLAN 100] ******************************************************************
ok: [csr1000v1]
ok: [csr1000v2]
ok: [csr1000v3]

PLAY RECAP ****************************************************************************
csr1000v1                 : ok=1    changed=1    unreachable=0    failed=0
csr1000v2                 : ok=1    changed=1    unreachable=0    failed=0
csr1000v3                 : ok=1    changed=1    unreachable=0    failed=0
```

This confirms that the VLAN configuration has been successfully pushed to all devices.

If there are errors like unreachable hosts or authentication issues, Ansible will output descriptive error messages. Check:
- Inventory IP and credentials
- SSH reachability (`ssh admin@192.0.2.1`)
- Ansible collections installed

---

## Ansible Modules
Ansible uses network-specific modules:
- `ios_config`, `ios_command` for Cisco IOS
- `nxos_config`, `eos_config`, etc.
- `netconf_config`, `restconf_config` for API-driven automation

---

## Jinja2 Templates with Ansible
Ansible supports Jinja2 for dynamic configuration rendering.

**Example Template (`vlan_template.j2`)**
```jinja
vlan {{ vlan_id }}
 name {{ vlan_name }}
```

**Task with template:**
```yaml
- name: Render VLAN config
  template:
    src: vlan_template.j2
    dest: rendered_config.txt
```

---

## Structured Variables
Store configuration variables in YAML under `group_vars/` or `host_vars/`.

**Example `host_vars/csr1000v1.yaml`:**
```yaml
vlan_id: 100
vlan_name: PROD_VLAN
```

---

## NetBox as Dynamic Inventory
NetBox can act as a dynamic inventory source for Ansible:
1. Sync inventory via NetBox plugin
2. Pull device groups, IPs, and custom fields
3. Feed into Ansible for dynamic playbook execution

---

## CI/CD with Ansible
Ansible can integrate with GitLab CI/CD to:
- Validate syntax and test rendering
- Deploy configuration only after approval
- Run pyATS tests post-deployment

---

## Comparison: Netmiko vs Ansible
| Feature | Netmiko | Ansible |
|--------|---------|---------|
| Language | Python | YAML |
| Paradigm | Imperative | Declarative |
| Reuse | Functions | Roles/Tasks |
| Scaling | Script per task | Inventory + Playbooks |
| State-aware | No | Yes (idempotent) |

Use **Netmiko** for granular control, **Ansible** for repeatable orchestration.

---

## Advanced Concepts
- **Ansible Roles**: Break complex playbooks into reusable modules
- **Check Mode**: Dry-run to test changes before applying
- **Tags**: Run only specific tasks
- **Handlers**: Trigger actions on change
- **Lookups & Filters**: Extend logic

---

## Example Use Case: Automate VLAN Deployment
**Structure:**
```
├── group_vars/
│   └── all.yaml
├── templates/
│   └── vlan_template.j2
├── inventory.yaml
├── configure_vlan.yml
```

**Playbook:**
```yaml
- name: Deploy VLANs from YAML
  hosts: cisco
  tasks:
    - name: Render VLAN config
      template:
        src: vlan_template.j2
        dest: vlan.cfg
    - name: Push VLAN config
      ios_config:
        src: vlan.cfg
```

---

## Homework
1. Use Ansible to configure OSPF across 3 routers using variables and Jinja2.
2. Convert a Netmiko script to Ansible playbook.
3. Explore NetBox dynamic inventory and pull device IPs.
4. Build a GitLab pipeline to validate and deploy an Ansible playbook.
5. Write a custom role for BGP automation.

---

## Key Takeaways
✅ Ansible offers declarative, scalable, and agentless network automation. With structured inventories, Jinja2 templating, and tight Git integration, it allows consistent and repeatable deployments at scale.

