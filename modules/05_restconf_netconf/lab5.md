---

## Document 2: Python Basics for Network Automation - Module 5 Lab Guide

```markdown
# Python Basics for Network Automation: Module 5 Lab Guide

## Using APIs to Retrieve Data on Cisco Network Devices - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 5 of the Python Basics for Network Automation Lab Guide! In this module, you will gain hands-on experience with using APIs to retrieve data. We will focus on **REST APIs** and the `requests` Python library.

We will use **dummy API information** for Cisco DNA Center/Catalyst Center and Cisco IOS XE RESTCONF. **It is crucial that you replace these dummy values with the actual URLs, usernames, and passwords of your lab environment (e.g., Cisco DevNet Sandbox) to make the code functional.**

**Lab Objectives:**
*   Install the `requests` library.
*   Make a simple GET request to a public REST API.
*   Query device information from Cisco DNA Center/Catalyst Center (using dummy credentials).
*   Query device performance data from Cisco IOS XE (using dummy credentials).
*   Build a simple monitoring tool using API concepts.

**Prerequisites:**
*   Completion of Module 1, Module 2, Module 3, and Module 4 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   An active internet connection (for public API calls and potential lab access).
*   **Optional but Recommended:** Access to a Cisco DNA Center/Catalyst Center sandbox or an IOS XE device with RESTCONF enabled (e.g., Cisco DevNet Sandboxes).

Let's start exploring APIs!

---

## Lab Setup: Single File Approach

For this module, we will keep all the code in a single Python file.

1.  **Navigate** to your main `network_automation_labs` directory.
2.  **Create a new Python file** for this module's labs:
    ```bash
    cd network_automation_labs
    touch api_lab.py
    ```

### Task 0.1: Define API Information

This section will hold the dummy API connection details.

1.  Open `api_lab.py` in your code editor.
2.  Add the following Python code. **REPLACE THE DUMMY VALUES WITH YOUR ACTUAL LAB API DETAILS!**
    ```python
    # api_lab.py

    # --- Import necessary libraries ---
    import requests
    import json # For pretty-printing JSON
    import time # For monitoring lab
    import random # For simulating dynamic data

    # --- API Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
    # If you don't have access to these, the code will attempt to connect and fail,
    # demonstrating error handling. You can then proceed with the simulated labs.
    API_INFO = {
        # Cisco DNA Center / Catalyst Center Details
        "dnac_url": "https://YOUR_DNAC_IP_OR_HOSTNAME", # e.g., sandbox-dnac.cisco.com
        "dnac_username": "YOUR_DNAC_USERNAME", # e.g., devnetuser
        "dnac_password": "YOUR_DNAC_PASSWORD", # e.g., C!sco12345
        
        # Cisco IOS XE RESTCONF Details (for a router with RESTCONF enabled)
        "iosxe_restconf_url": "https://YOUR_IOSXE_IP/restconf/data", # e.g., 192.168.1.1/restconf/data
        "iosxe_username": "YOUR_IOSXE_USERNAME", # e.g., cisco
        "iosxe_password": "YOUR_IOSXE_PASSWORD", # e.g., cisco
        
        "verify_ssl": False # Set to True in production if you have proper CA certificates
    }
    ```
3.  Save `api_lab.py`.

---

## Lab 1: Querying Data with `requests`

**Objective:** Learn how to use the `requests` library to interact with REST APIs.

### Task 1.1: Install `requests`

1.  Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).
2.  Install the `requests` library:
    ```bash
    pip install requests
    ```
    *Expected Observation:* `requests` and its dependencies will be installed. You should see a "Successfully installed..." message.

### Task 1.2: Make a Simple GET Request to a Public Dummy API

We will use JSONPlaceholder (`https://jsonplaceholder.typicode.com`), a free public API that provides fake data for testing.

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the `API_INFO` dictionary:
    ```python
    # ... (previous code including imports and API_INFO) ...

    print("--- Lab 1.2: Make a Simple GET Request to Public API ---")

    # The URL for a single post from JSONPlaceholder API
    api_url_single_post = "https://jsonplaceholder.typicode.com/posts/1"

    try:
        print(f"Attempting to fetch data from: {api_url_single_post}")
        # Make the GET request
        response = requests.get(api_url_single_post)
        
        # Check if the request was successful (status code 200-299).
        # This will raise an HTTPError for 4xx or 5xx responses.
        response.raise_for_status() 

        # Parse the JSON response into a Python dictionary
        data = response.json()

        print("\n--- API Response (Python Dictionary) ---")
        print(json.dumps(data, indent=2)) # Pretty print the dictionary as JSON

        # Access specific data points
        print(f"\nUser ID: {data['userId']}")
        print(f"Post Title: {data['title']}")

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from API.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("\nLab 1.2 complete.")
    ```
3.  Save `api_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory:
    ```bash
    python api_lab.py
    ```
    *Expected Output (content from live API, will vary slightly):*
    ```
    --- Lab 1.2: Make a Simple GET Request to Public API ---
    Attempting to fetch data from: https://jsonplaceholder.typicode.com/posts/1

    --- API Response (Python Dictionary) ---
    {
      "userId": 1,
      "id": 1,
      "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
      "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
    }

    User ID: 1
    Post Title: sunt aut facere repellat provident occaecati excepturi optio reprehenderit

    Lab 1.2 complete.
    ```

---

## Lab 2: Querying Cisco DNA Center / Catalyst Center

**Objective:** Learn to interact with a Cisco controller API using basic authentication and token handling.

### Task 2.1: Get Authentication Token from DNAC/Catalyst Center

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the previous lab:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 2.1: Get Authentication Token from DNAC/Catalyst Center ---")

    dnac_token = None
    try:
        if not API_INFO["dnac_url"].startswith("https://YOUR_DNAC_IP"):
            auth_url = f"{API_INFO['dnac_url']}/dna/system/api/v1/auth/token"
            headers = {"Content-Type": "application/json"}
            
            print(f"Attempting to get token from: {auth_url}")
            response = requests.post(
                auth_url,
                auth=(API_INFO['dnac_username'], API_INFO['dnac_password']),
                headers=headers,
                verify=API_INFO['verify_ssl'] # Use verify_ssl from API_INFO
            )
            response.raise_for_status()
            dnac_token = response.json()["Token"]
            print("Successfully obtained DNAC token.")
            print(f"Token (first 10 chars): {dnac_token[:10]}...")
        else:
            print("Skipping DNAC token acquisition: Please update API_INFO['dnac_url'] with your actual lab URL.")
    except requests.exceptions.RequestException as e:
        print(f"Error getting DNAC token: {e}")
        print("Please ensure DNAC/Catalyst Center is reachable and credentials are correct.")
    except Exception as e:
        print(f"An unexpected error occurred during DNAC token acquisition: {e}")

    print("\nLab 2.1 complete.")
    ```
3.  Save `api_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory.
    *Expected Output (if dummy URL/credentials are not replaced):*
    ```
    --- Lab 2.1: Get Authentication Token from DNAC/Catalyst Center ---
    Skipping DNAC token acquisition: Please update API_INFO['dnac_url'] with your actual lab URL.

    Lab 2.1 complete.
    ```
    *Expected Output (if you replace with real, reachable DNAC/Catalyst Center info):*
    ```
    --- Lab 2.1: Get Authentication Token from DNAC/Catalyst Center ---
    Attempting to get token from: https://YOUR_DNAC_IP_OR_HOSTNAME/dna/system/api/v1/auth/token
    Successfully obtained DNAC token.
    Token (first 10 chars): eyJhbGci...

    Lab 2.1 complete.
    ```

### Task 2.2: Query Network Device List from DNAC/Catalyst Center

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 2.2: Query Network Device List from DNAC/Catalyst Center ---")

    if dnac_token: # Only proceed if token was successfully obtained
        try:
            devices_url = f"{API_INFO['dnac_url']}/dna/intent/api/v1/network-device"
            headers = {
                "Content-Type": "application/json",
                "X-Auth-Token": dnac_token # Use the obtained token
            }
            
            print(f"Attempting to fetch devices from: {devices_url}")
            response = requests.get(
                devices_url,
                headers=headers,
                verify=API_INFO['verify_ssl']
            )
            response.raise_for_status()
            devices = response.json()["response"] # DNAC often wraps results in a "response" key

            print(f"\nFound {len(devices)} devices in DNAC/Catalyst Center:")
            print("\n--- First 3 Devices ---")
            for device in devices[:3]: # Print first 3 for brevity
                print(f"  Name: {device.get('hostname', 'N/A')}")
                print(f"  IP: {device.get('managementIpAddress', 'N/A')}")
                print(f"  Type: {device.get('type', 'N/A')}")
                print(f"  Serial: {device.get('serialNumber', 'N/A')}")
                print("-" * 20)
        except requests.exceptions.RequestException as e:
            print(f"Error querying DNAC devices: {e}")
            print("Please ensure DNAC/Catalyst Center is reachable and token is valid.")
        except Exception as e:
            print(f"An unexpected error occurred during DNAC device query: {e}")
    else:
        print("Skipping DNAC device query: No valid token available.")

    print("\nLab 2.2 complete.")
    ```
3.  Save `api_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory.
    *Expected Output (if dummy URL/credentials are not replaced or token acquisition failed):*
    ```
    --- Lab 2.2: Query Network Device List from DNAC/Catalyst Center ---
    Skipping DNAC device query: No valid token available.

    Lab 2.2 complete.
    ```
    *Expected Output (if you replace with real, reachable DNAC/Catalyst Center info):*
    ```
    --- Lab 2.2: Query Network Device List from DNAC/Catalyst Center ---
    Attempting to fetch devices from: https://YOUR_DNAC_IP_OR_HOSTNAME/dna/intent/api/v1/network-device

    Found X devices in DNAC/Catalyst Center:

    --- First 3 Devices ---
    Name: R1
    IP: 10.10.20.40
    Type: Cisco Catalyst 8000V Virtual Router
    Serial: 9Z244G86C0A
    --------------------
    Name: SW1
    IP: 10.10.20.41
    Type: Cisco Catalyst 9300 Series Switches
    Serial: FHH24210123
    --------------------
    Name: AP1
    IP: 10.10.20.42
    Type: Cisco Aironet 1850 Series Access Point
    Serial: FGL23210123
    --------------------

    Lab 2.2 complete.
    ```

---

## Lab 3: Querying Cisco IOS XE RESTCONF

**Objective:** Learn to query operational data directly from a Cisco IOS XE router using RESTCONF.

### Task 3.1: Get CPU Utilization via RESTCONF

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the previous lab:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 3.1: Get CPU Utilization via RESTCONF ---")

    try:
        if not API_INFO["iosxe_restconf_url"].startswith("https://YOUR_IOSXE_IP"):
            print("Skipping IOS XE RESTCONF CPU query: Please update API_INFO['iosxe_restconf_url'] with your actual lab URL.")
        else:
            # Path to CPU utilization data in the Cisco-IOS-XE-process-cpu-oper YANG model
            cpu_path = "Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"
            full_url = f"{API_INFO['iosxe_restconf_url']}/{cpu_path}"
            
            headers = {
                "Content-Type": "application/yang-data+json", # Request JSON YANG data
                "Accept": "application/yang-data+json"
            }
            
            print(f"Attempting to fetch CPU data from: {full_url}")
            response = requests.get(
                full_url,
                headers=headers,
                auth=(API_INFO['iosxe_username'], API_INFO['iosxe_password']),
                verify=API_INFO['verify_ssl']
            )
            response.raise_for_status()
            cpu_data = response.json()

            # Extract CPU total utilization (5-second average)
            cpu_total = cpu_data['Cisco-IOS-XE-process-cpu-oper:cpu-usage']['cpu-utilization']['cpu-total-utilization']
            print(f"\nIOS XE CPU Utilization (5-sec average): {cpu_total}%")
            print(json.dumps(cpu_data, indent=2)) # Print full CPU data for inspection

    except requests.exceptions.RequestException as e:
        print(f"Error getting IOS XE RESTCONF CPU data: {e}")
        print("Please ensure IOS XE device is reachable, RESTCONF is enabled, and credentials are correct.")
    except Exception as e:
        print(f"An unexpected error occurred during IOS XE RESTCONF CPU query: {e}")

    print("\nLab 3.1 complete.")
    ```
3.  Save `api_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory.
    *Expected Output (if dummy URL/credentials are not replaced):*
    ```
    --- Lab 3.1: Get CPU Utilization via RESTCONF ---
    Skipping IOS XE RESTCONF CPU query: Please update API_INFO['iosxe_restconf_url'] with your actual lab URL.

    Lab 3.1 complete.
    ```
    *Expected Output (if you replace with real, reachable IOS XE info):*
    ```
    --- Lab 3.1: Get CPU Utilization via RESTCONF ---
    Attempting to fetch CPU data from: https://YOUR_IOSXE_IP/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization

    IOS XE CPU Utilization (5-sec average): 5%
    {
      "Cisco-IOS-XE-process-cpu-oper:cpu-usage": {
        "cpu-utilization": [
          {
            "five-seconds": 5,
            "one-minute": 6,
            "five-minutes": 7,
            "cpu-total-utilization": 5
          }
        ]
      }
    }

    Lab 3.1 complete.
    ```

### Task 3.2: Get Interface Operational Status via RESTCONF

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 3.2: Get Interface Operational Status via RESTCONF ---")

    try:
        if not API_INFO["iosxe_restconf_url"].startswith("https://YOUR_IOSXE_IP"):
            print("Skipping IOS XE RESTCONF Interface query: Please update API_INFO['iosxe_restconf_url'] with your actual lab URL.")
        else:
            # Path to operational status of a specific interface (e.g., GigabitEthernet1)
            # This uses the ietf-interfaces YANG model
            interface_name = "GigabitEthernet1" # Replace with an actual interface name on your device
            interface_path = f"ietf-interfaces:interfaces/interface={interface_name}/oper-status"
            full_url = f"{API_INFO['iosxe_restconf_url']}/{interface_path}"
            
            headers = {
                "Content-Type": "application/yang-data+json",
                "Accept": "application/yang-data+json"
            }
            
            print(f"Attempting to fetch interface status from: {full_url}")
            response = requests.get(
                full_url,
                headers=headers,
                auth=(API_INFO['iosxe_username'], API_INFO['iosxe_password']),
                verify=API_INFO['verify_ssl']
            )
            response.raise_for_status()
            interface_data = response.json()

            status = interface_data['ietf-interfaces:oper-status']
            print(f"\nInterface {interface_name} Operational Status: {status}")
            print(json.dumps(interface_data, indent=2)) # Print full interface data for inspection

    except requests.exceptions.RequestException as e:
        print(f"Error getting IOS XE RESTCONF Interface status: {e}")
        print("Please ensure IOS XE device is reachable, RESTCONF is enabled, and credentials are correct.")
    except Exception as e:
        print(f"An unexpected error occurred during IOS XE RESTCONF Interface query: {e}")

    print("\nLab 3.2 complete.")
    ```
3.  Save `api_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory.
    *Expected Output (if dummy URL/credentials are not replaced):*
    ```
    --- Lab 3.2: Get Interface Operational Status via RESTCONF ---
    Skipping IOS XE RESTCONF Interface query: Please update API_INFO['iosxe_restconf_url'] with your actual lab URL.

    Lab 3.2 complete.
    ```
    *Expected Output (if you replace with real, reachable IOS XE info):*
    ```
    --- Lab 3.2: Get Interface Operational Status via RESTCONF ---
    Attempting to fetch interface status from: https://YOUR_IOSXE_IP/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1/oper-status

    Interface GigabitEthernet1 Operational Status: up
    {
      "ietf-interfaces:oper-status": "up"
    }

    Lab 3.2 complete.
    ```

---

## Lab 4: Building a Simple Monitoring Tool

**Objective:** Build a simple monitoring tool that periodically polls simulated data and checks thresholds. This task will use simulated data for simplicity, but the logic is directly applicable to real API calls.

### Task 4.1: Build the Monitoring Logic

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the previous lab:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 4.1: Build the Monitoring Logic ---")

    # This function simulates getting performance data from a device API
    # The CPU and interface status will change randomly over time
    _simulated_cpu_counter = 0 # Global counter for CPU simulation

    def get_simulated_device_performance(device_name):
        """
        Simulates an API call to get device performance data.
        Returns a dictionary with CPU and interface stats that change over time.
        """
        global _simulated_cpu_counter # Access the global counter

        if device_name == "Router1":
            _simulated_cpu_counter = (_simulated_cpu_counter + 5) # Increment counter
            cpu = 60 + (_simulated_cpu_counter % 30) # CPU between 60 and 89
            g0_1_status = "up" if random.random() > 0.1 else "down" # 10% chance of being down
            return {
                "device_name": "Router1",
                "cpu_utilization_percent": cpu,
                "interfaces": [
                    {"name": "GigabitEthernet0/0", "status": "up"},
                    {"name": "GigabitEthernet0/1", "status": g0_1_status}
                ]
            }
        elif device_name == "SwitchA":
            cpu = 20 + (random.randint(0, 20)) # CPU between 20 and 40
            return {
                "device_name": "SwitchA",
                "cpu_utilization_percent": cpu,
                "interfaces": [
                    {"name": "GigabitEthernet0/1", "status": "up"}
                ]
            }
        else:
            return None # Device not found

    def monitor_device(device_name, cpu_threshold=80, interface_down_alert=True):
        """
        Monitors a device's performance data, checks thresholds, and prints alerts.
        """
        print(f"\nMonitoring {device_name}...")
        performance_data = get_simulated_device_performance(device_name)
        
        if performance_data:
            cpu = performance_data["cpu_utilization_percent"]
            interfaces = performance_data["interfaces"]
            
            print(f"  Current CPU: {cpu}%")
            
            # Check CPU threshold
            if cpu >= cpu_threshold: 
                print(f"  !!! ALERT: {device_name} CPU utilization ({cpu}%) is at or above threshold ({cpu_threshold}%).")
            
            # Check interface status
            for iface in interfaces:
                if iface['status'] == "down" and interface_down_alert:
                    print(f"  !!! ALERT: {device_name} Interface {iface['name']} is DOWN!")
        else:
            print(f"  Could not retrieve data for {device_name}.")

    # We will run this in the next task
    print("\nLab 4.1 complete. (Monitoring will run in next task)")
    ```

### Task 4.2: Run the Monitoring Tool

Finally, we'll put it all together in a loop to simulate continuous monitoring.

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 4.2: Run the Monitoring Tool ---")

    # Main loop for continuous monitoring
    print("Starting continuous network monitoring (Ctrl+C to stop)...")
    try:
        for i in range(1, 11): # Run 10 monitoring cycles
            print(f"\n--- Monitoring Cycle {i} ---")
            monitor_device("Router1", cpu_threshold=75) # Set a CPU threshold for Router1
            monitor_device("SwitchA", cpu_threshold=35) # Set a CPU threshold for SwitchA
            time.sleep(3) # Wait 3 seconds before the next monitoring cycle
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"An error occurred during monitoring: {e}")

    print("\nLab 4.2 complete.")
    ```
3.  Save `api_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory:
    ```bash
    python api_lab.py
    ```
    *Expected Output (output will change over time, and alerts will appear):*
    ```
    --- Lab 4.2: Run the Monitoring Tool ---
    Starting continuous network monitoring (Ctrl+C to stop)...

    --- Monitoring Cycle 1 ---

    Monitoring Router1...
      Current CPU: 60%
    Monitoring SwitchA...
      Current CPU: 25%

    --- Monitoring Cycle 2 ---

    Monitoring Router1...
      Current CPU: 65%
      !!! ALERT: Router1 Interface GigabitEthernet0/1 is DOWN!
    Monitoring SwitchA...
      Current CPU: 30%

    --- Monitoring Cycle 3 ---

    Monitoring Router1...
      Current CPU: 70%
    Monitoring SwitchA...
      Current CPU: 35%
      !!! ALERT: SwitchA CPU utilization (35%) is at or above threshold (35%).

    --- Monitoring Cycle 4 ---

    Monitoring Router1...
      Current CPU: 75%
      !!! ALERT: Router1 CPU utilization (75%) is at or above threshold (75%).
    Monitoring SwitchA...
      Current CPU: 20%

    ... (continues for 10 cycles, or until Ctrl+C) ...

    Monitoring stopped by user.
    Lab 4.2 complete.
    ```
    *Observation:* You will see CPU values changing and alerts appearing when thresholds are met or interfaces go down (simulated). This demonstrates a basic monitoring loop.

---

## Conclusion

You've now completed Module 5 and gained practical experience with using APIs to retrieve data! You can now:

*   Understand the role of APIs in modern network automation.
*   Make basic GET requests to REST APIs using the `requests` library.
*   Query information from Cisco DNA Center/Catalyst Center (with your lab info).
*   Query operational data from Cisco IOS XE RESTCONF (with your lab info).
*   Build a simple monitoring tool that polls data and checks thresholds.

APIs are a powerful and increasingly common way to interact with network devices and controllers. These foundational skills will serve you well as you explore more advanced automation topics.

**Keep Automating!**

---