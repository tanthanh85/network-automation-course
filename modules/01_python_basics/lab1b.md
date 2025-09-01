# Python Basics for Network Automation: Lab Guide

## Hands-on Exercises to Build Your Skills

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to the Python Basics for Network Automation Lab Guide! This document provides hands-on exercises designed to reinforce the theoretical concepts covered in the "Python Basics for Network Automation: Theory Guide." By completing these labs, you will gain practical experience with fundamental Python programming and its application in a network automation context.

**Lab Objectives:**
*   Set up a Python development environment.
*   Understand and manipulate basic Python data types.
*   Implement control flow using conditionals and loops.
*   Create and use functions for code reusability.
*   Organize code using modules and packages.
*   Perform file input/output operations.
*   Gain a conceptual understanding of key network automation libraries.

**Prerequisites:**
*   A computer with a modern operating system (Windows, macOS, or Linux).
*   Python 3.x installed (refer to the Theory Guide for installation instructions).
*   A code editor (VS Code recommended).
*   An active internet connection for installing packages.

**How to Use This Guide:**
*   Follow the instructions step-by-step.
*   Type out the code yourself; do not just copy-paste. This helps with muscle memory and understanding.
*   Experiment with the code. Change values, try different conditions, and see what happens.
*   If you encounter errors, read the error messages carefully. They often provide clues.
*   Refer back to the "Theory Guide" if you need to review a concept.

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
    *Expected Output:* `Python 3.x.x` (where `x.x` is your installed version).
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
        .\na_env\Scripts\Activate.ps1
        ```
    *You should see `(na_env)` at the beginning of your terminal prompt, indicating the environment is active.*

### Task 1.3: Basic Python Interpreter Usage

The Python interpreter allows you to execute Python code line by line.

1.  With your virtual environment active, type `python` (or `python3`) and press Enter to enter the interpreter.
    ```bash
    (na_env) $ python
    Python 3.x.x (...)
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    ```
2.  Perform some basic arithmetic:
    ```python
    >>> 5 + 3
    8
    >>> 10 / 2
    5.0
    >>> "Hello" + " Python"
    'Hello Python'
    ```
3.  Assign a value to a variable and print it:
    ```python
    >>> device_name = "CiscoRouter1"
    >>> print(device_name)
    CiscoRouter1
    ```
4.  Exit the interpreter:
    ```python
    >>> exit()
    ```

### Task 1.4: Your First Python Script ("Hello Network!")

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

### Task 1.5: Deactivate the Virtual Environment

1.  When you are done with your lab work for the day, deactivate the environment:
    ```bash
    deactivate
    ```
    *The `(na_env)` prefix should disappear from your prompt.*

---

## Lab 2: Variables, Data Types & Operators

**Objective:** Practice declaring variables, understanding different data types, and using various operators.

### Task 2.1: Declare and Print Variables of Different Types

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `data_types.py`.
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

    # Tuple of IP and subnet mask
    ip_subnet = ("192.168.1.1", "255.255.255.0")
    print(f"IP/Subnet: {ip_subnet}, Type: {type(ip_subnet)}")

    # Dictionary for device details
    device_details = {
        "name": "EdgeSwitch-LA",
        "ip": "10.0.0.5",
        "vendor": "Cisco",
        "ports": 48
    }
    print(f"Device Details: {device_details}, Type: {type(device_details)}")

    # Accessing elements from list and dictionary
    print(f"First interface: {interfaces}")
    print(f"Device vendor from dictionary: {device_details['vendor']}")
    ```
4.  Save and run `data_types.py`. Observe the output.

### Task 2.2: Practice with Operators

1.  In the same `data_types.py` file (or a new `operators.py`), add the following code to experiment with operators.
2.  **Arithmetic Operators:**
    ```python
    # Arithmetic Operators
    print("\n--- Arithmetic Operations ---")
    num_ports = 24
    expansion_modules = 2
    total_ports = num_ports + (expansion_modules * 8) # Assuming 8 ports per module
    print(f"Total ports: {total_ports}")

    uptime_minutes = 150
    uptime_hours = uptime_minutes / 60
    print(f"Uptime in hours: {uptime_hours}")

    packets_sent = 1005
    packets_received = 1000
    packet_loss_percent = ((packets_sent - packets_received) / packets_sent) * 100
    print(f"Packet loss: {packet_loss_percent:.2f}%") # Format to 2 decimal places
    ```
3.  **Comparison Operators:**
    ```python
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
    ```
4.  **Logical Operators:**
    ```python
    # Logical Operators
    print("\n--- Logical Operations ---")
    has_credentials = True
    is_reachable = False
    can_login = has_credentials and is_reachable
    print(f"Can login to device?: {can_login}")

    is_primary = False
    is_backup = True
    is_redundant = is_primary or is_backup
    print(f"Is device redundant?: {is_redundant}")

    is_maintenance_mode = False
    should_process = not is_maintenance_mode
    print(f"Should process device (not in maintenance)?: {should_process}")
    ```
5.  Save and run your script.

---

## Lab 3: Control Flow - Conditionals

**Objective:** Learn to use `if`, `elif`, and `else` statements to control program flow based on conditions.

### Task 3.1: Simple Device Status Check

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `device_check.py`.
3.  Add the following code:
    ```python
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
5.  Change `device_status` to `"down"` and run again.
6.  Change `device_status` to `"unknown"` and run again.

### Task 3.2: Nested Conditionals and Combined Conditions

1.  Modify `device_check.py` to include nested conditions and combined logical conditions.
    ```python
    device_status = "up"
    device_type = "router"
    config_pending = True # Try changing this to False
    interface_state = "up" # Try changing this to "down"

    print(f"Checking device status for a {device_type}...")

    if device_status == "up":
        print("Device is operational.")
        if device_type == "router":
            print("  This is a router. Specific router tasks can be performed.")
            if config_pending:
                print("  Warning: Configuration changes are pending. Apply or discard.")
            else:
                print("  No pending configuration changes.")
        elif device_type == "switch":
            print("  This is a switch. Specific switch tasks can be performed.")
        else:
            print("  Device type not specifically handled.")

        # Combined condition check
        if device_type == "router" and interface_state == "down":
            print("  Critical Alert: A router interface is down!")
        elif device_type == "switch" and interface_state == "down":
            print("  Warning: A switch interface is down. Check port.")

    elif device_status == "down":
        print("Device is down. Cannot perform any operations.")
    else:
        print("Device status is unknown. Cannot proceed.")

    print("--- Detailed Check Complete ---")
    ```
2.  Experiment with different combinations of `device_status`, `config_pending`, and `interface_state` to see how the output changes.

---

## Lab 4: Control Flow - Loops

**Objective:** Implement `for` and `while` loops for repetitive tasks.

### Task 4.1: Iterate Through a List of Devices (`for` loop)

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `device_loop.py`.
3.  Add the following code to simulate connecting to multiple devices:
    ```python
    device_ips = ["192.168.1.10", "192.168.1.11", "192.168.1.12", "192.168.1.13"]
    device_names = ["R1-HQ", "SW1-Branch", "FW1-DMZ"]

    print("--- Processing Device IPs ---")
    for ip in device_ips:
        print(f"Attempting to connect to IP: {ip}")
        # In a real script, you'd have Netmiko/NAPALM connection code here

    print("\n--- Processing Device Names ---")
    for name in device_names:
        print(f"Performing health check on device: {name}")

    print("\n--- Iterating with range() ---")
    # Use range to perform an action a specific number of times
    for i in range(1, 4): # This will iterate for i = 1, 2, 3
        print(f"Sending configuration batch {i}...")

    print("\n--- Iterating through dictionary items ---")
    device_inventory = {
        "R1": {"ip": "192.168.1.1", "os": "IOS"},
        "SW1": {"ip": "192.168.1.2", "os": "NX-OS"},
        "FW1": {"ip": "192.168.1.3", "os": "ASA"}
    }
    for hostname, details in device_inventory.items():
        print(f"Device: {hostname}, IP: {details['ip']}, OS: {details['os']}")
    ```
4.  Save and run `device_loop.py`.

### Task 4.2: Implement a Retry Mechanism (`while` loop)

1.  In the same `device_loop.py` file, add the following code to simulate retrying a connection attempt until successful or max retries are met.
    ```python
    import time # We need this to simulate a delay

    print("\n--- Connection Retry Mechanism ---")
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
2.  Save and run `device_loop.py`. Observe how the `while` loop behaves.

---

## Lab 5: Functions

**Objective:** Define and use functions to create reusable blocks of code.

### Task 5.1: Create a Simple Function

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `network_functions.py`.
3.  Add a simple function to greet a device:
    ```python
    def greet_device(hostname):
        """
        Prints a greeting message for a given device hostname.
        """
        print(f"Hello, {hostname}! Ready for automation.")

    # Call the function
    greet_device("Router-HQ")
    greet_device("Switch-Access-01")
    ```
4.  Save and run `network_functions.py`.

### Task 5.2: Function with Multiple Parameters and a Return Value

1.  Modify `network_functions.py` by adding a function that simulates sending a command and returns the output.
    ```python
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
        print(f"Connecting to {ip_address}...")
        print(f"Sending command: '{command}'")
        # Simulate different outputs based on command
        if command == "show ip interface brief":
            return f"""
Interface              IP-Address      OK? Method Status        Protocol
GigabitEthernet0/0     192.168.1.1     YES manual up            up
Loopback0              1.1.1.1         YES manual up            up
Vlan1                  unassigned      YES unset  down          down
"""
        elif command == "show version":
            return f"Cisco IOS Software, C800 Series Software (C800-UNIVERSALK9-M), Version 15.6(3)M2, RELEASE SOFTWARE (fc1)\nDevice {ip_address}"
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
3.  Save and run `network_functions.py`.

---

## Lab 6: Modules and Packages

**Objective:** Understand how to use built-in modules and conceptually structure your code into packages.

### Task 6.1: Use Built-in Modules (`os`, `sys`)

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `module_practice.py`.
3.  Add the following code to use the `os` (operating system) and `sys` (system-specific parameters and functions) modules:
    ```python
    import os
    import sys

    print("--- OS Module Examples ---")
    # Get the current working directory
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")

    # List contents of the current directory
    print("Files and directories in current path:")
    for item in os.listdir(current_dir):
        print(f"  - {item}")

    # Check if a file exists
    if os.path.exists("module_practice.py"):
        print("\n'module_practice.py' exists in this directory.")
    else:
        print("\n'module_practice.py' does NOT exist in this directory.")

    print("\n--- Sys Module Examples ---")
    # Get Python version
    print(f"Python version: {sys.version}")

    # Get the platform
    print(f"Operating System Platform: {sys.platform}")

    # Get the Python executable path
    print(f"Python Executable Path: {sys.executable}")
    ```
4.  Save and run `module_practice.py`.

### Task 6.2: Install and Use a Third-Party Module (`requests`)

1.  Ensure your `na_env` virtual environment is active.
2.  Install the `requests` library (a popular library for making HTTP requests):
    ```bash
    pip install requests
    ```
3.  In `module_practice.py`, add the following code to make a simple API call to a public dummy API.
    ```python
    import requests
    import json # For pretty-printing JSON

    print("\n--- Requests Module Example (Dummy API) ---")
    # This is a free, public API for testing: JSONPlaceholder
    api_url = "https://jsonplaceholder.typicode.com/posts/1"

    try:
        response = requests.get(api_url)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

        data = response.json() # Parse JSON response into a Python dictionary
        print(f"Status Code: {response.status_code}")
        print("API Response (JSON):")
        print(json.dumps(data, indent=2)) # Pretty print the JSON

        print(f"\nTitle from API: {data['title']}")

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from API.")
    ```
4.  Save and run `module_practice.py`.

### Task 6.3: Conceptual Package Structure (No Code Execution)

This task is for understanding how packages are structured. You don't need to write executable code for this part, but you can create the directories and empty `__init__.py` files to see the structure.

1.  In your `network_automation_labs` directory, create the following directory and file structure:
    ```
    network_automation_labs/
    ├── na_env/
    ├── hello_network.py
    ├── data_types.py
    ├── device_check.py
    ├── device_loop.py
    ├── network_functions.py
    ├── module_practice.py
    |
    ├── my_network_automation/  <-- This will be your main package directory
    │   ├── __init__.py         <-- Makes 'my_network_automation' a Python package
    │   ├── main.py             <-- Main script that uses other modules
    │   │
    │   ├── device_ops/         <-- Sub-package for device operations
    │   │   ├── __init__.py
    │   │   ├── connect.py      <-- Module for connection functions
    │   │   └── config.py       <-- Module for configuration functions
    │   │
    │   └── utils/              <-- Sub-package for utility functions
    │       ├── __init__.py
    │       └── parser.py       <-- Module for parsing output
    ```
2.  **Conceptual `main.py` content:**
    ```python
    # my_network_automation/main.py

    # Import functions from your custom modules within the package
    from device_ops.connect import connect_to_device
    from device_ops.config import apply_config
    from utils.parser import parse_interface_status

    print("Starting network automation task...")

    # Simulate using functions from your modules
    device_ip = "192.168.1.50"
    username = "admin"
    password = "password"
    commands = ["interface Loopback0", "ip address 1.1.1.1 255.255.255.255"]
    raw_output = "GigabitEthernet0/1 up up"

    # Assume these functions are defined in connect.py, config.py, parser.py
    # connect_to_device(device_ip, username, password)
    # apply_config(device_ip, commands)
    # parsed_data = parse_interface_status(raw_output)

    print("Network automation task completed.")
    ```
    *This demonstrates how `main.py` imports and uses components from other modules within the `my_network_automation` package, showcasing the benefits of organized code.*

---

## Lab 7: Working with Files

**Objective:** Practice reading data from and writing data to text files.

### Task 7.1: Read Device List from a File

1.  Activate your `na_env` virtual environment.
2.  Create a new text file named `devices.txt` in your `network_automation_labs` directory.
3.  Add the following content to `devices.txt`:
    ```
    192.168.1.10
    192.168.1.11
    192.168.1.12
    router-hq.example.com
    switch-access.example.com
    ```
4.  Create a new Python file named `file_io_lab.py`.
5.  Add the following code to read the device IPs/hostnames from `devices.txt`:
    ```python
    print("--- Reading Device List from devices.txt ---")
    device_targets = []
    try:
        with open("devices.txt", "r") as f:
            for line in f:
                device_targets.append(line.strip()) # .strip() removes whitespace including newlines
        print("Successfully read devices:")
        for device in device_targets:
            print(f"- {device}")
    except FileNotFoundError:
        print("Error: 'devices.txt' not found. Please create it as instructed.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    ```
6.  Save and run `file_io_lab.py`.

### Task 7.2: Write Configuration Backup to a File

1.  In the same `file_io_lab.py` file, add the following code to simulate writing a configuration backup to a new file.
    ```python
    print("\n--- Writing Configuration Backup to File ---")
    device_config = """
version 15.6
hostname My-Lab-Router
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface Loopback0
 ip address 10.0.0.1 255.255.255.255
end
"""
    backup_filename = "My-Lab-Router_config_backup_20250901.txt"

    try:
        with open(backup_filename, "w") as f: # 'w' mode will create or overwrite the file
            f.write(device_config)
        print(f"Configuration backup successfully written to: {backup_filename}.")
    except IOError as e:
        print(f"Error writing backup file: {e}")
    ```
2.  Save and run `file_io_lab.py`.
3.  Check your `network_automation_labs` directory. You should find a new file named `My-Lab-Router_config_backup_20250901.txt` containing the configuration.

### Task 7.3: Append to a Log File

1.  In the same `file_io_lab.py` file, add the following code to append log entries to a file.
    ```python
    import datetime

    print("\n--- Appending to a Log File ---")
    log_filename = "automation_log.txt"

    def log_action(message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        try:
            with open(log_filename, "a") as f: # 'a' mode appends to the file
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
3.  Open `automation_log.txt` to see the appended entries.

---

## Lab 8: Introduction to Network Automation Libraries (Conceptual & Simple API Interaction)

**Objective:** Understand the conceptual usage of Netmiko and NAPALM, and perform a simple API interaction using `requests`.

**Note:** For this lab, you will not be connecting to actual network devices unless you have a lab environment (e.g., GNS3, EVE-NG, or virtual machines) set up. The provided code snippets for Netmiko and NAPALM are conceptual to demonstrate their structure and common methods. The `requests` part will interact with a public dummy API.

### Task 8.1: Conceptual Netmiko Usage

1.  Activate your `na_env` virtual environment.
2.  Install Netmiko (even if you don't have a real device, this ensures the library is available):
    ```bash
    pip install netmiko
    ```
3.  Create a new Python file named `net_libs_lab.py`.
4.  Add the following conceptual Netmiko code:
    ```python
    # net_libs_lab.py
    from netmiko import ConnectHandler
    import time

    print("--- Conceptual Netmiko Usage ---")

    # Define a dummy device dictionary (replace with your actual device details if you have one)
    dummy_device = {
        "device_type": "cisco_ios",
        "host": "192.168.1.100", # Placeholder IP
        "username": "admin",
        "password": "cisco",
        "secret": "enable"
    }

    try:
        # Simulate connecting (this part would fail without a real device)
        print(f"Attempting to connect to {dummy_device['host']} using Netmiko...")
        # with ConnectHandler(**dummy_device) as net_connect:
        #     net_connect.enable() # Enter enable mode
        #     output = net_connect.send_command("show version")
        #     print("\n--- Simulated 'show version' output ---")
        #     print(output)
        #     config_output = net_connect.send_config_set(["hostname NEW_HOSTNAME", "no logging console"])
        #     print("\n--- Simulated config output ---")
        #     print(config_output)

        print("Netmiko connection and command execution simulated successfully.")
        print("To run this for real, you need a reachable network device and correct credentials.")
        print("Commented out actual Netmiko calls to prevent errors in this lab environment.")

    except Exception as e:
        print(f"An error occurred during Netmiko conceptual usage (expected if no real device): {e}")

    ```
5.  Save and run `net_libs_lab.py`. Observe the output indicating the conceptual nature.

### Task 8.2: Conceptual NAPALM Usage

1.  Ensure your `na_env` virtual environment is active.
2.  Install NAPALM:
    ```bash
    pip install napalm
    ```
3.  In `net_libs_lab.py`, add the following conceptual NAPALM code:
    ```python
    # Continue in net_libs_lab.py
    from napalm import get_network_driver
    import json # For pretty printing JSON output

    print("\n--- Conceptual NAPALM Usage ---")

    # Define a dummy device dictionary for NAPALM
    dummy_napalm_device = {
        "hostname": "192.168.1.101", # Placeholder IP
        "username": "admin",
        "password": "cisco",
        "optional_args": {"secret": "enable"}
    }

    try:
        # Get the appropriate driver (e.g., 'ios', 'junos', 'nxos', 'eos')
        driver = get_network_driver("ios")

        # Simulate connecting and getting facts
        print(f"Attempting to connect to {dummy_napalm_device['hostname']} using NAPALM...")
        # with driver(**dummy_napalm_device) as device:
        #     device.open()
        #     facts = device.get_facts()
        #     print("\n--- Simulated Device Facts (NAPALM) ---")
        #     print(json.dumps(facts, indent=2))
        #     interfaces = device.get_interfaces()
        #     print("\n--- Simulated Interfaces (NAPALM) ---")
        #     print(json.dumps(interfaces, indent=2))
        #     device.close()

        print("NAPALM connection and getter execution simulated successfully.")
        print("To run this for real, you need a reachable network device and correct credentials.")
        print("Commented out actual NAPALM calls to prevent errors in this lab environment.")

    except Exception as e:
        print(f"An error occurred during NAPALM conceptual usage (expected if no real device): {e}")
    ```
4.  Save and run `net_libs_lab.py`.

### Task 8.3: Simple API Interaction with `requests`

1.  Ensure your `na_env` virtual environment is active. (You should have installed `requests` in Lab 6, Task 6.2).
2.  In `net_libs_lab.py`, add the following code to interact with a public API. This part *will* execute successfully as it doesn't require a local network device.
    ```python
    # Continue in net_libs_lab.py
    import requests
    import json

    print("\n--- Real API Interaction with Requests (Public Dummy API) ---")

    # This API provides fake data for testing
    # We will get a list of fake 'users'
    users_api_url = "https://jsonplaceholder.typicode.com/users"

    try:
        print(f"Making GET request to: {users_api_url}")
        response = requests.get(users_api_url)
        response.raise_for_status() # Check for HTTP errors (4xx or 5xx)

        users_data = response.json() # Parse the JSON response

        print(f"Successfully retrieved {len(users_data)} users.")
        print("First 3 users:")
        for i, user in enumerate(users_data[:3]): # Iterate through first 3 users
            print(f"  User {i+1}:")
            print(f"    ID: {user['id']}")
            print(f"    Name: {user['name']}")
            print(f"    Email: {user['email']}")
            print(f"    City: {user['address']['city']}") # Access nested dictionary
            print("-" * 20)

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from API.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    ```
3.  Save and run `net_libs_lab.py`. You should see actual data retrieved from the API.

---

## Conclusion

Congratulations! You've completed the Python Basics for Network Automation Lab Guide. You've gained hands-on experience with core Python concepts, file operations, and a conceptual understanding of how Python libraries are used in network automation.

Keep practicing, explore the documentation of libraries like Netmiko and NAPALM, and start thinking about how you can apply these skills to automate tasks in your own network environment.

**Happy Automating!**