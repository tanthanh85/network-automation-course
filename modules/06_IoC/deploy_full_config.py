# deploy_full_config.py

import yaml # For loading YAML data
from jinja2 import Environment, FileSystemLoader # For Jinja2 templating
from netmiko import ConnectHandler # For Netmiko device interaction
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException # For error handling
import logging # For logging messages
import os # For path operations

# --- 1. Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 2. Define Router Connection Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
# This dictionary holds the connection parameters for your Cisco IOS XE router.
# Ensure your router is reachable via SSH and has the correct credentials.
ROUTER_CONNECTION_INFO = {
    "device_type": "cisco_ios",
    "host": "10.10.20.48",        # <<< REPLACE THIS
    "username": "developer",     # <<< REPLACE THIS
    "password": "C1sco12345",     # <<< REPLACE THIS
    "secret": "YOUR_ENABLE_PASSWORD", # <<< REPLACE THIS (if your router uses enable password)
    "port": 22,                      # Default SSH port
}

# --- 3. Define File Paths ---
DATA_FILE = "network_data.yaml"
TEMPLATE_DIR = "templates" # Directory where Jinja2 templates are stored
TEMPLATE_FILE = "router_full_config.j2" # The specific Jinja2 template to use

# --- 4. Main Deployment Function ---
def deploy_full_configuration():
    """
    Orchestrates the IaC deployment process for a single router:
    1. Loads network data for the specific router from YAML.
    2. Renders configuration using Jinja2.
    3. Pushes the generated configuration to the router via Netmiko.
    """
    logging.info(f"\n--- Starting IaC Deployment Workflow for {ROUTER_CONNECTION_INFO['host']} ---")

    # Load all network data from YAML file
    try:
        with open(DATA_FILE, 'r') as f:
            all_network_data = yaml.safe_load(f)
        logging.info(f"Successfully loaded data from {DATA_FILE}.")
    except Exception as e:
        logging.error(f"Error loading network data from {DATA_FILE}: {e}")
        return False

    # Find the specific router's data from the loaded YAML
    target_router_data = None
    for router_entry in all_network_data.get('routers', []):
        if router_entry.get('mgmt_ip') == ROUTER_CONNECTION_INFO['host']:
            target_router_data = router_entry
            break
    
    if not target_router_data:
        logging.error(f"Router with IP {ROUTER_CONNECTION_INFO['host']} not found in {DATA_FILE}. Aborting.")
        return False

    # Set up Jinja2 environment to load templates from the 'templates' directory
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)
    
    # Render the template with the specific router's data
    rendered_config = template.render(router=target_router_data) # Pass the single router's data as 'router'
    logging.info(f"--- Rendered Configuration for {target_router_data['name']} ---")
    logging.info(f"\n{rendered_config}") # Display the generated config
    logging.info(f"------------------------------------")

    # Netmiko's send_config_set expects a list of configuration commands.
    # Split the rendered config string by lines and filter out empty ones.
    config_commands_list = [line for line in rendered_config.splitlines() if line.strip()]

    if not config_commands_list:
        logging.error("Generated configuration is empty. Aborting deployment.")
        return False

    # --- Push Configuration via Netmiko ---
    host = ROUTER_CONNECTION_INFO.get('host')
    try:
        logging.info(f"Connecting to {host} via Netmiko...")
        with ConnectHandler(**ROUTER_CONNECTION_INFO) as net_connect:
            logging.info(f"Connected to {host}. Pushing configuration...")
            
            # Use send_config_set to push the list of commands
            output = net_connect.send_config_set(config_commands_list)
            
            logging.info(f"Netmiko push output:\n{output}")
            logging.info(f"Configuration successfully pushed to {host}.")
            return True
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        logging.error(f"Netmiko connection/authentication error to {host}: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during deployment to {host}: {e}")
        return False


if __name__ == "__main__":
    print("\n=== Starting IaC Deployment Script ===")
    
    success = deploy_full_configuration()
    
    if success:
        print(f"\nDeployment to {ROUTER_CONNECTION_INFO['host']} completed successfully!")
        print("Please log in to your router and verify the new configuration.")
    else:
        print(f"\nDeployment to {ROUTER_CONNECTION_INFO['host']} failed. Check logs for details.")
    
    print("\n=== Script Finished ===")

