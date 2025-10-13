# NASP: Module 1 Lab Guide

## Your First Steps with Python for Networking - Hands-on Exercises

---

## Introduction

Welcome to Module 1 of the NASP Lab Guide! This guide provides hands-on exercises to help you understand the fundamental Python concepts introduced in the  Module 1 Theory Guide.

**Lab Objectives:**
*   Set up your Python development environment.
*   Write and run your first Python script.
*   Work with Python variables, data types, and operators.
*   Understand and manipulate common data representation formats (JSON, YAML, XML).
*   Implement control flow using conditionals and loops.
*   Create and use functions for code reusability.
*   Organize code using modules and packages.
*   Perform file input/output operations.

**Prerequisites:**
*   A computer with a modern operating system (Windows, macOS, or Linux).
*   Python 3.x installed (refer to the Theory Guide for installation instructions).
*   A code editor (VS Code recommended).
*   An active internet connection for installing new libraries.

**How to Use This Guide:**
*   Follow the instructions step-by-step.
*   Type out the code yourself; do not just copy-paste. This helps build muscle memory and understanding.
*   Experiment with the code. Change values, try different conditions, and see what happens.
*   If you encounter errors, read the error messages carefully. They often provide clues.
*   Refer back to the "Module 1 Theory Guide" if you need to review a concept.

Let's begin!

---

## Lab 1: Python Environment Setup & Basic Interaction

**Objective:** Get your Python environment ready and perform basic interactions with the Python interpreter and scripts.

### Task 1.1: Verify Python Installation

1.  Open your terminal (macOS/Linux) or Command Prompt/PowerShell (Windows).
2.  Type the following command and press Enter:
    ```bash
    python --version
    ```
    *Expected Output:* `Python 3.x.x` (e.g., `Python 3.10.5`).
    *If you get an error or Python 2.x, try `python3 --version` or ensure Python is correctly added to your system's PATH.*

### Task 1.2: Create and Activate a Virtual Environment

It's good practice to create a separate virtual environment for each project.

1.  Create a new directory for your lab work (e.g., `network_automation_labs`).
    ```bash
    mkdir network_automation_labs
    cd network_automation_labs
    ```
2.  Create a virtual environment named `na_env` inside this directory:
    ```bash
    python -m venv na_env
    ```
3.  Activate the virtual environment:
    *   **Linux/macOS:**
        ```bash
        source na_env/bin/activate
        ```
    *   **Windows (Command Prompt):**
        ```cmd
        na_env\Scripts\activate.bat
        ```
    *   **Windows (PowerShell):**
        ```powershell
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
        .\na_env\Scripts\Activate.ps1
        ```
    *Expected Observation:* You should see `(na_env)` at the beginning of your terminal prompt, indicating the environment is active.

### Task 1.3: Your First Python Script ("Hello Network!")

1.  Open your chosen code editor (e.g., VS Code).
2.  Create a new file named `hello_network.py` inside your `network_automation_labs` directory.
3.  Add the following code to the file:
    ```python
    # This is a simple Python script
    print("Hello, Network Automation World!")
    print("This is my first Python script for networking.")
    ```
4.  Save the file.
5.  Go back to your terminal (ensure `na_env` is still active).
6.  Run your script:
    ```bash
    python hello_network.py
    ```
    *Expected Output:*
    ```
    Hello, Network Automation World!
    This is my first Python script for networking.
    ```

### Task 1.4: Deactivate the Virtual Environment

1.  When you are done with your lab work for the day, deactivate the environment:
    ```bash
    deactivate
    ```
    *Expected Observation:* The `(na_env)` prefix should disappear from your prompt.

---

## Lab 2: Variables, Data Types & Operators

**Objective:** Practice declaring variables, understanding different data types, and using various operators.

### Task 2.1: Declare and Print Variables of Different Types

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `data_types_lab.py`.
3.  Add the following code, declaring variables of various types and printing them along with their types using `type()`:
    ```python
    # Integer
    vlan_id = 100
    print(f"VLAN ID: {vlan_id}, Type: {type(vlan_id)}")

    # Float
    temperature = 25.7
    print(f"Temperature: {temperature}, Type: {type(temperature)}")

    # String
    device_hostname = "CoreRouter-NYC"
    print(f"Device Hostname: {device_hostname}, Type: {type(device_hostname)}")

    # Boolean
    is_up = True
    print(f"Is Device Up?: {is_up}, Type: {type(is_up)}")

    # List of interfaces
    interfaces = ["GigabitEthernet0/1", "Loopback0", "Vlan10"]
    print(f"Interfaces: {interfaces}, Type: {type(interfaces)}")
    print(f"First interface in list: {interfaces}") # Accessing an item
    interfaces.append("TenGigabitEthernet1/1") # Add a new item
    print(f"Interfaces after append: {interfaces}")


    # Tuple of IP and subnet mask
    ip_subnet = ("192.168.1.1", "255.255.255.0")
    print(f"IP/Subnet: {ip_subnet}, Type: {type(ip_subnet)}")
    print(f"IP from tuple: {ip_subnet}") # Accessing an item


    # Dictionary for device details
    device_details = {
        "name": "EdgeSwitch-LA",
        "ip": "10.0.0.5",
        "vendor": "Cisco",
        "ports": 48
    }
    print(f"Device Details: {device_details}, Type: {type(device_details)}")
    print(f"Device vendor from dictionary: {device_details['vendor']}") # Accessing by key
    device_details["location"] = "Los Angeles" # Add a new key-value pair
    print(f"Device details after adding location: {device_details}")
    ```
4.  Save and run `data_types_lab.py`.
    *Expected Output (might vary slightly in dictionary order):*
    ```
    VLAN ID: 100, Type: <class 'int'>
    Temperature: 25.7, Type: <class 'float'>
    Device Hostname: CoreRouter-NYC, Type: <class 'str'>
    Is Device Up?: True, Type: <class 'bool'>
    Interfaces: ['GigabitEthernet0/1', 'Loopback0', 'Vlan10'], Type: <class 'list'>
    First interface in list: GigabitEthernet0/1
    Interfaces after append: ['GigabitEthernet0/1', 'Loopback0', 'Vlan10', 'TenGigabitEthernet1/1']
    IP/Subnet: ('192.168.1.1', '255.255.255.0'), Type: <class 'tuple'>
    IP from tuple: 192.168.1.1
    Device Details: {'name': 'EdgeSwitch-LA', 'ip': '10.0.0.5', 'vendor': 'Cisco', 'ports': 48}, Type: <class 'dict'>
    Device vendor from dictionary: Cisco
    Device details after adding location: {'name': 'EdgeSwitch-LA', 'ip': '10.0.0.5', 'vendor': 'Cisco', 'ports': 48, 'location': 'Los Angeles'}
    ```

### Task 2.2: Practice with Operators

1.  In the same `data_types_lab.py` file, add the following code to experiment with operators:
    ```python
    # Arithmetic Operators
    print("\n--- Arithmetic Operations ---")
    num_ports = 24
    expansion_modules = 2
    total_ports = num_ports + (expansion_modules * 8) # Assuming 8 ports per module
    print(f"Total ports: {total_ports}")

    uptime_minutes = 150
    uptime_hours = uptime_minutes / 60
    print(f"Uptime in hours: {uptime_hours:.2f}") # Format to 2 decimal places

    # Comparison Operators
    print("\n--- Comparison Operations ---")
    current_temp = 75
    threshold_temp = 80
    is_over_threshold = current_temp > threshold_temp
    print(f"Is current temp over threshold ({threshold_temp})?: {is_over_threshold}")

    device_status = "active"
    required_status = "active"
    is_status_match = (device_status == required_status)
    print(f"Does device status match required status?: {is_status_match}")

    # Logical Operators
    print("\n--- Logical Operations ---")
    has_credentials = True
    is_reachable = False
    can_login = has_credentials and is_reachable # Both must be True
    print(f"Can login to device?: {can_login}")

    is_primary = False
    is_backup = True
    is_redundant = is_primary or is_backup # At least one must be True
    print(f"Is device redundant?: {is_redundant}")

    is_maintenance_mode = False
    should_process = not is_maintenance_mode # Reverses the boolean
    print(f"Should process device (not in maintenance)?: {should_process}")
    ```
2.  Save and run your script.
    *Expected Output:*
    ```
    --- Arithmetic Operations ---
    Total ports: 40
    Uptime in hours: 2.50

    --- Comparison Operations ---
    Is current temp over threshold (80)?: False
    Does device status match required status?: True

    --- Logical Operations ---
    Can login to device?: False
    Is device redundant?: True
    Should process device (not in maintenance)?: True
    ```

---

## Lab 3: Working with Data Formats (JSON, YAML, XML)

**Objective:** Learn how to read and write data using JSON, YAML, and XML formats, which are commonly used in network automation.

### Task 3.1: Working with JSON

1.  Ensure your `na_env` virtual environment is active.
2.  Create a new Python file named `data_formats_lab.py`.
3.  Add the following code to work with JSON:
    ```python
    import json

    print("--- Working with JSON ---")

    # 1. Python Dictionary (our data)
    device_inventory = {
        "device_id": "R1-Core",
        "ip_address": "10.0.0.1",
        "vendor": "Cisco",
        "model": "ISR4431",
        "interfaces": [
            {"name": "GigabitEthernet0/0/0", "status": "up", "ip": "10.0.0.1"},
            {"name": "GigabitEthernet0/0/1", "status": "down", "ip": "unassigned"}
        ],
        "credentials": {"username": "admin", "password": "cisco"}
    }

    # 2. Convert Python Dictionary to JSON String (Serialization)
    json_output_string = json.dumps(device_inventory, indent=4) # indent for pretty-print
    print("\nPython Dictionary converted to JSON String:")
    print(json_output_string)
    print(f"Type of json_output_string: {type(json_output_string)}")

    # 3. Convert JSON String to Python Dictionary (Deserialization)
    json_input_string = '{"switch_name": "SW1", "vlans": 100, "ports": ["Fa0/1", "Fa0/2"]}'
    python_dict_from_json = json.loads(json_input_string)
    print("\nJSON String converted to Python Dictionary:")
    print(python_dict_from_json)
    print(f"Type of python_dict_from_json: {type(python_dict_from_json)}")
    print(f"Switch Name: {python_dict_from_json['switch_name']}, VLANs: {python_dict_from_json['vlans']}")

    # 4. Write Python Dictionary to a JSON File
    output_filename_json = "device_inventory.json"
    with open(output_filename_json, "w") as f:
        json.dump(device_inventory, f, indent=4)
    print(f"\nPython dictionary saved to {output_filename_json}")

    # 5. Read JSON File to Python Dictionary
    with open(output_filename_json, "r") as f:
        loaded_json_data = json.load(f)
    print(f"\nData loaded from {output_filename_json}:")
    print(loaded_json_data)
    print(f"Loaded device ID: {loaded_json_data['device_id']}")
    ```
4.  Save and run `data_formats_lab.py`.
    *Expected Output (console, dictionary order might vary):*
    ```
    --- Working with JSON ---

    Python Dictionary converted to JSON String:
    {
        "device_id": "R1-Core",
        "ip_address": "10.0.0.1",
        "vendor": "Cisco",
        "model": "ISR4431",
        "interfaces": [
            {
                "name": "GigabitEthernet0/0/0",
                "status": "up",
                "ip": "10.0.0.1"
            },
            {
                "name": "GigabitEthernet0/0/1",
                "status": "down",
                "ip": "unassigned"
            }
        ],
        "credentials": {
            "username": "admin",
            "password": "cisco"
        }
    }
    Type of json_output_string: <class 'str'>

    JSON String converted to Python Dictionary:
    {'switch_name': 'SW1', 'vlans': 100, 'ports': ['Fa0/1', 'Fa0/2']}
    Type of python_dict_from_json: <class 'dict'>
    Switch Name: SW1, VLANs: 100

    Python dictionary saved to device_inventory.json

    Data loaded from device_inventory.json:
    {'device_id': 'R1-Core', 'ip_address': '10.0.0.1', 'vendor': 'Cisco', 'model': 'ISR4431', 'interfaces': [{'name': 'GigabitEthernet0/0/0', 'status': 'up', 'ip': '10.0.0.1'}, {'name': 'GigabitEthernet0/0/1', 'status': 'down', 'ip': 'unassigned'}], 'credentials': {'username': 'admin', 'password': 'cisco'}}
    Loaded device ID: R1-Core
    ```
    *Expected File Creation:* A file named `device_inventory.json` should be created in your `network_automation_labs` directory with the formatted JSON content.

### Task 3.2: Working with YAML

1.  Ensure your `na_env` virtual environment is active.
2.  **Install PyYAML:**
    ```bash
    pip install PyYAML
    ```
3.  In `data_formats_lab.py`, add the following code to work with YAML:
    ```python
    import yaml

    print("\n--- Working with YAML ---")

    # 1. Python Dictionary (our data)
    network_topology = {
        "site": "Headquarters",
        "routers": [
            {"name": "R1", "ip": "192.168.1.1", "os": "IOS-XE"},
            {"name": "R2", "ip": "192.168.1.2", "os": "IOS-XR"}
        ],
        "switches": [
            {"name": "SW1", "ip": "192.168.1.10", "model": "Catalyst 9300"}
        ],
        "firewall": {"name": "FW1", "ip": "192.168.1.20"}
    }

    # 2. Convert Python Dictionary to YAML String
    yaml_output_string = yaml.dump(network_topology, sort_keys=False, default_flow_style=False)
    print("\nPython Dictionary converted to YAML String:")
    print(yaml_output_string)
    print(f"Type of yaml_output_string: {type(yaml_output_string)}")

    # 3. Convert YAML String to Python Dictionary
    yaml_input_string = """
    device_name: AccessSwitch
    ports:
      - Gi0/1
      - Gi0/2
    vlan_access: 10
    """
    python_dict_from_yaml = yaml.safe_load(yaml_input_string)
    print("\nYAML String converted to Python Dictionary:")
    print(python_dict_from_yaml)
    print(f"Type of python_dict_from_yaml: {type(python_dict_from_yaml)}")
    print(f"Device Name: {python_dict_from_yaml['device_name']}, Ports: {python_dict_from_yaml['ports']}")

    # 4. Write Python Dictionary to a YAML File
    output_filename_yaml = "network_topology.yaml"
    with open(output_filename_yaml, "w") as f:
        yaml.dump(network_topology, f, sort_keys=False, default_flow_style=False)
    print(f"\nPython dictionary saved to {output_filename_yaml}")

    # 5. Read YAML File to Python Dictionary
    with open(output_filename_yaml, "r") as f:
        loaded_yaml_data = yaml.safe_load(f)
    print(f"\nData loaded from {output_filename_yaml}:")
    print(loaded_yaml_data)
    print(f"Loaded site: {loaded_yaml_data['site']}")
    ```
4.  Save and run `data_formats_lab.py`.
    *Expected Output (console):*
    ```
    --- Working with YAML ---

    Python Dictionary converted to YAML String:
    site: Headquarters
    routers:
    - name: R1
      ip: 192.168.1.1
      os: IOS-XE
    - name: R2
      ip: 192.168.1.2
      os: IOS-XR
    switches:
    - name: SW1
      ip: 192.168.1.10
      model: Catalyst 9300
    firewall:
      name: FW1
      ip: 192.168.1.20

    Type of yaml_output_string: <class 'str'>

    YAML String converted to Python Dictionary:
    {'device_name': 'AccessSwitch', 'ports': ['Gi0/1', 'Gi0/2'], 'vlan_access': 10}
    Type of python_dict_from_yaml: <class 'dict'>
    Device Name: AccessSwitch, Ports: ['Gi0/1', 'Gi0/2']

    Python dictionary saved to network_topology.yaml

    Data loaded from network_topology.yaml:
    {'site': 'Headquarters', 'routers': [{'name': 'R1', 'ip': '192.168.1.1', 'os': 'IOS-XE'}, {'name': 'R2', 'ip': '192.168.1.2', 'os': 'IOS-XR'}], 'switches': [{'name': 'SW1', 'ip': '192.168.1.10', 'model': 'Catalyst 9300'}], 'firewall': {'name': 'FW1', 'ip': '192.168.1.20'}}
    Loaded site: Headquarters
    ```
    *Expected File Creation:* A file named `network_topology.yaml` should be created in your `network_automation_labs` directory with the formatted YAML content.

### Task 3.3: Working with XML (`xmltodict`)

1.  Ensure your `na_env` virtual environment is active.
2.  **Install xmltodict:**
    ```bash
    pip install xmltodict
    ```
3.  In `data_formats_lab.py`, add the following code to work with XML:
    ```python
    import xmltodict
    import json # Used here to pretty-print the Python dictionary result

    print("\n--- Working with XML (using xmltodict) ---")

    # 1. XML String (simulating data from a device or old API)
    xml_input_string = """
    <device_status>
        <hostname>LabRouter</hostname>
        <uptime_days>150</uptime_days>
        <interfaces>
            <interface>
                <name>GigabitEthernet0/0</name>
                <state>up</state>
                <ip_address>192.168.1.1</ip_address>
            </interface>
            <interface>
                <name>Loopback0</name>
                <state>up</state>
                <ip_address>1.1.1.1</ip_address>
            </interface>
        </interfaces>
        <cpu_utilization>25</cpu_utilization>
    </device_status>
    """

    # 2. Convert XML String to Python Dictionary
    # force_list=('interface',) ensures 'interface' is always a list, even if only one exists.
    # This makes iterating over interfaces safer.
    python_dict_from_xml = xmltodict.parse(xml_input_string, force_list=('interface',))
    print("\nXML String converted to Python Dictionary:")
    print(json.dumps(python_dict_from_xml, indent=4)) # Pretty-print the dict
    print(f"Type of python_dict_from_xml: {type(python_dict_from_xml)}")

    # Accessing data from the converted dictionary
    hostname = python_dict_from_xml['device_status']['hostname']
    print(f"\nHostname from XML: {hostname}")
    print("Interface States:")
    for iface in python_dict_from_xml['device_status']['interfaces']['interface']:
        print(f"  - {iface['name']}: {iface['state']} (IP: {iface['ip_address']})")

    # 3. Convert Python Dictionary to XML String
    python_dict_to_xml = {
        'network_device': {
            'hostname': 'SwitchA',
            'model': 'Cisco 2960',
            'vlans': {
                'vlan': [
                    {'id': 10, 'name': 'DATA'},
                    {'id': 20, 'name': 'VOICE'}
                ]
            }
        }
    }
    
    # pretty=True for human-readable XML output
    xml_output_string = xmltodict.unparse(python_dict_to_xml, pretty=True)
    print("\nPython Dictionary converted to XML String:")
    print(xml_output_string)
    print(f"Type of xml_output_string: {type(xml_output_string)}")
    ```
4.  Save and run `data_formats_lab.py`.
    *Expected Output (console):*
    ```
    --- Working with XML (using xmltodict) ---

    XML String converted to Python Dictionary:
    {
        "device_status": {
            "hostname": "LabRouter",
            "uptime_days": "150",
            "interfaces": {
                "interface": [
                    {
                        "name": "GigabitEthernet0/0",
                        "state": "up",
                        "ip_address": "192.168.1.1"
                    },
                    {
                        "name": "Loopback0",
                        "state": "up",
                        "ip_address": "1.1.1.1"
                    }
                ]
            },
            "cpu_utilization": "25"
        }
    }
    Type of python_dict_from_xml: <class 'dict'>

    Hostname from XML: LabRouter
    Interface States:
      - GigabitEthernet0/0: up (IP: 192.168.1.1)
      - Loopback0: up (IP: 1.1.1.1)

    Python Dictionary converted to XML String:
    <?xml version="1.0" encoding="utf-8"?>
    <network_device>
      <hostname>SwitchA</hostname>
      <model>Cisco 2960</model>
      <vlans>
        <vlan>
          <id>10</id>
          <name>DATA</name>
        </vlan>
        <vlan>
          <id>20</id>
          <name>VOICE</name>
        </vlan>
      </vlans>
    </network_device>
    Type of xml_output_string: <class 'str'>
    ```

---

## Lab 4: Control Flow - Conditionals

**Objective:** Learn to use `if`, `elif`, and `else` statements to control program flow based on conditions.

### Task 4.1: Simple Device Status Check

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `control_flow_lab.py`.
3.  Add the following code:
    ```python
    # control_flow_lab.py
    device_status = "up" # Try changing this to "down" or "unknown"
    device_type = "router"

    print(f"Checking device status for a {device_type}...")

    if device_status == "up":
        print("Device is operational. Proceed with configuration.")
    elif device_status == "down":
        print("Device is down. Investigate connectivity issues.")
    else:
        print("Device status is unknown. Manual check required.")

    print("--- Check Complete ---")
    ```
4.  Run the script with `device_status = "up"`.
    *Expected Output:*
    ```
    Checking device status for a router...
    Device is operational. Proceed with configuration.
    --- Check Complete ---
    ```
5.  Change `device_status` to `"down"` and run again.
    *Expected Output:*
    ```
    Checking device status for a router...
    Device is down. Investigate connectivity issues.
    --- Check Complete ---
    ```
6.  Change `device_status` to `"unknown"` and run again.
    *Expected Output:*
    ```
    Checking device status for a router...
    Device status is unknown. Manual check required.
    --- Check Complete ---
    ```

### Task 4.2: Nested Conditionals and Combined Conditions

1.  Modify `control_flow_lab.py` to include nested conditions and combined logical conditions.
    ```python
    # ... (previous code) ...

    print("\n--- Detailed Device Check ---")
    device_status_detailed = "up"
    device_type_detailed = "router"
    config_pending = True # Try changing this to False
    interface_state = "up" # Try changing this to "down"

    if device_status_detailed == "up":
        print("Device is operational.")
        if device_type_detailed == "router":
            print("  This is a router. Specific router tasks can be performed.")
            if config_pending:
                print("  Warning: Configuration changes are pending. Apply or discard.")
            else:
                print("  No pending configuration changes.")
        elif device_type_detailed == "switch":
            print("  This is a switch. Specific switch tasks can be performed.")
        else:
            print("  Device type not specifically handled.")

        # Combined condition check
        if device_type_detailed == "router" and interface_state == "down":
            print("  Critical Alert: A router interface is down!")
        elif device_type_detailed == "switch" and interface_state == "down":
            print("  Warning: A switch interface is down. Check port.")

    elif device_status_detailed == "down":
        print("Device is down. Cannot perform any operations.")
    else:
        print("Device status is unknown. Cannot proceed.")

    print("--- Detailed Check Complete ---")
    ```
2.  Experiment with different combinations of `device_status_detailed`, `config_pending`, and `interface_state` to see how the output changes.
    *Expected Output (with `device_status_detailed="up"`, `device_type_detailed="router"`, `config_pending=True`, `interface_state="up"`):*
    ```
    --- Detailed Device Check ---
    Device is operational.
      This is a router. Specific router tasks can be performed.
      Warning: Configuration changes are pending. Apply or discard.
    --- Detailed Check Complete ---
    ```
    *Expected Output (with `device_status_detailed="up"`, `device_type_detailed="router"`, `config_pending=False`, `interface_state="down"`):*
    ```
    --- Detailed Device Check ---
    Device is operational.
      This is a router. Specific router tasks can be performed.
      No pending configuration changes.
      Critical Alert: A router interface is down!
    --- Detailed Check Complete ---
    ```

---

## Lab 5: Control Flow - Loops

**Objective:** Implement `for` and `while` loops for repetitive tasks.

### Task 5.1: Iterate Through a List of Devices (`for` loop)

1.  In `control_flow_lab.py`, add the following code to simulate connecting to multiple devices:
    ```python
    # ... (previous code) ...

    print("\n--- Processing Devices with For Loop ---")
    device_ips_list = ["192.168.1.10", "192.168.1.11", "192.168.1.12"]
    device_names_list = ["R1-HQ", "SW1-Branch", "FW1-DMZ"]

    print("Processing Device IPs:")
    for ip in device_ips_list:
        print(f"  Attempting to connect to IP: {ip}")

    print("\nProcessing Device Names:")
    for name in device_names_list:
        print(f"  Performing health check on device: {name}")

    print("\nIterating with range():")
    # Use range to perform an action a specific number of times
    for i in range(1, 4): # This will iterate for i = 1, 2, 3
        print(f"  Sending configuration batch {i}...")

    print("\nIterating through dictionary items:")
    device_inventory_dict = {
        "R1": {"ip": "192.168.1.1", "os": "IOS"},
        "SW1": {"ip": "192.168.1.2", "os": "NX-OS"},
        "FW1": {"ip": "192.168.1.3", "os": "ASA"}
    }
    for hostname, details in device_inventory_dict.items():
        print(f"  Device: {hostname}, IP: {details['ip']}, OS: {details['os']}")
    ```
2.  Save and run `control_flow_lab.py`.
    *Expected Output:*
    ```
    --- Processing Devices with For Loop ---
    Processing Device IPs:
      Attempting to connect to IP: 192.168.1.10
      Attempting to connect to IP: 192.168.1.11
      Attempting to connect to IP: 192.168.1.12

    Processing Device Names:
      Performing health check on device: R1-HQ
      Performing health check on device: SW1-Branch
      Performing health check on device: FW1-DMZ

    Iterating with range():
      Sending configuration batch 1...
      Sending configuration batch 2...
      Sending configuration batch 3...

    Iterating through dictionary items:
      Device: R1, IP: 192.168.1.1, OS: IOS
      Device: SW1, IP: 192.168.1.2, OS: NX-OS
      Device: FW1, IP: 192.168.1.3, OS: ASA
    ```

### Task 5.2: Implement a Retry Mechanism (`while` loop)

1.  In the same `control_flow_lab.py` file, add the following code to simulate retrying a connection attempt until successful or max retries are met.
    ```python
    # ... (previous code) ...
    import time # We need this to simulate a delay

    print("\n--- Connection Retry Mechanism with While Loop ---")
    target_device_ip = "192.168.1.100"
    max_attempts = 3
    attempts = 0
    connection_successful = False

    while not connection_successful and attempts < max_attempts:
        attempts += 1
        print(f"Attempting to connect to {target_device_ip} (Attempt {attempts}/{max_attempts})...")
        time.sleep(2) # Simulate network delay

        # Simulate connection success on the 2nd attempt
        if attempts == 2:
            connection_successful = True
            print(f"Successfully connected to {target_device_ip}!")
        else:
            print("Connection failed. Retrying...")

    if not connection_successful:
        print(f"Failed to connect to {target_device_ip} after {max_attempts} attempts.")
    ```
2.  Save and run `control_flow_lab.py`.
    *Expected Output (after previous outputs):*
    ```
    --- Connection Retry Mechanism with While Loop ---
    Attempting to connect to 192.168.1.100 (Attempt 1/3)...
    Connection failed. Retrying...
    Attempting to connect to 192.168.1.100 (Attempt 2/3)...
    Successfully connected to 192.168.1.100!
    ```

---

## Lab 6: Functions

**Objective:** Define and use functions to create reusable blocks of code.

### Task 6.1: Create a Simple Function

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `functions_lab.py`.
3.  Add a simple function to greet a device:
    ```python
    # functions_lab.py
    def greet_device(hostname):
        """
        Prints a greeting message for a given device hostname.
        """
        print(f"Hello, {hostname}! Ready for automation.")

    # Call the function
    greet_device("Router-HQ")
    greet_device("Switch-Access-01")
    ```
4.  Save and run `functions_lab.py`.
    *Expected Output:*
    ```
    Hello, Router-HQ! Ready for automation.
    Hello, Switch-Access-01! Ready for automation.
    ```

### Task 6.2: Function with Multiple Parameters and a Return Value

1.  Modify `functions_lab.py` by adding a function that simulates sending a command and returns the output.
    ```python
    # ... (previous code) ...

    def send_command_to_device(ip_address, command):
        """
        Simulates sending a command to a network device and returns a dummy output.
        In a real scenario, this would involve SSH/Telnet connection.

        Args:
            ip_address (str): The IP address of the device.
            command (str): The command to send.

        Returns:
            str: A simulated command output.
        """
        print(f"\nConnecting to {ip_address}...")
        print(f"Sending command: '{command}'")
        # Simulate different outputs based on command
        if "show ip interface brief" in command:
            return f"""
Interface              IP-Address      OK? Method Status        Protocol
GigabitEthernet0/0     192.168.1.1     YES manual up            up
Loopback0              1.1.1.1         YES manual up            up
Vlan1                  unassigned      YES unset  down          down
"""
        elif "show version" in command:
            return f"Cisco IOS Software, C800 Series (C800-UNIVERSALK9-M), Version 15.6\nDevice {ip_address}"
        else:
            return f"Command '{command}' executed on {ip_address} (Simulated Output)"

    # Call the function and store the returned value
    router_ip = "192.168.1.10"
    output1 = send_command_to_device(router_ip, "show ip interface brief")
    print("\n--- Output 1 ---")
    print(output1)

    output2 = send_command_to_device("192.168.1.20", "show version")
    print("\n--- Output 2 ---")
    print(output2)

    # Use the function in a loop
    devices_to_check = ["192.168.1.30", "192.168.1.40"]
    for device in devices_to_check:
        status_output = send_command_to_device(device, "show interface status")
        print(f"\n--- Status for {device} ---")
        print(status_output)
    ```
3.  Save and run `functions_lab.py`.
    *Expected Output (after previous outputs):*
    ```
    Connecting to 192.168.1.10...
    Sending command: 'show ip interface brief'

    --- Output 1 ---

Interface              IP-Address      OK? Method Status        Protocol
GigabitEthernet0/0     192.168.1.1     YES manual up            up
Loopback0              1.1.1.1         YES manual up            up
Vlan1                  unassigned      YES unset  down          down


    Connecting to 192.168.1.20...
    Sending command: 'show version'

    --- Output 2 ---
    Cisco IOS Software, C800 Series (C800-UNIVERSALK9-M), Version 15.6
    Device 192.168.1.20

    Connecting to 192.168.1.30...
    Sending command: 'show interface status'

    --- Status for 192.168.1.30 ---
    Command 'show interface status' executed on 192.168.1.30 (Simulated Output)

    Connecting to 192.168.1.40...
    Sending command: 'show interface status'

    --- Status for 192.168.1.40 ---
    Command 'show interface status' executed on 192.168.1.40 (Simulated Output)
    ```

---

## Lab 7: Modules and Packages

**Objective:** Understand how to use built-in modules and conceptually structure your code into packages.

### Task 7.1: Use Built-in Modules (`os`, `sys`)

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `modules_packages_lab.py`.
3.  Add the following code to use the `os` (operating system) and `sys` (system-specific parameters and functions) modules:
    ```python
    # modules_packages_lab.py
    import os # Provides a way of using operating system dependent functionality
    import sys # Provides access to system-specific parameters and functions

    print("--- OS Module Examples ---")
    # Get the current working directory
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")

    # List contents of the current directory
    print("Files and directories in current path:")
    for item in os.listdir(current_dir):
        print(f"  - {item}")

    # Check if a file exists
    if os.path.exists("modules_packages_lab.py"):
        print("\n'modules_packages_lab.py' exists in this directory.")
    else:
        print("\n'modules_packages_lab.py' does NOT exist in this directory.")

    print("\n--- Sys Module Examples ---")
    # Get Python version
    print(f"Python version: {sys.version.split()}") # Just the version number

    # Get the operating system platform
    print(f"Operating System Platform: {sys.platform}")

    # Get the Python executable path
    print(f"Python Executable Path: {sys.executable}")
    ```
4.  Save and run `modules_packages_lab.py`.
    *Expected Output (will vary based on your system and files in directory):*
    ```
    --- OS Module Examples ---
    Current working directory: /path/to/your/network_automation_labs
    Files and directories in current path:
      - na_env
      - hello_network.py
      - data_types_lab.py
      - data_formats_lab.py
      - control_flow_lab.py
      - functions_lab.py
      - modules_packages_lab.py
    'modules_packages_lab.py' exists in this directory.

    --- Sys Module Examples ---
    Python version: 3.x.x
    Operating System Platform: linux (or win32, darwin)
    Python Executable Path: /path/to/your/network_automation_labs/na_env/bin/python
    ```

### Task 7.2: Conceptual Package Structure (No Code Execution)

This task is for understanding how packages are structured. You don't need to write executable code for this part, but you can create the directories and empty `__init__.py` files to see the structure.

1.  In your `network_automation_labs` directory, create the following directory and file structure:
    ```
    network_automation_labs/
    ├── na_env/
    ├── hello_network.py
    ├── data_types_lab.py
    ├── data_formats_lab.py
    ├── control_flow_lab.py
    ├── functions_lab.py
    ├── modules_packages_lab.py
    |
    ├── my_network_automation/  <-- This will be your main package directory
    │   ├── __init__.py         <-- Makes 'my_network_automation' a Python package (can be empty)
    │   ├── main_script.py      <-- Main script that uses other modules
    │   │
    │   ├── device_operations/  <-- Sub-package for device-specific tasks
    │   │   ├── __init__.py
    │   │   ├── connect.py      <-- Module for connection functions (e.g., SSH, Telnet)
    │   │   └── config.py       <-- Module for configuration functions
    │   │
    │   └── utilities/          <-- Sub-package for general utility functions
    │       ├── __init__.py
    │       └── parsers.py      <-- Module for parsing command output
    ```
    *Expected Observation:* You should have a new folder structure resembling the diagram. The `__init__.py` files are essential for Python to recognize these folders as packages.

2.  **Conceptual `main_script.py` content (do NOT run this, it's just to show imports):**
    ```python
    # my_network_automation/main_script.py

    # Import functions from your custom modules within the package
    from device_operations.connect import connect_to_device
    from device_operations.config import apply_config
    from utilities.parsers import parse_interface_status

    print("Starting network automation task...")

    # In a real scenario, you would call these functions:
    # device_ip = "192.168.1.50"
    # username = "admin"
    # password = "password"
    # commands = ["interface Loopback0", "ip address 1.1.1.1 255.255.255.255"]
    # raw_output = "GigabitEthernet0/1 up up"

    # connection = connect_to_device(device_ip, username, password)
    # if connection:
    #     apply_config(connection, commands)
    #     parsed_data = parse_interface_status(raw_output)
    #     print(parsed_data)

    print("Network automation task completed (conceptually).")
    ```
    *Expected Observation:* This code is for illustration purposes. If you were to create these files and run `main_script.py` (after defining the functions in `connect.py`, `config.py`, and `parsers.py`), you would see the print statements indicating the start and completion of the conceptual task.

---

## Lab 8: Working with Files

**Objective:** Practice reading data from and writing data to text files.

### Task 8.1: Write Data to a File

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `file_io_lab.py`.
3.  Add the following code to simulate writing a configuration to a file:
    ```python
    # file_io_lab.py
    print("--- Writing Configuration to File ---")
    device_config_to_save = """
        version 15.6
        hostname My-Lab-Router
        interface Loopback0
        ip address 1.1.1.1 255.255.255.255
        end"""
    output_config_filename = "router_config_backup.txt"

    try:
        # Open in "w" (write) mode. This will create the file or overwrite it if it exists.
        with open(output_config_filename, "w") as f: 
            f.write(device_config_to_save)
        print(f"Configuration backup successfully written to: {output_config_filename}")
    except IOError as e:
        print(f"Error writing backup file: {e}")
    ```
4.  Save and run `file_io_lab.py`.
    *Expected Output:*
    ```
    --- Writing Configuration to File ---
    Configuration backup successfully written to: router_config_backup.txt
    ```
    *Expected File Creation:* A file named `router_config_backup.txt` should be created in your `network_automation_labs` directory with the content provided in `device_config_to_save`.

### Task 8.2: Read Data from a File

1.  Create a new text file named `device_ips.txt` in your `network_automation_labs` directory.
2.  Add the following content to `device_ips.txt`:
    ```
    192.168.1.10
    192.168.1.11
    192.168.1.12
    router-hq.example.com
    switch-access.example.com
    ```
3.  In the same `file_io_lab.py`, add the following code to read the device IPs/hostnames from `device_ips.txt`:
    ```python
    # ... (previous code) ...

    print("\n--- Reading Device List from device_ips.txt ---")
    input_device_filename = "device_ips.txt"
    device_targets = []

    try:
        # Open in "r" (read) mode.
        with open(input_device_filename, "r") as f:
            for line in f:
                device_targets.append(line.strip()) # .strip() removes whitespace including newlines
        print("Successfully read devices:")
        for device in device_targets:
            print(f"- {device}")
    except FileNotFoundError:
        print(f"Error: '{input_device_filename}' not found. Please create it as instructed.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    ```
4.  Save and run `file_io_lab.py`.
    *Expected Output (after previous outputs):*
    ```
    --- Reading Device List from device_ips.txt ---
    Successfully read devices:
    - 192.168.1.10
    - 192.168.1.11
    - 192.168.1.12
    - router-hq.example.com
    - switch-access.example.com
    ```

### Task 8.3: Append Data to a Log File

1.  In the same `file_io_lab.py` file, add the following code to append log entries to a file.
    ```python
    # ... (previous code) ...
    import datetime

    print("\n--- Appending to a Log File ---")
    log_filename = "automation_log.txt"

    def log_action(message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        try:
            # Open in "a" (append) mode. This will add to the end of the file.
            with open(log_filename, "a") as f: 
                f.write(log_entry)
            print(f"Logged: {message}")
        except IOError as e:
            print(f"Error writing to log file: {e}")

    log_action("Started device inventory script.")
    log_action("Processed device 192.168.1.10 successfully.")
    log_action("Error: Device 192.168.1.11 unreachable.")
    log_action("Finished device inventory script.")
    ```
2.  Save and run `file_io_lab.py` multiple times.
    *Expected Output (console, after previous outputs):*
    ```
    --- Appending to a Log File ---
    Logged: Started device inventory script.
    Logged: Processed device 192.168.1.10 successfully.
    Logged: Error: Device 192.168.1.11 unreachable.
    Logged: Finished device inventory script.
    ```
    *Expected File Creation/Modification:* A file named `automation_log.txt` should be created (or appended to if it already exists) in your `network_automation_labs` directory, with timestamped log entries.

---

## Lab 9: Introduction to Network Automation Libraries (Conceptual)

**Objective:** Understand the conceptual usage of key network automation libraries. (Actual hands-on with these will come in later modules).

### Task 9.1: Conceptual Netmiko Usage

1.  Activate your `na_env` virtual environment.
2.  **Install Netmiko:**
    ```bash
    pip install netmiko
    ```
3.  Create a new Python file named `net_libs_conceptual_lab.py`.
4.  Add the following conceptual Netmiko code:
    ```python
    # net_libs_conceptual_lab.py
    # import ConnectHandler # We're just showing the concept, not running real code here

    print("--- Conceptual Netmiko Usage ---")

    # Imagine this is your device's information
    device_info = {
        "device_type": "cisco_ios",
        "host": "192.168.1.10",
        "username": "admin",
        "password": "cisco",
        "secret": "enable_pass"
    }

    print(f"Netmiko would connect to {device_info['host']} via SSH.")
    print("It would then send commands like 'show version' or 'configure terminal'.")
    print("Example: net_connect = ConnectHandler(**device_info)")
    print("         output = net_connect.send_command('show ip interface brief')")
    print("         net_connect.send_config_set(['hostname NEW_ROUTER', 'no logging console'])")
    print("\n(Note: This is conceptual. Running this requires a real, reachable device.)")
    ```
5.  Save and run `net_libs_conceptual_lab.py`.
    *Expected Output:*
    ```
    --- Conceptual Netmiko Usage ---
    Netmiko would connect to 192.168.1.10 via SSH.
    It would then send commands like 'show version' or 'configure terminal'.
    Example: net_connect = ConnectHandler(**device_info)
             output = net_connect.send_command('show ip interface brief')
             net_connect.send_config_set(['hostname NEW_ROUTER', 'no logging console'])

    (Note: This is conceptual. Running this requires a real, reachable device.)
    ```

### Task 9.2: Conceptual NAPALM Usage

1.  Ensure your `na_env` virtual environment is active.
2.  **Install NAPALM:**
    ```bash
    pip install napalm
    ```
3.  In `net_libs_conceptual_lab.py`, add the following conceptual NAPALM code:
    ```python
    # ... (previous code) ...
    # import get_network_driver # We're just showing the concept, not running real code here

    print("\n--- Conceptual NAPALM Usage ---")

    # NAPALM provides a unified way to get data and configure different vendors
    print("NAPALM abstracts away vendor differences.")
    print("You'd specify a driver (e.g., 'ios', 'junos').")
    print("Example: driver = get_network_driver('ios')")
    print("         device = driver(hostname='192.168.1.10', username='admin', password='cisco')")
    print("         device.open()")
    print("         facts = device.get_facts()")
    print("         device.load_merge_candidate(filename='new_config.txt')")
    print("         device.commit_config()")
    print("\n(Note: This is conceptual. Running this requires a real, reachable device.)")
    ```
4.  Save and run `net_libs_conceptual_lab.py`.
    *Expected Output (after previous outputs):*
    ```
    --- Conceptual NAPALM Usage ---
    NAPALM abstracts away vendor differences.
    You'd specify a driver (e.g., 'ios', 'junos').
    Example: driver = get_network_driver('ios')
             device = driver(hostname='192.168.1.10', username='admin', password='cisco')
             device.open()
             facts = device.get_facts()
             device.load_merge_candidate(filename='new_config.txt')
             device.commit_config()

    (Note: This is conceptual. Running this requires a real, reachable device.)
    ```

### Task 9.3: Conceptual Requests Usage

1.  Ensure your `na_env` virtual environment is active.
2.  **Install Requests:**
    ```bash
    pip install requests
    ```
3.  In `net_libs_conceptual_lab.py`, add the following conceptual Requests code:
    ```python
    # ... (previous code) ...
    import requests # This one we can actually run!
    import json # For pretty-printing API responses

    print("\n--- Conceptual Requests Usage (Real API Call) ---")

    # Requests is used for talking to web-based APIs (like Meraki, DNA Center)
    # We'll use a public dummy API for a real example.
    api_url = "https://jsonplaceholder.typicode.com/posts/1"

    try:
        print(f"Making a GET request to: {api_url}")
        response = requests.get(api_url)
        response.raise_for_status() # Check for HTTP errors (like 404, 500)

        data = response.json() # Parse the JSON response
        print("API Response (first few lines):")
        print(json.dumps(data, indent=2)[:200] + "...") # Print first 200 chars
        print(f"\nTitle from API: {data['title']}")

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response.")
    ```
4.  Save and run `net_libs_conceptual_lab.py`.
    *Expected Output (after previous outputs, content will come from the live API):*
    ```
    --- Conceptual Requests Usage (Real API Call) ---
    Making a GET request to: https://jsonplaceholder.typicode.com/posts/1
    API Response (first few lines):
    {
      "userId": 1,
      "id": 1,
      "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
      "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
    }...

    Title from API: sunt aut facere repellat provident occaecati excepturi optio reprehenderit
    ```

---

## Conclusion

Congratulations! You've completed Module 1 and gained hands-on experience with the fundamental Python concepts crucial for network automation. You can now:

*   Set up your Python environment.
*   Work with basic Python data types and operators.
*   Understand and process JSON, YAML, and XML data.
*   Control the flow of your programs using conditionals and loops.
*   Write reusable code with functions.
*   Organize your projects using modules and packages.
*   Perform basic file operations.
*   Have a conceptual understanding of key network automation libraries.

Keep practicing these skills, as they form the bedrock of all your future automation endeavors.



---