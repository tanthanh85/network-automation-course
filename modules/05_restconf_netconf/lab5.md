Python Basics for Network Automation: Module 5 Lab Guide
========================================================

Using APIs to Retrieve Data on Cisco Network Devices - Hands-on Exercises
-------------------------------------------------------------------------

\[Your Organization/Name\] September 01, 2025

Introduction
------------

Welcome to Module 5 of the Python Basics for Network Automation Lab Guide! In this module, you will gain hands-on experience with using APIs to retrieve data. We will use a single Cisco IOS XE router to demonstrate how to:

*   Discover the YANG models and capabilities supported by the device.
*   Retrieve CPU and Memory utilization using RESTCONF with JSON YANG payloads.
*   Retrieve GigabitEthernet1 input and output utilization using NETCONF with XML YANG payloads.

We will then use Python Flask to build a simple web-based monitoring tool that displays these specific metrics.

It is crucial that you replace the dummy values for your IOS XE router with its actual IP address, username, and password to make the code functional.

Lab Objectives:
---------------

*   Install the `requests`, `ncclient`, `xmltodict`, and `Flask` libraries.
*   Discover supported YANG models and capabilities via RESTCONF.
*   Discover supported YANG models and capabilities via NETCONF.
*   Understand how to manually derive RESTCONF URIs and construct NETCONF XML filters using public YANG models (e.g., from `yangcatalog.org`).
*   Learn to install and use Cisco Yangsuite to explore YANG models and generate API payloads, and compare its output with manual derivation.
*   Query Cisco IOS XE router's CPU and Memory utilization using RESTCONF with JSON YANG paths.
*   Query Cisco IOS XE router's GigabitEthernet1 input and output utilization using NETCONF with XML YANG filters.
*   Build a simple monitoring tool using Python Flask to display this data, demonstrating the use of both RESTCONF and NETCONF for different data points.

Prerequisites:
--------------

*   Completion of Module 1, Module 2, Module 3, and Module 4 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   An active internet connection.
*   Access to a Cisco IOS XE router with both RESTCONF and NETCONF enabled (e.g., Cisco DevNet Sandboxes). You will need its IP, username, and password.
    *   To enable RESTCONF on IOS XE:
    ```bash
    configure terminal
    restconf
    ip http authentication local
    ip http secure-server
    ! Ensure SSH is enabled as RESTCONF runs over HTTPS
    line vty 0 4
    login local
    transport input ssh
    end
    write memory
    ```
    *   To enable NETCONF on IOS XE:
    ```bash
    configure terminal
    netconf-yang
    ! Ensure SSH is enabled as NETCONF runs over SSH
    line vty 0 4
    login local
    transport input ssh
    end
    write memory
    ```
    *   Optional: Docker installed on your machine if you plan to install Yangsuite locally. Alternatively, access to a Cisco DevNet Sandbox with Yangsuite pre-installed. Note: Cisco Yangsuite can be accessed by reserving the "IOS XE on Cat8kv" sandbox lab on Cisco DevNet. Yangsuite will be accessible from `http://10.10.20.50:8480` within that sandbox environment.

Let's start exploring APIs and Flask!


Lab Setup: Project Structure
----------------------------

For this module, we will structure our project for better organization.


Navigate to your main network_automation_labs directory.
Create a new directory for this module's labs:
    ```bash
    mkdir module5_api_lab
    cd module5_api_lab
    ```
Inside module5_api_lab, create the following directories:
    ```bash
    mkdir templates
    mkdir static
    ```
Inside module5_api_lab, create the following empty Python files:
    ```bash
    touch __init__.py
    touch config.py
    touch iosxe_api_functions.py
    touch app.py
    ```
Inside the templates directory, create an empty HTML file:
    ```bash
    touch templates/index.html
    ```
Inside the static directory, create an empty CSS file:
    ```bash
    touch static/style.css
    ```
Your directory structure should now look like this:
```
network_automation_labs/
└── module5_api_lab/
    ├── __init__.py
    ├── config.py
    ├── iosxe_api_functions.py
    ├── app.py
    ├── templates/
    │   └── index.html
    └── static/
        └── style.css
```
### Task 0.1: Populate config.py

This file will store your IOS XE RESTCONF and NETCONF connection details.


Open config.py in your code editor.
Add the following Python code. REPLACE THE DUMMY VALUES WITH YOUR ACTUAL LAB IOS XE ROUTER DETAILS!

```python
# config.py

# --- IOS XE API Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
# This router should be reachable and have RESTCONF and NETCONF enabled.
# We use a single set of credentials for both APIs on the same device.
IOSXE_DEVICE_INFO = {
    "host": "YOUR_IOSXE_IP", # e.g., 10.10.20.40 (from Cisco DevNet Sandbox)
    "username": "YOUR_IOSXE_USERNAME", # e.g., developer
    "password": "YOUR_IOSXE_PASSWORD", # e.g., C!sco12345
    "restconf_port": 443, # Default HTTPS port for RESTCONF
    "netconf_port": 830, # Default NETCONF over SSH port
    "verify_ssl": False # Set to True in production for RESTCONF if you have proper CA certificates
}
```
Save `config.py`.

* * *

Lab 0: Discovering YANG Capabilities
------------------------------------

Objective: Learn how to programmatically discover the YANG models and capabilities supported by your Cisco IOS XE router via RESTCONF and NETCONF. This is crucial for understanding what data you can query.

### Task 0.1: Understanding Capability Discovery

Before you can query specific data from a device using YANG-based APIs, you need to know _what_ YANG models the device supports. This process is called "capability discovery."

*   RESTCONF Capability Discovery: RESTCONF exposes its capabilities at a specific well-known URI (`/restconf/data/ietf-restconf-monitoring:restconf-state/capabilities`). This URI points to the `ietf-restconf-monitoring` YANG model, which describes the RESTCONF server's capabilities, including the list of supported YANG modules.
*   NETCONF Capability Discovery: NETCONF capabilities are exchanged during the initial session establishment phase. When your `ncclient` Python script connects to a NETCONF device, the device advertises its supported capabilities, including the YANG models it implements. `ncclient` automatically captures these in the `manager.connected_capabilities` attribute.

### Task 0.2: Implement Capability Discovery Functions in `iosxe_api_functions.py`

The `iosxe_api_functions.py` file will contain the Python functions to perform these discovery operations.

Open `iosxe_api_functions.py` in your code editor. Add the following Python code. Ensure the `_make_restconf_get_request` and `_make_netconf_get_request` helper functions are also present, as they are used by the discovery functions.

```python
# iosxe_api_functions.py
import requests
import json
from ncclient import manager
from ncclient.operations import RPCError
import xml.etree.ElementTree as ET
import xmltodict # For easier XML to dict conversion
import logging

from config import IOSXE_DEVICE_INFO # Import device info from config.py

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- RESTCONF Base URLs ---
RESTCONF_BASE_URL = f"https://{IOSXE_DEVICE_INFO['host']}:{IOSXE_DEVICE_INFO['restconf_port']}/restconf/data"
# This is the well-known URI for RESTCONF capability discovery
RESTCONF_MONITORING_URL = f"https://{IOSXE_DEVICE_INFO['host']}:{IOSXE_DEVICE_INFO['restconf_port']}/restconf/data/ietf-restconf-monitoring:restconf-state/capabilities"


# --- Generic API Helper Functions (used by discovery and data retrieval) ---
def _make_restconf_get_request(path):
    """Internal helper to make a RESTCONF GET request."""
    full_url = f"{RESTCONF_BASE_URL}/{path}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    try:
        response = requests.get(
            full_url,
            headers=headers,
            auth=(IOSXE_DEVICE_INFO['username'], IOSXE_DEVICE_INFO['password']),
            verify=IOSXE_DEVICE_INFO['verify_ssl']
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"RESTCONF Request Error for {path}: {e}")
        return None
    except json.JSONDecodeError:
        logging.error(f"RESTCONF JSON Decode Error for {path} response.")
        return None
    except Exception as e:
        logging.error(f"RESTCONF Unexpected Error for {path}: {e}")
        return None

def _make_netconf_get_request(xml_filter):
    """Internal helper to make a NETCONF GET request."""
    host = IOSXE_DEVICE_INFO['host']
    username = IOSXE_DEVICE_INFO['username']
    password = IOSXE_DEVICE_INFO['password']
    port = IOSXE_DEVICE_INFO['netconf_port']

    try:
        logging.info(f"Connecting to {host}:{port} via NETCONF...")
        with manager.connect(host=host,
                             port=port,
                             username=username,
                             password=password,
                             hostkey_verify=False, # Set to True in production with proper host keys
                             device_params={'name': 'iosxe'},
                             allow_agent=False,
                             look_for_keys=False) as m:
            logging.info(f"Successfully connected to {host} via NETCONF. Sending GET request.")
            
            netconf_reply = m.get(filter=('subtree', xml_filter))
            raw_xml = netconf_reply.xml
            parsed_data = xmltodict.parse(raw_xml)
            
            return parsed_data

    except RPCError as e:
        logging.error(f"NETCONF RPC Error for {host}: {e.info}")
        logging.error(f"Error message: {e.message}")
        return None
    except Exception as e:
        logging.error(f"NETCONF An unexpected error occurred connecting or fetching data from {host}: {e}")
        return None


# --- Capability Discovery Functions ---

def discover_restconf_capabilities():
    """Discovers and returns supported YANG modules via RESTCONF."""
    headers = {
        "Accept": "application/yang-data+json"
    }
    try:
        response = requests.get(
            RESTCONF_MONITORING_URL,
            headers=headers,
            auth=(IOSXE_DEVICE_INFO['username'], IOSXE_DEVICE_INFO['password']),
            verify=IOSXE_DEVICE_INFO['verify_ssl']
        )
        response.raise_for_status()
        data = response.json()
        
        modules = []
        # The capabilities are usually under 'ietf-restconf-monitoring:capabilities'
        # and then 'capability' is a list of URIs
        capabilities_list = data.get('ietf-restconf-monitoring:capabilities', {}).get('capability', [])
        for cap_uri in capabilities_list:
            # Extract module name from URI (e.g., urn:ietf:params:xml:ns:yang:ietf-interfaces?module=ietf-interfaces&revision=2018-02-20)
            if 'module=' in cap_uri:
                module_name = cap_uri.split('module=')[1].split('&')[0]
                modules.append(module_name)
        return sorted(list(set(modules))) # Return unique sorted module names
    except Exception as e:
        logging.error(f"Error discovering RESTCONF capabilities: {e}")
        return []

def discover_netconf_capabilities():
    """Discovers and returns supported YANG modules via NETCONF."""
    host = IOSXE_DEVICE_INFO['host']
    username = IOSXE_DEVICE_INFO['username']
    password = IOSXE_DEVICE_INFO['password']
    port = IOSXE_DEVICE_INFO['netconf_port']

    try:
        logging.info(f"Connecting to {host}:{port} for NETCONF capabilities discovery...")
        with manager.connect(host=host,
                             port=port,
                             username=username,
                             password=password,
                             hostkey_verify=False,
                             device_params={'name': 'iosxe'},
                             allow_agent=False,
                             look_for_keys=False) as m:
            logging.info(f"Successfully connected to {host} for NETCONF capabilities. Retrieving capabilities.")
            
            modules = []
            # ncclient's manager object holds the connected capabilities
            for capability in m.connected_capabilities:
                # Capabilities are typically in the format:
                # urn:ietf:params:xml:ns:netconf:base:1.0
                # urn:ietf:params:xml:ns:yang:ietf-interfaces?module=ietf-interfaces&revision=2018-02-20
                if 'module=' in capability:
                    module_name = capability.split('module=')[1].split('&')[0]
                    modules.append(module_name)
            return sorted(list(set(modules))) # Return unique sorted module names
    except Exception as e:
        logging.error(f"Error discovering NETCONF capabilities: {e}")
        return []


# --- Data Retrieval Functions (for CPU, Memory, and GigabitEthernet1 utilization) ---
# (These functions will be fully detailed in the next section, but are included here for completeness
# if you are copying the entire file at once)

def get_cpu_utilization_restconf():
    """Queries and returns CPU utilization from IOS XE via RESTCONF."""
    path = "Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"
    data = _make_restconf_get_request(path)
    if data:
        try:
            cpu_total = data.get('Cisco-IOS-XE-process-cpu-oper:cpu-usage', {}).get('cpu-utilization', {}).get('five-seconds')
            return int(cpu_total) if cpu_total is not None else "N/A"
        except (TypeError, ValueError) as e:
            logging.error(f"Error parsing RESTCONF CPU data: {e}")
            return "N/A"
    return "N/A"

def get_memory_utilization_restconf():
    """Queries and returns memory utilization from IOS XE via RESTCONF."""
    path = "Cisco-IOS-XE-memory-oper:memory-statistics"
    data = _make_restconf_get_request(path)
    if data:
        try:
            mem_stats = data.get('Cisco-IOS-XE-memory-oper:memory-statistics', {}).get('memory-statistic', [{}])
            if mem_stats and isinstance(mem_stats, list) and len(mem_stats) > 0:
                mem_stats = mem_stats[0]
            
            used = mem_stats.get('used-memory')
            total = mem_stats.get('total-memory')
            return int(used) if used is not None else "N/A", int(total) if total is not None else "N/A"
        except (TypeError, ValueError, IndexError) as e:
            logging.error(f"Error parsing RESTCONF Memory data: {e}")
            return "N/A", "N/A"
    return "N/A", "N/A"

def get_gigabitethernet1_utilization_netconf():
    """Queries and returns GigabitEthernet1 input/output utilization via NETCONF."""
    interface_filter = """
    <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>GigabitEthernet1</name>
            <statistics>
                <in-octets/>
                <out-octets/>
                <in-unicast-pkts/>
                <out-unicast-pkts/>
            </statistics>
        </interface>
    </interfaces-state>
    """
    data = _make_netconf_get_request(interface_filter)
    stats = {
        "in_octets": "N/A",
        "out_octets": "N/A",
        "in_pkts": "N/A",
        "out_pkts": "N/A"
    }
    if data:
        try:
            iface_data = data.get('rpc-reply', {}).get('data', {}).get('interfaces-state', {}).get('interface', {})
            if isinstance(iface_data, list):
                iface_data = iface_data[0] if iface_data else {}

            statistics = iface_data.get('statistics', {})
            
            stats["in_octets"] = statistics.get('in-octets', "N/A")
            stats["out_octets"] = statistics.get('out-octets', "N/A")
            stats["in_pkts"] = statistics.get('in-unicast-pkts', "N/A")
            stats["out_pkts"] = statistics.get('out-unicast-pkts', "N/A")
            
        except (TypeError, ValueError, IndexError) as e:
            logging.error(f"Error parsing NETCONF GigabitEthernet1 stats: {e}")
    return stats


# Standalone test for functions (only runs when this file is executed directly)
if __name__ == '__main__':
    print("--- Testing iosxe_api_functions.py (Capabilities, RESTCONF & NETCONF) ---")
    print("Note: This will attempt to connect to the IOS XE router defined in config.py.")

    print("\n--- Discovering Capabilities ---")
    print("RESTCONF Supported Modules:")
    restconf_caps = discover_restconf_capabilities()
    for module in restconf_caps:
        print(f"  - {module}")
    
    print("\nNETCONF Supported Modules:")
    netconf_caps = discover_netconf_capabilities()
    for module in netconf_caps:
        print(f"  - {module}")

    print("\n--- RESTCONF Data (CPU & Memory) ---")
    # Test CPU
    cpu_rc = get_cpu_utilization_restconf()
    print(f"RESTCONF CPU Utilization (5-sec): {cpu_rc}%")

    # Test Memory
    mem_used_rc, mem_total_rc = get_memory_utilization_restconf()
    print(f"RESTCONF Memory: {mem_used_rc} used / {mem_total_rc} total bytes")

    print("\n--- NETCONF Data (GigabitEthernet1 Utilization) ---")
    # Test GigabitEthernet1 Utilization
    gigabit_stats_nc = get_gigabitethernet1_utilization_netconf()
    print(f"NETCONF GigabitEthernet1 In-Octets: {gigabit_stats_nc['in_octets']}")
    print(f"NETCONF GigabitEthernet1 Out-Octets: {gigabit_stats_nc['out_octets']}")
    print(f"NETCONF GigabitEthernet1 In-Packets: {gigabit_stats_nc['in_pkts']}")
    print(f"NETCONF GigabitEthernet1 Out-Packets: {gigabit_stats_nc['out_pkts']}")

    print("\n--- Test Complete ---")
```
Save `iosxe_api_functions.py`.

### Task 0.4: Install Libraries

Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory). Navigate into your `module5_api_lab` directory:
    ```bash
    cd module5_api_lab
    ```
Install the necessary libraries:
    ```bash
    pip install requests ncclient xmltodict flask
    ```
### Task 0.5: Run Standalone Script to Discover Capabilities

Now, execute the `iosxe_api_functions.py` script. Its `if __name__ == '__main__':` block is configured to first run the capability discovery functions and then the data retrieval functions.
    ```bash
    python iosxe_api_functions.py
    ```
Expected Output (console - partial, focusing on capabilities):
    ```console
    --- Testing iosxe_api_functions.py (Capabilities, RESTCONF & NETCONF) ---
    Note: This will attempt to connect to the IOS XE router defined in config.py.

    --- Discovering Capabilities ---
    Connecting to YOUR_IOSXE_IP:443 for RESTCONF capabilities discovery...
    RESTCONF Supported Modules:
    - Cisco-IOS-XE-acl
    - Cisco-IOS-XE-aaa
    - Cisco-IOS-XE-process-cpu-oper  # Look for this one!
    - Cisco-IOS-XE-memory-oper     # Look for this one!
    ... (many more modules) ...
    - ietf-interfaces              # Look for this one!
    - ietf-restconf-monitoring
    ...

    Connecting to YOUR_IOSXE_IP:830 for NETCONF capabilities discovery...
    Successfully connected to YOUR_IOSXE_IP for NETCONF capabilities. Retrieving capabilities.
    NETCONF Supported Modules:
    - Cisco-IOS-XE-acl
    - Cisco-IOS-XE-aaa
    - Cisco-IOS-XE-process-cpu-oper  # Look for this one!
    - Cisco-IOS-XE-memory-oper     # Look for this one!
    ... (many more modules) ...
    - ietf-interfaces              # Look for this one!
    - ietf-netconf
    ...
    ```
_Note: The list of modules will be extensive and vary slightly based on your IOS XE version. The important part is to confirm that modules like `Cisco-IOS-XE-process-cpu-oper`, `Cisco-IOS-XE-memory-oper`, and `ietf-interfaces` are present, as these are used in the data retrieval tasks._

* * *

Understanding YANG, RESTCONF URIs, and NETCONF XML Filters
----------------------------------------------------------

Before diving into the Python code for data retrieval, it's crucial to understand how we determine the specific data we want to retrieve using YANG, RESTCONF, and NETCONF.

YANG (Yet Another Next Generation): YANG is a data modeling language used to define the configuration and state data of network devices. Think of it as a schema or blueprint that precisely describes what data is available on a device and how it's structured. Network devices expose their capabilities and data through YANG models.

### Methodology: From YANG Model to API Payload

The process of building API calls from YANG models involves a few key steps:

#### Step 1: Find the Relevant YANG Model

*   Public Repositories: The most common place to find standardized and vendor-specific YANG models is public repositories.
    *   `yangcatalog.org`: This is an excellent resource for finding, browsing, and downloading YANG modules from various vendors (including Cisco) and standards bodies (IETF, IEEE).
        *   How to use `yangcatalog.org`:
            1.  Go to `https://www.yangcatalog.org/`.
            2.  Use the search bar to look for keywords related to the data you need (e.g., "cpu", "memory", "interfaces").
            3.  Filter by `Organization` (e.g., `Cisco`, `IETF`) or `Module Name`.
            4.  Once you find a module (e.g., `Cisco-IOS-XE-process-cpu-oper`), click on it to view its details, including its namespace and a tree representation. The tree view is particularly helpful for visualizing the data hierarchy.
*   Vendor Documentation: Cisco DevNet provides documentation and bundles of YANG models specific to IOS XE versions.

#### Step 2: Understand the YANG Tree Structure

Once you have identified a YANG model, you need to understand its structure:

*   Module Name: The name of the YANG file (e.g., `Cisco-IOS-XE-process-cpu-oper`).
*   Namespace: A unique URI associated with the module, found at the top of the YANG file (e.g., `namespace "http://cisco.com/ns/yang/Cisco-IOS-XE-process-cpu-oper";`). This is critical for NETCONF.
*   Containers: Logical groupings of data (like folders). Represented by `container` keyword in YANG.
*   Lists: Collections of similar items (like a table). Represented by `list` keyword. Lists have `key` elements that uniquely identify each item.
*   Leaves: Actual data points (like files). Represented by `leaf` keyword.
*   `config true/false`: Indicates if the data is configurable (`true`) or operational state data (`false`). For this lab, we are interested in operational state data.

#### Step 3: Constructing RESTCONF URIs (Manual Derivation)

RESTCONF uses HTTP methods (GET, POST, PUT, DELETE) over HTTPS to interact with YANG-modeled data. The structure of a RESTCONF URI directly maps to the YANG data model.

General RESTCONF URI Structure for Data Retrieval: `https://:/restconf/data/:`

*   The `:` prefix is used to disambiguate elements if multiple modules define elements with the same name. It's often used for the first element after `/restconf/data/`.
*   Subsequent elements are separated by `/`.
*   If you're querying a specific item in a list, you'd use `list-name=key-value`.

Examples for this Lab (Manual Derivation):

*   CPU Utilization:
    
    *   YANG Model (from `yangcatalog.org`): `Cisco-IOS-XE-process-cpu-oper.yang`
    *   YANG Path (from tree view): `cpu-usage/cpu-utilization/five-seconds`
    *   Module Name: `Cisco-IOS-XE-process-cpu-oper`
    *   RESTCONF URI Path: `Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization`
        *   _Explanation:_ We request the `cpu-utilization` container within the `cpu-usage` container from the `Cisco-IOS-XE-process-cpu-oper` module. The RESTCONF server will return the entire `cpu-utilization` data (including 1-min, 5-min, etc.), from which our Python code will specifically extract `five-seconds`.
*   Memory Utilization:
    
    *   YANG Model (from `yangcatalog.org`): `Cisco-IOS-XE-memory-oper.yang`
    *   YANG Path (from tree view): `memory-statistics/memory-statistic/used-memory` and `memory-statistics/memory-statistic/total-memory`
    *   Module Name: `Cisco-IOS-XE-memory-oper`
    *   RESTCONF URI Path: `Cisco-IOS-XE-memory-oper:memory-statistics`
        *   _Explanation:_ We request the `memory-statistics` container. It contains a list of `memory-statistic` entries (one per memory pool). We'll typically take the first entry to represent overall system memory.

#### Step 4: Constructing NETCONF XML Filters (Manual Derivation)

NETCONF uses XML-based RPCs (Remote Procedure Calls) to interact with devices. To retrieve specific data, you construct an XML filter that mirrors the YANG data model you want.

General NETCONF XML Filter Structure:
    ```xml
    <top-level-container xmlns="<YANG_NAMESPACE_URI>">
        <nested-container>
            <list-entry>
                <key-leaf>value</key-leaf> <!-- To filter a specific list item -->
                <data-leaf/> <!-- Request this specific leaf -->
            </list-entry>
        </nested-container>
    </top-level-container>
    ```
Key points for XML filters:

*   Namespaces (`xmlns`): Each top-level element (and sometimes nested ones) must specify its YANG namespace URI. This URI is defined within the YANG model itself (e.g., `namespace "http://cisco.com/ns/yang/Cisco-IOS-XE-process-cpu-oper";`).
*   Empty Tags (``): To request a specific data leaf or container, you include an empty XML tag for that element in your filter. This tells NETCONF to return the value of that leaf/container.
*   Filtering Lists: If you want data for a specific item in a YANG list (e.g., a particular interface), you include the list's key(s) as an XML element with its value.

Examples for this Lab (Manual Derivation):

*   GigabitEthernet1 Utilization (Input/Output Octets/Packets):
    *   YANG Model (from `yangcatalog.org`): `ietf-interfaces.yang` (standard IETF model)
    *   YANG Path (from tree view): `interfaces-state/interface[name='GigabitEthernet1']/statistics`
    *   Namespace: `urn:ietf:params:xml:ns:yang:ietf-interfaces` (found in the `ietf-interfaces.yang` file)
    *   XML Filter:
    ```xml
    <top-level-container xmlns="<YANG_NAMESPACE_URI>">
    <nested-container>
        <list-entry>
            <key-leaf>value</key-leaf> <!-- To filter a specific list item -->
            <data-leaf/> <!-- Request this specific leaf -->
        </list-entry>
    </nested-container>
    </top-level-container>
    ```
Key points for XML filters:

*   Namespaces (`xmlns`): Each top-level element (and sometimes nested ones) must specify its YANG namespace URI. This URI is defined within the YANG model itself (e.g., `namespace "http://cisco.com/ns/yang/Cisco-IOS-XE-process-cpu-oper";`).
*   Empty Tags (``): To request a specific data leaf or container, you include an empty XML tag for that element in your filter. This tells NETCONF to return the value of that leaf/container.
*   Filtering Lists: If you want data for a specific item in a YANG list (e.g., a particular interface), you include the list's key(s) as an XML element with its value.

Examples for this Lab (Manual Derivation):

*   GigabitEthernet1 Utilization (Input/Output Octets/Packets):
    *   YANG Model (from `yangcatalog.org`): `ietf-interfaces.yang` (standard IETF model)
    *   YANG Path (from tree view): `interfaces-state/interface[name='GigabitEthernet1']/statistics`
    *   Namespace: `urn:ietf:params:xml:ns:yang:ietf-interfaces` (found in the `ietf-interfaces.yang` file)
    *   XML Filter:
    ```xml
    <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
        <name>GigabitEthernet1</name>
        <statistics>
            <in-octets/>
            <out-octets/>
            <in-unicast-pkts/>
            <out-unicast-pkts/>
        </statistics>
    </interface>
    </interfaces-state>
    ```
    *   _Explanation:_ We specify the `interfaces-state` container with its namespace. Inside it, we filter for the `interface` list entry where the `name` key is `GigabitEthernet1`. Then, within that specific interface, we request the `statistics` container and its desired leaves (`in-octets`, `out-octets`, etc.) by providing empty tags.

### Using Cisco Yangsuite to Explore YANG Models and Generate Payloads

Cisco Yangsuite is a powerful web-based tool that can significantly simplify the process of exploring YANG models and constructing RESTCONF URIs and NETCONF XML/JSON payloads. It's an excellent way to validate your manual derivations.

#### Yangsuite Installation (Optional - Choose One Method):

1.  Cisco DevNet Sandbox: The easiest way to access Yangsuite is often through a Cisco DevNet Sandbox environment (e.g., "IOS XE on Cat8kv"). Note: Cisco Yangsuite can be accessed by reserving the "IOS XE on Cat8kv" sandbox lab on Cisco DevNet. Yangsuite will be accessible from `http://10.10.20.50:8480` within that sandbox environment.
2.  Local Docker Installation (Recommended for Local Setup):
    *   Prerequisite: Ensure Docker Desktop (Windows/macOS) or Docker Engine (Linux) is installed and running on your machine.
    *   Steps:
        *   Open your terminal/command prompt.
        *   Pull the Yangsuite Docker image:
        ```bash
        docker pull cisco/yangsuite
        ```
        *   Run the container, mapping port 8443 (HTTPS) to a local port (e.g., 8443):
        ```bash
        docker run -p 8443:8443 -d cisco/yangsuite
        ```
        *   *   Wait a minute or two for the container to start.
        *   Open your web browser and navigate to `https://localhost:8443`. You might encounter a certificate warning, which you can safely bypass for a local lab environment.
        *   Log in with default credentials: `admin` / `admin`.
    *   Note: For more advanced installations (e.g., persistent data, specific networks), refer to the official Cisco Yangsuite documentation.

#### How to Use Yangsuite to Generate Payloads:

Once Yangsuite is running and you're logged in:

1.  Add a Device:
    
    *   Navigate to Devices -> Add Device.
    *   Fill in your IOS XE router's details (IP, username, password, NETCONF/RESTCONF ports).
    *   Crucially, under Capabilities, click "Fetch" for both NETCONF and RESTCONF. This will connect to your device and pull all the YANG models it supports.
    *   Save the device.
2.  Explore YANG Models:
    
    *   Go to YANG Files -> YANG Explorer.
    *   Select your newly added device from the dropdown.
    *   You'll see a tree-like structure of all the YANG models supported by your device. Use the search bar to find specific models (e.g., `Cisco-IOS-XE-process-cpu-oper`, `ietf-interfaces`).
3.  Generate RESTCONF Payloads using Yangsuite:
    
    *   For CPU Utilization:
        
        1.  In YANG Explorer, find and expand `Cisco-IOS-XE-process-cpu-oper`.
        2.  Expand `cpu-usage`.
        3.  Select `cpu-utilization`.
        4.  In the right-hand panel, click the RESTCONF tab. Yangsuite will display the URI (e.g., `/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization`). This should match your manual derivation.
        5.  You can also try the "GET" button to execute the call directly from Yangsuite and see the JSON response.
    *   For Memory Utilization:
        
        1.  In YANG Explorer, find and expand `Cisco-IOS-XE-memory-oper`.
        2.  Select `memory-statistics`.
        3.  In the right-hand panel, click the RESTCONF tab. Yangsuite will display the URI (e.g., `/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics`). This should match your manual derivation.
4.  Generate NETCONF XML Filters using Yangsuite:
    
    *   For GigabitEthernet1 Utilization:
        1.  In YANG Explorer, find and expand `ietf-interfaces`.
        2.  Expand `interfaces-state`.
        3.  Expand `interface`.
        4.  This is a list. To filter for `GigabitEthernet1`, click the `+` next to the `name` leaf under `interface`. A pop-up will appear. Enter `GigabitEthernet1` as the value and click "Add".
        5.  Now, expand `statistics` under the `interface` you just filtered.
        6.  For each desired leaf (`in-octets`, `out-octets`, `in-unicast-pkts`, `out-unicast-pkts`), click the `+` next to it. This marks them for inclusion in the filter.
        7.  In the right-hand panel, click the NETCONF tab. Yangsuite will display the XML filter (e.g., the `...` block) that you can copy and use. This should match your manual derivation.
        8.  You can also try the "GET" button to execute the call directly from Yangsuite and see the XML response.

Yangsuite is an invaluable tool for understanding the YANG data models and quickly generating the correct API calls without manually constructing complex URIs or XML filters. It's highly recommended to use it to experiment and validate your understanding.

* * *

### Task 0.3: Populate iosxe\_api\_functions.py

This file will contain reusable functions to query data from the IOS XE router using both RESTCONF and NETCONF.

Open `iosxe_api_functions.py` in your code editor. Add the following Python code:
```python
# iosxe_api_functions.py
import requests
import json
from ncclient import manager
from ncclient.operations import RPCError
import xml.etree.ElementTree as ET
import xmltodict # For easier XML to dict conversion
import logging

from config import IOSXE_DEVICE_INFO # Import device info from config.py

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- RESTCONF Base URLs ---
RESTCONF_BASE_URL = f"https://{IOSXE_DEVICE_INFO['host']}:{IOSXE_DEVICE_INFO['restconf_port']}/restconf/data"
# This is the well-known URI for RESTCONF capability discovery
RESTCONF_MONITORING_URL = f"https://{IOSXE_DEVICE_INFO['host']}:{IOSXE_DEVICE_INFO['restconf_port']}/restconf/data/ietf-restconf-monitoring:restconf-state/capabilities"


# --- Generic API Helper Functions (used by discovery and data retrieval) ---
def _make_restconf_get_request(path):
    """Internal helper to make a RESTCONF GET request."""
    full_url = f"{RESTCONF_BASE_URL}/{path}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    try:
        response = requests.get(
            full_url,
            headers=headers,
            auth=(IOSXE_DEVICE_INFO['username'], IOSXE_DEVICE_INFO['password']),
            verify=IOSXE_DEVICE_INFO['verify_ssl']
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"RESTCONF Request Error for {path}: {e}")
        return None
    except json.JSONDecodeError:
        logging.error(f"RESTCONF JSON Decode Error for {path} response.")
        return None
    except Exception as e:
        logging.error(f"RESTCONF Unexpected Error for {path}: {e}")
        return None

def _make_netconf_get_request(xml_filter):
    """Internal helper to make a NETCONF GET request."""
    host = IOSXE_DEVICE_INFO['host']
    username = IOSXE_DEVICE_INFO['username']
    password = IOSXE_DEVICE_INFO['password']
    port = IOSXE_DEVICE_INFO['netconf_port']

    try:
        logging.info(f"Connecting to {host}:{port} via NETCONF...")
        with manager.connect(host=host,
                             port=port,
                             username=username,
                             password=password,
                             hostkey_verify=False, # Set to True in production with proper host keys
                             device_params={'name': 'iosxe'},
                             allow_agent=False,
                             look_for_keys=False) as m:
            logging.info(f"Successfully connected to {host} via NETCONF. Sending GET request.")
            
            netconf_reply = m.get(filter=('subtree', xml_filter))
            raw_xml = netconf_reply.xml
            parsed_data = xmltodict.parse(raw_xml)
            
            return parsed_data

    except RPCError as e:
        logging.error(f"NETCONF RPC Error for {host}: {e.info}")
        logging.error(f"Error message: {e.message}")
        return None
    except Exception as e:
        logging.error(f"NETCONF An unexpected error occurred connecting or fetching data from {host}: {e}")
        return None


# --- Capability Discovery Functions ---

def discover_restconf_capabilities():
    """Discovers and returns supported YANG modules via RESTCONF."""
    headers = {
        "Accept": "application/yang-data+json"
    }
    try:
        response = requests.get(
            RESTCONF_MONITORING_URL,
            headers=headers,
            auth=(IOSXE_DEVICE_INFO['username'], IOSXE_DEVICE_INFO['password']),
            verify=IOSXE_DEVICE_INFO['verify_ssl']
        )
        response.raise_for_status()
        data = response.json()
        
        modules = []
        # The capabilities are usually under 'ietf-restconf-monitoring:capabilities'
        # and then 'capability' is a list of URIs
        capabilities_list = data.get('ietf-restconf-monitoring:capabilities', {}).get('capability', [])
        for cap_uri in capabilities_list:
            # Extract module name from URI (e.g., urn:ietf:params:xml:ns:yang:ietf-interfaces?module=ietf-interfaces&revision=2018-02-20)
            if 'module=' in cap_uri:
                module_name = cap_uri.split('module=')[1].split('&')[0]
                modules.append(module_name)
        return sorted(list(set(modules))) # Return unique sorted module names
    except Exception as e:
        logging.error(f"Error discovering RESTCONF capabilities: {e}")
        return []

def discover_netconf_capabilities():
    """Discovers and returns supported YANG modules via NETCONF."""
    host = IOSXE_DEVICE_INFO['host']
    username = IOSXE_DEVICE_INFO['username']
    password = IOSXE_DEVICE_INFO['password']
    port = IOSXE_DEVICE_INFO['netconf_port']

    try:
        logging.info(f"Connecting to {host}:{port} for NETCONF capabilities discovery...")
        with manager.connect(host=host,
                             port=port,
                             username=username,
                             password=password,
                             hostkey_verify=False,
                             device_params={'name': 'iosxe'},
                             allow_agent=False,
                             look_for_keys=False) as m:
            logging.info(f"Successfully connected to {host} for NETCONF capabilities. Retrieving capabilities.")
            
            modules = []
            # ncclient's manager object holds the connected capabilities
            for capability in m.connected_capabilities:
                # Capabilities are typically in the format:
                # urn:ietf:params:xml:ns:netconf:base:1.0
                # urn:ietf:params:xml:ns:yang:ietf-interfaces?module=ietf-interfaces&revision=2018-02-20
                if 'module=' in capability:
                    module_name = capability.split('module=')[1].split('&')[0]
                    modules.append(module_name)
            return sorted(list(set(modules))) # Return unique sorted module names
    except Exception as e:
        logging.error(f"Error discovering NETCONF capabilities: {e}")
        return []


# --- Data Retrieval Functions (for CPU, Memory, and GigabitEthernet1 utilization) ---

def get_cpu_utilization_restconf():
    """Queries and returns CPU utilization from IOS XE via RESTCONF."""
    # YANG Path: Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization
    # Module: Cisco-IOS-XE-process-cpu-oper
    path = "Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"
    data = _make_restconf_get_request(path)
    if data:
        try:
            cpu_total = data.get('Cisco-IOS-XE-process-cpu-oper:cpu-usage', {}).get('cpu-utilization', {}).get('five-seconds')
            return int(cpu_total) if cpu_total is not None else "N/A"
        except (TypeError, ValueError) as e:
            logging.error(f"Error parsing RESTCONF CPU data: {e}")
            return "N/A"
    return "N/A"

def get_memory_utilization_restconf():
    """Queries and returns memory utilization from IOS XE via RESTCONF."""
    # YANG Path: Cisco-IOS-XE-memory-oper:memory-statistics
    # Module: Cisco-IOS-XE-memory-oper
    path = "Cisco-IOS-XE-memory-oper:memory-statistics"
    data = _make_restconf_get_request(path)
    if data:
        try:
            mem_stats = data.get('Cisco-IOS-XE-memory-oper:memory-statistics', {}).get('memory-statistic', [{}])
            if mem_stats and isinstance(mem_stats, list) and len(mem_stats) > 0:
                mem_stats = mem_stats[0]
            
            used = mem_stats.get('used-memory')
            total = mem_stats.get('total-memory')
            return int(used) if used is not None else "N/A", int(total) if total is not None else "N/A"
        except (TypeError, ValueError, IndexError) as e:
            logging.error(f"Error parsing RESTCONF Memory data: {e}")
            return "N/A", "N/A"
    return "N/A", "N/A"

def get_gigabitethernet1_utilization_netconf():
    """Queries and returns GigabitEthernet1 input/output utilization via NETCONF."""
    # YANG Path: /interfaces-state/interface[name='GigabitEthernet1']/statistics
    # Module: ietf-interfaces
    # Namespace: urn:ietf:params:xml:ns:yang:ietf-interfaces
    interface_filter = """
    <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>GigabitEthernet1</name>
            <statistics>
                <in-octets/>
                <out-octets/>
                <in-unicast-pkts/>
                <out-unicast-pkts/>
            </statistics>
        </interface>
    </interfaces-state>
    """
    data = _make_netconf_get_request(interface_filter)
    stats = {
        "in_octets": "N/A",
        "out_octets": "N/A",
        "in_pkts": "N/A",
        "out_pkts": "N/A"
    }
    if data:
        try:
            iface_data = data.get('rpc-reply', {}).get('data', {}).get('interfaces-state', {}).get('interface', {})
            if isinstance(iface_data, list):
                iface_data = iface_data[0] if iface_data else {}

            statistics = iface_data.get('statistics', {})
            
            stats["in_octets"] = statistics.get('in-octets', "N/A")
            stats["out_octets"] = statistics.get('out-octets', "N/A")
            stats["in_pkts"] = statistics.get('in-unicast-pkts', "N/A")
            stats["out_pkts"] = statistics.get('out-unicast-pkts', "N/A")
            
        except (TypeError, ValueError, IndexError) as e:
            logging.error(f"Error parsing NETCONF GigabitEthernet1 stats: {e}")
    return stats


# Standalone test for functions (only runs when this file is executed directly)
if __name__ == '__main__':
    print("--- Testing iosxe_api_functions.py (Capabilities, RESTCONF & NETCONF) ---")
    print("Note: This will attempt to connect to the IOS XE router defined in config.py.")

    print("\n--- Discovering Capabilities ---")
    print("RESTCONF Supported Modules:")
    restconf_caps = discover_restconf_capabilities()
    for module in restconf_caps:
        print(f"  - {module}")
    
    print("\nNETCONF Supported Modules:")
    netconf_caps = discover_netconf_capabilities()
    for module in netconf_caps:
        print(f"  - {module}")

    print("\n--- RESTCONF Data (CPU & Memory) ---")
    # Test CPU
    cpu_rc = get_cpu_utilization_restconf()
    print(f"RESTCONF CPU Utilization (5-sec): {cpu_rc}%")

    # Test Memory
    mem_used_rc, mem_total_rc = get_memory_utilization_restconf()
    print(f"RESTCONF Memory: {mem_used_rc} used / {mem_total_rc} total bytes")

    print("\n--- NETCONF Data (GigabitEthernet1 Utilization) ---")
    # Test GigabitEthernet1 Utilization
    gigabit_stats_nc = get_gigabitethernet1_utilization_netconf()
    print(f"NETCONF GigabitEthernet1 In-Octets: {gigabit_stats_nc['in_octets']}")
    print(f"NETCONF GigabitEthernet1 Out-Octets: {gigabit_stats_nc['out_octets']}")
    print(f"NETCONF GigabitEthernet1 In-Packets: {gigabit_stats_nc['in_pkts']}")
    print(f"NETCONF GigabitEthernet1 Out-Packets: {gigabit_stats_nc['out_pkts']}")

    print("\n--- Test Complete ---")
```

Save `iosxe_api_functions.py`.

### Task 0.4: Populate templates/index.html

This file defines the HTML structure for your web dashboard, now displaying specific metrics from RESTCONF and NETCONF.

Open `templates/index.html` in your code editor. Add the following HTML code:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IOS XE Router Monitor (RESTCONF & NETCONF)</title>
    <meta http-equiv="refresh" content="5"> <!-- Auto-refresh page every 5 seconds -->
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <h1>Cisco IOS XE Router Monitor</h1>
        <p>Last updated: {{ current_time }}</p>
        
        <div class="api-section">
            <h2>RESTCONF Data (CPU & Memory)</h2>
            <div class="metric">
                <strong>CPU Utilization (5-sec):</strong> <span id="cpu_util_rc">{{ cpu_util_rc }}%</span>
                {% if cpu_util_rc != 'N/A' and cpu_util_rc|int > 75 %} <span class="alert">(HIGH)</span> {% endif %}
            </div>
            
            <div class="metric">
                <strong>Memory Used:</strong> <span id="memory_used_rc">{{ memory_used_rc }}</span> bytes
                <strong>Total Memory:</strong> <span id="memory_total_rc">{{ memory_total_rc }}</span> bytes
            </div>
        </div>

        <hr> <!-- Separator between API types -->

        <div class="api-section">
            <h2>NETCONF Data (GigabitEthernet1 Utilization)</h2>
            <div class="metric">
                <strong>GigabitEthernet1 In-Octets:</strong> <span id="gig1_in_octets">{{ gig1_in_octets }}</span>
            </div>
            <div class="metric">
                <strong>GigabitEthernet1 Out-Octets:</strong> <span id="gig1_out_octets">{{ gig1_out_octets }}</span>
            </div>
            <div class="metric">
                <strong>GigabitEthernet1 In-Packets:</strong> <span id="gig1_in_pkts">{{ gig1_in_pkts }}</span>
            </div>
            <div class="metric">
                <strong>GigabitEthernet1 Out-Packets:</strong> <span id="gig1_out_pkts">{{ gig1_out_pkts }}</span>
            </div>
        </div>
    </div>
</body>
</html>
```
Save `templates/index.html`.

### Task 0.5: Populate static/style.css

This file defines the styling for your web dashboard.

Open `static/style.css` in your code editor. Add the following CSS code:
```css
body { 
    font-family: Arial, sans-serif; 
    margin: 20px; 
    background-color: #f4f4f4; 
    color: #333; 
}
.container { 
    background-color: #fff; 
    padding: 20px; 
    border-radius: 8px; 
    box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
    max-width: 900px; /* Slightly wider to accommodate both sections */
    margin: auto; 
}
h1 { 
    color: #0056b3; 
    text-align: center;
}
h2 {
    color: #007bff;
    border-bottom: 2px solid #007bff;
    padding-bottom: 5px;
    margin-top: 20px;
}
h3 {
    color: #007bff;
    margin-top: 15px;
}
.api-section {
    margin-bottom: 30px;
    padding: 15px;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    background-color: #fdfdfd;
}
.metric { 
    margin-bottom: 10px; 
    padding: 10px; 
    border: 1px solid #ddd; 
    border-radius: 4px; 
}
.metric strong { 
    color: #007bff; 
}
.alert { 
    color: red; 
    font-weight: bold; 
}
table { /* Removed table, but keeping styles just in case for future use */
    width: 100%; 
    border-collapse: collapse; 
    margin-top: 15px; 
}
th, td { 
    border: 1px solid #ddd; 
    padding: 8px; 
    text-align: left; 
}
th { 
    background-color: #f2f2f2; 
}
.status-up { 
    color: green; 
    font-weight: bold; 
}
.status-down { 
    color: red; 
    font-weight: bold; 
}
hr {
    border: 0;
    height: 1px;
    background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));
    margin: 40px 0;
}
```
Save `static/style.css`.

### Task 0.6: Populate app.py

This is the main Flask application file that will bring everything together.

Open `app.py` in your code editor. Add the following Python code:
```python
# app.py
from flask import Flask, render_template
import time
from .iosxe_api_functions import (
    get_cpu_utilization_restconf, get_memory_utilization_restconf,
    get_gigabitethernet1_utilization_netconf
)

app = Flask(__name__)

@app.route('/')
def index():
    """
    Main dashboard route. Fetches metrics from RESTCONF and NETCONF and renders the HTML template.
    """
    # --- Fetch RESTCONF Data (CPU & Memory) ---
    cpu_rc = get_cpu_utilization_restconf()
    mem_used_rc, mem_total_rc = get_memory_utilization_restconf()
    
    # --- Fetch NETCONF Data (GigabitEthernet1 Utilization) ---
    gigabit_stats_nc = get_gigabitethernet1_utilization_netconf()

    # Render the HTML template with the fetched data
    return render_template(
        'index.html',
        # RESTCONF Data
        cpu_util_rc=cpu_rc,
        memory_used_rc=mem_used_rc,
        memory_total_rc=mem_total_rc,
        # NETCONF Data
        gig1_in_octets=gigabit_stats_nc['in_octets'],
        gig1_out_octets=gigabit_stats_nc['out_octets'],
        gig1_in_pkts=gigabit_stats_nc['in_pkts'],
        gig1_out_pkts=gigabit_stats_nc['out_pkts'],
        current_time=time.strftime("%Y-%m-%d %H:%M:%S")
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```
Save `app.py`.

Lab 1: Query Cisco IOS XE Router Performance (RESTCONF & NETCONF)
-----------------------------------------------------------------

Objective: Verify that your API functions can retrieve the specific data points from the router using RESTCONF and NETCONF.

### Task 1.1: Run `iosxe_api_functions.py` Standalone

After completing Lab 0 and verifying capability discovery, proceed to run the full standalone test. This will execute the data retrieval functions for CPU, Memory, and GigabitEthernet1 utilization.

Ensure your `na_env` virtual environment is active and you are in the `module5_api_lab` directory.
    ```bash
    python iosxe_api_functions.py
    ```
Expected Output (if dummy IOS XE info is not replaced or APIs are not enabled): You will see various error messages indicating connection refused or authentication failures for both RESTCONF and NETCONF attempts. This is normal if the router details are incorrect or the APIs are not properly configured.

Expected Output (if you replace with real, reachable IOS XE info and both APIs are enabled):
```console
--- Testing iosxe_api_functions.py (Capabilities, RESTCONF & NETCONF) ---
Note: This will attempt to connect to the IOS XE router defined in config.py.
... (Output from capability discovery) ...

--- RESTCONF Data (CPU & Memory) ---
RESTCONF CPU Utilization (5-sec): 5% # Or actual value
RESTCONF Memory: 123456789 used / 987654321 total bytes # Or actual values

--- NETCONF Data (GigabitEthernet1 Utilization) ---
Connecting to YOUR_IOSXE_IP:830 via NETCONF...
Successfully connected to YOUR_IOSXE_IP via NETCONF. Sending GET request.
NETCONF GigabitEthernet1 In-Octets: 12345678 # Or actual value
NETCONF GigabitEthernet1 Out-Octets: 9876543 # Or actual value
NETCONF GigabitEthernet1 In-Packets: 123456 # Or actual value
NETCONF GigabitEthernet1 Out-Packets: 98765 # Or actual value

--- Test Complete ---
```
_Note: The exact values will vary based on your router's state. You might see some `Connecting to...` messages for NETCONF for each call, as `ncclient` establishes a new session per `_make_netconf_get_request` call in this simplified example._

Lab 2: Build a Simple Monitoring Tool using Python Flask
--------------------------------------------------------

Objective: Create a Flask web application to display the router's performance metrics, sourcing CPU/Memory from RESTCONF and GigE1 stats from NETCONF.

### Task 2.1: Run the Flask Application

Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).

Navigate into your `module5_api_lab` directory:
```bash
cd module5_api_lab
```
Run the Flask application:
```bash
python app.py
```
Expected Output (console):
```console
Connecting to YOUR_IOSXE_IP:830 via NETCONF...
Successfully connected to YOUR_IOSXE_IP via NETCONF. Sending GET request.
# ... (output from metric fetching, will repeat every 5 seconds) ...
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Port: 5000
Press CTRL+C to quit
 * Restarting with stat
Press CTRL+C to quit
```
Open your web browser and navigate to `http://127.0.0.1:5000` (or `http://localhost:5000`). If you are running this on a remote server, use that server's IP address.

Observation: The web page will display the current metrics from your router, with CPU and Memory sourced from RESTCONF, and GigabitEthernet1 utilization sourced from NETCONF. It will automatically refresh every 5 seconds, fetching new data via both API methods. If your router's CPU goes above 75%, you will see a "(HIGH)" alert next to the CPU utilization.

Conclusion
----------

You've now completed Module 5 and gained practical experience with using APIs to retrieve data! You can now:

*   Understand the role of APIs in modern network automation.
*   Discover supported YANG models and capabilities on Cisco IOS XE routers via both RESTCONF and NETCONF.
*   Understand how to manually derive RESTCONF URIs and construct NETCONF XML filters using YANG models (e.g., from `yangcatalog.org`).
*   Install and use Cisco Yangsuite (optionally) to explore YANG models and generate API payloads, and compare its output with manual derivation.
*   Query operational data like CPU and Memory utilization from Cisco IOS XE using RESTCONF with JSON YANG paths.
*   Query operational data like GigabitEthernet1 statistics from Cisco IOS XE using NETCONF with XML YANG filters.
*   Build a simple monitoring tool using Python Flask to display real-time router metrics sourced from different APIs.

RESTCONF and NETCONF, both leveraging YANG data models, provide powerful, programmatic, and standardized ways to interact with network devices. This lab demonstrates how you can combine different API approaches to gather the specific data you need. These foundational skills will serve you well as you explore more advanced automation topics.

Keep Automating!