from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios",
    "ip": "sandbox-iosxe-latest-1.cisco.com",
    "username": "developer",
    "password": "C1sco12345",
}

commands = [
    "no router ospf 1"
]

with ConnectHandler(**device) as conn:
    output = conn.send_config_set(commands)
    print("✅ Rolled back OSPF config")
    print(output)
