from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios",
    "host": "10.10.20.48",
    "username": "developer",
    "password": "C1sco12345",
}

net_connect = None
try:
    # Establish the SSH connection
    print(f"Connecting to {device['host']}...")
    net_connect = ConnectHandler(**device)
    print("Connection successful!")

    config_commands = [
    "interface Loopback100",
    "description Configured_by_Netmiko",
    "ip address 10.100.0.1 255.255.255.255",
    "no shutdown"
    ]
    output_config = net_connect.send_config_set(config_commands)
    print(output_config)

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if net_connect:
        net_connect.disconnect()
        print("Disconnected from device.")