---

## Document 2: Python Basics for Network Automation - Module 5 Lab Guide (Complete Markdown Block)

```markdown
# Python Basics for Network Automation: Module 5 Lab Guide

## Using APIs to Retrieve Data on Cisco Network Devices - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 5 of the Python Basics for Network Automation Lab Guide! In this module, you will gain hands-on experience with using APIs to retrieve data. We will focus on **RESTCONF on Cisco IOS XE routers** and the `requests` Python library. We will then use **Python Flask** to build a simple web-based monitoring tool.

**It is crucial that you replace the dummy values for your IOS XE router with its actual IP address, username, and password to make the code functional.**

**Lab Objectives:**
*   Install the `requests` and `Flask` libraries.
*   Query Cisco IOS XE router's performance data (CPU, memory, interfaces) using RESTCONF.
*   Build a simple monitoring tool using Python Flask to display this data.

**Prerequisites:**
*   Completion of Module 1, Module 2, Module 3, and Module 4 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   An active internet connection.
*   **Access to a Cisco IOS XE router with RESTCONF enabled (e.g., Cisco DevNet Sandboxes).** You will need its IP, username, and password.

Let's start exploring APIs and Flask!

---

## Lab Setup: Single File Approach

For this module, we will keep all the code in a single Python file.

1.  **Navigate** to your main `network_automation_labs` directory.
2.  **Create a new Python file** for this module's labs:
    ```bash
    cd network_automation_labs
    touch iosxe_monitor_flask.py
    ```

### Task 0.1: Define IOS XE API Information

This section will hold the dummy IOS XE RESTCONF connection details.

1.  Open `iosxe_monitor_flask.py` in your code editor.
2.  Add the following Python code. **REPLACE THE DUMMY VALUES WITH YOUR ACTUAL LAB IOS XE ROUTER DETAILS!**
    ```python
    # iosxe_monitor_flask.py

    # --- Import necessary libraries ---
    import requests
    import json # For pretty-printing JSON
    import time # For delays
    from flask import Flask, render_template_string # For the web app

    # --- IOS XE RESTCONF API Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
    # This router should be reachable and have RESTCONF enabled.
    IOSXE_API_INFO = {
        "host": "YOUR_IOSXE_IP", # e.g., 10.10.20.40 (from Cisco DevNet Sandbox)
        "username": "YOUR_IOSXE_USERNAME", # e.g., developer
        "password": "YOUR_IOSXE_PASSWORD", # e.g., C!sco12345
        "port": 443, # Default HTTPS port for RESTCONF
        "verify_ssl": False # Set to True in production if you have proper CA certificates
    }

    # Base URL for RESTCONF data (e.g., https://10.10.20.40:443/restconf/data)
    RESTCONF_BASE_URL = f"https://{IOSXE_API_INFO['host']}:{IOSXE_API_INFO['port']}/restconf/data"

    # --- Flask App Initialization ---
    app = Flask(__name__)

    # Global variable to store the latest metrics fetched from the router
    # This will be updated periodically and displayed by Flask.
    latest_metrics = {
        "cpu_util": "N/A",
        "memory_used": "N/A",
        "memory_total": "N/A",
        "interfaces": []
    }
    ```
3.  Save `iosxe_monitor_flask.py`.

---

## Lab 1: Query Cisco IOS XE Router Performance (RESTCONF)

**Objective:** Learn to query CPU, memory, and interface utilization from a Cisco IOS XE router using RESTCONF.

### Task 1.1: Install `requests` and `Flask`

1.  Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).
2.  Install the `requests` and `Flask` libraries:
    ```bash
    pip install requests Flask
    ```
    *Expected Observation:* `requests`, `Flask`, and their dependencies will be installed. You should see "Successfully installed..." messages.

### Task 1.2: Function to Get RESTCONF Data

This function will be a reusable helper to make GET requests to the IOS XE RESTCONF API.

1.  Open `iosxe_monitor_flask.py` in your code editor.
2.  Add the following function below the `latest_metrics` dictionary:
    ```python
    # ... (previous code including imports and Flask app init) ...

    def get_restconf_data(path):
        """
        Makes a GET request to the IOS XE RESTCONF API for a given YANG path.
        Returns the JSON response as a Python dictionary, or None on error.
        """
        full_url = f"{RESTCONF_BASE_URL}/{path}"
        headers = {
            "Content-Type": "application/yang-data+json", # Request JSON YANG data
            "Accept": "application/yang-data+json"
        }
        
        try:
            print(f"Fetching: {full_url}")
            response = requests.get(
                full_url,
                headers=headers,
                auth=(IOSXE_API_INFO['username'], IOSXE_API_INFO['password']),
                verify=IOSXE_API_INFO['verify_ssl']
            )
            response.raise_for_status() # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {path}: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {path} response.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred for {path}: {e}")
            return None

    # ... (rest of the code will go here) ...
    ```

### Task 1.3: Functions to Query Specific Performance Metrics

Now, let's create functions to get CPU, Memory, and Interface data using `get_restconf_data`.

1.  Open `iosxe_monitor_flask.py` in your code editor.
2.  Add the following functions below `get_restconf_data`:
    ```python
    # ... (previous code) ...

    def get_cpu_utilization():
        """Queries and returns CPU utilization from IOS XE via RESTCONF."""
        path = "Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"
        data = get_restconf_data(path)
        if data:
            # Accessing nested data: cpu-usage -> cpu-utilization (which is a list) -> first item -> cpu-total-utilization
            # Using .get() for safer access in case keys are missing
            cpu_total = data.get('Cisco-IOS-XE-process-cpu-oper:cpu-usage', {}).get('cpu-utilization', [{}])[0].get('cpu-total-utilization')
            return cpu_total if cpu_total is not None else "N/A"
        return "N/A"

    def get_memory_utilization():
        """Queries and returns memory utilization from IOS XE via RESTCONF."""
        # Note: This path gets overall memory stats. Specific pools might be under different paths.
        path = "Cisco-IOS-XE-memory-oper:memory-statistics"
        data = get_restconf_data(path)
        if data:
            # Accessing nested data: memory-statistics -> memory-statistic (which is a list) -> first item
            # We'll assume the first item in the list is the relevant one for total/used.
            # Convert to int, as values might be strings or None
            mem_stats = data.get('Cisco-IOS-XE-memory-oper:memory-statistics', {}).get('memory-statistic', [{}])
            if mem_stats and isinstance(mem_stats, list) and len(mem_stats) > 0:
                used = mem_stats[0].get('used-memory')
                total = mem_stats[0].get('total-memory')
                return int(used) if used is not None else "N/A", int(total) if total is not None else "N/A"
        return "N/A", "N/A"

    def get_interface_status():
        """Queries and returns interface operational status from IOS XE via RESTCONF."""
        # This path gets all interfaces. You might filter for specific ones.
        path = "ietf-interfaces:interfaces/interface" 
        data = get_restconf_data(path)
        interfaces = []
        if data:
            # Accessing nested data: interfaces -> interface (which is a list)
            iface_list = data.get('ietf-interfaces:interfaces', {}).get('interface', [])
            for iface in iface_list:
                name = iface.get('name')
                oper_status = iface.get('oper-status')
                # Optionally, get input/output rates from ietf-interfaces:interfaces-state
                # This would require another GET request to ietf-interfaces:interfaces-state/interface=<name>/statistics
                # For simplicity, we'll just get name and oper-status here.
                if name and oper_status:
                    interfaces.append({"name": name, "status": oper_status})
        return interfaces

    # ... (rest of the code will go here) ...
    ```

### Task 1.4: Test the Metric Functions (Standalone)

Let's test these functions before building the Flask app.

1.  Open `iosxe_monitor_flask.py` in your code editor.
2.  Add the following code at the very end of the file (outside any Flask app routes):
    ```python
    # ... (previous code) ...

    # --- Standalone Test Section ---
    if __name__ == '__main__':
        print("--- Testing RESTCONF Metric Functions ---")
        print("Note: This will attempt to connect to the IOS XE router defined in IOSXE_API_INFO.")

        # Test CPU
        cpu = get_cpu_utilization()
        print(f"\nRouter CPU Utilization: {cpu}%")

        # Test Memory
        mem_used, mem_total = get_memory_utilization()
        print(f"Router Memory: {mem_used} used / {mem_total} total bytes")

        # Test Interfaces
        interfaces = get_interface_status()
        print("\nRouter Interfaces:")
        if interfaces:
            for iface in interfaces:
                print(f"  {iface['name']}: {iface['status']}")
        else:
            print("  No interfaces found or error retrieving.")

        print("\n--- RESTCONF Metric Functions Test Complete ---")
        print("Now, let's start the Flask app...")
        
        # --- Run the Flask App (will be covered in Lab 2) ---
        # app.run(debug=True, host='0.0.0.0', port=5000)
    ```
3.  Save `iosxe_monitor_flask.py`.
4.  **Run the script** from your `network_automation_labs` directory:
    ```bash
    python iosxe_monitor_flask.py
    ```
    *Expected Output (if dummy IOS XE info is not replaced):*
    ```
    --- Testing RESTCONF Metric Functions ---
    Note: This will attempt to connect to the IOS XE router defined in IOSXE_API_INFO.
    Fetching: https://YOUR_IOSXE_IP:443/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization
    Error fetching Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization: HTTPSConnectionPool(host='YOUR_IOSXE_IP', port=443): Max retries exceeded with url: /restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x...>: Failed to establish a new connection: [Errno 111] Connection refused'))
    Router CPU Utilization: N/A%
    Fetching: https://YOUR_IOSXE_IP:443/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics
    Error fetching Cisco-IOS-XE-memory-oper:memory-statistics: HTTPSConnectionPool(host='YOUR_IOSXE_IP', port=443): Max retries exceeded with url: /restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x...>: Failed to establish a new connection: [Errno 111] Connection refused'))
    Router Memory: N/A used / N/A total bytes
    Fetching: https://YOUR_IOSXE_IP:443/restconf/data/ietf-interfaces:interfaces/interface
    Error fetching ietf-interfaces:interfaces/interface: HTTPSConnectionPool(host='YOUR_IOSXE_IP', port=443): Max retries exceeded with url: /restconf/data/ietf-interfaces:interfaces/interface (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x...>: Failed to establish a new connection: [Errno 111] Connection refused'))

    Router Interfaces:
      No interfaces found or error retrieving.

    --- RESTCONF Metric Functions Test Complete ---
    Now, let's start the Flask app...
    ```
    *Expected Output (if you replace with real, reachable IOS XE info):*
    ```
    --- Testing RESTCONF Metric Functions ---
    Note: This will attempt to connect to the IOS XE router defined in IOSXE_API_INFO.
    Fetching: https://YOUR_IOSXE_IP:443/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization

    Router CPU Utilization: 5%
    Fetching: https://YOUR_IOSXE_IP:443/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics

    Router Memory: 123456789 used / 987654321 total bytes
    Fetching: https://YOUR_IOSXE_IP:443/restconf/data/ietf-interfaces:interfaces/interface

    Router Interfaces:
      GigabitEthernet1: up
      Loopback0: up
      Vlan1: up

    --- RESTCONF Metric Functions Test Complete ---
    Now, let's start the Flask app...
    ```

---

## Lab 2: Build a Simple Monitoring Tool using Python Flask

**Objective:** Create a Flask web application to display the router's performance metrics.

### Task 2.1: Define Flask Routes and HTML Template

We'll define a route for the main dashboard page and a simple HTML template string.

1.  Open `iosxe_monitor_flask.py` in your code editor.
2.  Add the following Flask route and HTML template below the `get_interface_status` function:
    ```python
    # ... (previous code) ...

    # --- HTML Template for Flask Dashboard ---
    # This is a simple HTML string embedded directly in our Python file.
    # In larger apps, this would be in a separate .html file.
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IOS XE Router Monitor</title>
        <meta http-equiv="refresh" content="5"> <!-- Auto-refresh page every 5 seconds -->
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
            .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 800px; margin: auto; }
            h1 { color: #0056b3; }
            .metric { margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            .metric strong { color: #007bff; }
            .alert { color: red; font-weight: bold; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .status-up { color: green; font-weight: bold; }
            .status-down { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Cisco IOS XE Router Monitor</h1>
            <p>Last updated: {{ current_time }}</p>
            
            <div class="metric">
                <strong>CPU Utilization (5-sec):</strong> <span id="cpu_util">{{ cpu_util }}%</span>
                {% if cpu_util != 'N/A' and cpu_util > 75 %} <span class="alert">(HIGH)</span> {% endif %}
            </div>
            
            <div class="metric">
                <strong>Memory Used:</strong> <span id="memory_used">{{ memory_used }}</span> bytes
                <strong>Total Memory:</strong> <span id="memory_total">{{ memory_total }}</span> bytes
            </div>

            <h2>Interfaces</h2>
            <table id="interfaces_table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for iface in interfaces %}
                    <tr>
                        <td>{{ iface.name }}</td>
                        <td class="status-{{ iface.status }}">{{ iface.status }}</td>
                    </tr>
                    {% endfor %}
                    {% if not interfaces %}
                    <tr><td colspan="2">No interface data available or error fetching.</td></tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    @app.route('/')
    def index():
        """
        Main dashboard route. Fetches metrics and renders the HTML template.
        """
        global latest_metrics # Access the global variable

        # Fetch current metrics from the router
        cpu = get_cpu_utilization()
        mem_used, mem_total = get_memory_utilization()
        interfaces = get_interface_status()

        # Update the global variable
        latest_metrics = {
            "cpu_util": cpu,
            "memory_used": mem_used,
            "memory_total": mem_total,
            "interfaces": interfaces
        }
        
        # Render the HTML template with the fetched data
        return render_template_string(
            HTML_TEMPLATE,
            cpu_util=latest_metrics["cpu_util"],
            memory_used=latest_metrics["memory_used"],
            memory_total=latest_metrics["memory_total"],
            interfaces=latest_metrics["interfaces"],
            current_time=time.strftime("%Y-%m-%d %H:%M:%S")
        )

    # ... (rest of the code, including the __main__ block, will go here) ...
    ```

### Task 2.2: Run the Flask Application

Now, let's run the Flask app and view the monitoring dashboard in your browser.

1.  Open `iosxe_monitor_flask.py` in your code editor.
2.  **Uncomment** the `app.run()` line in the `if __name__ == '__main__':` block at the very end of the file:
    ```python
    # ... (previous code) ...

    # --- Standalone Test Section ---
    if __name__ == '__main__':
        print("--- Testing RESTCONF Metric Functions ---")
        print("Note: This will attempt to connect to the IOS XE router defined in IOSXE_API_INFO.")

        # Test CPU
        cpu = get_cpu_utilization()
        print(f"\nRouter CPU Utilization: {cpu}%")

        # Test Memory
        mem_used, mem_total = get_memory_utilization()
        print(f"Router Memory: {mem_used} used / {mem_total} total bytes")

        # Test Interfaces
        interfaces = get_interface_status()
        print("\nRouter Interfaces:")
        if interfaces:
            for iface in interfaces:
                print(f"  {iface['name']}: {iface['status']}")
        else:
            print("  No interfaces found or error retrieving.")

        print("\n--- RESTCONF Metric Functions Test Complete ---")
        print("Now, let's start the Flask app...")
        
        # --- Run the Flask App ---
        # debug=True allows auto-reloading and provides debug info
        # host='0.0.0.0' makes the app accessible from other devices on your network
        # port=5000 is the default Flask port
        app.run(debug=True, host='0.0.0.0', port=5000)
    ```
3.  Save `iosxe_monitor_flask.py`.
4.  **Run the script** from your `network_automation_labs` directory:
    ```bash
    python iosxe_monitor_flask.py
    ```
    *Expected Output (console):*
    ```
    --- Testing RESTCONF Metric Functions ---
    Note: This will attempt to connect to the IOS XE router defined in IOSXE_API_INFO.
    Fetching: https://YOUR_IOSXE_IP:443/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization
    # ... (output from metric fetching, similar to Task 1.4) ...
    --- RESTCONF Metric Functions Test Complete ---
    Now, let's start the Flask app...
     * Serving Flask app 'iosxe_monitor_flask'
     * Debug mode: on
     * Running on all addresses (0.0.0.0)
     * Port: 5000
    Press CTRL+C to quit
     * Restarting with stat
    Press CTRL+C to quit
    ```
5.  **Open your web browser** and navigate to `http://127.0.0.1:5000` (or `http://localhost:5000`). If you are running this on a remote server, use that server's IP address.

    *Expected Web Browser Output (content will reflect your router's actual data and update every 5 seconds):*
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IOS XE Router Monitor</title>
        <meta http-equiv="refresh" content="5"> <!-- Auto-refresh page every 5 seconds -->
        <style>
            /* ... (CSS styles as defined in HTML_TEMPLATE) ... */
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Cisco IOS XE Router Monitor</h1>
            <p>Last updated: YYYY-MM-DD HH:MM:SS (current time)</p>
            
            <div class="metric">
                <strong>CPU Utilization (5-sec):</strong> <span id="cpu_util">5%</span>
                 <!-- (HIGH) might appear if CPU > 75% -->
            </div>
            
            <div class="metric">
                <strong>Memory Used:</strong> <span id="memory_used">123456789</span> bytes
                <strong>Total Memory:</strong> <span id="memory_total">987654321</span> bytes
            </div>

            <h2>Interfaces</h2>
            <table id="interfaces_table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>GigabitEthernet1</td>
                        <td class="status-up">up</td>
                    </tr>
                    <tr>
                        <td>Loopback0</td>
                        <td class="status-up">up</td>
                    </tr>
                    <tr>
                        <td>Vlan1</td>
                        <td class="status-up">up</td>
                    </tr>
                    <!-- ... (other interfaces from your router) ... -->
                </tbody>
            </table>
        </div>
    </body>
    </html>
    ```
    *Observation:* The web page will display the current metrics from your router and automatically refresh every 5 seconds, fetching new data. If your router's CPU goes above 75%, you will see a "(HIGH)" alert next to the CPU utilization.

---

## Conclusion

You've now completed Module 5 and gained practical experience with using APIs to retrieve data! You can now:

*   Understand the role of APIs in modern network automation.
*   Query operational data from Cisco IOS XE RESTCONF (with your lab info).
*   Build a simple monitoring tool using Python Flask to display real-time router metrics.

APIs are a powerful and increasingly common way to interact with network devices and controllers. These foundational skills will serve you well as you explore more advanced automation topics.

**Keep Automating!**

---