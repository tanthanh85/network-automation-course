# Module 5 — Using APIs to Retrieve Data on Cisco Network Devices

---

## 1. Introduction
Modern network devices expose structured, programmatic interfaces to interact with configuration and operational data. Instead of relying solely on CLI scraping, Python can leverage APIs like **RESTCONF** and **NETCONF** to retrieve, modify, or monitor network state in a secure and scalable way. These API interfaces are powered by standardized data models such as **YANG**.

---

## 2. Why Use APIs for Network Automation?
CLI is designed for humans. API is designed for machines. When building automated systems that need to:
- Query interface status from 100+ routers
- Push a new routing policy or QoS policy
- Detect threshold violations and generate alerts

Using structured data returned from an API ensures:
- **Reliable parsing** (no screen scraping)
- **Standard format** (JSON or XML)
- **Model-driven configuration** (YANG-based)
- **Granular control** (only the data you need)

Cisco routers support both RESTCONF and NETCONF starting from IOS XE 16.3 and above.

---

## 3. YANG Data Models
YANG is the common schema language for modeling device configuration and operational data. Devices implement different YANG modules (like native, OpenConfig, IETF standard).

Example YANG structure for interfaces:
```json
{
  "ietf-interfaces:interfaces": {
    "interface": [
      {
        "name": "GigabitEthernet1",
        "enabled": true,
        "type": "iana-if-type:ethernetCsmacd"
      }
    ]
  }
}
```

---

## 4. RESTCONF vs NETCONF
| Feature               | RESTCONF                            | NETCONF                              |
|------------------------|--------------------------------------|----------------------------------------|
| Protocol               | HTTPS                                | SSH                                    |
| Payload format         | JSON or XML                          | XML only                               |
| Style                  | RESTful (GET, POST, PUT, PATCH)      | RPC-based                              |
| Simpler for Monitoring| ✅ Yes                               | ❌ Verbose                             |
| Better for Config Push| ⚠️ Complex                          | ✅ Better suited                       |
| Python Library         | requests                             | ncclient                              |

---

## 5. Enabling RESTCONF & NETCONF on Cisco Router
```shell
conf t
ip http secure-server
restconf
netconf-yang
username admin privilege 15 secret cisco123
``` 
Test with Postman or curl:
```bash
curl -k -u admin:cisco123 https://<ip>/restconf/data/ietf-interfaces:interfaces
```

---

## 6. Sample Project Structure
```bash
nasp-lab5/
├── inventory.yaml                     # Device credentials
├── restconf/
│   ├── get_interfaces.py             # Pull interfaces
│   └── get_cpu.py                    # Pull CPU data
├── netconf/
│   ├── get_hostname.py              # Retrieve device hostname
│   └── get_bgp_neighbors.py         # Pull BGP peerings
├── utils/
│   ├── restconf_helper.py
│   └── netconf_helper.py
```

---

## 7. inventory.yaml
```yaml
devices:
  - name: csr1
    ip: 192.168.1.10
    port: 443
    netconf_port: 830
    username: admin
    password: cisco123
```

---

## 8. RESTCONF in Python
**restconf/get_interfaces.py**
```python
from utils.restconf_helper import get_restconf
url = "/data/ietf-interfaces:interfaces"
data = get_restconf(url)

for intf in data['ietf-interfaces:interfaces']['interface']:
    print(f"{intf['name']} ➡️ Enabled: {intf['enabled']}, Type: {intf['type']}")
```

**utils/restconf_helper.py**
```python
import requests, yaml
from requests.auth import HTTPBasicAuth

with open("../inventory.yaml") as f:
    device = yaml.safe_load(f)['devices'][0]

BASE_URL = f"https://{device['ip']}:{device['port']}"
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

requests.packages.urllib3.disable_warnings()

def get_restconf(path):
    url = BASE_URL + path
    resp = requests.get(url, auth=HTTPBasicAuth(device['username'], device['password']),
                        headers=HEADERS, verify=False)
    return resp.json()
```

---

## 9. NETCONF in Python
**netconf/get_hostname.py**
```python
from utils.netconf_helper import netconf_connect
import xmltodict

m = netconf_connect()
filter = """
<filter>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname></hostname>
  </native>
</filter>
"""
response = m.get(filter)
data = xmltodict.parse(response.xml)
host = data['rpc-reply']['data']['native']['hostname']
print("Hostname:", host)
m.close_session()
```

**utils/netconf_helper.py**
```python
from ncclient import manager
import yaml

with open("../inventory.yaml") as f:
    device = yaml.safe_load(f)['devices'][0]

def netconf_connect():
    return manager.connect(
        host=device['ip'],
        port=device['netconf_port'],
        username=device['username'],
        password=device['password'],
        hostkey_verify=False,
        device_params={'name': 'csr'},
        look_for_keys=False,
        allow_agent=False
    )
```

---

## 10. Error Handling in API Automation
| Problem             | Cause                          | Solution                                  |
|---------------------|-------------------------------|--------------------------------------------|
| 401 Unauthorized    | Invalid credentials           | Check username/password                   |
| 403 Forbidden       | RESTCONF disabled             | Run `restconf` in config                  |
| Timeout/Refused     | Wrong port/firewall           | Check IP/port/firewall                    |
| Empty data          | Filter mismatch or bad path   | Double-check the filter structure         |

---

## 11. Real Use Cases
- Monitor interface status across 500 routers
- Push ACL changes using RESTCONF PATCH
- Validate BGP uptime across WAN via NETCONF
- Auto-discover device inventory
- Use structured API responses in Grafana dashboards

---

## 12. Best Practices
- Use YAML/JSON for parameters (inventory, config payload)
- Modularize code into helpers (restconf_helper, netconf_helper)
- Use `xmltodict` to convert NETCONF XML into Python dict
- Validate responses before accessing nested fields
- Always wrap API calls in `try/except`

---


