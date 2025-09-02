---

## Document 2: Python Basics for Network Automation - Module 4 Lab Guide

```markdown
# Python Basics for Network Automation: Module 4 Lab Guide

## Programming Device Automation with Paramiko Library - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 4 of the Python Basics for Network Automation Lab Guide! In this module, you will gain hands-on experience with the **Paramiko** library. Paramiko provides a lower-level way to interact with network devices via SSH compared to Netmiko.

For these labs, you will use **dummy IP addresses and credentials** initially. **It is crucial that you replace these dummy values with the actual IP addresses, usernames, and passwords of your lab equipment (e.g., Cisco IOS XE routers in a sandbox) to make the code functional.**

**Lab Objectives:**
*   Install the Paramiko library.
*   Organize your project into separate Python files for devices and Paramiko operations.
*   Define device dictionaries with real parameters.
*   Connect to a single network device using Paramiko.
*   Execute commands remotely and retrieve device output.
*   Implement robust error handling for Paramiko operations.

**Prerequisites:**
*   Completion of Module 1, Module 2, and Module 3 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   **Access to a network device (e.g., Cisco IOS XE router, virtual lab device) with SSH enabled and known credentials.** You will need to replace dummy values with your device's actual information.

Let's start automating with Paramiko!

---

## Lab Setup: Creating Your Project Structure

We will continue with the modular project structure.

1.  **Navigate** to your main `network_automation_labs` directory.
2.  **Create a new directory** for this module's labs:
    ```bash
    mkdir module4_paramiko_lab
    cd module4_paramiko_lab
    ```
3.  **Inside `module4_paramiko_lab`, create the following empty files:**
    *   `__init__.py` (This makes `module4_paramiko_lab` a Python package)
    *   `devices.py`
    *   `paramiko_operations.py`
    *   `lab_single_device.py`

    Your directory structure should now look like this:
    ```
    network_automation_labs/
    ├── na_env/
    ├── module4_paramiko_lab/
    │   ├── __init__.py
    │   ├── devices.py
    │   ├── paramiko_operations.py
    │   └── lab_single_device.py
    ├── ... (other module files)
    ```

### Task 0.1: Populate `devices.py`

This file will store the connection details for your network devices.

1.  Open `devices.py` in your code editor.
2.  Add the following Python code. **Remember to replace the DUMMY VALUES with your actual lab device details!**
    ```python
    # devices.py

    # REPLACE THESE DUMMY VALUES WITH YOUR ACTUAL LAB DEVICE DETAILS!
    # This device should be reachable and have SSH enabled with the provided credentials.
    single_device = {
        "host": "192.168.1.10", # DUMMY IP - REPLACE WITH YOUR DEVICE'S IP
        "username": "dummy_user", # DUMMY USERNAME - REPLACE WITH YOUR DEVICE'S USERNAME
        "password": "dummy_password", # DUMMY PASSWORD - REPLACE WITH YOUR DEVICE'S PASSWORD
        "port": 22, # Default SSH port
    }
    ```
3.  Save `devices.py`.

### Task 0.2: Populate `paramiko_operations.py`

This file will contain reusable Paramiko functions.

1.  Open `paramiko_operations.py` in your code editor.
2.  Add the following Python code:
    ```python
    # paramiko_operations.py
    import paramiko
    from paramiko.ssh_exception import AuthenticationException, SSHException, BadHostKeyException
    import socket # For handling connection errors
    import time # For timing operations

    def connect_to_device(device_info):
        """
        Establishes an SSH connection to a device using Paramiko.
        Returns the SSHClient object if successful, None otherwise.
        """
        host = device_info.get("host")
        username = device_info.get("username")
        password = device_info.get("password")
        port = device_info.get("port", 22)

        client = paramiko.SSHClient()
        # This policy automatically adds the remote host's key to the local known_hosts file.
        # For production, it's more secure to manually add keys or use AutoAddPolicy only for first connection.
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 

        print(f"Connecting to {host}...")
        try:
            client.connect(
                hostname=host,
                username=username,
                password=password,
                port=port,
                timeout=10 # Connection timeout in seconds
            )
            print(f"Successfully connected to {host}.")
            return client
        except AuthenticationException:
            print(f"Error: Authentication failed for {host}. Check username/password.")
        except BadHostKeyException as e:
            print(f"Error: Bad host key for {host}: {e}. Host key might have changed.")
        except socket.timeout:
            print(f"Error: Connection to {host} timed out. Device might be unreachable or SSH is not enabled.")
        except SSHException as e:
            print(f"Error: SSH connection failed for {host}: {e}.")
        except Exception as e:
            print(f"An unexpected error occurred connecting to {host}: {e}")
        return None # Return None if connection fails

    def execute_command(client, command):
        """
        Executes a single command on the remote device using an active SSHClient.
        Returns the stdout and stderr output as strings.
        """
        if not client:
            return "Error: SSHClient not connected.", ""

        print(f"  Executing command: '{command}'...")
        try:
            # exec_command returns stdin, stdout, stderr file-like objects
            stdin, stdout, stderr = client.exec_command(command)
            
            # Read the output from stdout and stderr
            output = stdout.read().decode('utf-8').strip()
            errors = stderr.read().decode('utf-8').strip()
            
            if errors:
                print(f"  Command '{command}' produced errors:\n{errors}")
            return output, errors
        except SSHException as e:
            print(f"Error executing command '{command}': {e}")
            return "", f"SSH Error: {e}"
        except Exception as e:
            print(f"An unexpected error occurred executing '{command}': {e}")
            return "", f"Unexpected Error: {e}"

    def close_connection(client):
        """
        Closes the SSH connection.
        """
        if client:
            client.close()
            print("Connection closed.")
    ```
3.  Save `paramiko_operations.py`.

---

## Lab 1: Paramiko Basics - Connecting and Executing Commands (Single Device)

**Objective:** Get familiar with Paramiko's `SSHClient` and `exec_command()` method.

### Task 1.1: Install Paramiko

1.  Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).
2.  Navigate into your `module4_paramiko_lab` directory:
    ```bash
    cd module4_paramiko_lab
    ```
3.  Install Paramiko:
    ```bash
    pip install paramiko
    ```
    *Expected Observation:* Paramiko and its dependencies will be installed. You should see a "Successfully installed..." message.

### Task 1.2: Connect to a Device

We will use the `connect_to_device` function to establish an SSH connection.

1.  Open `lab_single_device.py` in your code editor.
2.  Add the following code. This script will import the `single_device` dictionary and the `connect_to_device` and `close_connection` functions.
    ```python
    # lab_single_device.py
    from .devices import single_device # Import the single device dictionary
    from .paramiko_operations import connect_to_device, close_connection # Import functions

    print("--- Lab 1.2: Connect to a Device ---")
    
    client = None # Initialize client variable
    try:
        client = connect_to_device(single_device)
        if client:
            print(f"Successfully obtained Paramiko client for {single_device['host']}.")
        else:
            print(f"Failed to obtain Paramiko client for {single_device['host']}.")
    except Exception as e:
        print(f"An unexpected error occurred during client connection attempt: {e}")
    finally:
        close_connection(client) # Always ensure connection is closed
    
    print("\nLab 1.2 complete.")
    ```
3.  Save `lab_single_device.py`.
4.  **Run the script** from your `module4_paramiko_lab` directory:
    ```bash
    python lab_single_device.py
    ```
    *Expected Output (if dummy IP is unreachable or credentials are wrong):*
    ```
    --- Lab 1.2: Connect to a Device ---
    Connecting to 192.168.1.10...
    Error: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.
    Failed to obtain Paramiko client for 192.168.1.10.
    Connection closed.

    Lab 1.2 complete.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects):*
    ```
    --- Lab 1.2: Connect to a Device ---
    Connecting to YOUR_DEVICE_IP...
    Successfully connected to YOUR_DEVICE_IP.
    Successfully obtained Paramiko client for YOUR_DEVICE_IP.
    Connection closed.

    Lab 1.2 complete.
    ```

### Task 1.3: Execute `show` Commands

Now, use the `execute_command()` function to retrieve information from the device.

1.  Open `lab_single_device.py` in your code editor.
2.  Add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 1.3: Execute 'show' Commands ---")
    client = None
    try:
        client = connect_to_device(single_device)
        if client:
            print(f"Connected to {single_device['host']}.")

            # Execute 'show version' command
            print("\nCollecting 'show version'...")
            stdout_output, stderr_output = execute_command(client, "show version")
            print("\n--- show version output ---")
            print(stdout_output[:500] + "...") # Print first 500 characters for brevity
            if stderr_output:
                print(f"--- show version errors ---\n{stderr_output}")

            # Execute 'show ip interface brief' command
            print("\nCollecting 'show ip interface brief'...")
            stdout_output, stderr_output = execute_command(client, "show ip interface brief")
            print("\n--- show ip interface brief output ---")
            print(stdout_output)
            if stderr_output:
                print(f"--- show ip interface brief errors ---\n{stderr_output}")

        else:
            print(f"Failed to connect to {single_device['host']}.")
    except Exception as e:
        print(f"An unexpected error occurred during command execution: {e}")
    finally:
        close_connection(client)
    
    print("\nLab 1.3 complete.")
    ```
3.  Save `lab_single_device.py`.
4.  **Run the script** from your `module4_paramiko_lab` directory:
    ```bash
    python lab_single_device.py
    ```
    *Expected Output (if dummy IP is unreachable or credentials are wrong):*
    ```
    --- Lab 1.3: Execute 'show' Commands ---
    Connecting to 192.168.1.10...
    Error: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.
    Failed to connect to 192.168.1.10.
    Connection closed.

    Lab 1.3 complete.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects):*
    ```
    --- Lab 1.3: Execute 'show' Commands ---
    Connecting to YOUR_DEVICE_IP...
    Successfully connected to YOUR_DEVICE_IP.
    Connected to YOUR_DEVICE_IP.

    Collecting 'show version'...
      Executing command: 'show version'...

    --- show version output ---
    Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.9.4
    ... (actual version output from your device) ...

    Collecting 'show ip interface brief'...
      Executing command: 'show ip interface brief'...

    --- show ip interface brief output ---
    Interface              IP-Address      OK? Method Status        Protocol
    GigabitEthernet0/0     192.168.1.1     YES manual up            up
    Loopback0              1.1.1.1         YES manual up            up
    Vlan1                  unassigned      YES unset  down          down
    ... (actual interface brief output from your device) ...
    Connection closed.

    Lab 1.3 complete.
    ```

---

## Conclusion

You've now completed Module 4 and gained practical experience with the **Paramiko** library! You can now:

*   Understand Paramiko's role as a lower-level SSH library.
*   Organize your Python automation code into a modular project structure.
*   Define device connection parameters for Paramiko.
*   Connect to devices using Paramiko's `SSHClient`.
*   Execute commands remotely and retrieve their `stdout` and `stderr` output.
*   Implement basic error handling for Paramiko operations.

Paramiko provides the foundational building blocks for many SSH-based automation tasks and is crucial for scenarios requiring fine-grained control over the SSH session.

**Keep Automating!**

---