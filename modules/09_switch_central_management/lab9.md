# Python Basics for Network Automation: Module 9 Lab Guide

## Creating a Management Console for Cisco Switches - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 9 of the Python Basics for Network Automation Lab Guide! In this module, you will build a simple Python-based management console for Cisco switches. This console will allow an administrator to interactively configure VLANs and assign ports.

**It is crucial that you replace the dummy values for your Cisco switch with its actual IP address, username, and password to make the code functional.**

**Lab Objectives:**
*   Set up a basic console structure.
*   Define a list of switches for the console to manage.
*   Implement functions to get VLAN information from a switch.
*   Implement functions to get port-to-VLAN assignments.
*   Implement functions to create VLANs.
*   Implement functions to assign ports to VLANs.
*   Build an interactive menu-driven console.

**Prerequisites:**
*   Completion of Module 1 through Module 8 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   An active internet connection.
*   **Access to a Cisco IOS switch (e.g., Cisco Packet Tracer, GNS3, EVE-NG, or a physical switch) with SSH enabled.** You will need its IP, username, and password.

Let's build a console!

---

## Lab Setup: Project Structure

For this module, we will keep the project structure simple with a few files.

1.  **Navigate** to your main `network_automation_labs` directory.
2.  **Create a new directory** for this module's labs:
    ```bash
    mkdir module9_console_lab
    cd module9_console_lab
    ```
3.  **Inside `module9_console_lab`, create the following empty Python files:**
    ```bash
    touch config.py
    touch switch_ops.py
    touch management_console.py
    ```

Your directory structure should now look like this:
```
network_automation_labs/
└── module9_console_lab/
├── config.py
├── switch_ops.py
└── management_console.py
```
### Task 0.1: Install `netmiko`

1.  Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).
2.  Navigate into your `module9_console_lab` directory:
    ```bash
    cd module9_console_lab
    ```
3.  Install the `netmiko` library:
    ```bash
    pip install netmiko
    ```
    *Expected Observation:* `netmiko` and its dependencies will be installed. You should see "Successfully installed..." messages.

### Task 0.2: Populate `config.py`

This file will store your switch connection details and a list of managed switches.

1.  Open `config.py` in your code editor.
2.  Add the following Python code. **REPLACE THE DUMMY VALUES WITH YOUR ACTUAL LAB SWITCH DETAILS!**
    ```python
    # config.py

    # --- Cisco Switch Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
    # This switch should be reachable and have SSH enabled.
    # You can add more switches to this list if you have them.
    MANAGED_SWITCHES = [
        {
            "device_type": "cisco_ios", # Or 'cisco_nxos' if applicable
            "host": "devnetsandboxiosxec9k.cisco.com", # e.g., 192.168.1.10
            "username": "YOUR_SWITCH_USERNAME",
            "password": "YOUR_SWITCH_PASSWORD",
            "secret": "YOUR_SWITCH_ENABLE_PASSWORD", # If your switch uses enable password
            "port": 22, # Default SSH port
        },
        # {
        #     "device_type": "cisco_ios",
        #     "host": "YOUR_SWITCH_IP_2",
        #     "username": "YOUR_SWITCH_USERNAME",
        #     "password": "YOUR_SWITCH_PASSWORD",
        #     "secret": "YOUR_SWITCH_ENABLE_PASSWORD",
        #     "port": 22,
        # },
    ]
    ```
3.  Save `config.py`.

### Task 0.3: Populate `switch_ops.py`

This file will contain reusable functions for switch operations using Netmiko.

1.  Open `switch_ops.py` in your code editor.
2.  Add the following Python code:
    ```python
    # switch_ops.py
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoBaseException
    import logging
    import re # For regular expressions to parse output

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def get_switch_connection(device_info):
        """Establishes a Netmiko connection to a switch."""
        host = device_info['host']
        try:
            logging.info(f"Connecting to {host}...")
            net_connect = ConnectHandler(**device_info)
            logging.info(f"Successfully connected to {host}.")
            return net_connect
        except (NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoBaseException) as e:
            logging.error(f"Connection error to {host}: {e}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred connecting to {host}: {e}")
            return None

    def get_vlan_brief(net_connect):
        """Retrieves and parses 'show vlan brief' output."""
        try:
            output = net_connect.send_command("show vlan brief")
            vlans = []
            # Regex to parse VLAN ID, Name, Status, and Ports
            # Example line: 10   VLAN_DATA                        active    Fa0/1, Fa0/2
            vlan_pattern = re.compile(r"(\d+)\s+([a-zA-Z0-9_-]+)\s+(active|act/unsup|suspended)\s*(.*)")
            
            for line in output.splitlines():
                match = vlan_pattern.match(line.strip())
                if match:
                    vlan_id = match.group(1)
                    vlan_name = match.group(2)
                    vlan_status = match.group(3)
                    vlan_ports = [p.strip() for p in match.group(4).split(',') if p.strip()]
                    vlans.append({
                        "id": vlan_id,
                        "name": vlan_name,
                        "status": vlan_status,
                        "ports": vlan_ports
                    })
            return vlans
        except Exception as e:
            logging.error(f"Error getting VLAN brief: {e}")
            return []

    def get_interface_vlan_assignment(net_connect, interface_name):
        """Retrieves and parses 'show interfaces <interface> switchport' output."""
        try:
            output = net_connect.send_command(f"show interfaces {interface_name} switchport")
            vlan_assignment = {}
            
            # Regex to find Access Mode VLAN
            access_vlan_match = re.search(r"Access Mode VLAN:\s+(\d+)", output)
            if access_vlan_match:
                vlan_assignment["access_vlan"] = access_vlan_match.group(1)
            
            # Regex to find Administrative Mode
            admin_mode_match = re.search(r"Administrative Mode:\s+(\w+)", output)
            if admin_mode_match:
                vlan_assignment["admin_mode"] = admin_mode_match.group(1)
            
            # Regex to find Operational Mode
            oper_mode_match = re.search(r"Operational Mode:\s+(\w+)", output)
            if oper_mode_match:
                vlan_assignment["oper_mode"] = oper_mode_match.group(1)

            return vlan_assignment
        except Exception as e:
            logging.error(f"Error getting interface {interface_name} VLAN assignment: {e}")
            return {}

    def create_vlan(net_connect, vlan_id, vlan_name):
        """Creates a new VLAN on the switch."""
        try:
            config_commands = [
                f"vlan {vlan_id}",
                f"name {vlan_name}"
            ]
            output = net_connect.send_config_set(config_commands)
            logging.info(f"VLAN {vlan_id} '{vlan_name}' creation output:\n{output}")
            return True
        except Exception as e:
            logging.error(f"Error creating VLAN {vlan_id}: {e}")
            return False

    def assign_port_to_vlan(net_connect, interface_name, vlan_id):
        """Assigns a port (or port range) to an access VLAN."""
        try:
            config_commands = [
                f"interface {interface_name}",
                "switchport mode access",
                f"switchport access vlan {vlan_id}"
            ]
            output = net_connect.send_config_set(config_commands)
            logging.info(f"Port {interface_name} assignment to VLAN {vlan_id} output:\n{output}")
            return True
        except Exception as e:
            logging.error(f"Error assigning {interface_name} to VLAN {vlan_id}: {e}")
            return False

    # Standalone test for functions (only runs when this file is executed directly)
    if __name__ == '__main__':
        from config import MANAGED_SWITCHES
        if MANAGED_SWITCHES:
            test_device = MANAGED_SWITCHES
            print(f"--- Testing switch_ops.py functions on {test_device['host']} ---")
            net_conn = get_switch_connection(test_device)
            if net_conn:
                # Test get_vlan_brief
                print("\n--- show vlan brief ---")
                vlans = get_vlan_brief(net_conn)
                for vlan in vlans:
                    print(f"VLAN ID: {vlan['id']}, Name: {vlan['name']}, Ports: {', '.join(vlan['ports'])}")
                
                # Test create_vlan
                print("\n--- Creating VLAN 999 ---")
                create_vlan(net_conn, 999, "TEST_VLAN_999")

                # Test assign_port_to_vlan (adjust interface if Fa0/1 is not available)
                print("\n--- Assigning Fa0/1 to VLAN 999 ---")
                assign_port_to_vlan(net_conn, "FastEthernet0/1", 999)

                # Test get_interface_vlan_assignment
                print("\n--- Checking Fa0/1 assignment ---")
                fa0_1_vlan = get_interface_vlan_assignment(net_conn, "FastEthernet0/1")
                print(f"Fa0/1 assignment: {fa0_1_vlan}")

                net_conn.disconnect()
                print("--- Test Complete ---")
            else:
                print("Failed to connect for standalone test.")
        else:
            print("No switches defined in config.py for standalone test.")
    ```
3.  Save `switch_ops.py`.

### Task 0.4: Populate `management_console.py`

This is the main Python script that will run the interactive management console.

1.  Open `management_console.py` in your code editor.
2.  Add the following Python code:
    ```python
    # management_console.py
    from switch_ops import get_switch_connection, get_vlan_brief, create_vlan, assign_port_to_vlan, get_interface_vlan_assignment
    from config import MANAGED_SWITCHES
    import logging
    import time

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def display_menu():
        """Displays the main menu options to the admin."""
        print("\n--- Switch Management Console ---")
        print("1. Select Switch")
        print("2. List Available VLANs on Selected Switch")
        print("3. List Ports Belonging to a VLAN on Selected Switch")
        print("4. Create New VLAN on Selected Switch")
        print("5. Assign Port(s) to VLAN on Selected Switch")
        print("6. Exit")
        print("---------------------------------")

    def select_switch():
        """Allows the admin to choose a switch from the managed list."""
        if not MANAGED_SWITCHES:
            print("No switches defined in config.py.")
            return None

        print("\n--- Available Switches ---")
        for i, switch in enumerate(MANAGED_SWITCHES):
            print(f"{i+1}. {switch['host']}")
        print("--------------------------")

        while True:
            try:
                choice = int(input("Enter number of switch to select: "))
                if 1 <= choice <= len(MANAGED_SWITCHES):
                    selected = MANAGED_SWITCHES[choice-1]
                    print(f"Selected switch: {selected['host']}")
                    return selected
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def list_vlans(selected_switch_info):
        """Lists all VLANs on the selected switch."""
        if not selected_switch_info:
            print("No switch selected.")
            return

        net_conn = get_switch_connection(selected_switch_info)
        if net_conn:
            print(f"\n--- VLANs on {selected_switch_info['host']} ---")
            vlans = get_vlan_brief(net_conn)
            if vlans:
                for vlan in vlans:
                    print(f"  ID: {vlan['id']}, Name: {vlan['name']}, Status: {vlan['status']}, Ports: {', '.join(vlan['ports'])}")
            else:
                print("  No VLANs found or error retrieving.")
            net_conn.disconnect()
        else:
            print(f"Failed to connect to {selected_switch_info['host']}.")

    def list_ports_in_vlan(selected_switch_info):
        """Lists ports belonging to a specific VLAN on the selected switch."""
        if not selected_switch_info:
            print("No switch selected.")
            return

        vlan_id = input("Enter VLAN ID to list ports for: ")
        net_conn = get_switch_connection(selected_switch_info)
        if net_conn:
            print(f"\n--- Ports in VLAN {vlan_id} on {selected_switch_info['host']} ---")
            vlans = get_vlan_brief(net_conn)
            found_vlan = False
            for vlan in vlans:
                if vlan['id'] == vlan_id:
                    print(f"  VLAN {vlan_id} ({vlan['name']}) Ports: {', '.join(vlan['ports'])}")
                    found_vlan = True
                    break
            if not found_vlan:
                print(f"  VLAN {vlan_id} not found or has no assigned ports.")
            net_conn.disconnect()
        else:
            print(f"Failed to connect to {selected_switch_info['host']}.")

    def handle_create_vlan(selected_switch_info):
        """Handles creating a new VLAN."""
        if not selected_switch_info:
            print("No switch selected.")
            return

        vlan_id = input("Enter new VLAN ID (e.g., 100): ")
        vlan_name = input("Enter new VLAN Name (e.g., DATA_VLAN): ")

        net_conn = get_switch_connection(selected_switch_info)
        if net_conn:
            if create_vlan(net_conn, vlan_id, vlan_name):
                print(f"Successfully sent commands to create VLAN {vlan_id}.")
            else:
                print(f"Failed to create VLAN {vlan_id}.")
            net_conn.disconnect()
        else:
            print(f"Failed to connect to {selected_switch_info['host']}.")

    def handle_assign_port_to_vlan(selected_switch_info):
        """Handles assigning port(s) to a VLAN."""
        if not selected_switch_info:
            print("No switch selected.")
            return

        interface_name = input("Enter interface name (e.g., FastEthernet0/1 or GigabitEthernet1/0/1): ")
        vlan_id = input("Enter VLAN ID to assign port(s) to: ")

        net_conn = get_switch_connection(selected_switch_info)
        if net_conn:
            if assign_port_to_vlan(net_conn, interface_name, vlan_id):
                print(f"Successfully sent commands to assign {interface_name} to VLAN {vlan_id}.")
                # Optional: Verify assignment
                time.sleep(2) # Give switch time to update
                assigned_vlan_info = get_interface_vlan_assignment(net_conn, interface_name)
                if assigned_vlan_info and assigned_vlan_info.get("access_vlan") == vlan_id:
                    print(f"Verification: {interface_name} is now in VLAN {vlan_id} (Access Mode).")
                else:
                    print(f"Verification: Could not confirm {interface_name} in VLAN {vlan_id}.")
            else:
                print(f"Failed to assign {interface_name} to VLAN {vlan_id}.")
            net_conn.disconnect()
        else:
            print(f"Failed to connect to {selected_switch_info['host']}.")

    def main():
        """Main function to run the management console."""
        selected_switch = None
        while True:
            display_menu()
            choice = input("Enter your choice: ")

            if choice == '1':
                selected_switch = select_switch()
            elif choice == '2':
                list_vlans(selected_switch)
            elif choice == '3':
                list_ports_in_vlan(selected_switch)
            elif choice == '4':
                handle_create_vlan(selected_switch)
            elif choice == '5':
                handle_assign_port_to_vlan(selected_switch)
            elif choice == '6':
                print("Exiting console. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    if __name__ == '__main__':
        main()
    ```
3.  Save `management_console.py`.

---

## Lab 1: Interact with the Management Console

**Objective:** Run the console and perform various VLAN and port management tasks.

### Task 1.1: Run the Management Console

1.  **Ensure you have updated `config.py` with your real switch details.**
2.  **Run the console script** from your `module9_console_lab` directory:
    ```bash
    python management_console.py
    ```
    *Expected Output (console):*
    ```
    --- Switch Management Console ---
    1. Select Switch
    2. List Available VLANs on Selected Switch
    3. List Ports Belonging to a VLAN on Selected Switch
    4. Create New VLAN on Selected Switch
    5. Assign Port(s) to VLAN on Selected Switch
    6. Exit
    ---------------------------------
    Enter your choice: 
    ```

### Task 1.2: Select a Switch

1.  At the prompt, enter `1` and press Enter.
2.  Enter the number corresponding to your switch (e.g., `1`) and press Enter.
    *Expected Output:*
    ```
    --- Available Switches ---
    1. YOUR_SWITCH_IP_1
    --------------------------
    Enter number of switch to select: 1
    Selected switch: YOUR_SWITCH_IP_1
    ```

### Task 1.3: List Available VLANs

1.  At the main menu, enter `2` and press Enter.
    *Expected Output (will show VLANs from your switch):*
    ```
    --- VLANs on YOUR_SWITCH_IP_1 ---
      ID: 1, Name: default, Status: active, Ports: Fa0/1, Fa0/2, Fa0/3, Fa0/4, Fa0/5, Fa0/6, Fa0/7, Fa0/8, Fa0/9, Fa0/10, Fa0/11, Fa0/12, Gi0/1, Gi0/2
      ID: 10, Name: DATA_VLAN, Status: active, Ports: 
      ID: 20, Name: VOICE_VLAN, Status: active, Ports: 
    --- Switch Management Console ---
    ... (menu again) ...
    ```

### Task 1.4: Create a New VLAN

1.  At the main menu, enter `4` and press Enter.
2.  Enter a new VLAN ID (e.g., `50`) and a name (e.g., `MANAGEMENT`).
    *Expected Output:*
    ```
    Enter new VLAN ID (e.g., 100): 50
    Enter new VLAN Name (e.g., DATA_VLAN): MANAGEMENT
    Connecting to YOUR_SWITCH_IP_1...
    Successfully connected to YOUR_SWITCH_IP_1.
    VLAN 50 'MANAGEMENT' creation output:
    configure terminal
    Enter configuration commands, one per line.  End with CNTL/Z.
    YOUR_SWITCH_PROMPT(config)#vlan 50
    YOUR_SWITCH_PROMPT(config-vlan)#name MANAGEMENT
    YOUR_SWITCH_PROMPT(config-vlan)#end
    YOUR_SWITCH_PROMPT#
    Successfully sent commands to create VLAN 50.
    ```
3.  **Manual Verification:** You can now choose option `2` from the menu to list VLANs again and confirm VLAN 50 is present, or log in to your switch and run `show vlan brief`.

### Task 1.5: Assign Port(s) to a VLAN

1.  At the main menu, enter `5` and press Enter.
2.  Enter an interface name (e.g., `FastEthernet0/1`) and the VLAN ID (e.g., `50`).
    *Expected Output:*
    ```
    Enter interface name (e.g., FastEthernet0/1 or GigabitEthernet1/0/1): FastEthernet0/1
    Enter VLAN ID to assign port(s) to: 50
    Connecting to YOUR_SWITCH_IP_1...
    Successfully connected to YOUR_SWITCH_IP_1.
    Port FastEthernet0/1 assignment to VLAN 50 output:
    configure terminal
    Enter configuration commands, one per line.  End with CNTL/Z.
    YOUR_SWITCH_PROMPT(config)#interface FastEthernet0/1
    YOUR_SWITCH_PROMPT(config-if)#switchport mode access
    YOUR_SWITCH_PROMPT(config-if)#switchport access vlan 50
    YOUR_SWITCH_PROMPT(config-if)#end
    YOUR_SWITCH_PROMPT#
    Successfully sent commands to assign FastEthernet0/1 to VLAN 50.
    Verification: FastEthernet0/1 is now in VLAN 50 (Access Mode).
    ```
3.  **Manual Verification:** You can now choose option `3` from the menu and enter `50` to list ports in VLAN 50, or log in to your switch and run `show vlan brief` or `show interfaces FastEthernet0/1 switchport`.

### Task 1.6: List Ports Belonging to a VLAN

1.  At the main menu, enter `3` and press Enter.
2.  Enter the VLAN ID (e.g., `50`) to see which ports belong to it.
    *Expected Output:*
    ```
    Enter VLAN ID to list ports for: 50

    --- Ports in VLAN 50 on YOUR_SWITCH_IP_1 ---
      VLAN 50 (MANAGEMENT) Ports: Fa0/1
    ```

### Task 1.7: Exit the Console

1.  At the main menu, enter `6` and press Enter.
    *Expected Output:*
    ```
    Exiting console. Goodbye!
    ```

---

## Conclusion

You've now completed Module 9 and built a functional, interactive management console for Cisco switches! You can now:

*   Understand the benefits of a Python-based management console.
*   Automate VLAN creation and port assignment using Netmiko.
*   Retrieve and display switch configuration details (VLANs, port assignments).
*   Build a menu-driven Python application.

This module demonstrates how to create more interactive and user-friendly automation tools that can empower network administrators.

**Keep Automating!**

---