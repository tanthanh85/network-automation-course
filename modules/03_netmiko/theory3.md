# Python Basics for Network Automation: Module 3 Theory Guide

## Programming Automation using Netmiko Library

**[Your Organization/Name]**
**September 01, 2025**

---

## 1. Introduction to Netmiko

In Module 1, you learned Python basics and how data is represented. In Module 2, you explored how to make your scripts faster using concurrency. Now, it's time to apply these skills to a real-world network automation tool: **Netmiko**.

**What is Netmiko?**
Netmiko is a powerful Python library that makes it easy to connect to network devices (like routers, switches, and firewalls) and send commands to them. It supports many different vendors, including Cisco (IOS, IOS-XE, NX-OS), Juniper, Arista, and more.

**Why use Netmiko?**
*   **Simplifies SSH/Telnet:** It handles the complexities of connecting to devices over SSH (Secure Shell) or Telnet, including authentication, command prompts, and pagination (when a command output is too long and requires pressing "Space" or "Enter").
*   **Cross-Vendor Support:** You can use a similar approach to interact with devices from different manufacturers.
*   **Automation Power:** It's a foundational tool for automating tasks like:
    *   Collecting `show` command outputs (e.g., `show version`, `show ip interface brief`).
    *   Pushing configuration changes (e.g., creating VLANs, configuring interfaces).
    *   Performing configuration backups.
    *   Checking device status.

---

## 2. Netmiko Basics: Getting Started

Before you can use Netmiko, you need to install it and understand how to tell it about the device you want to connect to.

*   **2.1 Installation:**
    *   Always install Netmiko within your project's virtual environment (as learned in Module 1).
    *   Open your terminal (with your virtual environment activated) and run:
        ```bash
        pip install netmiko
        ```

*   **2.2 Device Dictionary (Connection Parameters):**
    *   Netmiko needs to know details about the device it's connecting to. You provide this information in a Python dictionary.
    *   **Common Parameters:**
        *   `device_type`: (Required) Specifies the vendor and OS type (e.g., `"cisco_ios"`, `"cisco_nxos"`, `"juniper_junos"`). This tells Netmiko how to interact with the device's command line.
        *   `host`: (Required) The IP address or hostname of the device.
        *   `username`: (Required) The username for logging in.
        *   `password`: (Required) The password for logging in.
        *   `port`: (Optional) The port number (default is 22 for SSH, 23 for Telnet).
        *   `secret`: (Optional) The enable password (for Cisco devices, to enter privileged EXEC mode).
        *   `session_log`: (Optional) Path to a file where Netmiko will log the entire SSH session (useful for debugging).

    **Example Device Dictionary:**
    ```python
    cisco_router = {
        "device_type": "cisco_ios",
        "host": "192.168.1.1",
        "username": "admin",
        "password": "mysecretpassword",
        "secret": "myenablepassword", # Used for 'enable' command
        "port": 22,
        "session_log": "router_session.log"
    }
    ```
    *Note: In real scripts, avoid hardcoding passwords directly. Use environment variables, secure password managers, or prompt for input (e.g., using `getpass.getpass()`). For this module's labs, we'll use simulated hardcoded values for simplicity.*

*   **2.3 `ConnectHandler`: Establishing the Connection**
    *   `ConnectHandler` is the main class in Netmiko used to establish and manage the connection to a network device.
    *   It takes the device dictionary as input.
    *   **Best Practice:** Use `ConnectHandler` with a `with` statement. This ensures the connection is properly opened and automatically closed when you're done, even if errors occur.
    ```python
    from netmiko import ConnectHandler

    device = {
        "device_type": "cisco_ios",
        "host": "192.168.1.1",
        "username": "admin",
        "password": "cisco",
    }

    try:
        with ConnectHandler(**device) as net_connect: # **device unpacks the dictionary
            print(f"Successfully connected to {device['host']}")
            # Perform operations here
        print(f"Connection to {device['host']} closed.")
    except Exception as e:
        print(f"Failed to connect to {device['host']}: {e}")
    ```
    **Expected Output (if connection is simulated successfully):**
    ```
    Successfully connected to 192.168.1.1
    Connection to 192.168.1.1 closed.
    ```

---

## 3. Performing Operations: Commands and Configurations

Once connected, Netmiko provides methods to send commands and push configurations.

*   **3.1 `send_command()`: Executing `show` Commands**
    The `send_command()` method is designed to execute a single command on the connected device and retrieve its output. It's primarily used for "show" commands to gather operational status and configuration details.

    A key feature of `send_command()` is its ability to integrate with TextFSM for intelligent parsing of command output into structured data. This transforms raw, human-readable text into easily consumable Python data structures (like lists of dictionaries), making automation tasks significantly more efficient and reliable.

    How TextFSM Works: TextFSM is a Python module that uses predefined templates to parse semi-structured text output into structured data. For common network commands (e.g., `show ip interface brief`, `show version`), Netmiko often ships with built-in TextFSM templates or can utilize community-contributed ones. When `use_textfsm=True`, Netmiko attempts to match the command output against an appropriate TextFSM template and returns the parsed data.

    Key Arguments:

    *   `command_string` (required): The exact command to be sent to the device (e.g., `"show version"`).
    *   `use_textfsm` (optional, default: `False`): If set to `True`, Netmiko will attempt to parse the command output using TextFSM templates. Note: TextFSM must be installed (`pip install textfsm`). When `True`, the return type changes from a string to a list of dictionaries (or a dictionary for single-entry outputs).
    *   `delay_factor` (optional): A multiplier applied to Netmiko's internal delays, useful for slower devices or complex commands that take longer to execute.
    *   `strip_prompt` (optional, default: `True`): Removes the device's command prompt from the output.
    *   `strip_command` (optional, default: `True`): Removes the command itself from the output, returning only the command's response.

    Example: Retrieving and Parsing Interface Information

    Let's illustrate how `send_command()` works, particularly highlighting the benefit of `use_textfsm`.

    ```python
    import os
    from netmiko import ConnectHandler
    from getpass import getpass

    # Device details (replace with your actual device info)
    device = {
        "device_type": "cisco_ios",
        "host": os.getenv("NETMIKO_HOSTNAME"), # Using environment variables for security
        "username": os.getenv("NETMIKO_USERNAME"),
        "password": os.getenv("NETMIKO_PASSWORD"),
        "secret": os.getenv("NETMIKO_SECRET", getpass("Enter enable password: ")), # Optional enable password
    }

    net_connect = None
    try:
        # Establish the SSH connection
        print(f"Connecting to {device['host']}...")
        net_connect = ConnectHandler(**device)
        print("Connection successful!")

        # --- Example 1: Raw Output (without TextFSM) ---
        print("\n--- Raw Output: show ip interface brief ---")
        raw_output = net_connect.send_command("show ip interface brief")
        print(raw_output)
        print(f"Type of raw_output: {type(raw_output)}")

        # --- Example 2: Parsed Output (with TextFSM) ---
        print("\n--- Parsed Output (TextFSM): show ip interface brief ---")
        # Requires 'pip install textfsm'
        parsed_output = net_connect.send_command("show ip interface brief", use_textfsm=True)
        
        # The parsed output is typically a list of dictionaries
        print(parsed_output)
        print(f"Type of parsed_output: {type(parsed_output)}")

        # Accessing structured data is much easier
        print("\n--- Accessing Specific Parsed Data ---")
        for interface_data in parsed_output:
            print(f"Interface: {interface_data['intf']}, IP Address: {interface_data['ipaddr']}, Status: {interface_data['status']}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if net_connect:
            net_connect.disconnect()
            print("Disconnected from device.")
    ```
    Expected Output (Illustrative):
    ```bash
    Connecting to 192.168.1.10...
    Connection successful!

    --- Raw Output: show ip interface brief ---
    Interface              IP-Address      OK? Method Status        Protocol
    GigabitEthernet0/0     192.168.1.1     YES manual up            up
    Loopback0              1.1.1.1         YES manual up            up
    Vlan1                  unassigned      YES unset  down          down
    Type of raw_output: <class 'str'>

    --- Parsed Output (TextFSM): show ip interface brief ---
    [
        {'intf': 'GigabitEthernet0/0', 'ipaddr': '192.168.1.1', 'ok': 'YES', 'method': 'manual', 'status': 'up', 'proto': 'up'},
        {'intf': 'Loopback0', 'ipaddr': '1.1.1.1', 'ok': 'YES', 'method': 'manual', 'status': 'up', 'proto': 'up'},
        {'intf': 'Vlan1', 'ipaddr': 'unassigned', 'ok': 'YES', 'method': 'unset', 'status': 'down', 'proto': 'down'}
    ]
    Type of parsed_output: <class 'list'>

    --- Accessing Specific Parsed Data ---
    Interface: GigabitEthernet0/0, IP Address: 192.168.1.1, Status: up
    Interface: Loopback0, IP Address: 1.1.1.1, Status: up
    Interface: Vlan1, IP Address: unassigned, Status: down

    Disconnected from device.
    ```
    As demonstrated, use_textfsm=True transforms the raw string output into a list of dictionaries, where each dictionary represents a row of data with clearly defined keys (e.g., intf, ipaddr, status). This structured format is vastly superior for programmatic access, filtering, and further automation logic compared to parsing raw text with regular expressions.


*   **3.2 `send_config_set()`: Pushing Configuration Changes**
    *   Used to send a list of configuration commands to the device. Netmiko handles entering and exiting configuration mode.
    *   It returns the output of the configuration commands.
    *   **Arguments:**
        *   `config_commands`: A list of strings, where each string is a configuration command.
        *   `cmd_verify`: (Optional) If `True`, Netmiko will verify each command was successfully applied (default: `True`).
        *   `exit_config_mode`: (Optional) If `True`, Netmiko will exit configuration mode after sending commands (default: `True`).

    **Example:**
    ```python
    # Assuming net_connect is an active connection
    config_commands = [
        "interface Loopback100",
        "description Configured_by_Netmiko",
        "ip address 10.0.0.1 255.255.255.255",
        "no shutdown"
    ]
    output_config = net_connect.send_config_set(config_commands)
    print(output_config)
    ```
    **Expected Output (example):**
    ```
    config terminal
    Enter configuration commands, one per line.  End with CNTL/Z.
    Router(config)#interface Loopback100
    Router(config-if)#description Configured_by_Netmiko
    Router(config-if)#ip address 10.0.0.1 255.255.255.255
    Router(config-if)#no shutdown
    Router(config-if)#exit
    Router(config)#end
    Router#
    ```

*   **3.3 Automating Backup Tasks**
    *   To back up a device's configuration, you typically send a `show running-config` command and save the output to a file.
    *   **Steps:**
        1.  Connect to the device.
        2.  Execute `net_connect.send_command("show running-config")`.
        3.  Save the returned string to a text file.

    **Example (saving to file):**
    ```python
    # Assuming net_connect is an active connection and config_output is the result
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{net_connect.base_prompt}_running_config_{timestamp}.txt"
    
    with open(backup_filename, "w") as f:
        f.write(config_output)
    print(f"Configuration backup saved to {backup_filename}")
    ```

---

## 4. Managing Multiple Network Devices at Scale

Connecting to one device is easy, but network automation often involves managing dozens, hundreds, or even thousands of devices. This is where the concurrency concepts from Module 2 become essential.

*   **Why Concurrency?**
    *   Network operations (SSH connections, sending commands, waiting for replies) are primarily **I/O-bound** tasks. Your script spends most of its time waiting for the device to respond.
    *   If you process devices one by one (sequentially), your script will be very slow.
    *   Using concurrency (multithreading or asynchronous programming) allows your script to initiate connections and send commands to multiple devices *at the same time*, effectively utilizing the waiting periods.

*   **Using `concurrent.futures.ThreadPoolExecutor` for Scale:**
    *   From Module 2, you know about `threading`. For managing a pool of threads to execute tasks concurrently, Python's `concurrent.futures` module provides `ThreadPoolExecutor`.
    *   It's simpler than managing individual `threading.Thread` objects, as it handles thread creation and management for you. You just give it tasks, and it runs them in available threads.
    *   **Steps:**
        1.  Define a function that handles all Netmiko operations for a *single* device.
        2.  Create a list of all device dictionaries.
        3.  Use `ThreadPoolExecutor` to execute your single-device function for each device in the list concurrently.

    **Conceptual Example:**
    ```python
    from concurrent.futures import ThreadPoolExecutor
    from netmiko import ConnectHandler
    # ... other imports (time, etc.)

    # List of all your devices
    all_devices = [
        {"device_type": "cisco_ios", "host": "192.168.1.1", ...},
        {"device_type": "cisco_ios", "host": "192.168.1.2", ...},
        # ... many more devices
    ]

    def process_single_device(device_info):
        """
        Function to be executed by each thread for a single device.
        Contains all Netmiko logic.
        """
        hostname = device_info['host']
        try:
            with ConnectHandler(**device_info) as net_connect:
                print(f"Connected to {hostname}. Collecting data...")
                output = net_connect.send_command("show version")
                return f"Successfully processed {hostname}. Version: {output.splitlines()}"
        except Exception as e:
            return f"Failed to process {hostname}: {e}"

    # Main execution
    if __name__ == "__main__":
        max_workers = 5 # Number of concurrent threads (adjust based on device capacity)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # map() applies process_single_device to each item in all_devices
            # and returns results as they complete.
            results = executor.map(process_single_device, all_devices)
            
            for res in results:
                print(res)
        print("All devices processed.")
    ```
    *Note: For very large-scale automation (hundreds to thousands of devices), `asyncio` (from Module 2) combined with async-compatible network libraries (like `asyncssh` or `httpx` for APIs) often offers even better performance and scalability than `ThreadPoolExecutor` due to its lower overhead.*

---

## 5. Error Handling

Network automation scripts frequently encounter errors (e.g., device unreachable, wrong credentials, command not found). Robust scripts include `try-except` blocks to gracefully handle these issues.

*   **Common Netmiko Exceptions:**
    *   `NetmikoTimeoutException`: Device did not respond within the expected time.
    *   `NetmikoAuthenticationException`: Incorrect username or password.
    *   `NetmikoValueError`: Invalid `device_type` or other parameter.

    **Example:**
    ```python
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

    device = {
        "device_type": "cisco_ios",
        "host": "192.168.1.99", # Non-existent IP
        "username": "baduser",
        "password": "badpassword",
    }

    try:
        with ConnectHandler(**device) as net_connect:
            print(f"Connected to {device['host']}")
    except NetmikoTimeoutException:
        print(f"Error: Connection to {device['host']} timed out. Device might be unreachable.")
    except NetmikoAuthenticationException:
        print(f"Error: Authentication failed for {device['host']}. Check username/password.")
    except Exception as e: # Catch any other unexpected errors
        print(f"An unexpected error occurred connecting to {device['host']}: {e}")
    ```
    **Expected Output (if device is unreachable):**
    ```
    Error: Connection to 192.168.1.99 timed out. Device might be unreachable.
    ```

---

## 6. Summary

Netmiko is your essential tool for interacting with network devices at the command-line level. By combining Netmiko with Python's concurrency features, you can build powerful and efficient automation scripts to manage your network infrastructure at scale.

**Key Takeaways:**
*   Netmiko simplifies SSH/Telnet connections.
*   Device parameters are passed via a dictionary to `ConnectHandler`.
*   `send_command()` retrieves information.
*   `send_config_set()` pushes configurations.
*   `ThreadPoolExecutor` helps run Netmiko tasks concurrently on multiple devices.
*   Always include error handling (`try-except`) for robust scripts.

---