import yaml
from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler

# Load YAML data
with open('data/ospf_data.yaml') as f:
    ospf_data = yaml.safe_load(f)

# Load Jinja2 template
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('ospf_template.j2')
config = template.render(ospf=ospf_data['ospf'])

# Print for confirmation
print("Generated OSPF Config:")
print(config)

# Connect to router
device = {
    "device_type": "cisco_ios",
    "ip": "sandbox-iosxe-latest-1.cisco.com",
    "username": "developer",
    "password": "C1sco12345",
}

with ConnectHandler(**device) as conn:
    conn.send_config_set(config.splitlines())
    print("✅ Configuration pushed")
