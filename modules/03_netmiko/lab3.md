# Python Basics for Network Automation: Module 3 Lab Guide

## Programming Automation using Netmiko Library - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 3 of the Python Basics for Network Automation Lab Guide! In this module, you will gain hands-on experience with the Netmiko library. We will use actual Netmiko library calls in the code. For these labs, you will use **dummy IP addresses and credentials** initially. **It is crucial that you replace these dummy values with the actual IP addresses, usernames, and passwords of your lab equipment (e.g., Cisco IOS XE routers in a sandbox) to make the code functional.**

**Lab Objectives:**
*   Install the Netmiko library.
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

## Lab 1: Netmiko Basics - Connecting and Sending Commands (Single Device)

**Objective:** Get familiar with Netmiko's `ConnectHandler` and `send_command()` method.

### Task 1.1: Install Netmiko

1.  Activate your `na_env` virtual environment in your terminal.
2.  Install Netmiko:
    ```bash
    pip install netmiko
    ```
    *Expected Observation:* Netmiko and its dependencies will be installed. You should see a "Successfully installed..." message.

### Task 1.2: Connect to a Single Device

We will use the actual `netmiko.ConnectHandler` to attempt a connection.

1.  Create a new Python file named `netmiko_lab.py`.
2.  Add the following code to the file. **Remember to replace the dummy values with your actual lab device details!**
    ```python
    # netmiko_lab.py
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoException
    import time
    import datetime # For backup filename
    import os       # For checking file existence

    # --- Dummy Device Information (REPLACE WITH YOUR ACTUAL LAB DEVICE DETAILS) ---
    # These are placeholder values. Your code will not work until you replace them.
    cisco_device = {
        "device_type": "cisco_ios",
        "host": "192.168.1.10", # DUMMY IP - REPLACE WITH YOUR DEVICE'S IP
        "username": "dummy_user", # DUMMY USERNAME - REPLACE WITH YOUR DEVICE'S USERNAME
        "password": "dummy_password", # DUMMY PASSWORD - REPLACE WITH YOUR DEVICE'S PASSWORD
        "secret": "dummy_enable", # DUMMY ENABLE PASSWORD - REPLACE IF YOUR DEVICE USES ONE
        "port": 22, # Default SSH port
        # "session_log": "device_session.log", # Uncomment to log SSH session
    }

    print("--- Lab 1.2: Connect to a Single Device ---")
    net_connect = None # Initialize connection variable
    try:
        # Establish the SSH connection using ConnectHandler
        # The 'with' statement ensures the connection is properly closed
        with ConnectHandler(**cisco_device) as net_connect:
            print(f"Successfully connected to {cisco_device['host']}.")
            # You can perform operations here
        print(f"Connection to {cisco_device['host']} closed.")
    except NetmikoTimeoutException:
        print(f"Error: Connection to {cisco_device['host']} timed out. Device might be unreachable or SSH is not enabled.")
    except NetmikoAuthenticationException:
        print(f"Error: Authentication failed for {cisco_device['host']}. Check username/password/enable password.")
    except NetmikoException as e:
        print(f"An Netmiko-specific error occurred connecting to {cisco_device['host']}: {e}")
    except Exception as e: # Catch any other unexpected errors
        print(f"An unexpected error occurred connecting to {cisco_device['host']}: {e}")
    ```
3.  Save and run `netmiko_lab.py`.
    *Expected Output (if dummy IP is unreachable or credentials are wrong):*
    ```
    --- Lab 1.2: Connect to a Single Device ---
    Error: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects):*
    ```
    --- Lab 1.2: Connect to a Single Device ---
    Successfully connected to YOUR_DEVICE_IP.
    Connection to YOUR_DEVICE_IP closed.
    ```

### Task 1.3: Send `show` Commands

Now, use the `send_command()` method to retrieve information from the device.

1.  In `netmiko_lab.py`, add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 1.3: Send 'show' Commands ---")
    net_connect = None
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            print(f"Connected to {cisco_device['host']}.")

            # Send 'show version' command
            print("\nCollecting 'show version'...")
            version_output = net_connect.send_command("show version")
            print("\n--- show version output ---")
            print(version_output[:500] + "...") # Print first 500 characters for brevity

            # Send 'show ip interface brief' command
            print("\nCollecting 'show ip interface brief'...")
            ip_int_brief_output = net_connect.send_command("show ip interface brief")
            print("\n--- show ip interface brief output ---")
            print(ip_int_brief_output)

        print(f"Command collection complete for {cisco_device['host']}.")
    except NetmikoTimeoutException:
        print(f"Error: Connection to {cisco_device['host']} timed out during command execution.")
    except NetmikoAuthenticationException:
        print(f"Error: Authentication failed for {cisco_device['host']}. Check username/password/enable password.")
    except NetmikoException as e:
        print(f"An Netmiko-specific error occurred during command collection for {cisco_device['host']}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during command collection for {cisco_device['host']}: {e}")
    ```
2.  Save and run `netmiko_lab.py`.
    *Expected Output (if dummy IP is unreachable or credentials are wrong):*
    ```
    --- Lab 1.3: Send 'show' Commands ---
    Error: Connection to 192.168.1.10 timed out during command execution.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects):*
    ```
    --- Lab 1.3: Send 'show' Commands ---
    Connected to YOUR_DEVICE_IP.

    Collecting 'show version'...

    --- show version output ---
    Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.9.4
    ... (actual version output from your device) ...

    Collecting 'show ip interface brief'...

    --- show ip interface brief output ---
    Interface              IP-Address      OK? Method Status        Protocol
    GigabitEthernet0/0     192.168.1.1     YES manual up            up
    Loopback0              1.1.1.1         YES manual up            up
    Vlan1                  unassigned      YES unset  down          down
    ... (actual interface brief output from your device) ...
    Command collection complete for YOUR_DEVICE_IP.
    ```

---

## Lab 2: Automating Configuration and Backups (Single Device)

**Objective:** Learn to use `send_config_set()` for configuration and capture `show running-config` for backup.

### Task 2.1: Push Configuration Changes

1.  In `netmiko_lab.py`, add the following code:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 2.1: Push Configuration Changes ---")
    net_connect = None
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            print(f"Connected to {cisco_device['host']}.")

            config_commands = [
                "interface Loopback100",
                "description CONFIGURED_BY_NETMIKO_LAB",
                "ip address 10.0.0.100 255.255.255.255",
                "no shutdown",
                "router ospf 1",
                "network 10.0.0.0 0.0.0.255 area 0"
            ]

            print("\nApplying configuration commands...")
            # send_config_set handles entering and exiting config mode
            config_output = net_connect.send_config_set(config_commands)
            print("\n--- Configuration Output ---")
            print(config_output)

            print(f"Configuration applied to {cisco_device['host']}.")
        
    except NetmikoTimeoutException:
        print(f"Error: Connection to {cisco_device['host']} timed out during config application.")
    except NetmikoAuthenticationException:
        print(f"Error: Authentication failed for {cisco_device['host']}. Check username/password/enable password.")
    except NetmikoException as e:
        print(f"An Netmiko-specific error occurred during config application for {cisco_device['host']}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during config application for {cisco_device['host']}: {e}")
    ```
2.  Save and run `netmiko_lab.py`.
    *Expected Output (if dummy IP is unreachable or credentials are wrong):*
    ```
    --- Lab 2.1: Push Configuration Changes ---
    Error: Connection to 192.168.1.10 timed out during config application.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects):*
    ```
    --- Lab 2.1: Push Configuration Changes ---
    Connected to YOUR_DEVICE_IP.

    Applying configuration commands...

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
    Configuration applied to YOUR_DEVICE_IP.
    ```
    *Observation:* If you connected to a real device, you could now log in and verify the Loopback100 interface and OSPF configuration.

### Task 2.2: Perform Configuration Backups

1.  In `netmiko_lab.py`, add the following code:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 2.2: Perform Configuration Backups ---")
    net_connect = None
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            print(f"Connected to {cisco_device['host']}.")

            print("\nCollecting 'show running-config' for backup...")
            running_config_output = net_connect.send_command("show running-config")
            
            # Create a timestamp for the filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # Use device host for filename
            backup_filename = f"{cisco_device['host']}_running_config_{timestamp}.txt" 
            
            # Save the output to a file
            with open(backup_filename, "w") as f:
                f.write(running_config_output)
            
            print(f"\nConfiguration backup saved to {backup_filename}.")
            
            # Verify file creation (optional)
            if os.path.exists(backup_filename):
                print(f"File '{backup_filename}' successfully created in current directory.")
            else:
                print(f"Error: File '{backup_filename}' was not created.")

            print(f"Backup process complete for {cisco_device['host']}.")
        
    except NetmikoTimeoutException:
        print(f"Error: Connection to {cisco_device['host']} timed out during backup.")
    except NetmikoAuthenticationException:
        print(f"Error: Authentication failed for {cisco_device['host']}. Check username/password/enable password.")
    except NetmikoException as e:
        print(f"An Netmiko-specific error occurred during backup for {cisco_device['host']}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during backup for {cisco_device['host']}: {e}")
    ```
2.  Save and run `netmiko_lab.py`.
    *Expected Output (if dummy IP is unreachable or credentials are wrong):*
    ```
    --- Lab 2.2: Perform Configuration Backups ---
    Error: Connection to 192.168.1.10 timed out during backup.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects, filename timestamp will vary):*
    ```
    --- Lab 2.2: Perform Configuration Backups ---
    Connected to YOUR_DEVICE_IP.

    Collecting 'show running-config' for backup...

    Configuration backup saved to YOUR_DEVICE_IP_running_config_20250901_HHMMSS.txt.
    File 'YOUR_DEVICE_IP_running_config_20250901_HHMMSS.txt' successfully created in current directory.
    Backup process complete for YOUR_DEVICE_IP.
    ```
    *Expected File Creation:* A file named `YOUR_DEVICE_IP_running_config_YYYYMMDD_HHMMSS.txt` (with the current date/time) will be created in your `network_automation_labs` directory. It will contain the `show running-config` output from your device.

---

## Lab 3: Managing Multiple Network Devices at Scale (Concurrency)

**Objective:** Apply concurrency concepts from Module 2 to manage multiple devices using Netmiko, leveraging `ThreadPoolExecutor` for concurrent connections.

### Task 3.1: Define Multiple Dummy Devices

1.  In `netmiko_lab.py`, add a list of multiple dummy devices. **Remember to replace these with your actual lab device details!**
    ```python
    # ... (previous code) ...

    # --- List of multiple dummy devices (REPLACE WITH YOUR ACTUAL LAB DEVICE DETAILS) ---
    # Make sure these IPs are reachable in your lab environment
    # and use the correct username/password for each.
    multi_devices = [
        {
            "device_type": "cisco_ios",
            "host": "192.168.1.10", # DUMMY IP 1
            "username": "dummy_user",
            "password": "dummy_password",
            "secret": "dummy_enable",
        },
        {
            "device_type": "cisco_ios",
            "host": "192.168.1.11", # DUMMY IP 2
            "username": "dummy_user",
            "password": "dummy_password",
            "secret": "dummy_enable",
        },
        {
            "device_type": "cisco_ios",
            "host": "192.168.1.12", # DUMMY IP 3
            "username": "dummy_user",
            "password": "dummy_password",
            "secret": "dummy_enable",
        },
        # Add more devices as needed for your lab setup
    ]
    ```

### Task 3.2: Create a Function to Process a Single Device

This function will encapsulate all Netmiko operations for one device. It will be run concurrently for each device by the `ThreadPoolExecutor`.

1.  In `netmiko_lab.py`, add the following function:
    ```python
    # ... (previous code) ...

    def process_device_concurrently(device_info):
        """
        Connects to a single device, collects data, and applies a simple config.
        This function will be run by each thread in the ThreadPoolExecutor.
        """
        hostname = device_info['host']
        results = []
        net_connect = None
        try:
            with ConnectHandler(**device_info) as net_connect:
                print(f"[{hostname}] Connected. Collecting version...")
                version_output = net_connect.send_command("show version")
                results.append(f"[{hostname}] Version: {version_output.splitlines()}...") # Get first line of version

                print(f"[{hostname}] Applying simple config...")
                # Example: Change hostname and add a Loopback
                config_commands = [f"hostname {hostname}-AUTOMATED", "interface Loopback99", "ip address 10.0.0.99 255.255.255.255", "no shutdown"]
                net_connect.send_config_set(config_commands)
                results.append(f"[{hostname}] Config applied.")

                print(f"[{hostname}] Collecting running-config for backup...")
                running_config = net_connect.send_command("show running-config")
                # In a real scenario, you'd save this to a file for each device
                results.append(f"[{hostname}] Running-config collected (length: {len(running_config)}).")
                
                return "\n".join(results) + f"\n[{hostname}] Successfully processed."
        except NetmikoTimeoutException:
            return f"[{hostname}] Failed: Connection timed out. Device unreachable or SSH issue."
        except NetmikoAuthenticationException:
            return f"[{hostname}] Failed: Authentication failed. Check username/password/enable password."
        except NetmikoException as e:
            return f"[{hostname}] Failed: Netmiko error - {e}"
        except Exception as e:
            return f"[{hostname}] Failed: Unexpected error - {e}"
    ```

### Task 3.3: Use `ThreadPoolExecutor` for Concurrent Processing

1.  In `netmiko_lab.py`, add the following main execution block:
    ```python
    # ... (previous code) ...
    from concurrent.futures import ThreadPoolExecutor
    import time # For timing

    print("\n--- Lab 3.3: Managing Multiple Devices at Scale (Concurrency) ---")
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
    ```
2.  Save and run `netmiko_lab.py`.
    *Expected Output (if using dummy IPs/credentials, you'll see errors):*
    ```
    --- Lab 3.3: Managing Multiple Devices at Scale (Concurrency) ---
    [192.168.1.10] Failed: Connection timed out. Device unreachable or SSH issue.
    [192.168.1.11] Failed: Connection timed out. Device unreachable or SSH issue.
    [192.168.1.12] Failed: Connection timed out. Device unreachable or SSH issue.

    --- All Device Processing Complete ---
    [192.168.1.10] Failed: Connection timed out. Device unreachable or SSH issue.
    ----------------------------------------
    [192.168.1.11] Failed: Connection timed out. Device unreachable or SSH issue.
    ----------------------------------------
    [192.168.1.12] Failed: Connection timed out. Device unreachable or SSH issue.
    ----------------------------------------

    Total processing time: X.xx seconds.
    Processed 3 devices with 3 concurrent workers.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects, order will be interleaved):*
    ```
    --- Lab 3.3: Managing Multiple Devices at Scale (Concurrency) ---
    [YOUR_DEVICE_IP_1] Connected. Collecting version...
    [YOUR_DEVICE_IP_2] Connected. Collecting version...
    [YOUR_DEVICE_IP_3] Connected. Collecting version...
    [YOUR_DEVICE_IP_1] Applying simple config...
    [YOUR_DEVICE_IP_2] Applying simple config...
    [YOUR_DEVICE_IP_3] Applying simple config...
    [YOUR_DEVICE_IP_1] Collecting running-config for backup...
    [YOUR_DEVICE_IP_2] Collecting running-config for backup...
    [YOUR_DEVICE_IP_3] Collecting running-config for backup...

    --- All Device Processing Complete ---
    [YOUR_DEVICE_IP_1] Version: Cisco IOS Software, IOS-XE Software, ...
    [YOUR_DEVICE_IP_1] Config applied.
    [YOUR_DEVICE_IP_1] Running-config collected (length: XXX).
    [YOUR_DEVICE_IP_1] Successfully processed.
    ----------------------------------------
    [YOUR_DEVICE_IP_2] Version: Cisco IOS Software, IOS-XE Software, ...
    [YOUR_DEVICE_IP_2] Config applied.
    [YOUR_DEVICE_IP_2] Running-config collected (length: XXX).
    [YOUR_DEVICE_IP_2] Successfully processed.
    ----------------------------------------
    [YOUR_DEVICE_IP_3] Version: Cisco IOS Software, IOS-XE Software, ...
    [YOUR_DEVICE_IP_3] Config applied.
    [YOUR_DEVICE_IP_3] Running-config collected (length: XXX).
    [YOUR_DEVICE_IP_3] Successfully processed.
    ----------------------------------------

    Total processing time: X.xx seconds.
    Processed 3 devices with 3 concurrent workers.
    ```
    *Observation:* The total time taken will be significantly less than if you processed each device one by one, demonstrating the power of concurrency for I/O-bound tasks like network automation.

---

## Conclusion

You've now completed Module 3 and gained practical experience with the Netmiko library! You can now:

*   Understand Netmiko's role in network automation.
*   Define device connection parameters.
*   Connect to devices and send commands.
*   Push configuration changes and perform backups.
*   Apply concurrency concepts to manage multiple devices efficiently.
*   Implement basic error handling for network operations.

Netmiko is a fundamental tool for CLI-based network automation. In the next modules, you'll explore other aspects of network automation, including working with APIs and structured data.

**Keep Automating!**

---