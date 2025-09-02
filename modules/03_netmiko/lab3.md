# Python Basics for Network Automation: Module 3 Lab Guide

## Programming Automation using Netmiko Library - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 3 of the Python Basics for Network Automation Lab Guide! In this module, you will gain hands-on experience with the Netmiko library. Since we are focusing on Python concepts and not actual network setup at this stage, all Netmiko interactions in these labs will be **simulated** using Python's `print()` statements and `time.sleep()` to mimic network delays. This allows you to understand Netmiko's usage without needing a live network device.

**Lab Objectives:**
*   Install the Netmiko library.
*   Understand and define Netmiko device dictionaries.
*   Simulate connecting to a single network device.
*   Simulate sending `show` commands and capturing output.
*   Simulate pushing configuration changes.
*   Simulate performing configuration backups.
*   Simulate managing multiple network devices concurrently using `ThreadPoolExecutor`.

**Prerequisites:**
*   Completion of Module 1 and Module 2 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).

Let's start automating with Netmiko!

---

## Lab 1: Netmiko Basics - Connecting and Sending Commands (Simulated Single Device)

**Objective:** Get familiar with Netmiko's connection and command-sending methods through simulation.

### Task 1.1: Install Netmiko

1.  Activate your `na_env` virtual environment in your terminal.
2.  Install Netmiko:
    ```bash
    pip install netmiko
    ```
    *Expected Observation:* Netmiko and its dependencies will be installed. You should see a "Successfully installed..." message.

### Task 1.2: Simulate Connecting to a Single Device

We will create simple functions to mimic Netmiko's connection behavior.

1.  Create a new Python file named `netmiko_lab.py`.
2.  Add the following code to the file. These functions will simulate the actions of Netmiko.
    ```python
    # netmiko_lab.py
    import time
    import random
    import datetime # For backup filename
    import os       # For checking file existence

    # --- Simulation Functions (mimic Netmiko behavior) ---

    def simulate_connect(device_info):
        """Simulates establishing a connection to a device."""
        host = device_info.get("host", "unknown_host")
        print(f"Simulating connection to {host}...")
        time.sleep(random.uniform(0.5, 1.5)) # Simulate connection delay
        print(f"Simulated connection established to {host}.")
        return {"connected": True, "host": host, "prompt": f"{host}#"} # Return a simulated connection object

    def simulate_disconnect(simulated_connection):
        """Simulates disconnecting from a device."""
        host = simulated_connection.get("host", "unknown_host")
        print(f"Simulating disconnection from {host}.")
        time.sleep(0.2) # Simulate disconnection delay
        print(f"Simulated disconnection complete from {host}.")

    def simulate_send_command(simulated_connection, command_string):
        """Simulates sending a command and returning output."""
        host = simulated_connection.get("host", "unknown_host")
        print(f"  Sending simulated command '{command_string}' to {host}...")
        time.sleep(random.uniform(0.5, 1.0)) # Simulate command execution delay
        
        # Simulate different outputs based on command
        if "show version" in command_string:
            return f"""
Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.9.4
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2020 by Cisco Systems, Inc.

{host} uptime is 1 week, 2 days, 3 hours, 4 minutes
System image file is "flash:cat3k_caa-universalk9.16.9.4.SPA.bin"
"""
        elif "show ip interface brief" in command_string:
            return f"""
Interface              IP-Address      OK? Method Status        Protocol
GigabitEthernet0/0     192.168.1.1     YES manual up            up
GigabitEthernet0/1     unassigned      YES unset  down          down
Loopback0              1.1.1.1         YES manual up            up
Vlan1                  unassigned      YES unset  down          down
"""
        elif "show running-config" in command_string:
            return f"""
Building configuration...

Current configuration : 1234 bytes
!
version 16.9
service timestamps debug datetime msec
service timestamps log datetime msec
hostname {host}
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 negotiation auto
!
end
"""
        else:
            return f"Simulated output for '{command_string}' on {host}\n"

    def simulate_send_config_set(simulated_connection, config_commands):
        """Simulates sending configuration commands."""
        host = simulated_connection.get("host", "unknown_host")
        print(f"  Sending simulated config commands to {host}...")
        output = "config terminal\n"
        for cmd in config_commands:
            time.sleep(0.3) # Simulate command application delay
            output += f"  {host}(config)# {cmd}\n"
        output += f"  {host}(config)#end\n"
        output += f"{host}#"
        print(f"  Simulated config complete for {host}.")
        return output

    # --- End of Simulation Functions ---


    # Define a simulated Cisco device (Netmiko device dictionary format)
    cisco_device = {
        "device_type": "cisco_ios",
        "host": "192.168.1.10", # Simulated IP
        "username": "admin",
        "password": "password123",
        "secret": "enable_pass",
    }

    print("--- Lab 1.2: Simulate Connecting to a Single Device ---")
    sim_conn = None # Initialize to None
    try:
        sim_conn = simulate_connect(cisco_device) # Call our simulation function
        if sim_conn["connected"]:
            print(f"Successfully used simulated connection to {cisco_device['host']}.")
        else:
            print(f"Simulated connection failed for {cisco_device['host']}.")
    except Exception as e:
        print(f"An error occurred during simulated connection: {e}")
    finally:
        if sim_conn and sim_conn["connected"]:
            simulate_disconnect(sim_conn)
    ```
3.  Save and run `netmiko_lab.py`.
    *Expected Output:*
    ```
    --- Lab 1.2: Simulate Connecting to a Single Device ---
    Simulating connection to 192.168.1.10...
    Simulated connection established to 192.168.1.10.
    Successfully used simulated connection to 192.168.1.10.
    Simulating disconnection from 192.168.1.10.
    Simulated disconnection complete from 192.168.1.10.
    ```

### Task 1.3: Simulate Sending `show` Commands

Now, use the `simulate_send_command()` function.

1.  In `netmiko_lab.py`, add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 1.3: Simulate Sending 'show' Commands ---")
    sim_conn = None
    try:
        sim_conn = simulate_connect(cisco_device)
        if sim_conn["connected"]:
            print(f"Connected to {cisco_device['host']}.")

            # Send 'show version' command
            print("\nCollecting 'show version'...")
            version_output = simulate_send_command(sim_conn, "show version")
            print("\n--- show version output ---")
            print(version_output[:300] + "...") # Print first 300 characters to keep output concise

            # Send 'show ip interface brief' command
            print("\nCollecting 'show ip interface brief'...")
            ip_int_brief_output = simulate_send_command(sim_conn, "show ip interface brief")
            print("\n--- show ip interface brief output ---")
            print(ip_int_brief_output)

        else:
            print(f"Simulated connection failed for {cisco_device['host']}.")
    except Exception as e:
        print(f"Simulated command collection failed: {e}")
    finally:
        if sim_conn and sim_conn["connected"]:
            simulate_disconnect(sim_conn)
    ```
2.  Save and run `netmiko_lab.py`.
    *Expected Output (outputs will be simulated as defined in `simulate_send_command`):*
    ```
    --- Lab 1.3: Simulate Sending 'show' Commands ---
    Simulating connection to 192.168.1.10...
    Simulated connection established to 192.168.1.10.
    Connected to 192.168.1.10.

    Collecting 'show version'...
      Sending simulated command 'show version' to 192.168.1.10...

    --- show version output ---

    Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.9.4
    Technical Support: http://www.cisco.com/techsupport
    Copyright (c) 1986-2020 by Cisco Systems, Inc.

    192.168.1.10 uptime is 1 week, 2 days, 3 hours, 4 minutes
    System image file is "flash:cat3k_caa-universalk9.16.9.4.SPA.bin"
    ...

    Collecting 'show ip interface brief'...
      Sending simulated command 'show ip interface brief' to 192.168.1.10...

    --- show ip interface brief output ---
    Interface              IP-Address      OK? Method Status        Protocol
    GigabitEthernet0/0     192.168.1.1     YES manual up            up
    GigabitEthernet0/1     unassigned      YES unset  down          down
    Loopback0              1.1.1.1         YES manual up            up
    Vlan1                  unassigned      YES unset  down          down

    Simulating disconnection from 192.168.1.10.
    Simulated disconnection complete from 192.168.1.10.
    ```

---

## Lab 2: Automating Configuration and Backups (Simulated Single Device)

**Objective:** Learn to use `simulate_send_config_set()` for configuration and capture `show running-config` for backup.

### Task 2.1: Simulate Pushing Configuration Changes

1.  In `netmiko_lab.py`, add the following code:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 2.1: Simulate Pushing Configuration Changes ---")
    sim_conn = None
    try:
        sim_conn = simulate_connect(cisco_device)
        if sim_conn["connected"]:
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
            config_output = simulate_send_config_set(sim_conn, config_commands)
            print("\n--- Configuration Output ---")
            print(config_output)

            print(f"Simulated configuration applied to {cisco_device['host']}.")
        else:
            print(f"Simulated connection failed for {cisco_device['host']}.")
    except Exception as e:
        print(f"Simulated configuration failed: {e}")
    finally:
        if sim_conn and sim_conn["connected"]:
            simulate_disconnect(sim_conn)
    ```
2.  Save and run `netmiko_lab.py`.
    *Expected Output:*
    ```
    --- Lab 2.1: Simulate Pushing Configuration Changes ---
    Simulating connection to 192.168.1.10...
    Simulated connection established to 192.168.1.10.
    Connected to 192.168.1.10.

    Applying configuration commands...
      Sending simulated config commands to 192.168.1.10...
      Simulated config complete for 192.168.1.10.

    --- Configuration Output ---
    config terminal
      192.168.1.10# interface Loopback100
      192.168.1.10# description CONFIGURED_BY_NETMIKO_LAB
      192.168.1.10# ip address 10.0.0.100 255.255.255.255
      192.168.1.10# no shutdown
      192.168.1.10# router ospf 1
      192.168.1.10# network 10.0.0.0 0.0.0.255 area 0
      192.168.1.10#end
    192.168.1.10#
    Simulated configuration applied to 192.168.1.10.
    Simulating disconnection from 192.168.1.10.
    Simulated disconnection complete from 192.168.1.10.
    ```

### Task 2.2: Simulate Performing Configuration Backups

1.  In `netmiko_lab.py`, add the following code:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 2.2: Simulate Performing Configuration Backups ---")
    sim_conn = None
    try:
        sim_conn = simulate_connect(cisco_device)
        if sim_conn["connected"]:
            print(f"Connected to {cisco_device['host']}.")

            print("\nCollecting 'show running-config' for backup...")
            running_config_output = simulate_send_command(sim_conn, "show running-config")
            
            # Create a timestamp for the filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{sim_conn['host']}_running_config_{timestamp}.txt"
            
            # Save the output to a file
            with open(backup_filename, "w") as f:
                f.write(running_config_output)
            
            print(f"\nSimulated configuration backup saved to {backup_filename}.")
            
            # Verify file creation (optional)
            if os.path.exists(backup_filename):
                print(f"File '{backup_filename}' successfully created in current directory.")
            else:
                print(f"Error: File '{backup_filename}' was not created.")

            print(f"Simulated backup process complete for {cisco_device['host']}.")
        else:
            print(f"Simulated connection failed for {cisco_device['host']}.")
    except Exception as e:
        print(f"Simulated backup process failed: {e}")
    finally:
        if sim_conn and sim_conn["connected"]:
            simulate_disconnect(sim_conn)
    ```
2.  Save and run `netmiko_lab.py`.
    *Expected Output (filename timestamp will vary):*
    ```
    --- Lab 2.2: Simulate Performing Configuration Backups ---
    Simulating connection to 192.168.1.10...
    Simulated connection established to 192.168.1.10.
    Connected to 192.168.1.10.

    Collecting 'show running-config' for backup...
      Sending simulated command 'show running-config' to 192.168.1.10...

    Simulated configuration backup saved to 192.168.1.10_running_config_20250901_HHMMSS.txt.
    File '192.168.1.10_running_config_20250901_HHMMSS.txt' successfully created in current directory.
    Simulated backup process complete for 192.168.1.10.
    Simulating disconnection from 192.168.1.10.
    Simulated disconnection complete from 192.168.1.10.
    ```
    *Expected File Creation:* A file named `192.168.1.10_running_config_YYYYMMDD_HHMMSS.txt` (with the current date/time) will be created in your `network_automation_labs` directory. It will contain the simulated output of `show running-config`.

---

## Lab 3: Managing Multiple Network Devices at Scale (Simulated Concurrency)

**Objective:** Apply concurrency concepts from Module 2 to manage multiple devices using Netmiko, leveraging `ThreadPoolExecutor` for simulated concurrent connections.

### Task 3.1: Define Multiple Simulated Devices

1.  In `netmiko_lab.py`, add a list of multiple simulated devices:
    ```python
    # ... (previous code) ...

    # --- List of multiple simulated devices ---
    simulated_devices = [
        {
            "device_type": "cisco_ios",
            "host": "192.168.1.10",
            "username": "admin",
            "password": "password123",
            "secret": "enable_pass",
        },
        {
            "device_type": "cisco_ios",
            "host": "192.168.1.11",
            "username": "admin",
            "password": "password123",
            "secret": "enable_pass",
        },
        {
            "device_type": "cisco_ios",
            "host": "192.168.1.12",
            "username": "admin",
            "password": "password123",
            "secret": "enable_pass",
        },
        {
            "device_type": "cisco_ios",
            "host": "192.168.1.13",
            "username": "admin",
            "password": "password123",
            "secret": "enable_pass",
        },
        {
            "device_type": "cisco_ios",
            "host": "192.168.1.14",
            "username": "admin",
            "password": "password123",
            "secret": "enable_pass",
        },
    ]
    ```

### Task 3.2: Create a Function to Process a Single Device

This function will encapsulate all Netmiko operations for one device. It will be run concurrently for each device.

1.  In `netmiko_lab.py`, add the following function:
    ```python
    # ... (previous code) ...

    def process_device_concurrently(device_info):
        """
        Simulates connecting to a single device, collecting data, and applying config.
        This function will be run by each thread in the ThreadPoolExecutor.
        """
        hostname = device_info['host']
        results = []
        sim_conn = None
        try:
            sim_conn = simulate_connect(device_info)
            if sim_conn["connected"]:
                print(f"[{hostname}] Connected. Collecting version...")
                version_output = simulate_send_command(sim_conn, "show version")
                results.append(f"[{hostname}] Version: {version_output.splitlines()}")

                print(f"[{hostname}] Applying simple config...")
                config_commands = [f"hostname {hostname}-NEW", "interface Loopback99", "no shutdown"]
                simulate_send_config_set(sim_conn, config_commands)
                results.append(f"[{hostname}] Config applied.")

                print(f"[{hostname}] Collecting running-config for backup...")
                running_config = simulate_send_command(sim_conn, "show running-config")
                # In a real scenario, you'd save this to a file
                results.append(f"[{hostname}] Running-config collected (length: {len(running_config)}).")
                
                return "\n".join(results) + f"\n[{hostname}] Successfully processed."
            else:
                return f"[{hostname}] Simulated connection failed."
        except Exception as e:
            return f"[{hostname}] Failed to process: {e}"
        finally:
            if sim_conn and sim_conn["connected"]:
                simulate_disconnect(sim_conn)
    ```

### Task 3.3: Use `ThreadPoolExecutor` for Simulated Concurrent Processing

1.  In `netmiko_lab.py`, add the following main execution block:
    ```python
    # ... (previous code) ...
    from concurrent.futures import ThreadPoolExecutor

    print("\n--- Lab 3.3: Managing Multiple Devices at Scale (Simulated Concurrency) ---")
    max_workers = 3 # Limit to 3 concurrent simulated connections at a time

    start_time = time.time()
    results_list = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # map() applies process_device_concurrently to each device in simulated_devices
        # and returns results as they complete.
        for result in executor.map(process_device_concurrently, simulated_devices):
            results_list.append(result)

    end_time = time.time()

    print("\n--- All Simulated Device Processing Complete ---")
    for res in results_list:
        print(res)
        print("-" * 40) # Separator for clarity

    print(f"\nTotal simulated processing time: {end_time - start_time:.2f} seconds.")
    print(f"Processed {len(simulated_devices)} devices with {max_workers} concurrent workers.")
    ```
2.  Save and run `netmiko_lab.py`.
    *Expected Output (order of device processing will be interleaved, total time will be significantly less than sequential):*
    ```
    --- Lab 3.3: Managing Multiple Devices at Scale (Simulated Concurrency) ---
    Simulating connection to 192.168.1.10...
    Simulating connection to 192.168.1.11...
    Simulating connection to 192.168.1.12...
    Simulated connection established to 192.168.1.10.
    [192.168.1.10] Connected. Collecting version...
      Sending simulated command 'show version' to 192.168.1.10...
    Simulated connection established to 192.168.1.11.
    [192.168.1.11] Connected. Collecting version...
      Sending simulated command 'show version' to 192.168.1.11...
    Simulated connection established to 192.168.1.12.
    [192.168.1.12] Connected. Collecting version...
      Sending simulated command 'show version' to 192.168.1.12...
    Simulating disconnection from 192.168.1.10.
    Simulated disconnection complete from 192.168.1.10.
    Simulating connection to 192.168.1.13...
    Simulated connection established to 192.168.1.13.
    [192.168.1.13] Connected. Collecting version...
      Sending simulated command 'show version' to 192.168.1.13...
    Simulating disconnection from 192.168.1.11.
    Simulated disconnection complete from 192.168.1.11.
    Simulating connection to 192.168.1.14...
    Simulated connection established to 192.168.1.14.
    [192.168.1.14] Connected. Collecting version...
      Sending simulated command 'show version' to 192.168.1.14...
    Simulating disconnection from 192.168.1.12.
    Simulated disconnection complete from 192.168.1.12.
    [192.168.1.10] Applying simple config...
      Sending simulated config commands to 192.168.1.10...
      Simulated config complete for 192.168.1.10.
    [192.168.1.10] Collecting running-config for backup...
      Sending simulated command 'show running-config' to 192.168.1.10...
    [192.168.1.13] Applying simple config...
      Sending simulated config commands to 192.168.1.13...
      Simulated config complete for 192.168.1.13.
    [192.168.1.13] Collecting running-config for backup...
      Sending simulated command 'show running-config' to 192.168.1.13...
    [192.168.1.14] Applying simple config...
      Sending simulated config commands to 192.168.1.14...
      Simulated config complete for 192.168.1.14.
    [192.168.1.14] Collecting running-config for backup...
      Sending simulated command 'show running-config' to 192.168.1.14...
    Simulating disconnection from 192.168.1.10.
    Simulated disconnection complete from 192.168.1.10.
    Simulating disconnection from 192.168.1.13.
    Simulated disconnection complete from 192.168.1.13.
    Simulating disconnection from 192.168.1.14.
    Simulated disconnection complete from 192.168.1.14.

    --- All Simulated Device Processing Complete ---
    [192.168.1.10] Version:
    Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.9.4
    Technical Support: http://www.cisco.com/techsupport
    Copyright (c) 1986-2020 by Cisco Systems, Inc.

    192.168.1.10 uptime is 1 week, 2 days, 3 hours, 4 minutes
    System image file is "flash:cat3k_caa-universalk9.16.9.4.SPA.bin"

    [192.168.1.10] Config applied.
    [192.168.1.10] Running-config collected (length: 200).
    [192.168.1.10] Successfully processed.
    ----------------------------------------
    [192.168.1.11] Version:
    Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.9.4
    Technical Support: http://www.cisco.com/techsupport
    Copyright (c) 1986-2020 by Cisco Systems, Inc.

    192.168.1.11 uptime is 1 week, 2 days, 3 hours, 4 minutes
    System image file is "flash:cat3k_caa-universalk9.16.9.4.SPA.bin"

    [192.168.1.11] Config applied.
    [192.168.1.11] Running-config collected (length: 200).
    [192.168.1.11] Successfully processed.
    ----------------------------------------
    [192.168.1.12] Version:
    Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.9.4
    Technical Support: http://www.cisco.com/techsupport
    Copyright (c) 1986-2020 by Cisco Systems, Inc.

    192.168.1.12 uptime is 1 week, 2 days, 3 hours, 4 minutes
    System image file is "flash:cat3k_caa-universalk9.16.9.4.SPA.bin"

    [192.168.1.12] Config applied.
    [192.168.1.12] Running-config collected (length: 200).
    [192.168.1.12] Successfully processed.
    ----------------------------------------
    [192.168.1.13] Version:
    Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.9.4
    Technical Support: http://www.cisco.com/techsupport
    Copyright (c) 1986-2020 by Cisco Systems, Inc.

    192.168.1.13 uptime is 1 week, 2 days, 3 hours, 4 minutes
    System image file is "flash:cat3k_caa-universalk9.16.9.4.SPA.bin"

    [192.168.1.13] Config applied.
    [192.168.1.13] Running-config collected (length: 200).
    [192.168.1.13] Successfully processed.
    ----------------------------------------
    [192.168.1.14] Version:
    Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.9.4
    Technical Support: http://www.cisco.com/techsupport
    Copyright (c) 1986-2020 by Cisco Systems, Inc.

    192.168.1.14 uptime is 1 week, 2 days, 3 hours, 4 minutes
    System image file is "flash:cat3k_caa-universalk9.16.9.4.SPA.bin"

    [192.168.1.14] Config applied.
    [192.168.1.14] Running-config collected (length: 200).
    [192.168.1.14] Successfully processed.
    ----------------------------------------

    Total simulated processing time: 5.xx seconds.
    Processed 5 devices with 3 concurrent workers.
    ```
    *Observation:* Note that the total time taken is much less than if you processed each device one by one (which would be approximately 5 devices * (0.5+0.5+0.3+0.3+0.5) seconds per device = ~10.5 seconds). Concurrency significantly speeds up I/O-bound tasks.

---

## Conclusion

You've now completed Module 3 and gained practical experience with the Netmiko library! You can now:

*   Understand Netmiko's role in network automation.
*   Define device connection parameters.
*   Simulate connecting to devices and sending commands.
*   Simulate pushing configuration changes and performing backups.
*   Apply concurrency concepts to manage multiple devices efficiently.

Netmiko is a fundamental tool for CLI-based network automation. In the next modules, you'll explore other aspects of network automation, including working with APIs and structured data.

**Keep Automating!**

---