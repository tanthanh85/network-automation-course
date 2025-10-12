# NASP: Module 10 Lab Guide

## Creating a Centralized Configuration Management Console for Cisco Routers - Hands-on Exercises

---

## Introduction

Welcome to Module 10 of the Python Basics for Network Automation Lab Guide! In this module, you will build a simple, centralized web-based management console for Cisco IOS XE routers using **Python Flask**.

This console will allow you to:
*   Manage a simple inventory of routers using SQLite.
*   Reboot a router.
*   Backup router configurations.
*   Retrieve "show logging" output.
*   Monitor interface bandwidth utilization.

**It is crucial that you replace the dummy values for your IOS XE router with its actual IP address, username, and password to make the code functional.**

**Lab Objectives:**
*   Set up the Flask project structure.
*   Implement inventory management (add/list/delete routers) to a SQLite database.
*   Develop backend functions for router operations (reboot, backup, logging, monitoring).
*   Create Flask routes and HTML templates for the web GUI.
*   Integrate long-running tasks as background threads.

**Prerequisites:**
*   Completion of Module 1 through Module 9 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   An active internet connection.
*   **Access to a Cisco IOS XE router with SSH and RESTCONF enabled (e.g., Cisco DevNet Sandboxes).** You will need its IP, username, and password.

Let's build a web console now!

---

## Lab Setup - Build Project Structure

For this module, we will create a dedicated project structure for our Flask application.

1.  **Navigate** to your main `network_automation_labs` directory.
2.  **Create a new directory** for this module's labs:
    ```bash
    mkdir module10_router_console
    cd module10_router_console
    ```
3.  **Inside `module10_router_console`, create the following directories:**
    ```bash
    mkdir database
    mkdir network_functions
    mkdir templates
    mkdir static
    mkdir backups
    mkdir logs
    ```
4.  **Inside `module10_router_console`, create the following empty Python files:**
    ```bash
    touch __init__.py
    touch app.py
    ```
5.  **Inside the `database` directory, create the following empty Python files:**
    ```bash
    touch database/__init__.py
    touch database/db_ops.py
    ```
6.  **Inside the `network_functions` directory, create the following empty Python files:**
    ```bash
    touch network_functions/__init__.py
    touch network_functions/netmiko_ops.py
    touch network_functions/restconf_ops.py
    ```
7.  **Inside the `templates` directory, create the following empty HTML files:**
    ```bash
    touch templates/index.html
    touch templates/inventory.html
    touch templates/router_actions.html
    touch templates/monitor_interface.html
    touch templates/logs_display.html
    ```
8.  **Inside the `static` directory, create an empty CSS file:**
    ```bash
    touch static/style.css
    ```

Your directory structure should now look like this:
```
network_automation_labs/
└── module10_router_console/
    ├── init.py
    ├── app.py
    ├── database/
    │   ├── init.py
    │   └── db_ops.py
    ├── network_functions/
    │   ├── init.py
    │   ├── netmiko_ops.py
    │   └── restconf_ops.py
    ├── templates/
    │   ├── index.html
    │   ├── inventory.html
    │   ├── router_actions.html
    │   ├── monitor_interface.html
    │   └── logs_display.html
    ├── static/
    │   └── style.css
    ├── backups/
    └── logs/
```
### Task 0.1: Install Required Libraries

1.  Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).
2.  Navigate into your `module10_router_console` directory:
    ```bash
    cd module10_router_console
    ```
3.  Install the necessary Python libraries:
    ```bash
    pip install Flask PyYAML netmiko requests
    ```
    *Expected Observation:* Libraries and their dependencies will be installed.

### Task 0.2: Populate `database/db_ops.py`

This file will handle all SQLite database operations for the inventory.

1.  Open `database/db_ops.py` in your code editor.
2.  Add the following Python code:
    ```python
    # database/db_ops.py
    import sqlite3
    import logging
    import os
    
    DB_FILE = "database/inventory.db"

    DEFAULT_ROUTER_INFO = {
        "device_type": "cisco_ios", # For Netmiko
        "host": "10.10.20.48", # e.g., 10.10.20.40
        "username": "developer",
        "password": "abcd",
        "secret": "abcd", # For Netmiko enable mode
        "port": 22, # Default SSH port for Netmiko
        "restconf_port": 443, # Default HTTPS port for RESTCONF
        "verify_ssl": False # Set to True in production if you have proper CA certificates
    }

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def _init_db():
        """Initializes the SQLite database and creates the routers table if it doesn't exist."""
        # Ensure the database directory exists
        db_dir = os.path.dirname(DB_FILE)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS routers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                host TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                secret TEXT,
                device_type TEXT NOT NULL,
                port INTEGER,
                restconf_port INTEGER,
                verify_ssl BOOLEAN
            )
        ''')
        conn.commit()
        conn.close()
        logging.info("SQLite database initialized.")

    def load_inventory():
        """Loads all routers from the SQLite database."""
        _init_db() # Ensure DB is initialized
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row # Allows accessing columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM routers")
        routers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return routers

    def get_router_by_name(router_name):
        """Retrieves a single router's info by name from the database."""
        _init_db()
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM routers WHERE name = ?", (router_name,))
        router = cursor.fetchone()
        conn.close()
        return dict(router) if router else None

    def add_router_to_inventory(router_data):
        """Adds a new router to the SQLite database."""
        _init_db()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO routers (name, host, username, password, secret, device_type, port, restconf_port, verify_ssl)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                router_data.get('name'),
                router_data.get('host'),
                router_data.get('username'),
                router_data.get('password'),
                router_data.get('secret'),
                router_data.get('device_type'),
                router_data.get('port'),
                router_data.get('restconf_port'),
                router_data.get('verify_ssl')
            ))
            conn.commit()
            logging.info(f"Router {router_data.get('name', router_data.get('host'))} added to DB.")
            return True
        except sqlite3.IntegrityError:
            logging.error(f"Router {router_data.get('name')} already exists in DB.")
            return False
        except Exception as e:
            logging.error(f"Error adding router to DB: {e}")
            return False
        finally:
            conn.close()

    def delete_router_from_inventory(router_name):
        """Deletes a router from the SQLite database by name."""
        _init_db()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM routers WHERE name = ?", (router_name,))
            conn.commit()
            if cursor.rowcount > 0:
                logging.info(f"Router {router_name} deleted from DB.")
                return True
            logging.warning(f"Router {router_name} not found in DB for deletion.")
            return False
        except Exception as e:
            logging.error(f"Error deleting router from DB: {e}")
            return False
        finally:
            conn.close()

    # Standalone test for functions (only runs when this file is executed directly)
    if __name__ == '__main__':
        
        print("--- Testing db_ops.py functions ---")
        
        test_router_name = "TestRouterDB"
        test_router_info = DEFAULT_ROUTER_INFO.copy()
        test_router_info['name'] = test_router_name
        
        # Test add/load/delete inventory
        print("\nTesting inventory management...")
        # Clean up previous test entry if exists
        delete_router_from_inventory(test_router_name) 
        
        if add_router_to_inventory(test_router_info):
            print(f"Router {test_router_name} added.")
        else:
            print(f"Failed to add {test_router_name}.")
        
        routers = load_inventory()
        print(f"Current inventory has {len(routers)} routers.")
        for r in routers:
            print(f"  - {r['name']} ({r['host']})")
        
        if delete_router_from_inventory(test_router_name):
            print(f"Router {test_router_name} deleted.")
        else:
            print(f"Failed to delete {test_router_name}.")
        
        print("\n--- Test Complete ---")
    ```
3.  Save `database/db_ops.py`.

### Task 0.3: Populate `network_functions/netmiko_ops.py`

This file will contain Netmiko-specific operations.

1.  Open `network_functions/netmiko_ops.py` in your code editor.
2.  Add the following Python code:
    ```python
    # network_functions/netmiko_ops.py
    import logging
    import os
    import datetime
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
    # Directory to store configuration backups
    BACKUP_DIR = "backups"

    # Directory to store logs
    LOGS_DIR = "logs"

    DB_FILE = "database/inventory.db"

    DEFAULT_ROUTER_INFO = {
        "device_type": "cisco_ios", # For Netmiko
        "host": "10.10.200.148", # e.g., 10.10.20.40
        "username": "developer",
        "password": "abcd",
        "secret": "abcd", # For Netmiko enable mode
        "port": 22, # Default SSH port for Netmiko
        "restconf_port": 443, # Default HTTPS port for RESTCONF
        "verify_ssl": False # Set to True in production if you have proper CA certificates
    }

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def _get_netmiko_connection(router_info):
        """Helper to establish Netmiko connection."""
        host = router_info.get('host')
        try:
            # Netmiko expects 'password' and 'secret' keys directly, not from router_info.get()
            # So, we create a connection dict with necessary fields
            conn_params = {
                "device_type": router_info.get('device_type'),
                "host": router_info.get('host'),
                "username": router_info.get('username'),
                "password": router_info.get('password'),
                "port": router_info.get('port'),
            }
            if router_info.get('secret'):
                conn_params['secret'] = router_info['secret']

            net_connect = ConnectHandler(**conn_params)
            logging.info(f"Netmiko: Successfully connected to {host}.")
            return net_connect
        except NetmikoTimeoutException as e:
            logging.error(f"Netmiko connection error to {host}: Connection timed out. {e}")
            return None
        except NetmikoAuthenticationException as e:
            logging.error(f"Netmiko connection error to {host}: Authentication failed. {e}")
            return None
        except Exception as e: # Catch any other unexpected errors during connection attempt
            logging.error(f"Netmiko unexpected error connecting to {host}: {e}")
            return None

    def reboot_router(router_info):
        """Reboots the specified router."""
        host = router_info.get('host')
        logging.info(f"Netmiko: Attempting to reboot router {host}...")
        net_connect = _get_netmiko_connection(router_info)
        if net_connect:
            try:
                # Send reload command, expect confirmation prompt
                output = net_connect.send_command("reload", expect_string=r"\[confirm\]", strip_prompt=False)
                # Send 'y' to confirm
                output += net_connect.send_command("y", strip_prompt=False)
                logging.info(f"Netmiko: Reboot command sent to {host}:\n{output}")
                return True
            except NetmikoTimeoutException as e:
                logging.error(f"Netmiko: Error sending reboot command to {host}: Connection timed out. {e}")
            except NetmikoAuthenticationException as e:
                logging.error(f"Netmiko: Error sending reboot command to {host}: Authentication failed. {e}")
            except Exception as e: # Catch any other unexpected errors during command execution
                logging.error(f"Netmiko: Unexpected error sending reboot command to {host}: {e}")
            finally:
                net_connect.disconnect()
        return False

    def backup_config(router_info):
        """Backs up the running configuration of the router."""
        host = router_info.get('host')
        logging.info(f"Netmiko: Attempting to backup config for router {host}...")
        net_connect = _get_netmiko_connection(router_info)
        if net_connect:
            try:
                output = net_connect.send_command("show running-config")
                
                os.makedirs(BACKUP_DIR, exist_ok=True) # Ensure backup directory exists
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = os.path.join(BACKUP_DIR, f"{host}_running_config_{timestamp}.txt")
                
                with open(backup_filename, 'w') as f:
                    f.write(output)
                logging.info(f"Netmiko: Backup successful for {host}. Saved to {backup_filename}")
                return True
            except NetmikoTimeoutException as e:
                logging.error(f"Netmiko: Error backing up config for {host}: Connection timed out. {e}")
            except NetmikoAuthenticationException as e:
                logging.error(f"Netmiko: Error backing up config for {host}: Authentication failed. {e}")
            except Exception as e: # Catch any other unexpected errors during command execution
                logging.error(f"Netmiko: Unexpected error backing up config for {host}: {e}")
            finally:
                net_connect.disconnect()
        return False

    def get_show_logging(router_info):
        """Retrieves 'show logging' output from the router."""
        host = router_info.get('host')
        logging.info(f"Netmiko: Attempting to get 'show logging' for router {host}...")
        net_connect = _get_netmiko_connection(router_info)
        if net_connect:
            try:
                output = net_connect.send_command("show logging")
                logging.info(f"Netmiko: Successfully retrieved 'show logging' from {host}.")
                return output
            except NetmikoTimeoutException as e:
                logging.error(f"Netmiko: Error getting 'show logging' from {host}: Connection timed out. {e}")
            except NetmikoAuthenticationException as e:
                logging.error(f"Netmiko: Error getting 'show logging' from {host}: Authentication failed. {e}")
            except Exception as e: # Catch any other unexpected errors during command execution
                logging.error(f"Netmiko: Unexpected error getting 'show logging' from {host}: {e}")
            finally:
                net_connect.disconnect()
        return None

    # Standalone test for functions (only runs when this file is executed directly)
    if __name__ == '__main__':
        
        print("--- Testing netmiko_ops.py functions ---")
        
        # Ensure backup/logs directories exist for testing
        os.makedirs(BACKUP_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)

        # Use DEFAULT_ROUTER_INFO for testing
        test_router_info = DEFAULT_ROUTER_INFO.copy()
        test_router_info['name'] = "TestRouterNetmiko" # Give it a name for logging
        
        # Test Backup
        print("\nTesting backup_config...")
        if backup_config(test_router_info):
            print("Backup test successful.")
        else:
            print("Backup test failed.")

        # Test get_show_logging
        print("\nTesting get_show_logging...")
        logs = get_show_logging(test_router_info)
        if logs:
            print("Show logging test successful. First 100 chars:\n", logs[:100])
        else:
            print("Show logging test failed.")

        # Test Reboot (CAUTION: This will actually reboot your router)
        # print("\nTesting reboot_router (CAUTION: Router will reboot!)...")
        # if reboot_router(test_router_info):
        #     print("Reboot command sent.")
        # else:
        #     print("Reboot command failed.")
        
        print("\n--- netmiko_ops.py Test Complete ---")
    ```
3.  Save `network_functions/netmiko_ops.py`.

### Task 0.4: Populate `network_functions/restconf_ops.py`

This file will contain RESTCONF-specific operations for monitoring.

1.  Open `network_functions/restconf_ops.py` in your code editor.
2.  Add the following Python code:
    ```python
    # network_functions/restconf_ops.py
    import logging
    import requests
    import json
    import time
    # No need to import BACKUP_DIR, LOGS_DIR here, as they are not used in this module.

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    DB_FILE = "database/inventory.db"

    DEFAULT_ROUTER_INFO = {
        "device_type": "cisco_ios", # For Netmiko
        "host": "10.10.200.148", # e.g., 10.10.20.40
        "username": "developer",
        "password": "abcd",
        "secret": "abcd", # For Netmiko enable mode
        "port": 22, # Default SSH port for Netmiko
        "restconf_port": 443, # Default HTTPS port for RESTCONF
        "verify_ssl": False # Set to True in production if you have proper CA certificates
    }

    def get_restconf_data(router_info, path):
        """
        Makes a GET request to the IOS XE RESTCONF API for a given YANG path.
        Returns the JSON response as a Python dictionary, or None on error.
        """
        host = router_info.get('host')
        restconf_port = router_info.get('restconf_port')
        username = router_info.get('username')
        password = router_info.get('password')
        verify_ssl = router_info.get('verify_ssl', False)

        RESTCONF_BASE_URL = f"https://{host}:{restconf_port}/restconf/data"
        full_url = f"{RESTCONF_BASE_URL}/{path}"

        headers = {
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json"
        }
        
        try:
            # logging.info(f"RESTCONF: Fetching {path} from {host}...") # Uncomment for debugging
            response = requests.get(
                full_url,
                headers=headers,
                auth=(username, password),
                verify=verify_ssl
            )
            response.raise_for_status() # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"RESTCONF HTTP error fetching {path} from {host}: {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.ConnectionError as e:
            logging.error(f"RESTCONF Connection error fetching {path} from {host}: {e}. Is device reachable and RESTCONF enabled?")
            return None
        except requests.exceptions.Timeout as e:
            logging.error(f"RESTCONF Timeout error fetching {path} from {host}: {e}. Device slow or unreachable?")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"RESTCONF general request error fetching {path} from {host}: {e}")
            return None
        except json.JSONDecodeError:
            logging.error(f"RESTCONF: JSON decode error for {path} response from {host}. Response was not valid JSON.")
            return None
        except Exception as e:
            logging.error(f"RESTCONF: Unexpected error fetching {path} from {host}: {e}")
            return None

    def get_interface_list(router_info):
        """Queries and returns a list of interface names from IOS XE via RESTCONF."""
        path = "ietf-interfaces:interfaces"
        data = get_restconf_data(router_info, path)
        interfaces = []
        if data:
            iface_list = data.get('ietf-interfaces:interfaces', {}).get('interface', [])
            for iface in iface_list:
                name = iface.get('name')
                if name:
                    interfaces.append(name)
        return interfaces

    def get_interface_stats_restconf(router_info, interface_name):
        """
        Retrieves interface statistics (in/out octets) via RESTCONF.
        Returns a dictionary or None.
        """
        path = f"ietf-interfaces:interfaces-state/interface={interface_name}/statistics"
        data = get_restconf_data(router_info, path)
        
        if data:
            # Access the specific interface data within the list
            # Note: data.get('ietf-interfaces:interfaces-state', {}).get('interface', [{}])
            # will always return the first item of the 'interface' list.
            # If the API response for 'interface={interface_name}' directly returns the interface object,
            # then you might not need the and 'interface' key.
            # Let's assume the API returns the specific interface object directly if queried by name.
            
            stats = data.get('ietf-interfaces:statistics', {})
            oper_status_data = get_restconf_data(router_info, f"ietf-interfaces:interfaces-state/interface={interface_name}/oper-status")
            oper_status = oper_status_data.get('ietf-interfaces:oper-status') if oper_status_data else "unknown"

            return {
                "in-octets": stats.get("in-octets"),
                "out-octets": stats.get("out-octets"),
                "status": oper_status
            }
        
        # If data fetching failed, try to get just oper-status
        oper_status_path = f"ietf-interfaces:interfaces-state/interface={interface_name}/oper-status"
        oper_status_data = get_restconf_data(router_info, oper_status_path)
        if oper_status_data:
            status = oper_status_data.get('ietf-interfaces:oper-status')
            return {"in-octets": "N/A", "out-octets": "N/A", "status": status}
        
        return {"in-octets": "N/A", "out-octets": "N/A", "status": "Error"}

    # Standalone test for functions (only runs when this file is executed directly)
    if __name__ == '__main__':
        
        print("--- Testing restconf_ops.py functions ---")
        
        test_router_info = DEFAULT_ROUTER_INFO.copy()
        test_router_info['name'] = "TestRouterRESTCONF" # Give it a name for logging
        
        # Test get_interface_list
        print("\nTesting get_interface_list...")
        interfaces = get_interface_list(test_router_info)
        if interfaces:
            print("Interface list successful:", interfaces)
        else:
            print("Interface list failed.")

        # Test get_interface_stats_restconf (requires RESTCONF enabled on router)
        if interfaces:
            print("\nTesting get_interface_stats_restconf for first interface GigabitEthernet1...")
            
            first_interface = "GigabitEthernet1" 
            interface_stats = get_interface_stats_restconf(test_router_info, first_interface)
            if interface_stats:
                print(f"Stats for {first_interface}:", interface_stats)
            else:
                print(f"Stats for {first_interface} failed.")
        else:
            print("\nNo interfaces to test stats for.")
        
        print("\n--- restconf_ops.py Test Complete ---")
    ```
3.  Save `network_functions/restconf_ops.py`.

### Task 0.5: Populate HTML Templates

These files define the structure and content of your web pages.

1.  Open `templates/index.html` in your code editor.
2.  Add the following HTML code:
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Router Management Console</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <div class="container">
            <h1>Router Management Console</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/inventory">Inventory Management</a>
                <a href="/actions">Router Actions</a>
                <a href="/monitor">Monitor Interfaces</a>
            </nav>
            <hr>
            <h2>Welcome!</h2>
            <p>Use the navigation above to manage your Cisco IOS XE routers.</p>
            <p>Currently managing <strong>{{ num_routers }}</strong> routers.</p>
        </div>
    </body>
    </html>
    ```
3.  Save `templates/index.html`.

4.  Open `templates/inventory.html` in your code editor.
5.  Add the following HTML code:
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Inventory Management</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <div class="container">
            <h1>Inventory Management</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/inventory">Inventory Management</a>
                <a href="/actions">Router Actions</a>
                <a href="/monitor">Monitor Interfaces</a>
            </nav>
            <hr>

            {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                <p class="message {{ category }}">{{ message }}</p>
                {% endfor %}
            {% endif %}
            {% endwith %}

            <h2>Add New Router</h2>
            <form action="/inventory" method="post">
                <label for="name">Name:</label><br>
                <input type="text" id="name" name="name" required><br><br>
                <label for="host">Host (IP/Hostname):</label><br>
                <input type="text" id="host" name="host" required><br><br>
                <label for="username">Username:</label><br>
                <input type="text" id="username" name="username" required><br><br>
                <label for="password">Password:</label><br>
                <input type="password" id="password" name="password" required><br><br>
                <label for="secret">Enable Password (optional):</label><br>
                <input type="password" id="secret" name="secret"><br><br>
                <label for="device_type">Device Type (e.g., cisco_ios):</label><br>
                <input type="text" id="device_type" name="device_type" value="cisco_ios" required><br><br>
                <label for="port">SSH Port:</label><br>
                <input type="number" id="port" name="port" value="22" required><br><br>
                <label for="restconf_port">RESTCONF Port:</label><br>
                <input type="number" id="restconf_port" name="restconf_port" value="443" required><br><br>
                <label for="verify_ssl">Verify SSL (True/False):</label><br>
                <input type="text" id="verify_ssl" name="verify_ssl" value="False" required><br><br>
                <input type="submit" value="Add Router">
            </form>

            <h2>Current Inventory</h2>
            {% if routers %}
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Host</th>
                        <th>Username</th>
                        <th>Device Type</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for router in routers %}
                    <tr>
                        <td>{{ router.name }}</td>
                        <td>{{ router.host }}</td>
                        <td>{{ router.username }}</td>
                        <td>{{ router.device_type }}</td>
                        <td>
                            <form action="/inventory/delete" method="post" style="display:inline;">
                                <input type="hidden" name="name" value="{{ router.name }}">
                                <input type="submit" value="Delete" onclick="return confirm('Are you sure you want to delete {{ router.name }}?');">
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>No routers in inventory. Add one above!</p>
            {% endif %}
        </div>
    </body>
    </html>
    ```
6.  Save `templates/inventory.html`.

7.  Open `templates/router_actions.html` in your code editor.
8.  Add the following HTML code:
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Router Actions</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <div class="container">
            <h1>Router Actions</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/inventory">Inventory Management</a>
                <a href="/actions">Router Actions</a>
                <a href="/monitor">Monitor Interfaces</a>
            </nav>
            <hr>

            {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                <p class="message {{ category }}">{{ message }}</p>
                {% endfor %}
            {% endif %}
            {% endwith %}

            <h2>Select Routers for Action</h2>
            {% if routers %}
            <form action="/actions" method="post">
                {% for router in routers %}
                <input type="checkbox" id="router_{{ loop.index }}" name="selected_routers" value="{{ router.name }}">
                <label for="router_{{ loop.index }}">{{ router.name }} ({{ router.host }})</label><br>
                {% endfor %}
                <br>
                <input type="submit" name="action" value="Reboot Selected">
                <input type="submit" name="action" value="Backup Config Selected">
                <input type="submit" name="action" value="Get Show Logging Selected">
            </form>
            {% else %}
            <p>No routers in inventory. Please add some via <a href="/inventory">Inventory Management</a>.</p>
            {% endif %}
        </div>
    </body>
    </html>
    ```
9.  Save `templates/router_actions.html`.

10. Open `templates/logs_display.html` in your code editor.
11. Add the following HTML code:
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Show Logging Output</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        <style>
            pre {
                background-color: #eee;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                white-space: pre-wrap; /* Wrap long lines */
                word-wrap: break-word; /* Break words to prevent overflow */
            }
            .log-section {
                border: 1px solid #ccc;
                padding: 10px;
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }
            .log-header {
                font-weight: bold;
                margin-bottom: 5px;
                color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Show Logging Output</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/inventory">Inventory Management</a>
                <a href="/actions">Router Actions</a>
                <a href="/monitor">Monitor Interfaces</a>
            </nav>
            <hr>

            {% if logs_data %}
                {% for router_name, log_output in logs_data.items() %}
                    <div class="log-section">
                        <div class="log-header">Logs for {{ router_name }} ({{ router_name_to_host.get(router_name, 'N/A') }})</div>
                        <pre>{{ log_output }}</pre>
                        <a href="/download_log/{{ router_name }}" download="{{ router_name }}_logging.txt">Download Log</a>
                    </div>
                {% endfor %}
            {% else %}
                <p>No logs to display or an error occurred.</p>
            {% endif %}
        </div>
    </body>
    </html>
    ```
12. Save `templates/logs_display.html`.

13. Open `templates/monitor_interface.html` in your code editor.
14. Add the following HTML code:
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Monitor Interfaces</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        <meta http-equiv="refresh" content="10"> <!-- Auto-refresh every 10 seconds -->
    </head>
    <body>
        <div class="container">
            <h1>Monitor Interfaces</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/inventory">Inventory Management</a>
                <a href="/actions">Router Actions</a>
                <a href="/monitor">Monitor Interfaces</a>
            </nav>
            <hr>

            <p>Last updated: {{ current_time }}</p>

            <h2>Select Interfaces to Monitor</h2>
            {% if routers %}
            <form action="/monitor" method="post">
                {% for router in routers %}
                <h3>{{ router.name }} ({{ router.host }})</h3>
                {% if all_interfaces.get(router.name) %}
                    {% for iface_name in all_interfaces.get(router.name) %}
                    <input type="checkbox" id="{{ router.name }}_{{ iface_name }}" name="selected_interfaces" value="{{ router.name }}|{{ iface_name }}" {% if iface_name in selected_interfaces_names.get(router.name, []) %}checked{% endif %}>
                    <label for="{{ router.name }}_{{ iface_name }}">{{ iface_name }}</label><br>
                    {% endfor %}
                {% else %}
                    <p>No interfaces found or error retrieving for this router.</p>
                {% endif %}
                {% endfor %}
                <br>
                <input type="submit" value="Update Monitored Interfaces">
            </form>
            {% else %}
            <p>No routers in inventory. Please add some via <a href="/inventory">Inventory Management</a>.</p>
            {% endif %}

            {% if monitored_data %}
            <h2>Live Interface Utilization</h2>
            <table>
                <thead>
                    <tr>
                        <th>Router</th>
                        <th>Interface</th>
                        <th>Status</th>
                        <th>In-Octets</th>
                        <th>Out-Octets</th>
                        <th>In-Utilization (bps)</th>
                        <th>Out-Utilization (bps)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in monitored_data %}
                    <tr>
                        <td>{{ item.router_name }}</td>
                        <td>{{ item.interface_name }}</td>
                        <td class="status-{{ item.status }}">{{ item.status }}</td>
                        <td>{{ item.in_octets }}</td>
                        <td>{{ item.out_octets }}</td>
                        <td>{{ item.in_util_bps | round(2) }}</td>
                        <td>{{ item.out_util_bps | round(2) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% elif selected_interfaces_names %}
            <p>Fetching data for selected interfaces...</p>
            {% endif %}
        </div>
    </body>
    </html>
    ```
15. Save `templates/monitor_interface.html`.

### Task 0.6: Populate `static/style.css`

This file defines the styling for your web dashboard.

1.  Open `static/style.css` in your code editor.
2.  Add the following CSS code:
    ```css
    body { 
        font-family: Arial, sans-serif; 
        margin: 20px; 
        background-color: #f4f4f4; 
        color: #333; 
    }
    .container { 
        background-color: #fff; 
        padding: 20px; 
        border-radius: 8px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        max-width: 900px; /* Wider for tables */
        margin: auto; 
    }
    h1, h2 { 
        color: #0056b3; 
    }
    nav {
        margin-bottom: 20px;
    }
    nav a {
        margin-right: 15px;
        text-decoration: none;
        color: #007bff;
        font-weight: bold;
    }
    nav a:hover {
        text-decoration: underline;
    }
    hr {
        border: 0;
        height: 1px;
        background: #eee;
        margin: 20px 0;
    }
    form {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    form label {
        display: inline-block;
        width: 150px;
        margin-bottom: 5px;
        font-weight: bold;
    }
    form input[type="text"],
    form input[type="password"],
    form input[type="number"] {
        width: calc(100% - 160px);
        padding: 8px;
        margin-bottom: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }
    form input[type="submit"] {
        background-color: #007bff;
        color: white;
        padding: 10px 15px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
        margin-right: 10px;
    }
    form input[type="submit"]:hover {
        background-color: #0056b3;
    }
    .message {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-top: 15px; 
    }
    th, td { 
        border: 1px solid #ddd; 
        padding: 8px; 
        text-align: left; 
    }
    th { 
        background-color: #f2f2f2; 
        color: #555;
    }
    tbody tr:nth-child(odd) {
        background-color: #f9f9f9;
    }
    .status-up { 
        color: green; 
        font-weight: bold; 
    }
    .status-down { 
        color: red; 
        font-weight: bold; 
    }
    .metric { 
        margin-bottom: 10px; 
        padding: 10px; 
        border: 1px solid #ddd; 
        border-radius: 4px; 
    }
    .metric strong { 
        color: #007bff; 
    }
    .alert { 
        color: red; 
        font-weight: bold; 
    }
    pre {
        background-color: #eee;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        white-space: pre-wrap; /* Wrap long lines */
        word-wrap: break-word; /* Break words to prevent overflow */
    }
    .log-section {
        border: 1px solid #ccc;
        padding: 10px;
        margin-bottom: 20px;
        background-color: #f9f9f9;
    }
    .log-header {
        font-weight: bold;
        margin-bottom: 5px;
        color: #0056b3;
    }
    ```
3.  Save `static/style.css`.

### Task 0.7: Populate `app.py`

This is the main Flask application file that will bring everything together.

1.  Open `app.py` in your code editor.
2.  Add the following Python code:
    ```python
    # app.py
    # app.py
    from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session # ADD session
    import time
    import threading
    import os
    import json # For parsing JSON from RESTCONF

    # Import functions and configurations from our modules
    from database.db_ops import load_inventory, add_router_to_inventory, delete_router_from_inventory, get_router_by_name
    from network_functions.netmiko_ops import reboot_router, backup_config, get_show_logging
    from network_functions.restconf_ops import get_interface_list, get_interface_stats_restconf
    # Directory to store configuration backups
    BACKUP_DIR = "backups"

    # Directory to store logs
    LOGS_DIR = "logs"

    app = Flask(__name__)
    app.secret_key = 'supersecretkey' # Needed for flash messages and session. CHANGE THIS IN PRODUCTION!

    # Ensure directories exist
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # --- Flask Routes ---

    @app.route('/')
    def index():
        """Home page displaying number of managed routers."""
        routers = load_inventory()
        return render_template('index.html', num_routers=len(routers))

    @app.route('/inventory', methods=['GET', 'POST'])
    def inventory_management():
        """Handles adding and listing routers in inventory."""
        if request.method == 'POST':
            # Handle adding a new router
            name = request.form['name']
            host = request.form['host']
            username = request.form['username']
            password = request.form['password']
            secret = request.form.get('secret', '') # Optional
            device_type = request.form.get('device_type', 'cisco_ios')
            port = int(request.form.get('port', 22))
            restconf_port = int(request.form.get('restconf_port', 443))
            verify_ssl_str = request.form.get('verify_ssl', 'False')
            verify_ssl = verify_ssl_str.lower() == 'true' # Convert string to boolean

            # Basic validation
            if not name or not host or not username or not password:
                flash('All required fields must be filled!', 'error')
            elif get_router_by_name(name):
                flash(f'Router with name "{name}" already exists!', 'error')
            else:
                new_router = {
                    "name": name,
                    "host": host,
                    "username": username,
                    "password": password,
                    "secret": secret,
                    "device_type": device_type,
                    "port": port,
                    "restconf_port": restconf_port,
                    "verify_ssl": verify_ssl
                }
                if add_router_to_inventory(new_router):
                    flash(f'Router "{name}" added successfully!', 'success')
                else:
                    flash(f'Failed to add router "{name}". See console for details.', 'error')
            return redirect(url_for('inventory_management'))
        
        routers = load_inventory()
        return render_template('inventory.html', routers=routers)

    @app.route('/inventory/delete', methods=['POST'])
    def inventory_delete():
        """Handles deleting a router from inventory."""
        router_name = request.form['name']
        if delete_router_from_inventory(router_name):
            flash(f'Router "{router_name}" deleted successfully!', 'success')
        else:
            flash(f'Router "{router_name}" not found for deletion.', 'error')
        return redirect(url_for('inventory_management'))

    @app.route('/actions', methods=['GET', 'POST'])
    def router_actions():
        """Handles router actions like reboot, backup, get logging."""
        routers = load_inventory()
        if request.method == 'POST':
            selected_router_names = request.form.getlist('selected_routers')
            action = request.form['action']

            if not selected_router_names:
                flash('Please select at least one router.', 'error')
                return redirect(url_for('router_actions'))

            for router_name in selected_router_names:
                router_info = get_router_by_name(router_name)
                if not router_info:
                    flash(f'Router "{router_name}" not found in inventory.', 'error')
                    continue

                if action == 'Reboot Selected':
                    # Run reboot in a separate thread to avoid blocking the GUI
                    thread = threading.Thread(target=reboot_router, args=(router_info,))
                    thread.start()
                    flash(f'Reboot command sent to {router_name} in background.', 'info')
                elif action == 'Backup Config Selected':
                    thread = threading.Thread(target=backup_config, args=(router_info,))
                    thread.start()
                    flash(f'Backup initiated for {router_name} in background. Check "{BACKUP_DIR}" folder.', 'info')
                elif action == 'Get Show Logging Selected':
                    # For show logging, we fetch and then redirect to a display page
                    # This might still block if many routers are selected.
                    # For simplicity, we'll collect logs sequentially here for display.
                    logs_data = {}
                    router_name_to_host = {}
                    for name in selected_router_names:
                        info = get_router_by_name(name)
                        if info:
                            log_output = get_show_logging(info)
                            # Save log to a temporary file for download link
                            if log_output:
                                temp_log_path = os.path.join(LOGS_DIR, f"{name}_logging.txt")
                                os.makedirs(LOGS_DIR, exist_ok=True)
                                with open(temp_log_path, 'w') as f:
                                    f.write(log_output)
                                logs_data[name] = log_output
                            else:
                                logs_data[name] = f"Error retrieving logs from {name}."
                            router_name_to_host[name] = info['host']
                    return render_template('logs_display.html', logs_data=logs_data, router_name_to_host=router_name_to_host)
            
            return redirect(url_for('router_actions')) # Redirect to prevent re-submission on refresh
        
        return render_template('router_actions.html', routers=routers)

    @app.route('/download_log/<router_name>')
    def download_log(router_name):
        """Allows downloading the last retrieved log for a router."""
        log_filename = f"{router_name}_logging.txt"
        temp_log_path = os.path.join(LOGS_DIR, log_filename)
        
        if os.path.exists(temp_log_path):
            return send_from_directory(LOGS_DIR, log_filename, as_attachment=True)
        else:
            flash(f"Log file for {router_name} not found. Please retrieve logs first.", "error")
            return redirect(url_for('router_actions'))


    @app.route('/monitor', methods=['GET', 'POST'])
    def monitor_interfaces():
        """Handles interface monitoring dashboard."""
        routers = load_inventory()
        all_interfaces = {} # Store {router_name: [interface_names]}
        monitored_data = [] # Store live stats

        # Retrieve previously selected interfaces from session or initialize an empty list
        # This list will store strings like "router_name|interface_name"
        monitored_interfaces_from_session = session.get('monitored_interfaces', [])

        # If the form was submitted (POST request), update the session with the new selection
        if request.method == 'POST':
            # Get the new selection from the form
            new_selection = request.form.getlist('selected_interfaces')
            # Store the new selection in the session
            session['monitored_interfaces'] = new_selection
            # Redirect to the GET version of the monitor page to prevent re-submission on refresh
            # and ensure the page loads from the session data.
            return redirect(url_for('monitor_interfaces'))

        # Prepare selected_interfaces_for_template for checking checkboxes in the HTML
        # This dictionary will be {router_name: [iface1, iface2], ...}
        selected_interfaces_for_template = {}
        for selected_iface_str in monitored_interfaces_from_session:
            try:
                # Split only on the first '|' to handle interface names that might contain '|'
                router_name, iface_name = selected_iface_str.split('|', 1)
                if router_name not in selected_interfaces_for_template:
                    selected_interfaces_for_template[router_name] = []
                selected_interfaces_for_template[router_name].append(iface_name)
            except ValueError:
                # Log a warning if an interface string in the session is malformed
                app.logger.warning(f"Invalid interface string in session: {selected_iface_str}")


        # Populate all_interfaces for display in the form (available interfaces)
        for router in routers:
            interfaces_list = get_interface_list(router) 
            all_interfaces[router['name']] = interfaces_list

        # Fetch live stats for the interfaces currently stored in the session
        for selected_iface_str in monitored_interfaces_from_session:
            try:
                router_name, iface_name = selected_iface_str.split('|', 1)
                router_info = get_router_by_name(router_name)
                if router_info:
                    stats = get_interface_stats_restconf(router_info, iface_name)
                    if stats:
                        # Corrected: Convert octets to int before division
                        in_octets = int(stats.get('in-octets', 0)) if stats.get('in-octets') is not None else 0
                        out_octets = int(stats.get('out-octets', 0)) if stats.get('out-octets') is not None else 0
                        
                        # Dummy calculation for bps for display purposes
                        # In a real scenario, you'd store previous octets and calculate diff/time
                        in_util_bps = in_octets / 1000 if in_octets is not None else 0
                        out_util_bps = out_octets / 1000 if out_octets is not None else 0

                        monitored_data.append({
                            "router_name": router_name,
                            "interface_name": iface_name,
                            "status": stats.get('status', 'N/A'),
                            "in_octets": in_octets,
                            "out_octets": out_octets,
                            "in_util_bps": in_util_bps,
                            "out_util_bps": out_util_bps
                        })
            except ValueError:
                app.logger.warning(f"Skipping monitoring for invalid interface string: {selected_iface_str}")
        
        return render_template(
            'monitor_interface.html', 
            routers=routers, 
            all_interfaces=all_interfaces,
            selected_interfaces_names=selected_interfaces_for_template, # Use the prepared dict here
            monitored_data=monitored_data,
            current_time=time.strftime("%Y-%m-%d %H:%M:%S")
        )

    # --- Main execution block for running Flask app ---
    if __name__ == '__main__':
        # To run the Flask app, you typically use 'flask run' from the terminal.
        # Set FLASK_APP environment variable first:
        # export FLASK_APP=app.py (Linux/macOS)
        # $env:FLASK_APP="app.py" (Windows PowerShell)
        # Then run: flask run --host=0.0.0.0 --port=5001 --debug
        # Or for simple testing, you can run it directly like this:
        app.run(debug=True, host='0.0.0.0', port=5001)
    ```
3.  Save `app.py`.

---

## Lab 1: Inventory Management

**Objective:** Use the web GUI to add, list, and delete routers from the inventory.

### Task 1.1: Start the Flask Application

1.  Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).
2.  Navigate into your `module10_router_console` directory:
    ```bash
    cd module10_router_console
    ```
3.  while in module10_router_console folder run app.py
    ```bash
    python app.py
    ```

    ```
    *Expected Output (console):*
    ```
     * Debug mode: on
     * Running on http://0.0.0.0:5001
    Press CTRL+C to quit
     * Restarting with stat
    Press CTRL+C to quit
    ```
    *(Note the `Running on http://0.0.0.0:5001` line, confirming it's running correctly.)*
5.  **Open your web browser** and navigate to `http://127.0.0.1:5001` (or `http://localhost:5001`).

### Task 1.2: Add a Router to Inventory

1.  In your web browser, navigate to the **"Inventory Management"** link (or go directly to `http://127.0.0.1:5001/inventory`).
2.  Fill out the "Add New Router" form. Use the information from `config.py` (your actual lab router details).
    *   **Name:** `MyLabRouter` (or any name you like)
    *   **Host:** `YOUR_ROUTER_IP`
    *   **Username:** `YOUR_ROUTER_USERNAME`
    *   **Password:** `YOUR_ROUTER_PASSWORD`
    *   **Enable Password:** `YOUR_ROUTER_ENABLE_PASSWORD` (if applicable)
    *   **Device Type:** `cisco_ios`
    *   **SSH Port:** `22`
    *   **RESTCONF Port:** `443`
    *   **Verify SSL:** `False` (or `True` if you have proper certs)
3.  Click **"Add Router"**.
    *Expected Web Output:* A green "Router 'MyLabRouter' added successfully!" message should appear, and the router should be listed in the "Current Inventory" table.
    *Verification:* Check your `inventory.db` file in your `module10_router_console/database` folder. Its presence confirms creation.

### Task 1.3: Delete a Router from Inventory

1.  In the "Current Inventory" table, find the router you just added.
2.  Click the **"Delete"** button next to its entry.
3.  Confirm the deletion when prompted.
    *Expected Web Output:* A green "Router 'MyLabRouter' deleted successfully!" message should appear, and the router should be removed from the table.

4.  **Re-add your router** using Task 1.2 so you have a router in inventory for the next labs.

---

## Lab 2: Router Actions (Reboot, Backup, Show Logging)

**Objective:** Use the web GUI to perform operational tasks on your managed routers.

### Task 2.1: Backup Configuration

1.  In your web browser, navigate to the **"Router Actions"** link (or go directly to `http://127.0.0.1:5001/actions`).
2.  Select the checkbox next to your router's name.
3.  Click **"Backup Config Selected"**.
    *Expected Web Output:* A green "Backup initiated for MyLabRouter in background. Check 'backups' folder." message.
    *Verification:* Check the `backups` directory inside your `module10_router_console` folder. A new file named `YOUR_ROUTER_IP_running_config_YYYYMMDD_HHMMSS.txt` should be created, containing your router's running configuration.

### Task 2.2: Retrieve "show logging" Output

1.  In your web browser, navigate to the **"Router Actions"** page again.
2.  Select the checkbox next to your router's name.
3.  Click **"Get Show Logging Selected"**.
    *Expected Web Output:* A new page will load displaying the "show logging" output for your router. You will also see a "Download Log" link.
    *Verification:* Click the "Download Log" link. A text file containing the log output should be downloaded to your computer.

### Task 2.3: Reboot Router (CAUTION!)

**WARNING: This will actually reboot your physical or virtual router. Ensure you understand the impact before proceeding.**

1.  In your web browser, navigate to the **"Router Actions"** page again.
2.  Select the checkbox next to your router's name.
3.  Click **"Reboot Selected"**.
    *Expected Web Output:* 
    A green "Reboot command sent to MyLabRouter in background." message.
    *Verification:* 
    Observe your router (via console or ping). It should start the reboot process. This will take some time.

---

## Lab 3: Monitor Interface Bandwidth Utilization

**Objective:** Use the web GUI to monitor bandwidth utilization for selected interfaces.

### Task 3.1: Select Interfaces to Monitor

1.  In your web browser, navigate to the **"Monitor Interfaces"** link (or go directly to `http://127.0.0.1:5001/monitor`).
2.  You should see your router listed. Select the checkboxes next to one or more interfaces you wish to monitor (e.g., `GigabitEthernet1`).
3.  Click **"Update Monitored Interfaces"**.
    
    *Expected Web Output:* 
    The page will refresh, and a new table titled "Live Interface Utilization" will appear, showing data for your selected interfaces. The page will automatically refresh every 10 seconds.

    *Observation:* The "In-Utilization (bps)" and "Out-Utilization (bps)" values will likely be very low or zero unless there is actual traffic flowing through those interfaces. These are calculated based on current octet counts, not historical data for true bandwidth.

---

## Conclusion

You've now completed Module 10 and built a functional, web-based management console for Cisco IOS XE routers! You can now:

*   Understand the benefits and architecture of a centralized management console.
*   Implement inventory management using an SQLite database.
*   Perform remote router actions (reboot, backup, show logging) via Netmiko.
*   Display and download command output from the web GUI.
*   Monitor interface bandwidth utilization using RESTCONF and display it in a Flask dashboard.
*   Handle long-running tasks in the background to keep the GUI responsive.

This module demonstrates how to create more interactive and user-friendly automation tools that can empower network administrators.

**Keep Automating!**

---