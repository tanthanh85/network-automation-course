from netmiko import ConnectHandler
cisco_router = {
    "device_type": "cisco_ios",
    "host": "10.10.20.48",
    "username": "developer",
    "password": "C1sco12345",
    "secret": "C1sco12345", # Used for 'enable' command
    "port": 22,
    "session_log": "router_session.log"
}

net_connect = None
try:
    # Establish the SSH connection
    print(f"Connecting to {cisco_router['host']}...")
    net_connect = ConnectHandler(**cisco_router)
    print("Connection successful!")

    # --- Example 1: Raw Output (without TextFSM) ---
    print("\n--- Raw Output: show ip interface brief ---")
    raw_output = net_connect.send_command("show ip interface brief")
    print(raw_output)
    print(f"Type of raw_output: {type(raw_output)}")

    # # --- Example 2: Parsed Output (with TextFSM) ---
    print("\n--- Parsed Output (TextFSM): show ip interface brief ---")
    # # Requires 'pip install textfsm'
    parsed_output = net_connect.send_command("show ip interface brief", use_textfsm=True)
    
    # # The parsed output is typically a list of dictionaries
    print(parsed_output)
    # print(f"Type of parsed_output: {type(parsed_output)}")

    # # Accessing structured data is much easier
    # print("\n--- Accessing Specific Parsed Data ---")
    # for interface_data in parsed_output:
    #     print(f"Interface: {interface_data['interface']}, IP Address: {interface_data['ip_address']}, Status: {interface_data['status']}")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if net_connect:
        net_connect.disconnect()
        print("Disconnected from device.")