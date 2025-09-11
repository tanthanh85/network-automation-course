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