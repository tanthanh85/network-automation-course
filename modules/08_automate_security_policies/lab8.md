# NASP: Module 8 Lab Guide

## Implementation of Security Policies using Python - Hands-on Exercises

---

## Introduction

Welcome to Module 8 of the NASP Lab Guide! In this module, you will get hands-on with automating network security policies, specifically focusing on **Cisco Firepower Threat Defense (FTD)** managed directly via its **Firepower Device Manager (FDM) API**.

**It is crucial that you replace the dummy values for your FTD device with its actual IP address, username, and password to make the code functional.**

**Lab Objectives:**
*   Understand FDM API authentication.
*   Automate a simple FTD Access Control List (ACL) configuration (create network objects and an access rule).
*   Simulate detecting unauthorized devices using Python.

**Prerequisites:**
*   Completion of Module 1 through Module 7 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   An active internet connection.
*   **Access to a Cisco FTD device with FDM enabled (e.g., Firepower 1000/2100 series).** You will need its IP, username, and password.

Let's automate security!

---

## Lab Setup: Project Structure

For this module, we will keep the project structure simple with a few files.

1.  **Navigate** to your main `network_automation_labs` directory.
2.  **Create a new directory** for this module's labs:
    ```bash
    mkdir module8_security_lab
    cd module8_security_lab
    ```
3.  **Inside `module8_security_lab`, create the following empty Python files:**
    ```bash
    touch config.py
    touch ftd_fdm_api_ops.py
    touch security_automation_main.py
    ```

Your directory structure should now look like this:
```
network_automation_labs/
    └── module8_security_lab/
        ├── config.py
        ├── ftd_fdm_api_ops.py
        └── security_automation_main.py
```
### Task 0.1: Install `requests`

1.  Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).
2.  Navigate into your `module8_security_lab` directory:
    ```bash
    cd module8_security_lab
    ```
3.  Install the `requests` library:
    ```bash
    pip install requests
    ```
    *Expected Observation:* `requests` and its dependencies will be installed. You should see "Successfully installed..." messages.

### Task 0.2: Populate `config.py`

This file will store your FTD device's FDM API connection details.

1.  Open `config.py` in your code editor.
2.  Add the following Python code. **REPLACE THE DUMMY VALUES WITH YOUR ACTUAL LAB FTD DETAILS!**
    ```python
    # config.py

    # --- FTD Device (FDM API) Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
    # This FTD should be reachable via HTTPS (FDM API).
    FTD_FDM_API_INFO = {
        "host": "YOUR_FTD_IP", # e.g., 192.168.1.100 (for a standalone FTD appliance)
        "username": "YOUR_FDM_USERNAME", # FDM API username
        "password": "YOUR_FDM_PASSWORD", # FDM API password
        "port": 443, # Default HTTPS port for FDM API
        "verify_ssl": False # Set to True in production if you have proper CA certificates
    }
    ```
3.  Save `config.py`.

### Task 0.3: Populate `ftd_fdm_api_ops.py`

This file will contain reusable functions for FDM API interactions.

1.  Open `ftd_fdm_api_ops.py` in your code editor.
2.  Add the following Python code:
    ```python
    # ftd_fdm_api_ops.py
    import requests
    import json
    import time
    from config import FTD_FDM_API_INFO # Import FDM API info from config.py
    import urllib3
    urllib3.disable_warnings()

    # Base URL for FDM API
    FDM_BASE_URL = f"https://{FTD_FDM_API_INFO['host']}:{FTD_FDM_API_INFO['port']}/api/fdm/v6"

    # Global variable to store token
    # In a real app, this might be managed more robustly (e.g., cached, refreshed)
    _FDM_AUTH_DATA = {"token": None, "expires": 0}

    def get_fdm_token():
        """
        Authenticates to FDM API and retrieves an access token.
        Caches the token until it expires.
        """
        global _FDM_AUTH_DATA
        
        # Check if token is still valid (e.g., valid for 30 minutes, refresh 1 minute before expiry)
        if _FDM_AUTH_DATA["token"] and _FDM_AUTH_DATA["expires"] > time.time() + (60 * 1):
            # print("Using cached FDM token.") # Uncomment for debugging
            return _FDM_AUTH_DATA["token"]

        auth_url = f"{FDM_BASE_URL}/fdm/token"
        headers = {"Content-Type": "application/json"}
        payload = {
            "username": FTD_FDM_API_INFO['username'],
            "password": FTD_FDM_API_INFO['password'],
            "grant_type": "password"
        }
        
        print("Attempting to get FDM token...")
        try:
            response = requests.post(
                auth_url,
                headers=headers,
                data=json.dumps(payload),
                verify=FTD_FDM_API_INFO['verify_ssl']
            )
            response.raise_for_status()
            
            token_data = response.json()
            token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 1800) # Default to 30 mins if not provided
            
            if token:
                _FDM_AUTH_DATA["token"] = token
                _FDM_AUTH_DATA["expires"] = time.time() + (expires_in - 60) # Set expiry 1 min before actual
                print("Successfully obtained new FDM token.")
                return token
            else:
                print("FDM token not found in response.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error getting FDM token: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred getting FDM token: {e}")
            return None

    def make_fdm_api_call(method, endpoint, payload=None, query_params=None):
        """
        Generic function to make API calls to FDM.
        Automatically handles authentication.
        """
        token = get_fdm_token()
        if not token:
            print("Failed to get FDM token. Cannot make API call.")
            return None

        url = f"{FDM_BASE_URL}/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        try:
            # print(f"Making {method} request to: {url}") # Uncomment for debugging
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=query_params, verify=FTD_FDM_API_INFO['verify_ssl'])
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(payload), verify=FTD_FDM_API_INFO['verify_ssl'])
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, data=json.dumps(payload), verify=FTD_FDM_API_INFO['verify_ssl'])
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, verify=FTD_FDM_API_INFO['verify_ssl'])
            else:
                print(f"Unsupported HTTP method: {method}")
                return None

            response.raise_for_status() # Raise an exception for HTTP errors
            
            # Some DELETE/PUT operations might return 204 No Content
            if response.status_code == 204:
                return {"status": "success", "message": "No Content"}
            
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error during FDM API call to {endpoint}: {e}")
            if response is not None:
                print(f"Response status: {response.status_code}, text: {response.text}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during FDM API call to {endpoint}: {e}")
            return None

    def get_access_policies():
        """Retrieves all Access Policies."""
        print("Retrieving Access Policies...")
        return make_fdm_api_call('GET', 'policy/accesspolicies')

    def get_network_objects():
        """
        Retrieves list of network objects. 
        """
        
        response = make_fdm_api_call('GET', 'object/networks')
        
        if response and response.get('items'):
            return response # Return the full response with 'items'
        return {"items": []} # Return empty if no items or error

    def create_network_object(name, value, obj_type="Host"): # FDM often uses Host/Network/Range
        """Creates a new network object."""
        # First, check if the object already exists to ensure idempotence
        existing_obj_response = get_network_objects(name=name)
        if existing_obj_response and existing_obj_response.get('items') and len(existing_obj_response['items']) > 0:
            existing_obj = existing_obj_response['items'] # Get the first matching object
            print(f"Network object '{name}' already exists with UUID: {existing_obj['id']}. Skipping creation.")
            return existing_obj # Return the existing object's data
        
        print(f"Creating network object: {name} ({value})...")
        payload = {
            "name": name,
            "value": value,
            "type": obj_type # e.g., "Host", "Network", "Range"
        }
        return make_fdm_api_call('POST', 'object/networks', payload)

    def create_access_rule(policy_uuid, rule_name, source_network_uuid, dest_network_uuid, action="PERMIT", position=1):
        """Creates a new access rule within a given policy."""
        print(f"Creating access rule '{rule_name}' in policy {policy_uuid}...")
        payload = {
            "ruleId":0,
            "name": rule_name,
            "action": action, # "PERMIT", "DENY"
            "sourceNetworks": [{"id": source_network_uuid, "type": "networkobject"}], # FDM uses Network type for objects
            "destinationNetworks": [{"id": dest_network_uuid, "type": "networkobject"}],
            "type": "accessrule",
            "enabled": True,
            "logTraffic": False, # Set to True for logging
            "rulePosition":  position #e.g 1,2,3...
        }
        return make_fdm_api_call('POST', f'accesspolicies/{policy_uuid}/accessrules', payload)

    def delete_access_rule(policy_uuid, rule_uuid):
        """Deletes an access rule from a given policy."""
        print(f"Deleting access rule {rule_uuid} from policy {policy_uuid}...")
        return make_fdm_api_call('DELETE', f'accesspolicies/{policy_uuid}/accessrules/{rule_uuid}')

    def deploy_changes_fdm():
        """
        Initiates deployment of pending changes on FDM.
        Note: FDM API often applies changes immediately. This is for persistence.
        """
        print("Initiating FDM deployment to make changes persistent...")
        return make_fdm_api_call('POST', 'deploy') # FDM has a simple /deploy endpoint

    # Standalone test for functions (only runs when this file is executed directly)
    if __name__ == '__main__':
        from .config import FTD_FDM_API_INFO # Import from parent config
        print("--- Testing ftd_fdm_api_ops.py Functions ---")
        # Note: This will attempt to connect to the FTD device defined in config.py.
        # It will likely fail if FTD is not reachable or credentials are wrong.

        # 1. Test Token Acquisition
        token = get_fdm_token()
        if not token:
            print("Failed to get token. Cannot proceed with further tests.")
        else:
            print(f"Token: {token[:10]}...")

            # 2. Test Get Access Policies
            acps = get_access_policies()
            if acps and acps.get('items'):
                print(f"\nFound {len(acps['items'])} Access Policies.")
                for acp in acps['items'][:2]: # Print first 2
                    print(f"  ACP Name: {acp['name']}, UUID: {acp['id']}")
            else:
                print("\nNo Access Policies found or error.")

            # 3. get network object list then print out
            networks = get_network_objects()
            if networks and networks.get('items'):
                if len(networks['items']) > 0:
                    
                    for net in networks['items']:
                        print(f"\nFound {net['name']} network object. UUID: {net['id']}")
                else:
                    print("\n no network found.")
            else:
                print("\nError retrieving network objects.")

            # Further tests (create, delete rules, deploy) would require careful setup
            # and are better done in the main script with specific logic.
            # This standalone test is just for basic connectivity and function calls.
            #4. Test create networks
            networks=[
                {"name":"LAN1",
                "network": "192.168.101.0/24",
                "type": "NETWORK"},
                {"name":"LAN2",
                "network": "192.168.102.0/24",
                "type": "NETWORK"},
                {"name":"LAN3",
                "network": "192.168.103.0/24",
                "type": "NETWORK"},
                {"name":"LAN4",
                "network": "192.168.104.0/24",
                "type": "NETWORK"},
                {"name":"LAN5",
                "network": "192.168.105.0/24",
                "type": "NETWORK"},
                {"name":"LAN6",
                "network": "192.168.106.0/24",
                "type": "NETWORK"},
                {"name":"LAN7",
                "network": "192.168.107.0/24",
                "type": "NETWORK"},
                {"name":"LAN8",
                "network": "192.168.108.0/24",
                "type": "NETWORK"},
                {"name":"LAN9",
                "network": "192.168.109.0/24",
                "type": "NETWORK"},
                {"name":"LAN10",
                "network": "192.168.110.0/24",
                "type": "NETWORK"}
            ]
        for net in networks:
            id=get_network_object_id(name=net['name'])
            if id:
                print(f"Network object '{net['name']}' already exists with UUID: {id}. Skipping creation.")
                #create_network=create_network_object(name=net["name"],value=net["network"],obj_type=net["type"])
            else:
                create_network=create_network_object(name=net["name"],value=net["network"],obj_type=net["type"])
        #5. Create access rules
        create_access_rule(policy_uuid=uuid,rule_name="Allow-LAN1-to-LAN2",source_network_uuid=get_network_object_id(name="LAN1"),dest_network_uuid=get_network_object_id(name="LAN2"),action="PERMIT",position=1)
        create_access_rule(policy_uuid=uuid,rule_name="Allow-LAN3-to-LAN4",source_network_uuid=get_network_object_id(name="LAN3"),dest_network_uuid=get_network_object_id(name="LAN4"),action="PERMIT",position=2)
        print("\n--- ftd_fdm_api_ops.py Test Complete ---")
    ```
3.  Save `ftd_fdm_api_ops.py`.

### Task 0.4: Populate `security_automation_main.py`

This is the main script that will orchestrate the security automation tasks.

1.  Open `security_automation_main.py` in your code editor.
2.  Add the following Python code:
    ```python
    # security_automation_main.py
    import logging
    import time
    from ftd_fdm_api_ops import get_access_policies, create_network_object, create_access_rule, delete_access_rule, get_network_object_id, deploy_changes_fdm
    from config import FTD_FDM_API_INFO # For host IP in messages

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def automate_firewall_rule_creation(ftd_host, source_ip, dest_ip, rule_name="Lab_Automated_Rule", policy_name="NGFW-Access-Policy"):
        """
        Automates the creation of a firewall rule on FDM.
        1. Finds the target Access Policy.
        2. Creates source and destination network objects.
        3. Creates the access rule.
        4. Initiates deployment (to make changes persistent).
        """
        logging.info(f"\n--- Starting Firewall Rule Automation ---")
        logging.info(f"Target FTD: {ftd_host}")
        logging.info(f"Rule: Allow {source_ip} to {dest_ip}")

        # 1. Get Access Policy UUID
        policy_uuid = None
        acps = get_access_policies()
        if acps and acps.get('items'):
            for acp in acps['items']:
                if acp['name'] == policy_name:
                    policy_uuid = acp['id']
                    logging.info(f"Found Access Policy '{policy_name}' with UUID: {policy_uuid}")
                    break
        if not policy_uuid:
            logging.error(f"Access Policy '{policy_name}' not found. Aborting rule creation.")
            return False

        # 2. Create Network Objects (if they don't exist)
        # Source object
        src_obj_name = f"Host_{source_ip.replace('.', '_')}"
        src_obj_data = create_network_object(src_obj_name, source_ip, "HOST")
        if not src_obj_data or not src_obj_data.get('id'):
            logging.error(f"Failed to create/get source object for {source_ip}. Aborting.")
            return False
        source_network_uuid = src_obj_data['id'] if 'id' in src_obj_data else src_obj_data['id'] # Handle both create and already exists response types
        logging.info(f"Source object '{src_obj_name}' UUID: {source_network_uuid}")

        # Destination object
        dest_obj_name = f"Host_{dest_ip.replace('.', '_')}"
        dest_obj_data = create_network_object(dest_obj_name, dest_ip, "HOST")
        if not dest_obj_data or not dest_obj_data.get('id'):
            logging.error(f"Failed to create/get destination object for {dest_ip}. Aborting.")
            return False
        dest_network_uuid = dest_obj_data['id'] if 'id' in dest_obj_data else dest_obj_data['id'] # Handle both create and already exists response types
        logging.info(f"Destination object '{dest_obj_name}' UUID: {dest_network_uuid}")

        # 3. Create the Access Rule
        rule_result = create_access_rule(policy_uuid, rule_name, source_network_uuid, dest_network_uuid, action="PERMIT", position=1)
        if rule_result and rule_result.get('id'):
            logging.info(f"Successfully created rule '{rule_name}' with UUID: {rule_result['id']}")
            # Store rule UUID for potential deletion later
            # created_rule_uuid = rule_result['id'] # Uncomment if needed for cleanup
        else:
            logging.error(f"Failed to create rule '{rule_name}'. Aborting.")
            return False

        # 4. Initiate Deployment (to make changes persistent)
        # deploy_result = deploy_changes_fdm()
        # if deploy_result and deploy_result.get('status') == 'success':
        #     logging.info("Deployment initiated successfully on FDM.")
        # else:
        #     logging.error("Failed to initiate deployment on FDM.")

        # logging.info(f"--- Firewall Rule Automation Complete ---")
        # return True

    def simulate_unauthorized_device_detection(network_segment="192.168.1.0/24"):
        """
        Simulates detecting unauthorized devices by comparing detected MACs/IPs
        against a whitelist.
        """
        logging.info(f"\n--- Starting Unauthorized Device Detection Simulation ---")
        logging.info(f"Scanning network segment: {network_segment}")

        # --- Simulated Data ---
        # In a real scenario, these would come from Netmiko (ARP/MAC tables),
        # DHCP logs, NAC API (e.g., Cisco ISE), etc.
        AUTHORIZED_DEVICES = {
            "AA:BB:CC:DD:EE:F1": "Server-1",
            "AA:BB:CC:DD:EE:F2": "Printer-A",
            "AA:BB:CC:DD:EE:F3": "Laptop-User1"
        }
        DETECTED_MACS_ON_NETWORK = [
            "AA:BB:CC:DD:EE:F1", # Authorized
            "AA:BB:CC:DD:EE:F3", # Authorized
            "DD:EE:FF:11:22:33", # Unauthorized
            "11:22:33:44:55:66"  # Unauthorized
        ]
        # --- End Simulated Data ---

        unauthorized_macs = []
        for mac in DETECTED_MACS_ON_NETWORK:
            if mac not in AUTHORIZED_DEVICES:
                unauthorized_macs.append(mac)
        
        if unauthorized_macs:
            logging.warning(f"!!! UNAUTHORIZED DEVICES DETECTED on {network_segment} (via simulated scan):")
            for mac in unauthorized_macs:
                logging.warning(f"    - MAC: {mac}")
            # In a real scenario, you would trigger actions here:
            # - Send email/Slack alert
            # - Trigger port shutdown via Netmiko
            # - Create blocking rule on FDM via API (using create_network_object and create_access_rule)
        else:
            logging.info(f"No unauthorized devices detected on {network_segment}.")

        logging.info(f"--- Unauthorized Device Detection Complete ---")

    if __name__ == '__main__':
        print("--- Running Security Automation Main Script ---")
        
        # Example 1: Automate Firewall Rule Creation
        automate_firewall_rule_creation(
            FTD_FDM_API_INFO['host'],
            source_ip="192.168.10.50",
            dest_ip="192.168.20.100",
            rule_name="Lab_Automated_Rule"
        )
        
        # Example 2: Detect Unauthorized Devices
        # simulate_unauthorized_device_detection("192.168.1.0/24")


        # deploy_result = deploy_changes_fdm()
        # print(deploy_result)
        # if deploy_result and deploy_result.get('status') == 'success':
        #     logging.info("Deployment initiated successfully on FDM.")
        # else:
        #     logging.error("Failed to initiate deployment on FDM.")
        # print(deploy_result['links']['self'])

        logging.info(f"--- Firewall Rule Automation Complete ---")
        # return True

        print("\n--- Security Automation Script Complete ---")
    ```
3.  Save `security_automation_main.py`.

---

## Lab 1: Automate Access Control List (ACL) Configurations

**Objective:** Use Python and FDM API functions to create a new firewall rule.

### Task 1.1: Run the `security_automation_main.py` Script

1.  **Ensure you have updated `config.py` with your real FTD device details.**
2.  **Run the script** from your `module8_security_lab` directory:
    ```bash
    python security_automation_main.py
    ```
    *Expected Output (if dummy FTD info is not replaced):*
    ```
    --- Running Security Automation Main Script ---

    --- Starting Firewall Rule Automation ---
    Target FTD: YOUR_FTD_IP
    Rule: Allow 192.168.10.50 to 192.168.20.100
    Attempting to get FDM token...
    Error getting FDM token: HTTPSConnectionPool(host='YOUR_FTD_IP', port=443): Max retries exceeded with url: /api/fdm/v6/token (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x...>: Failed to establish a new connection: [Errno 111] Connection refused'))
    Failed to get FDM token. Cannot make API call.
    Access Policy 'Default_Access_Policy' not found. Aborting rule creation.
    --- Firewall Rule Automation Complete ---

    --- Starting Unauthorized Device Detection Simulation ---
    Scanning network segment: 192.168.1.0/24
    !!! UNAUTHORIZED DEVICES DETECTED on 192.168.1.0/24 (via simulated scan):
        - MAC: DD:EE:FF:11:22:33
        - MAC: 11:22:33:44:55:66
    --- Unauthorized Device Detection Complete ---

    --- Security Automation Script Complete ---
    ```
    *Expected Output (if you replace with real, reachable FTD info):*
    ```
    --- Running Security Automation Main Script ---

    --- Starting Firewall Rule Automation ---
    Target FTD: YOUR_FTD_IP
    Rule: Allow 192.168.10.50 to 192.168.20.100
    Attempting to get FDM token...
    Successfully obtained new FDM token.
    Retrieving Access Policies...
    Found Access Policy 'Default_Access_Policy' with UUID: 00000000-0000-0000-0000-000000000001
    Retrieving network objects (name=Host_192_168_10_50)...
    Network object 'Host_192_168_10_50' already exists with UUID: 00000000-0000-0000-0000-000000000002. Skipping creation.
    Retrieving network objects (name=Host_192_168_20_100)...
    Network object 'Host_192_168_20_100' already exists with UUID: 00000000-0000-0000-0000-000000000003. Skipping creation.
    Creating access rule 'Lab_Automated_Rule' in policy 00000000-0000-0000-0000-000000000001...
    Successfully created rule 'Lab_Automated_Rule' with UUID: 00000000-0000-0000-0000-000000000004
    Initiating FDM deployment to make changes persistent...
    --- Firewall Rule Automation Complete ---

    --- Starting Unauthorized Device Detection Simulation ---
    Scanning network segment: 192.168.1.0/24
    !!! UNAUTHORIZED DEVICES DETECTED on 192.168.1.0/24 (via simulated scan):
        - MAC: DD:EE:FF:11:22:33
        - MAC: 11:22:33:44:55:66
    --- Unauthorized Device Detection Complete ---

    --- Security Automation Script Complete ---
    ```
    *Observation:* If successful, log in to your FDM web GUI (typically `https://<FTD_IP>`) and navigate to `Policies > Access Control`. You should see the newly created network objects and the access rule.

---

## Lab 2: Detect Unauthorized Devices using Python Scripts

**Objective:** Understand how Python can be used to detect unauthorized devices on the network.

### Task 2.1: Run the Detection Script

The `security_automation_main.py` script already contains the `simulate_unauthorized_device_detection` function and calls it.

1.  **Run the main script again:**
    ```bash
    python security_automation_main.py
    ```
    *Expected Output:* The output related to "Unauthorized Device Detection Simulation" will be the same as in Lab 1.1's output.

    ```
    --- Starting Unauthorized Device Detection Simulation ---
    Scanning network segment: 192.168.1.0/24
    !!! UNAUTHORIZED DEVICES DETECTED on 192.168.1.0/24 (via simulated scan):
        - MAC: DD:EE:FF:11:22:33
        - MAC: 11:22:33:44:55:66
    --- Unauthorized Device Detection Complete ---
    ```
    *Observation:* This simulation demonstrates the logic. In a real environment, `get_detected_mac_addresses_simulated` would be replaced with actual calls to network devices (e.g., `show mac address-table` via Netmiko), DHCP servers, or NAC systems (e.g., Cisco ISE API). The `AUTHORIZED_DEVICES` list would come from a trusted source (e.g., CMDB, inventory system).

---

## Conclusion

You've now completed Module 8 and gained practical experience with implementing security policies using Python! You can now:

*   Understand the importance of automating network security.
*   Automate Cisco FTD ACL configurations via the FDM API.
*   Build Python scripts to detect unauthorized devices on your network.

Automating security policies is a critical skill for maintaining a robust and compliant network infrastructure.

**Keep Automating!**

---