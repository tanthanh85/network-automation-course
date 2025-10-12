# NASP: Module 3 Lab Guide

## Programming Automation using Netmiko Library - Hands-on Exercises

---

## Introduction

Welcome to Module 3 of the Python Basics for Network Automation Lab Guide! In this module, you will gain hands-on experience with the Netmiko library. We will use actual Netmiko library calls in the code. For these labs, you will use **dummy IP addresses and credentials** initially. **It is crucial that you replace these dummy values with the actual IP addresses, usernames, and passwords of your lab equipment (e.g., Cisco IOS XE routers in a sandbox) to make the code functional.**

A key focus of this module is **project organization**. Instead of putting all code in one file, we will separate our code into logical modules, which is a best practice for any automation project.

**Lab Objectives:**
*   Install the Netmiko library.
*   Organize your project into separate Python files for devices, Netmiko operations, and lab execution.
*   Define Netmiko device dictionaries with real parameters.
*   Connect to a single network device using Netmiko.
*   Send `show` commands and capture output.
*   Push configuration changes.
*   Perform configuration backups.
*   Manage multiple network devices concurrently using `ThreadPoolExecutor`.
*   Implement robust error handling for Netmiko operations.

**Prerequisites:**
*   Completion of Module 1 and Module 2 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   **Access to a network device (e.g., Cisco IOS XE router, virtual lab device) with SSH enabled and known credentials.** You will need to replace dummy values with your device's actual information.

Let's start automating with Netmiko!

---

## Lab Setup: Creating Your Project Structure

Before we write any code, let's set up the recommended project structure.

1.  **Navigate** to your main `network_automation_labs` directory (from Module 1).
2.  **Create a new directory** for this module's labs:
    ```bash
    mkdir module3_netmiko_lab
    cd module3_netmiko_lab
    ```
3.  **Inside `module3_netmiko_lab`, create the following empty files:**
    *   `__init__.py` (This makes `module3_netmiko_lab` a Python package, allowing relative imports)
    *   `devices.py`
    *   `netmiko_operations.py`
    *   `lab_single_device.py`
    *   `lab_multi_device.py`

    Your directory structure should now look like this:
    ```
    network_automation_labs/
    ├── na_env/
    ├── module3_netmiko_lab/
    │   ├── __init__.py
    │   ├── devices.py
    │   ├── netmiko_operations.py
    │   ├── lab_single_device.py
    │   └── lab_multi_device.py
    ├── ... (other module files)
    ```

### Task 0.1: Populate `devices.py`

This file will store the connection details for your network devices.

1.  Open `devices.py` in your code editor.
2.  Add the following Python code. **Remember to replace the DUMMY VALUES with your actual lab device details!**
    ```python
    # devices.py

    # --- SINGLE DEVICE FOR LAB 1 & 2 ---
    # REPLACE THESE DUMMY VALUES WITH YOUR ACTUAL LAB DEVICE DETAILS!
    # This device should be reachable and have SSH enabled with the provided credentials.
    single_device = {
        "device_type": "cisco_ios",
        "host": "10.10.20.48", # DUMMY IP - REPLACE WITH YOUR DEVICE'S IP
        "username": "developer", # DUMMY USERNAME - REPLACE WITH YOUR DEVICE'S USERNAME
        "password": "C1sco12345", # DUMMY PASSWORD - REPLACE WITH YOUR DEVICE'S PASSWORD
        "secret": "dummy_enable", # DUMMY ENABLE PASSWORD - REPLACE IF YOUR DEVICE USES ONE
        "port": 22, # Default SSH port
        # "session_log": "device_session.log", # Uncomment to log SSH session
    }

    # --- MULTIPLE DEVICES FOR LAB 3 ---
    # REPLACE THESE DUMMY VALUES WITH YOUR ACTUAL LAB DEVICE DETAILS!
    # Add as many devices as you have available in your lab.
    multi_devices = [
        {
            "device_type": "cisco_ios",
            "host": "10.10.20.48", # DUMMY IP 1 (can be the same as single_device if you only have one)
            "username": "developer",
            "password": "C1sco12345",
            "secret": "dummy_enable",
        },
        {
            "device_type": "cisco_xr", # in Cisco Sandbox, this is a IOS XR router
            "host": "10.10.20.35", # DUMMY IP 2
            "username": "developer",
            "password": "C1sco12345",
            "secret": "dummy_enable",
        }

        # Add more device dictionaries here if you have more lab devices
        # Example:
        # {
        #     "device_type": "cisco_ios",
        #     "host": "192.168.1.13",
        #     "username": "dummy_user",
        #     "password": "dummy_password",
        #     "secret": "dummy_enable",
        # },
    ]
    ```
3.  Save `devices.py`.

### Task 0.2: Populate `netmiko_operations.py`

This file will contain all the reusable Netmiko functions.

1.  Open `netmiko_operations.py` in your code editor.
2.  Add the following Python code:
    ```python
    # netmiko_operations.py
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoBaseException
    import datetime
    import os
    import time # For ThreadPoolExecutor to see progress

    def get_netmiko_connection(device_info):
        """
        Establishes and returns a Netmiko connection object.
        Handles common connection exceptions.
        """
        host = device_info.get("host", "Unknown Host")
        try:
            # Use 'with' statement for ConnectHandler to ensure proper closing
            # However, for ThreadPoolExecutor, we return the object and let the caller manage 'with'
            # For simplicity here, we'll connect and return, but a real app might pass connection around.
            # For this lab, we'll connect inside each operation function.
            pass # We'll connect inside each specific operation function below
        except NetmikoTimeoutException:
            print(f"Error: Connection to {host} timed out. Device might be unreachable or SSH is not enabled.")
            raise # Re-raise to propagate the error
        except NetmikoAuthenticationException:
            print(f"Error: Authentication failed for {host}. Check username/password/enable password.")
            raise
        except NetmikoBaseException as e:
            print(f"An Netmiko-specific error occurred connecting to {host}: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred connecting to {host}: {e}")
            raise

    def get_device_info(device_info, command="show version"):
        """
        Connects to a device and sends a show command.
        Returns the command output or an error message.
        """
        host = device_info.get("host", "Unknown Host")
        try:
            with ConnectHandler(**device_info) as net_connect:
                print(f"[{host}] Connected. Sending command: '{command}'...")
                output = net_connect.send_command(command)
                return output
        except Exception as e:
            return f"Error getting info from {host}: {e}"

    def apply_config_commands(device_info, config_commands):
        """
        Connects to a device and applies a list of configuration commands.
        Returns the configuration output or an error message.
        """
        host = device_info.get("host", "Unknown Host")
        try:
            with ConnectHandler(**device_info) as net_connect:
                print(f"[{host}] Connected. Applying configuration...")
                output = net_connect.send_config_set(config_commands)
                return output
        except Exception as e:
            return f"Error applying config to {host}: {e}"

    def backup_running_config(device_info):
        """
        Connects to a device, collects running-config, and saves it to a file.
        Returns a success message or an error message.
        """
        host = device_info.get("host", "Unknown Host")
        try:
            with ConnectHandler(**device_info) as net_connect:
                print(f"[{host}] Connected. Collecting running-config for backup...")
                running_config = net_connect.send_command("show running-config")
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{host}_running_config_{timestamp}.txt"
                
                with open(backup_filename, "w") as f:
                    f.write(running_config)
                
                return f"Successfully backed up {host} to {backup_filename}"
        except Exception as e:
            return f"Error backing up {host}: {e}"

    def process_device_concurrently(device_info):
        """
        Function to be executed by each thread for a single device in concurrent labs.
        Performs multiple operations and returns a summary.
        """
        host = device_info.get("host", "Unknown Host")
        summary = [f"--- Processing {host} ---"]
        try:
            with ConnectHandler(**device_info) as net_connect:
                # 1. Get version
                version_output = net_connect.send_command("show version")
                summary.append(f"  Version: {version_output.splitlines()}")

                # 2. Apply simple config
                config_commands = [f"hostname {host}-AUTOMATED", "interface Loopback99", "ip address 10.0.0.99 255.255.255.255", "no shutdown"]
                net_connect.send_config_set(config_commands)
                summary.append("  Config applied (hostname, Loopback99).")

                # 3. Backup running-config
                running_config = net_connect.send_command("show running-config")
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{host}_running_config_{timestamp}.txt"
                with open(backup_filename, "w") as f:
                    f.write(running_config)
                summary.append(f"  Backed up running-config to {backup_filename}.")
            
            summary.append(f"--- {host} Processed Successfully ---")
            return "\n".join(summary)
        except NetmikoTimeoutException:
            return f"--- {host} Failed: Connection timed out. Device unreachable or SSH issue. ---"
        except NetmikoAuthenticationException:
            return f"--- {host} Failed: Authentication failed. Check username/password/enable password. ---"
        except NetmikoBaseException as e:
            return f"--- {host} Failed: Netmiko error - {e} ---"
        except Exception as e:
            return f"--- {host} Failed: Unexpected error - {e} ---"
    ```
3.  Save `netmiko_operations.py`.

---

## Lab 1: Netmiko Basics - Connecting and Sending Commands (Single Device)

**Objective:** Get familiar with Netmiko's `ConnectHandler` and `send_command()` method.

### Task 1.1: Install Netmiko

1.  Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).
2.  Navigate into your `module3_netmiko_lab` directory:
    ```bash
    cd module3_netmiko_lab
    ```
3.  Install Netmiko:
    ```bash
    pip install netmiko
    ```
    *Expected Observation:* Netmiko and its dependencies will be installed. You should see a "Successfully installed..." message.

### Task 1.2: Connect to a Single Device

We will use the actual `netmiko.ConnectHandler` to attempt a connection.

1.  Open `lab_single_device.py` in your code editor.
2.  Add the following code. This script will import the `single_device` dictionary and the `get_device_info` function.
    ```python
    # lab_single_device.py
    from devices import single_device # Import the single device dictionary
    from netmiko_operations import get_device_info, apply_config_commands, backup_running_config # Import the function to get device info

    print("--- Lab 1.2: Connect to a Single Device ---")
    
    # We call get_device_info with a simple command to test connectivity
    # The function handles the connection and disconnection internally.
    output = get_device_info(single_device, command="show clock")
    
    print("\n--- Connection Test Result ---")
    print(output)
    print("\nLab 1.2 complete.")
    ```
3.  Save `lab_single_device.py`.
4.  **Run the script** from your `module3_netmiko_lab` directory:
    ```bash
    python lab_single_device.py
    ```
    *Expected Output (if dummy IP is unreachable or credentials are wrong):*
    ```
    --- Lab 1.2: Connect to a Single Device ---
    [192.168.1.10] Connected. Sending command: 'show clock'...
    Error: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.

    --- Connection Test Result ---
    Error getting info from 192.168.1.10: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.

    Lab 1.2 complete.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects):*
    ```
    --- Lab 1.2: Connect to a Single Device ---
    [YOUR_DEVICE_IP] Connected. Sending command: 'show clock'...

    --- Connection Test Result ---
    YOUR_DEVICE_PROMPT#show clock
    *02:30:00.000 UTC Mon Sep 1 2025

    Lab 1.2 complete.
    ```

### Task 1.3: Send `show` Commands

Now, use the `get_device_info()` function to retrieve more detailed information from the device.

1.  Open `lab_single_device.py` in your code editor.
2.  Add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 1.3: Send 'show' Commands ---")

    print("\nCollecting 'show version'...")
    version_output = get_device_info(single_device, command="show version")
    print("\n--- show version output ---")
    print(version_output[:500] + "...") # Print first 500 characters for brevity

    print("\nCollecting 'show ip interface brief'...")
    ip_int_brief_output = get_device_info(single_device, command="show ip interface brief")
    print("\n--- show ip interface brief output ---")
    print(ip_int_brief_output)

    print("\nLab 1.3 complete.")
    ```
3.  Save `lab_single_device.py`.
4.  **Run the script** from your `module3_netmiko_lab` directory:
    ```bash
    python lab_single_device.py
    ```
    *Expected Output (if dummy IP is unreachable or credentials are wrong, you'll see errors for each call):*
    ```
    --- Lab 1.3: Send 'show' Commands ---

    Collecting 'show version'...
    [192.168.1.10] Connected. Sending command: 'show version'...
    Error: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.

    --- show version output ---
    Error getting info from 192.168.1.10: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled....

    Collecting 'show ip interface brief'...
    [192.168.1.10] Connected. Sending command: 'show ip interface brief'...
    Error: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.

    --- show ip interface brief output ---
    Error getting info from 192.168.1.10: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.

    Lab 1.3 complete.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects):*
    ```
    --- Lab 1.3: Send 'show' Commands ---

    Collecting 'show version'...
    [YOUR_DEVICE_IP] Connected. Sending command: 'show version'...

    --- show version output ---
    Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.9.4
    ... (actual version output from your device) ...

    Collecting 'show ip interface brief'...
    [YOUR_DEVICE_IP] Connected. Sending command: 'show ip interface brief'...

    --- show ip interface brief output ---
    Interface              IP-Address      OK? Method Status        Protocol
    GigabitEthernet0/0     192.168.1.1     YES manual up            up
    Loopback0              1.1.1.1         YES manual up            up
    Vlan1                  unassigned      YES unset  down          down
    ... (actual interface brief output from your device) ...

    Lab 1.3 complete.
    ```

---

## Lab 2: Automating Configuration and Backups (Single Device)

**Objective:** Learn to use `apply_config_commands()` for configuration and `backup_running_config()` for backup.

### Task 2.1: Push Configuration Changes

1.  Open `lab_single_device.py` in your code editor.
2.  Add the following code:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 2.1: Push Configuration Changes ---")

    config_commands = [
        "interface Loopback100",
        "description CONFIGURED_BY_NETMIKO_LAB",
        "ip address 10.0.0.100 255.255.255.255",
        "no shutdown",
        "router ospf 1",
        "network 10.0.0.0 0.0.0.255 area 0"
    ]

    print("\nApplying configuration commands...")
    config_output = apply_config_commands(single_device, config_commands)
    print("\n--- Configuration Output ---")
    print(config_output)

    print("\nLab 2.1 complete.")
    ```
3.  Save `lab_single_device.py`.
4.  **Run the script** from your `module3_netmiko_lab` directory:
    ```bash
    python lab_single_device.py
    ```
    *Expected Output (if dummy IP is unreachable or credentials are wrong):*
    ```
    --- Lab 2.1: Push Configuration Changes ---

    Applying configuration commands...
    [192.168.1.10] Connected. Applying configuration...
    Error applying config to 192.168.1.10: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.

    --- Configuration Output ---
    Error applying config to 192.168.1.10: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.

    Lab 2.1 complete.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects):*
    ```
    --- Lab 2.1: Push Configuration Changes ---

    Applying configuration commands...
    [YOUR_DEVICE_IP] Connected. Applying configuration...

    --- Configuration Output ---
    config terminal
    Enter configuration commands, one per line.  End with CNTL/Z.
    YOUR_DEVICE_PROMPT(config)#interface Loopback100
    YOUR_DEVICE_PROMPT(config-if)#description CONFIGURED_BY_NETMIKO_LAB
    YOUR_DEVICE_PROMPT(config-if)#ip address 10.0.0.100 255.255.255.255
    YOUR_DEVICE_PROMPT(config-if)#no shutdown
    YOUR_DEVICE_PROMPT(config-if)#router ospf 1
    YOUR_DEVICE_PROMPT(config-router)#network 10.0.0.0 0.0.0.255 area 0
    YOUR_DEVICE_PROMPT(config-router)#end
    YOUR_DEVICE_PROMPT#

    Lab 2.1 complete.
    ```
    *Observation:* If you connected to a real device, you could now log in and verify the Loopback100 interface and OSPF configuration.

### Task 2.2: Perform Configuration Backups

1.  Open `lab_single_device.py` in your code editor.
2.  Add the following code:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 2.2: Perform Configuration Backups ---")

    print("\nCollecting 'show running-config' for backup...")
    backup_result = backup_running_config(single_device)
    print(backup_result)

    print("\nLab 2.2 complete.")
    ```
3.  Save `lab_single_device.py`.
4.  **Run the script** from your `module3_netmiko_lab` directory:
    ```bash
    python lab_single_device.py
    ```
    *Expected Output (if dummy IP is unreachable or credentials are wrong):*
    ```
    --- Lab 2.2: Perform Configuration Backups ---

    Collecting 'show running-config' for backup...
    [192.168.1.10] Connected. Collecting running-config for backup...
    Error backing up 192.168.1.10: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.

    Lab 2.2 complete.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects, filename timestamp will vary):*
    ```
    --- Lab 2.2: Perform Configuration Backups ---

    Collecting 'show running-config' for backup...
    [YOUR_DEVICE_IP] Connected. Collecting running-config for backup...
    Successfully backed up YOUR_DEVICE_IP to YOUR_DEVICE_IP_running_config_20250901_HHMMSS.txt

    Lab 2.2 complete.
    ```
    *Expected File Creation:* A file named `YOUR_DEVICE_IP_running_config_YYYYMMDD_HHMMSS.txt` (with the current date/time) will be created in your `module3_netmiko_lab` directory. It will contain the `show running-config` output from your device.

---

## Lab 3: Managing Multiple Network Devices at Scale (Concurrency)

**Objective:** Apply concurrency concepts from Module 2 to manage multiple devices using Netmiko, leveraging `ThreadPoolExecutor` for concurrent connections.

### Task 3.1: Use `ThreadPoolExecutor` for Concurrent Processing
The Cisco sandbox lab has one IOS XE router and one IOS XR router. However SSH is not enabled on IOS XR router when the lab started. Please SSH to IOS XR router and issue the following commands:
```bash
    crypto key generate rsa
    configure terminal
    ssh server v2
    commit
```

1.  Open `lab_multi_device.py` in your code editor.
2.  Add the following code. This script will import the `multi_devices` list and the `process_device_concurrently` function.
    ```python
    # lab_multi_device.py
    from concurrent.futures import ThreadPoolExecutor
    import time

    from devices import multi_devices # Import the list of multiple devices
    from netmiko_operations import process_device_concurrently # Import the concurrent processing function

    print("--- Lab 3.1: Managing Multiple Devices at Scale (Concurrency) ---")
    # Adjust max_workers based on your system's capabilities and device limits.
    # Too many can overwhelm your machine or the devices.
    max_workers = 3 # Number of concurrent threads

    start_time = time.time()
    results_list = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # map() applies process_device_concurrently to each device in multi_devices
        # and returns results as they complete.
        for result in executor.map(process_device_concurrently, multi_devices):
            results_list.append(result)

    end_time = time.time()

    print("\n--- All Device Processing Complete ---")
    for res in results_list:
        print(res)
        print("-" * 40) # Separator for clarity

    print(f"\nTotal processing time: {end_time - start_time:.2f} seconds.")
    print(f"Processed {len(multi_devices)} devices with {max_workers} concurrent workers.")

    print("\nLab 3.1 complete.")
    ```
3.  Save `lab_multi_device.py`.
4.  **Run the script** from your `module3_netmiko_lab` directory:
    ```bash
    python lab_multi_device.py
    ```
    *Expected Output (if using dummy IPs/credentials, you'll see errors):*
    ```
    --- Lab 3.1: Managing Multiple Devices at Scale (Concurrency) ---
    [192.168.1.10] Connected. Collecting version...
    [192.168.1.11] Connected. Collecting version...
    [192.168.1.12] Connected. Collecting version...
    --- 192.168.1.10 Failed: Connection timed out. Device unreachable or SSH issue. ---
    --- 192.168.1.11 Failed: Connection timed out. Device unreachable or SSH issue. ---
    --- 192.168.1.12 Failed: Connection timed out. Device unreachable or SSH issue.

    --- All Device Processing Complete ---
    --- 192.168.1.10 Failed: Connection timed out. Device unreachable or SSH issue. ---
    ----------------------------------------
    --- 192.168.1.11 Failed: Connection timed out. Device unreachable or SSH issue. ---
    ----------------------------------------
    --- 192.168.1.12 Failed: Connection timed out. Device unreachable or SSH issue. ---
    ----------------------------------------

    Total processing time: X.xx seconds.
    Processed 3 devices with 3 concurrent workers.

    Lab 3.1 complete.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects, order will be interleaved):*
    ```
    --- Lab 3.1: Managing Multiple Devices at Scale (Concurrency) ---
    [YOUR_DEVICE_IP_1] Connected. Collecting version...
    [YOUR_DEVICE_IP_2] Connected. Collecting version...
    [YOUR_DEVICE_IP_3] Connected. Collecting version...
    [YOUR_DEVICE_IP_1] Applying simple config...
    [YOUR_DEVICE_IP_2] Applying simple config...
    [YOUR_DEVICE_IP_3] Applying simple config...
    [YOUR_DEVICE_IP_1] Backed up running-config to YOUR_DEVICE_IP_1_running_config_20250901_HHMMSS.txt.
    [YOUR_DEVICE_IP_2] Backed up running-config to YOUR_DEVICE_IP_2_running_config_20250901_HHMMSS.txt.
    [YOUR_DEVICE_IP_3] Backed up running-config to YOUR_DEVICE_IP_3_running_config_20250901_HHMMSS.txt.

    --- All Device Processing Complete ---
    --- Processing YOUR_DEVICE_IP_1 ---
      Version: Cisco IOS Software, IOS-XE Software, ...
      Config applied (hostname, Loopback99).
      Backed up running-config to YOUR_DEVICE_IP_1_running_config_20250901_HHMMSS.txt.
    --- YOUR_DEVICE_IP_1 Processed Successfully ---
    ----------------------------------------
    --- Processing YOUR_DEVICE_IP_2 ---
      Version: Cisco IOS Software, IOS-XE Software, ...
      Config applied (hostname, Loopback99).
      Backed up running-config to YOUR_DEVICE_IP_2_running_config_20250901_HHMMSS.txt.
    --- YOUR_DEVICE_IP_2 Processed Successfully ---
    ----------------------------------------
    --- Processing YOUR_DEVICE_IP_3 ---
      Version: Cisco IOS Software, IOS-XE Software, ...
      Config applied (hostname, Loopback99).
      Backed up running-config to YOUR_DEVICE_IP_3_running_config_20250901_HHMMSS.txt.
    --- YOUR_DEVICE_IP_3 Processed Successfully ---
    ----------------------------------------

    Total processing time: X.xx seconds.
    Processed 3 devices with 3 concurrent workers.

    Lab 3.1 complete.
    ```
    *Observation:* The total time taken will be significantly less than if you processed each device one by one, demonstrating the power of concurrency for I/O-bound tasks like network automation. You will also find backup files for each processed device in your `module3_netmiko_lab` directory.

---

## Conclusion

You've now completed Module 3 and gained practical experience with the Netmiko library! You can now:

*   Understand Netmiko's role in network automation.
*   Organize your Python automation code into a modular project structure.
*   Define device connection parameters.
*   Connect to devices and send commands.
*   Push configuration changes and perform backups.
*   Apply concurrency concepts to manage multiple devices efficiently.
*   Implement basic error handling for network operations.

Netmiko is a fundamental tool for CLI-based network automation. In the next modules, you'll explore other aspects of network automation, including working with APIs and structured data.

**Keep Automating!**

---