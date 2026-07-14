# netmiko_operations.py
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoBaseException
import datetime
import os
import time # For ThreadPoolExecutor to see progress

def get_device_info(device_info, command="show version",parse_output=False):
    """
    Connects to a device and sends a show command.
    Returns the command output or an error message.
    """
    host = device_info.get("host", "Unknown Host")
    
    try:
        with ConnectHandler(**device_info) as net_connect:
            print(f"[{host}] Connected. Sending command: '{command}'...")
            output = net_connect.send_command(command,use_textfsm=parse_output)
            return output
    except Exception as e:
        return f"Error getting info from {host}: {e}"

def apply_config_commands(device_info, config_commands):
    """
    Connects to a device and applies a list of configuration commands.
    Returns the configuration output or an error message.
    """
    host = device_info.get("host", "Unknown Host")
    try:
        with ConnectHandler(**device_info) as net_connect:
            print(f"[{host}] Connected. Applying configuration...")
            output = net_connect.send_config_set(config_commands)
            return output
    except Exception as e:
        return f"Error applying config to {host}: {e}"

def backup_running_config(device_info):
    """
    Connects to a device, collects running-config, and saves it to a file.
    Returns a success message or an error message.
    """
    host = device_info.get("host", "Unknown Host")
    try:
        with ConnectHandler(**device_info) as net_connect:
            print(f"[{host}] Connected. Collecting running-config for backup...")
            running_config = net_connect.send_command("show running-config")
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{host}_running_config_{timestamp}.txt"
            
            with open(backup_filename, "w") as f:
                f.write(running_config)
            
            return f"Successfully backed up {host} to {backup_filename}"
    except Exception as e:
        return f"Error backing up {host}: {e}"

def process_device_concurrently(device_info):
    """
    Function to be executed by each thread for a single device in concurrent labs.
    Performs multiple operations and returns a summary.
    """
    host = device_info.get("host", "Unknown Host")
    summary = [f"--- Processing {host} ---"]
    try:
        with ConnectHandler(**device_info) as net_connect:
            # 1. Get version
            version_output = net_connect.send_command("show version")
            summary.append(f"  Version: {version_output.splitlines()}")

            # 2. Apply simple config
            config_commands = [f"hostname {host}-AUTOMATED", "interface Loopback99", "ip address 10.0.0.99 255.255.255.255", "no shutdown"]
            net_connect.send_config_set(config_commands)
            summary.append("  Config applied (hostname, Loopback99).")

            # 3. Backup running-config
            running_config = net_connect.send_command("show running-config")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{host}_running_config_{timestamp}.txt"
            with open(backup_filename, "w") as f:
                f.write(running_config)
            summary.append(f"  Backed up running-config to {backup_filename}.")
        
        summary.append(f"--- {host} Processed Successfully ---")
        return "\n".join(summary)
    except NetmikoTimeoutException:
        return f"--- {host} Failed: Connection timed out. Device unreachable or SSH issue. ---"
    except NetmikoAuthenticationException:
        return f"--- {host} Failed: Authentication failed. Check username/password/enable password. ---"
    except NetmikoBaseException as e:
        return f"--- {host} Failed: Netmiko error - {e} ---"
    except Exception as e:
        return f"--- {host} Failed: Unexpected error - {e} ---"