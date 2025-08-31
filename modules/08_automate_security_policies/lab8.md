# Lab 8 — Automating ACLs on Cisco FTD using Python

## 🧪 Objective
In this lab, learners will automate Access Control List (ACL) deployment on a **Cisco Firepower Threat Defense (FTD)** firewall using its REST API interface. This demonstrates how Python can be used to enforce security policy dynamically and at scale.

We’ll connect to the **Cisco FTD DevNet Sandbox**, authenticate via REST API, and push new access control rules that block traffic from known malicious IPs and allow trusted networks.

---

## 🔧 Lab Environment
- Cisco FTD DevNet Sandbox: [https://devnetsandbox.cisco.com/](https://devnetsandbox.cisco.com/)
- Python 3.9+
- VSCode IDE
- `requests`, `json`, `yaml` libraries
- Postman (for manual API testing)

---

## 🗂️ Folder Structure
```
lab08_ftd_acl/
├── acl_data.yaml              # Security rules in YAML
├── render_acl.py              # Convert YAML into JSON payload
├── push_acl_ftd.py            # Auth and API push to Cisco FTD
└── ftd_utils.py               # Helper: login, token mgmt, etc.
```

---

## 📝 Step-by-Step Guide

### 1. 🔐 Setup Authentication
FTD REST API requires token-based auth. First, get the base64-encoded credentials:

```python
# ftd_utils.py
import requests

def get_token(base_url, username, password):
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(
        url=f"{base_url}/api/fdm/v6/fdm/token",
        auth=(username, password),
        headers=headers,
        verify=False
    )
    return resp.json()['accessToken']
```

### 2. 📄 Define ACL Rules in YAML
```yaml
acl_name: Block_Malicious
rules:
  - name: Deny_BadIP
    action: DENY
    src_ip: 203.0.113.45
    dest_ip: any
    protocol: ip
  - name: Permit_Internal
    action: PERMIT
    src_ip: 10.0.0.0/8
    dest_ip: any
    protocol: ip
```

### 3. 🧩 Convert YAML to REST Payload
```python
# render_acl.py
import yaml, json

def load_acl(yaml_file):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)

    rules = []
    for r in data['rules']:
        rules.append({
            "name": r['name'],
            "action": r['action'],
            "sourceNetworks": {"objects": [{"type": "Network", "value": r['src_ip']}]},
            "destinationNetworks": {"objects": [{"type": "Network", "value": r['dest_ip']}]},
            "type": "AccessRule",
            "enabled": True
        })
    return rules
```

### 4. 🚀 Push to Cisco FTD API
```python
# push_acl_ftd.py
import requests, ftd_utils, render_acl

FTD = {
    'base_url': 'https://sandbox-fdm.cisco.com',
    'username': 'admin',
    'password': 'C1sco12345'
}

acl_rules = render_acl.load_acl('acl_data.yaml')
token = ftd_utils.get_token(**FTD)
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

for rule in acl_rules:
    res = requests.post(
        f"{FTD['base_url']}/api/fdm/v6/policy/accesspolicies/ACCESS_POLICY_UUID/accessrules",
        headers=headers,
        json=rule,
        verify=False
    )
    print(res.status_code, res.text)
```
**Note**: Replace `ACCESS_POLICY_UUID` with actual policy ID from FTD.

---

## 🧪 Testing ACL with Postman (Optional)
1. Log in to Cisco FTD API and get token (same as Python).
2. Create a new `POST` request to `/api/fdm/v6/policy/accesspolicies/<id>/accessrules`
3. Paste a JSON rule and submit.
4. Observe return code `201 Created`.

---

## ✅ Expected Results
- New ACL rule appears in FTD’s GUI (Objects → Policies → Access Control)
- Malicious IPs are now blocked
- Internal traffic (10.0.0.0/8) is permitted

---

## 💡 Troubleshooting Tips
| Problem | Fix |
|--------|-----|
| 401 Unauthorized | Check FTD credentials or token expiration |
| 400 Bad Request | Ensure rule payload has required fields |
| SSL Error | Use `verify=False` or install FTD certs |

---

## 🧠 Takeaway Notes
- REST APIs make firewall automation scalable
- YAML → JSON transformation is key to data modeling
- Reusable helper scripts like `ftd_utils.py` are best practice
- All policy changes can now be tracked in Git
