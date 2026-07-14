# lab_single_device.py
from devices import single_device # Import the single device dictionary
from netmiko_operations import get_device_info, apply_config_commands, backup_running_config # Import the function to get device info
from pprint import pprint

print("--- Lab 1.2: Connect to a Single Device ---")

# We call get_device_info with a simple command to test connectivity
# The function handles the connection and disconnection internally.
output = get_device_info(single_device, command="show clock")

print("\n--- Connection Test Result ---")
print(output)
print("\nLab 1.2 complete.")

print("\n--- Lab 1.3: Send 'show' Commands ---")

print("\nCollecting 'show version'...")
version_output = get_device_info(single_device, command="show version",parse_output=False)
print("\n--- show version output ---")
print(version_output[0]['version']) # Print first 500 characters for brevity

print("\nCollecting 'show ip interface brief'...")
ip_int_brief_output = get_device_info(single_device, command="show ip interface brief",parse_output=True)
print("\n--- show ip interface brief output ---")
pprint(ip_int_brief_output,indent=4)

print("\nLab 1.3 complete.")

# ... (previous code) ...

print("\n--- Lab 2.1: Push Configuration Changes ---")

config_commands = [
    "interface Loopback100",
    "description CONFIGURED_BY_NETMIKO_LAB",
    "ip address 10.100.0.100 255.255.255.255",
    "no shutdown",
    "router ospf 1",
    "network 10.100.0.0 0.0.0.255 area 0"
]

print("\nApplying configuration commands...")
config_output = apply_config_commands(single_device, config_commands)
print("\n--- Configuration Output ---")
print(config_output)

print("\nLab 2.1 complete.")

# ... (previous code) ...

print("\n--- Lab 2.2: Perform Configuration Backups ---")

print("\nCollecting 'show running-config' for backup...")
backup_result = backup_running_config(single_device)
print(backup_result)

print("\nLab 2.2 complete.")

