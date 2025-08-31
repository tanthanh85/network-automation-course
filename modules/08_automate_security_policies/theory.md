# Module 8 — Automating Security Policies using Python

## 1. Overview

Security is one of the most critical aspects of network operations. Traditionally, network engineers configured security rules (ACLs, firewall rules, segmentation policies) manually per device, which is time-consuming and error-prone. In this module, we focus on how Python can help you **automate security policy enforcement** across the network infrastructure in a reliable, scalable, and version-controlled manner.

We will cover:
- Automating Access Control Lists (ACLs)
- Managing firewall rules across devices
- Detecting unauthorized devices or access using Python scripts

Python gives you the flexibility to read policy definitions from YAML or JSON, convert them into CLI commands or API payloads, and push them across many devices using SSH, RESTCONF, NETCONF, or even Ansible.

---

## 2. Why Automate Security Policies?

Manual changes to security rules:
- May introduce typos or misconfigurations
- Are hard to track and audit
- Cannot be replicated across 100+ devices quickly

Automating them brings:
- **Consistency**: Ensures the same policies across multiple routers, firewalls, or switches.
- **Version Control**: Track who changed what and roll back if needed.
- **Speed and Agility**: Implement new access policies in seconds.
- **Better Compliance**: Easier to audit and prove to security teams.

---

## 3. Python Use Cases for Security Automation

### a. ACL Deployment with Netmiko or Paramiko
- Read a YAML or CSV file of ACL rules
- Generate CLI commands with Jinja2 templates
- Push to Cisco IOS using Netmiko or Paramiko

Example ACL YAML:
```yaml
acl_name: BLOCK_BAD_IPS
rules:
  - seq: 10
    action: deny
    src: 203.0.113.45
    wildcard: 0.0.0.0
  - seq: 20
    action: permit
    src: any
```

Python can render it to:
```text
ip access-list extended BLOCK_BAD_IPS
  10 deny ip host 203.0.113.45 any
  20 permit ip any any
```

### b. Managing Firewall Rules
If you're using firewalls like Cisco ASA or Palo Alto, you can:
- Use Python with REST APIs (e.g., Cisco Firepower, PAN-OS)
- Automatically add/remove security policies
- Integrate with Git for CI/CD of security policies

### c. Unauthorized Device Detection
- Use Python to parse MAC address tables (`show mac address-table`)
- Compare against known inventory from NetBox or YAML
- Alert or block unknown MACs

---

## 4. Security Policy Data Modeling

You should never hardcode security rules into a script. Instead, model the policy using structured data:

- YAML → human-readable format for engineers
- JSON → used by APIs (Cisco, Fortinet, etc.)
- XML → supported in NETCONF (for firewall or router config)

Python makes it easy to parse these using:
- `yaml` module
- `json` module
- `xml.etree.ElementTree` or `xmltodict`

---

## 5. Integrating with External Systems

Security doesn't exist in isolation. You can:
- Pull threat intelligence feeds (e.g., Cisco Talos, AbuseIPDB) to block bad IPs
- Use SNMP or RESTCONF to read interface status
- Connect to Cisco ISE or SecureX APIs to identify threats

---

## 6. Tools You Can Combine with Python
- **Cisco SecureX**: Threat correlation via API
- **Cisco Firepower Management Center (FMC)**: REST API for rule management
- **Cisco ISE**: Session info + identity mapping
- **Ansible**: Deploy ACLs with multi-vendor playbooks
- **NetBox**: Store ACL templates or interface labels
- **Splunk/Syslog**: Python can parse logs for security alerts

---

## 7. Best Practices
- Store ACL/firewall rules in Git
- Use YAML/JSON to define reusable policies
- Test your scripts in a sandbox before deploying
- Include exception handling for device errors
- Modularize your code: functions for login, rendering config, pushing, validating
- Maintain a rollback plan

---

## 8. Summary
With Python, you gain full control over security policy deployment, monitoring, and enforcement. From ACLs and firewalls to device detection and rule compliance, Python becomes the cornerstone of **Network Security Automation**.



