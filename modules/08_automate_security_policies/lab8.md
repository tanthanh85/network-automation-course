# Python Basics for Network Automation: Module 8 Lab Guide

## Implementation of Security Policies using Python - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 8 of the Python Basics for Network Automation Lab Guide! In this module, you will get hands-on with automating network security policies, specifically focusing on **Cisco Firepower Threat Defense (FTD)** managed by the **Firepower Management Center (FMC) API**.

**It is crucial that you replace the dummy values for your FMC with its actual IP address, username, and password to make the code functional.**

**Lab Objectives:**
*   Understand FMC API authentication.
*   Automate a simple FTD Access Control List (ACL) configuration (create network objects and an access rule).
*   Initiate deployment of changes to FTD.
*   Simulate detecting unauthorized devices using Python.

**Prerequisites:**
*   Completion of Module 1 through Module 7 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   An active internet connection.
*   **Access to a Cisco Firepower Management Center (FMC) sandbox.**

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
    touch fmc_api_ops.py
    touch security_automation_main.py
    ```

Your directory structure should now look like this:
```
network_automation_labs/
└── module8_security_lab/
├── config.py
├── fmc_api_ops.py
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

This file will store your FMC API connection details.

1.  Open `config.py` in your code editor.
2.  Add the following Python code. **REPLACE THE DUMMY VALUES WITH YOUR ACTUAL LAB FMC DETAILS!**
    ```python
    # config.py

    # --- FMC API Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
    # This FMC should be reachable via HTTPS.
    FMC_API_INFO = {
        "host": "YOUR_FMC_IP_OR_HOSTNAME", # e.g., 10.10.20.50 (from Cisco DevNet Sandbox)
        "username": "YOUR_FMC_USERNAME", # e.g., admin
        "password": "YOUR_FMC_PASSWORD", # e.g., Admin123
        "port": 443, # Default HTTPS port for FMC API
        "verify_ssl": False # Set to True in production if you have proper CA certificates
    }
    ```
3.  Save `config.py`.

### Task 0.3: Populate `fmc_api_ops.py`

This file will contain reusable functions for FMC API interactions.

1.  Open `fmc_api_ops.py` in your code editor.
2.  Add the following Python code:
    ```python
    # fmc_api_ops.py
    import requests
    import json
    import time
    from .config import FMC_API_INFO # Import FMC API info from config.py

    # Base URL for FMC API
    FMC_BASE_URL = f"https://{FMC_API_INFO['host']}:{FMC_API_INFO['port']}/api/fmc_platform/v1"

    # Global variable to store token and domain UUID
    # In a real app, this might be managed more robustly (e.g., cached, refreshed)
    _FMC_AUTH_DATA = {"token": None, "domain_uuid": None, "expires": 0}

    def get_fmc_token():
        """
        Authenticates to FMC API and retrieves an access token and domain UUID.
        Caches the token until it expires.
        """
        global _FMC_AUTH_DATA
        
        # Check if token is still valid
        if _FMC_AUTH_DATA["token"] and _FMC_AUTH_DATA["expires"] > time.time() + 60: # Refresh 60s before expiry
            # print("Using cached FMC token.") # Uncomment for debugging
            return _FMC_AUTH_DATA["token"], _FMC_AUTH_DATA["domain_uuid"]

        auth_url = f"{FMC_BASE_URL}/auth/generatetoken"
        headers = {"Content-Type": "application/json"}
        
        print("Attempting to get FMC token...")
        try:
            response = requests.post(
                auth_url,
                auth=(FMC_API_INFO['username'], FMC_API_INFO['password']),
                headers=headers,
                verify=FMC_API_INFO['verify_ssl']
            )
            response.raise_for_status()
            
            # Token is in the header, Domain UUID is also in header
            token = response.headers.get('X-auth-access-token')
            domain_uuid = response.headers.get('DOMAIN_UUID')
            expires_at = int(response.headers.get('X-token-expiration')) # Unix timestamp
            
            if token and domain_uuid:
                _FMC_AUTH_DATA["token"] = token
                _FMC_AUTH_DATA["domain_uuid"] = domain_uuid
                _FMC_AUTH_DATA["expires"] = expires_at
                print("Successfully obtained new FMC token.")
                return token, domain_uuid
            else:
                print("FMC token or domain UUID not found in response headers.")
                return None, None
        except requests.exceptions.RequestException as e:
            print(f"Error getting FMC token: {e}")
            return None, None
        except Exception as e:
            print(f"An unexpected error occurred getting FMC token: {e}")
            return None, None

    def make_fmc_api_call(method, endpoint, payload=None):
        """
        Generic function to make API calls to FMC.
        Automatically handles authentication.
        """
        token, domain_uuid = get_fmc_token()
        if not token or not domain_uuid:
            print("Failed to get FMC token or domain UUID. Cannot make API call.")
            return None

        url = f"{FMC_BASE_URL}/fmc_config/v1/domain/{domain_uuid}/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "X-auth-access-token": token
        }
        
        try:
            # print(f"Making {method} request to: {url}") # Uncomment for debugging
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, verify=FMC_API_INFO['verify_ssl'])
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(payload), verify=FMC_API_INFO['verify_ssl'])
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, data=json.dumps(payload), verify=FMC_API_INFO['verify_ssl'])
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, verify=FMC_API_INFO['verify_ssl'])
            else:
                print(f"Unsupported HTTP method: {method}")
                return None

            response.raise_for_status() # Raise an exception for HTTP errors
            
            # Some DELETE/PUT operations might return 204 No Content
            if response.status_code == 204:
                return {"status": "success", "message": "No Content"}
            
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error during FMC API call to {endpoint}: {e}")
            if response is not None:
                print(f"Response status: {response.status_code}, text: {response.text}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during FMC API call to {endpoint}: {e}")
            return None

    def get_access_policies():
        """Retrieves all Access Control Policies."""
        print("Retrieving Access Control Policies...")
        return make_fmc_api_call('GET', 'policy/accesspolicies')

    def get_network_objects(name=None):
        """Retrieves network objects, optionally filtered by name."""
        print(f"Retrieving network objects (name={name})...")
        endpoint = 'object/networks'
        if name:
            endpoint += f'?name={name}'
        return make_fmc_api_call('GET', endpoint)

    def create_network_object(name, value, obj_type="Network"):
        """Creates a new network object."""
        print(f"Creating network object: {name} ({value})...")
        payload = {
            "name": name,
            "value": value,
            "type": obj_type # e.g., "Network", "Host", "Range"
        }
        return make_fmc_api_call('POST', 'object/networks', payload)

    def create_access_rule(policy_id, rule_name, source_network_id, dest_network_id, action="ALLOW", position="LAST"):
        """Creates a new access rule within a given policy."""
        print(f"Creating access rule '{rule_name}' in policy {policy_id}...")
        payload = {
            "name": rule_name,
            "action": action,
            "sourceNetworks": {"objects": [{"id": source_network_id, "type": "Network"}]},
            "destinationNetworks": {"objects": [{"id": dest_network_id, "type": "Network"}]},
            "type": "AccessRule",
            "enabled": True,
            "logTraffic": False, # Set to True for logging
            "rulePosition": {"action": position} # e.g., "LAST", "FIRST"
        }
        return make_fmc_api_call('POST', f'policy/accesspolicies/{policy_id}/accessrules', payload)

    def delete_access_rule(policy_id, rule_id):
        """Deletes an access rule from a given policy."""
        print(f"Deleting access rule {rule_id} from policy {policy_id}...")
        return make_fmc_api_call('DELETE', f'policy/accesspolicies/{policy_id}/accessrules/{rule_id}')

    def deploy_changes(device_ids):
        """Initiates deployment to specified FTD devices."""
        print(f"Initiating deployment to devices: {device_ids}...")
        payload = {
            "type": "DeploymentRequest",
            "version": "1.0",
            "deviceList": [{"id": dev_id, "type": "Device"} for dev_id in device_ids],
            "deploymentMode": "FORCED" # "FORCED" or "EVALUATE"
        }
        # Deployment API is under platform, not config
        url = f"https://{FMC_API_INFO['host']}:{FMC_API_INFO['port']}/api/fmc_platform/v1/domain/{_FMC_AUTH_DATA['domain_uuid']}/deployment/deploymentrequests"
        headers = {
            "Content-Type": "application/json",
            "X-auth-access-token": _FMC_AUTH_DATA["token"]
        }
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), verify=FMC_API_INFO['verify_ssl'])
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error initiating deployment: {e}")
            if response is not None:
                print(f"Response status: {response.status_code}, text: {response.text}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during deployment: {e}")
            return None

    # Standalone test for functions (only runs when this file is executed directly)
    if __name__ == '__main__':
        print("--- Testing fmc_api_ops.py Functions ---")
        # Note: This will attempt to connect to the FMC defined in config.py.
        # It will likely fail if FMC is not reachable or credentials are wrong.

        # 1. Test Token Acquisition
        token, domain = get_fmc_token()
        if not token:
            print("Failed to get token. Cannot proceed with further tests.")
        else:
            print(f"Token: {token[:10]}..., Domain: {domain}")

            # 2. Test Get Access Policies
            acps = get_access_policies()
            if acps and acps.get('items'):
                print(f"\nFound {len(acps['items'])} Access Control Policies.")
                for acp in acps['items'][:2]: # Print first 2
                    print(f"  ACP Name: {acp['name']}, ID: {acp['id']}")
                    # Store a sample policy ID for later use
                    # sample_acp_id = acp['id'] # Uncomment if you need to use this in interactive session
            else:
                print("\nNo Access Control Policies found or error.")

            # 3. Test Get Network Objects
            networks = get_network_objects(name="any-ipv4") # Search for a common object
            if networks and networks.get('items'):
                print(f"\nFound 'any-ipv4' object. ID: {networks['items']['id']}")
            else:
                print("\n'any-ipv4' object not found or error.")

            # Further tests (create, delete rules, deploy) would require careful setup
            # and are better done in the main script with specific logic.
            # This standalone test is just for basic connectivity and function calls.
        print("\n--- fmc_api_ops.py Test Complete ---")
    ```
3.  Save `fmc_api_ops.py`.

### Task 0.4: Populate `security_automation_main.py`

This is the main script that will orchestrate the security automation tasks.

1.  Open `security_automation_main.py` in your code editor.
2.  Add the following Python code:
    ```python
    # security_automation_main.py
    import logging
    import time
    from .fmc_api_ops import get_access_policies, create_network_object, create_access_rule, delete_access_rule, get_network_objects, deploy_changes
    from .config import FMC_API_INFO # For host IP in messages

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def automate_firewall_rule_creation(fmc_host, source_ip, dest_ip, rule_name="Lab_Automated_Rule", policy_name="Default Access Policy"):
        """
        Automates the creation of a firewall rule on FMC.
        1. Finds the target Access Control Policy.
        2. Creates source and destination network objects.
        3. Creates the access rule.
        4. Initiates deployment.
        """
        logging.info(f"\n--- Starting Firewall Rule Automation ---")
        logging.info(f"Target FMC: {fmc_host}")
        logging.info(f"Rule: Allow {source_ip} to {dest_ip}")

        # 1. Get Access Control Policy ID
        acp_id = None
        acps = get_access_policies()
        if acps and acps.get('items'):
            for acp in acps['items']:
                if acp['name'] == policy_name:
                    acp_id = acp['id']
                    logging.info(f"Found ACP '{policy_name}' with ID: {acp_id}")
                    break
        if not acp_id:
            logging.error(f"ACP '{policy_name}' not found. Aborting rule creation.")
            return False

        # 2. Create Network Objects (if they don't exist)
        # Check if source object exists
        src_obj_name = f"Host_{source_ip.replace('.', '_')}"
        src_obj_search = get_network_objects(name=src_obj_name)
        if src_obj_search and src_obj_search.get('items'):
            source_network_id = src_obj_search['items']['id']
            logging.info(f"Source object '{src_obj_name}' already exists with ID: {source_network_id}")
        else:
            new_src_obj = create_network_object(src_obj_name, source_ip, "Host")
            if new_src_obj and new_src_obj.get('id'):
                source_network_id = new_src_obj['id']
                logging.info(f"Created source object '{src_obj_name}' with ID: {source_network_id}")
            else:
                logging.error(f"Failed to create source object for {source_ip}. Aborting.")
                return False

        # Check if destination object exists
        dest_obj_name = f"Host_{dest_ip.replace('.', '_')}"
        dest_obj_search = get_network_objects(name=dest_obj_name)
        if dest_obj_search and dest_obj_search.get('items'):
            dest_network_id = dest_obj_search['items']['id']
            logging.info(f"Destination object '{dest_obj_name}' already exists with ID: {dest_network_id}")
        else:
            new_dest_obj = create_network_object(dest_obj_name, dest_ip, "Host")
            if new_dest_obj and new_dest_obj.get('id'):
                dest_network_id = new_dest_obj['id']
                logging.info(f"Created destination object '{dest_obj_name}' with ID: {dest_network_id}")
            else:
                logging.error(f"Failed to create destination object for {dest_ip}. Aborting.")
                return False

        # 3. Create the Access Rule
        rule_result = create_access_rule(acp_id, rule_name, source_network_id, dest_network_id, action="ALLOW", position="FIRST")
        if rule_result and rule_result.get('id'):
            logging.info(f"Successfully created rule '{rule_name}' with ID: {rule_result['id']}")
            # Store rule ID for potential deletion later
            # created_rule_id = rule_result['id'] # Uncomment if needed for cleanup
        else:
            logging.error(f"Failed to create rule '{rule_name}'. Aborting.")
            return False

        # 4. Initiate Deployment (conceptual - you'd need FTD device IDs for real deployment)
        # In a real scenario, you'd get FTD device IDs from FMC API (e.g., /api/fmc_config/v1/domain/{domainUUID}/devices/devicerecords)
        # For this lab, we'll just simulate the deployment initiation.
        logging.info("Simulating deployment initiation. (Real deployment requires FTD device IDs).")
        # Example of how to get FTD device IDs for deployment:
        # devices_rec = make_fmc_api_call('GET', 'devices/devicerecords')
        # if devices_rec and devices_rec.get('items'):
        #     ftd_device_ids = [dev['id'] for dev in devices_rec['items'] if 'FTD' in dev.get('type')]
        #     if ftd_device_ids:
        #         deployment_result = deploy_changes(ftd_device_ids)
        #         if deployment_result:
        #             logging.info(f"Deployment initiated successfully. Status: {deployment_result.get('status')}")
        #         else:
        #             logging.error("Failed to initiate deployment.")
        #     else:
        #         logging.warning("No FTD devices found for deployment.")
        # else:
        #     logging.warning("Could not retrieve device records for deployment.")

        logging.info(f"--- Firewall Rule Automation Complete ---")
        return True

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
            # - Create blocking rule on FMC via API (using create_network_object and create_access_rule)
        else:
            logging.info(f"No unauthorized devices detected on {network_segment}.")

        logging.info(f"--- Unauthorized Device Detection Complete ---")

    if __name__ == '__main__':
        print("--- Running Security Automation Main Script ---")
        
        # Example 1: Automate Firewall Rule Creation
        automate_firewall_rule_creation(
            FMC_API_INFO['host'],
            source_ip="192.168.10.50",
            dest_ip="192.168.20.100",
            rule_name="Lab_Automated_Rule"
        )
        
        # Example 2: Detect Unauthorized Devices
        simulate_unauthorized_device_detection("192.168.1.0/24")

        print("\n--- Security Automation Script Complete ---")
    ```
3.  Save `security_automation_main.py`.

---

## Lab 1: Automate Access Control List (ACL) Configurations

**Objective:** Use Python and FMC API functions to create a new firewall rule.

### Task 1.1: Run the `security_automation_main.py` Script

1.  **Ensure you have updated `config.py` with your real FMC device details.**
2.  **Run the script** from your `module8_security_lab` directory:
    ```bash
    python security_automation_main.py
    ```
    *Expected Output (if dummy FMC info is not replaced):*
    ```
    --- Running Security Automation Main Script ---

    --- Starting Firewall Rule Automation ---
    Target FMC: YOUR_FMC_IP_OR_HOSTNAME
    Rule: Allow 192.168.10.50 to 192.168.20.100
    Attempting to get FMC token...
    Error getting FMC token: HTTPSConnectionPool(host='YOUR_FMC_IP_OR_HOSTNAME', port=443): Max retries exceeded with url: /api/fmc_platform/v1/auth/generatetoken (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x...>: Failed to establish a new connection: [Errno 111] Connection refused'))
    Failed to get FMC token or domain UUID. Cannot make API call.
    ACP 'Default Access Policy' not found. Aborting rule creation.
    --- Firewall Rule Automation Complete ---

    --- Starting Unauthorized Device Detection Simulation ---
    Scanning network segment: 192.168.1.0/24
    !!! UNAUTHORIZED DEVICES DETECTED on 192.168.1.0/24 (via simulated scan):
        - MAC: DD:EE:FF:11:22:33
        - MAC: 11:22:33:44:55:66
    --- Unauthorized Device Detection Complete ---

    --- Security Automation Script Complete ---
    ```
    *Expected Output (if you replace with real, reachable FMC info):*
    ```
    --- Running Security Automation Main Script ---

    --- Starting Firewall Rule Automation ---
    Target FMC: YOUR_FMC_IP_OR_HOSTNAME
    Rule: Allow 192.168.10.50 to 192.168.20.100
    Attempting to get FMC token...
    Successfully obtained new FMC token.
    Retrieving Access Control Policies...
    Found ACP 'Default Access Policy' with ID: 00000000-0000-0000-0000-000000000001
    Retrieving network objects (name=Host_192_168_10_50)...
    Creating network object: Host_192_168_10_50 (192.168.10.50)...
    Created source object 'Host_192_168_10_50' with ID: 00000000-0000-0000-0000-000000000002
    Retrieving network objects (name=Host_192_168_20_100)...
    Creating network object: Host_192_168_20_100 (192.168.20.100)...
    Created destination object 'Host_192_168_20_100' with ID: 00000000-0000-0000-0000-000000000003
    Creating access rule 'Lab_Automated_Rule' in policy 00000000-0000-0000-0000-000000000001...
    Successfully created rule 'Lab_Automated_Rule' with ID: 00000000-0000-0000-0000-000000000004
    Simulating deployment initiation. (Real deployment requires FTD device IDs).
    --- Firewall Rule Automation Complete ---

    --- Starting Unauthorized Device Detection Simulation ---
    Scanning network segment: 192.168.1.0/24
    !!! UNAUTHORIZED DEVICES DETECTED on 192.168.1.0/24 (via simulated scan):
        - MAC: DD:EE:FF:11:22:33
        - MAC: 11:22:33:44:55:66
    --- Unauthorized Device Detection Complete ---

    --- Security Automation Script Complete ---
    ```
    *Observation:* If successful, log in to your FMC GUI, navigate to `Policies > Access Control`, select your policy (e.g., "Default Access Policy"), and you should see the newly created rule "Lab_Automated_Rule" at the top. Note that it's not yet deployed to the FTD device; you would need to initiate a deployment from the FMC GUI (or via API if you had the FTD device IDs).

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
*   Automate Cisco FTD ACL configurations via the FMC API.
*   Build Python scripts to detect unauthorized devices on your network.

Automating security policies is a critical skill for maintaining a robust and compliant network infrastructure.

**Keep Automating!**

---