# NASP: Module 4 Lab Guide

## Programming Device Automation with Paramiko Library - Hands-on Exercises

---

## Introduction

Welcome to Module 4 of the NASP Lab Guide! In this module, you will gain hands-on experience with the **Paramiko** library. We will focus on its most common use: connecting to a device and executing non-interactive commands.

For these labs, you will use **dummy IP addresses and credentials** initially. **It is crucial that you replace these dummy values with the actual IP addresses, usernames, and passwords of your lab equipment (e.g., Cisco IOS XE routers in a sandbox) to make the code functional.**

**Lab Objectives:**
*   Install the Paramiko library.
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

## Lab Setup: Single File Approach

For this simplified module, we will keep all the code in a single Python file.

1.  **Navigate** to your main `network_automation_labs` directory.
2.  **Create a new Python file** for this module's labs:
    ```bash
    cd network_automation_labs
    touch paramiko_simple_lab.py
    ```

### Task 0.1: Define Device Information

This section will hold the connection details for your network device.

1.  Open `paramiko_simple_lab.py` in your code editor.
2.  Add the following Python code. **Remember to replace the DUMMY VALUES with your actual lab device details!**
    ```python
    # paramiko_simple_lab.py

    # --- Import necessary libraries ---
    import paramiko
    import socket # For handling connection errors like timeouts
    from paramiko.ssh_exception import AuthenticationException, SSHException # Specific Paramiko errors

    # --- Dummy Device Information (REPLACE WITH YOUR ACTUAL LAB DEVICE DETAILS) ---
    # This device should be reachable and have SSH enabled with the provided credentials.
    DEVICE_INFO = {
        "host": "192.168.1.10", # DUMMY IP - REPLACE WITH YOUR DEVICE'S IP
        "username": "dummy_user", # DUMMY USERNAME - REPLACE WITH YOUR DEVICE'S USERNAME
        "password": "dummy_password", # DUMMY PASSWORD - REPLACE WITH YOUR DEVICE'S PASSWORD
        "port": 22, # Default SSH port
    }
    ```
3.  Save `paramiko_simple_lab.py`.

---

## Lab 1: Basic Connection and Command Execution

**Objective:** Connect to a device and execute a `show` command.

### Task 1.1: Install Paramiko

1.  Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).
2.  Install Paramiko:
    ```bash
    pip install paramiko
    ```
    *Expected Observation:* Paramiko and its dependencies will be installed. You should see a "Successfully installed..." message.

### Task 1.2: Connect to a Device and Run `show version`

1.  Open `paramiko_simple_lab.py` in your code editor.
2.  Add the following code below the `DEVICE_INFO` dictionary:
    ```python
    # ... (previous code including imports and DEVICE_INFO) ...

    print("--- Lab 1.2: Connect and Run 'show version' ---")

    client = None # Initialize client variable to None
    try:
        # 1. Create an SSH client object
        client = paramiko.SSHClient()

        # 2. Automatically add the remote host's key (convenient for labs, less secure for production)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 3. Connect to the device
        print(f"Connecting to {DEVICE_INFO['host']}...")
        client.connect(
            hostname=DEVICE_INFO['host'],
            username=DEVICE_INFO['username'],
            password=DEVICE_INFO['password'],
            port=DEVICE_INFO['port'],
            timeout=10 # Connection timeout
        )
        print(f"Successfully connected to {DEVICE_INFO['host']}.")

        # 4. Execute a command
        command = "show version"
        print(f"Executing command: '{command}'...")
        stdin, stdout, stderr = client.exec_command(command)

        # 5. Read and decode the output
        output = stdout.read().decode('utf-8').strip()
        errors = stderr.read().decode('utf-8').strip()

        print("\n--- Command Output ---")
        print(output[:500] + "...") # Print first 500 characters for brevity
        if errors:
            print(f"\n--- Command Errors ---\n{errors}")

    except AuthenticationException:
        print(f"Error: Authentication failed for {DEVICE_INFO['host']}. Check username/password.")
    except socket.timeout:
        print(f"Error: Connection to {DEVICE_INFO['host']} timed out. Device might be unreachable or SSH is not enabled.")
    except SSHException as e:
        print(f"Error: SSH connection failed for {DEVICE_INFO['host']}: {e}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # 6. Close the connection
        if client:
            client.close()
            print(f"\nConnection to {DEVICE_INFO['host']} closed.")

    print("\nLab 1.2 complete.")
    ```
3.  Save `paramiko_simple_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory:
    ```bash
    python paramiko_simple_lab.py
    ```
    *Expected Output (if dummy IP is unreachable or credentials are wrong):*
    ```
    --- Lab 1.2: Connect and Run 'show version' ---
    Connecting to 192.168.1.10...
    Error: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.

    Lab 1.2 complete.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects):*
    ```
    --- Lab 1.2: Connect and Run 'show version' ---
    Connecting to YOUR_DEVICE_IP...
    Successfully connected to YOUR_DEVICE_IP.
    Executing command: 'show version'...

    --- Command Output ---
    Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.9.4
    ... (actual version output from your device, up to 500 chars) ...

    Connection to YOUR_DEVICE_IP closed.

    Lab 1.2 complete.
    ```

### Task 1.3: Run Another Command (`show ip interface brief`)

1.  Open `paramiko_simple_lab.py` in your code editor.
2.  Add the following code below the previous task. This will run a second command, demonstrating reusability of the `exec_command` pattern.
    ```python
    # ... (previous code) ...

    print("\n--- Lab 1.3: Run 'show ip interface brief' ---")

    client = None
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {DEVICE_INFO['host']}...")
        client.connect(
            hostname=DEVICE_INFO['host'],
            username=DEVICE_INFO['username'],
            password=DEVICE_INFO['password'],
            port=DEVICE_INFO['port'],
            timeout=10
        )
        print(f"Successfully connected to {DEVICE_INFO['host']}.")

        command = "show ip interface brief"
        print(f"Executing command: '{command}'...")
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode('utf-8').strip()
        errors = stderr.read().decode('utf-8').strip()

        print("\n--- Command Output ---")
        print(output)
        if errors:
            print(f"\n--- Command Errors ---\n{errors}")

    except AuthenticationException:
        print(f"Error: Authentication failed for {DEVICE_INFO['host']}. Check username/password.")
    except socket.timeout:
        print(f"Error: Connection to {DEVICE_INFO['host']} timed out. Device might be unreachable or SSH is not enabled.")
    except SSHException as e:
        print(f"Error: SSH connection failed for {DEVICE_INFO['host']}: {e}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if client:
            client.close()
            print(f"\nConnection to {DEVICE_INFO['host']} closed.")

    print("\nLab 1.3 complete.")
    ```
3.  Save `paramiko_simple_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory:
    ```bash
    python paramiko_simple_lab.py
    ```
    *Expected Output (if dummy IP is unreachable or credentials are wrong):*
    ```
    --- Lab 1.3: Run 'show ip interface brief' ---
    Connecting to 192.168.1.10...
    Error: Connection to 192.168.1.10 timed out. Device might be unreachable or SSH is not enabled.

    Lab 1.3 complete.
    ```
    *Expected Output (if you replace with real, reachable device info and it connects):*
    ```
    --- Lab 1.3: Run 'show ip interface brief' ---
    Connecting to YOUR_DEVICE_IP...
    Successfully connected to YOUR_DEVICE_IP.
    Executing command: 'show ip interface brief'...

    --- Command Output ---
    Interface              IP-Address      OK? Method Status        Protocol
    GigabitEthernet0/0     192.168.1.1     YES manual up            up
    Loopback0              1.1.1.1         YES manual up            up
    Vlan1                  unassigned      YES unset  down          down
    ... (actual interface brief output from your device) ...

    Connection to YOUR_DEVICE_IP closed.

    Lab 1.3 complete.
    ```

---

## Conclusion

You've now completed Module 4 and gained practical experience with the **Paramiko** library! You can now:

*   Understand Paramiko's role as a lower-level SSH library.
*   Connect to devices using Paramiko's `SSHClient`.
*   Execute non-interactive commands remotely and retrieve their `stdout` and `stderr` output.
*   Implement robust error handling for Paramiko operations.

Paramiko provides the foundational building blocks for many SSH-based automation tasks and is crucial for scenarios requiring fine-grained control over the SSH session.

**Keep Automating!**

---