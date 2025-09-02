---

## Document 2: Python Basics for Network Automation - Module 5 Lab Guide (Complete Markdown Block)

```markdown
# Python Basics for Network Automation: Module 5 Lab Guide

## Using APIs to Retrieve Data on Cisco Network Devices - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 5 of the Python Basics for Network Automation Lab Guide! In this module, you will gain hands-on experience with using APIs to retrieve data. We will focus on **REST APIs** and the `requests` Python library.

Since setting up a real Cisco API environment can be complex for beginners, we will use **public dummy APIs** for general API interaction and **simulated Python dictionaries** to represent device performance data. This allows you to learn the core concepts without needing a specific network device or API key.

**Lab Objectives:**
*   Install the `requests` library.
*   Make a simple GET request to a public REST API.
*   Handle API responses and errors.
*   Simulate retrieving device performance data (CPU, memory, interfaces) using Python dictionaries.
*   Build a simple monitoring tool that polls simulated data and checks thresholds.

**Prerequisites:**
*   Completion of Module 1, Module 2, Module 3, and Module 4 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   An active internet connection (for public API calls).

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
2.  Add the following code:
    ```python
    # api_lab.py

    # --- Import necessary libraries ---
    import requests
    import json # For pretty-printing JSON
    import time # For monitoring lab

    print("--- Lab 1.2: Make a Simple GET Request ---")

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
    --- Lab 1.2: Make a Simple GET Request ---
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

### Task 1.3: Fetch and Process a List of Items

APIs often return lists of objects. We'll fetch a list of users and iterate through them.

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 1.3: Fetch and Process a List of Items ---")

    # The URL for a list of users from JSONPlaceholder API
    api_url_users = "https://jsonplaceholder.typicode.com/users"

    try:
        print(f"Attempting to fetch user data from: {api_url_users}")
        response = requests.get(api_url_users)
        response.raise_for_status() 

        # This time, data will be a list of dictionaries
        users_data = response.json()

        print(f"\nSuccessfully fetched {len(users_data)} users.")
        print("\n--- First 3 Users' Details ---")
        for i, user in enumerate(users_data[:3]): # Iterate through the first 3 users
            print(f"User {i+1}:")
            print(f"  Name: {user['name']}")
            print(f"  Email: {user['email']}")
            print(f"  City: {user['address']['city']}") # Access nested data
            print("-" * 20) # Separator

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from API.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("\nLab 1.3 complete.")
    ```
3.  Save `api_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory:
    ```bash
    python api_lab.py
    ```
    *Expected Output (content from live API, will vary slightly):*
    ```
    --- Lab 1.3: Fetch and Process a List of Items ---
    Attempting to fetch user data from: https://jsonplaceholder.typicode.com/users

    Successfully fetched 10 users.

    --- First 3 Users' Details ---
    User 1:
      Name: Leanne Graham
      Email: Sincere@april.biz
      City: Gwenborough
    --------------------
    User 2:
      Name: Ervin Howell
      Email: Shanna@melissa.tv
      City: Wisokyburgh
    --------------------
    User 3:
      Name: Clementine Bauch
      Email: Nathan@yesenia.net
      City: McKenziehaven
    --------------------

    Lab 1.3 complete.
    ```

---

## Lab 2: Querying Simulated Device Performance Data

**Objective:** Understand how to work with structured performance data, simulating what a device API might return.

### Task 2.1: Create a Function to Simulate Device Performance Data

This function will return a Python dictionary representing performance metrics.

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 2.1: Simulate Device Performance Data ---")

    def get_simulated_device_performance(device_name):
        """
        Simulates an API call to get device performance data.
        Returns a dictionary with CPU, memory, and interface stats.
        """
        if device_name == "Router1":
            return {
                "device_name": "Router1",
                "ip_address": "192.168.1.1",
                "cpu_utilization_percent": 75,
                "memory_total_mb": 4096,
                "memory_used_mb": 3072,
                "interfaces": [
                    {"name": "GigabitEthernet0/0", "status": "up", "input_rate_bps": 1000000, "output_rate_bps": 500000},
                    {"name": "GigabitEthernet0/1", "status": "down", "input_rate_bps": 0, "output_rate_bps": 0},
                    {"name": "Loopback0", "status": "up", "input_rate_bps": 0, "output_rate_bps": 0}
                ]
            }
        elif device_name == "SwitchA":
            return {
                "device_name": "SwitchA",
                "ip_address": "192.168.1.10",
                "cpu_utilization_percent": 30,
                "memory_total_mb": 2048,
                "memory_used_mb": 1024,
                "interfaces": [
                    {"name": "GigabitEthernet0/1", "status": "up", "input_rate_bps": 5000000, "output_rate_bps": 2000000},
                    {"name": "GigabitEthernet0/2", "status": "up", "input_rate_bps": 100000, "output_rate_bps": 50000}
                ]
            }
        else:
            return None # Device not found

    # Get data for Router1
    router1_perf = get_simulated_device_performance("Router1")
    print("\n--- Router1 Performance Data ---")
    print(json.dumps(router1_perf, indent=2))

    # Get data for SwitchA
    switch_a_perf = get_simulated_device_performance("SwitchA")
    print("\n--- SwitchA Performance Data ---")
    print(json.dumps(switch_a_perf, indent=2))

    print("\nLab 2.1 complete.")
    ```
3.  Save `api_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory:
    ```bash
    python api_lab.py
    ```
    *Expected Output:*
    ```
    --- Lab 2.1: Simulate Device Performance Data ---

    --- Router1 Performance Data ---
    {
      "device_name": "Router1",
      "ip_address": "192.168.1.1",
      "cpu_utilization_percent": 75,
      "memory_total_mb": 4096,
      "memory_used_mb": 3072,
      "interfaces": [
        {
          "name": "GigabitEthernet0/0",
          "status": "up",
          "input_rate_bps": 1000000,
          "output_rate_bps": 500000
        },
        {
          "name": "GigabitEthernet0/1",
          "status": "down",
          "input_rate_bps": 0,
          "output_rate_bps": 0
        },
        {
          "name": "Loopback0",
          "status": "up",
          "input_rate_bps": 0,
          "output_rate_bps": 0
        }
      ]
    }

    --- SwitchA Performance Data ---
    {
      "device_name": "SwitchA",
      "ip_address": "192.168.1.10",
      "cpu_utilization_percent": 30,
      "memory_total_mb": 2048,
      "memory_used_mb": 1024,
      "interfaces": [
        {
          "name": "GigabitEthernet0/1",
          "status": "up",
          "input_rate_bps": 5000000,
          "output_rate_bps": 2000000
        },
        {
          "name": "GigabitEthernet0/2",
          "status": "up",
          "input_rate_bps": 100000,
          "output_rate_bps": 50000
        }
      ]
    }

    Lab 2.1 complete.
    ```

### Task 2.2: Extract Specific Performance Metrics

Now, we'll access individual pieces of data from the simulated performance dictionaries.

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 2.2: Extract Specific Performance Metrics ---")

    # Extracting data from Router1's performance
    if router1_perf:
        print(f"\nRouter1 CPU: {router1_perf['cpu_utilization_percent']}%")
        print(f"Router1 Memory Used: {router1_perf['memory_used_mb']}MB out of {router1_perf['memory_total_mb']}MB")
        
        print("\nRouter1 Interfaces:")
        for iface in router1_perf['interfaces']:
            print(f"  - {iface['name']}: Status={iface['status']}, Input Rate={iface['input_rate_bps']} bps")
            if iface['name'] == "GigabitEthernet0/1":
                print(f"    Specific G0/1 status: {iface['status']}")
    else:
        print("Router1 data not available.")

    # Extracting data from SwitchA's performance
    if switch_a_perf:
        print(f"\nSwitchA CPU: {switch_a_perf['cpu_utilization_percent']}%")
        print(f"SwitchA G0/1 Input Rate: {switch_a_perf['interfaces']['input_rate_bps']} bps")
    else:
        print("SwitchA data not available.")

    print("\nLab 2.2 complete.")
    ```
3.  Save `api_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory:
    ```bash
    python api_lab.py
    ```
    *Expected Output:*
    ```
    --- Lab 2.2: Extract Specific Performance Metrics ---

    Router1 CPU: 75%
    Router1 Memory Used: 3072MB out of 4096MB

    Router1 Interfaces:
      - GigabitEthernet0/0: Status=up, Input Rate=1000000 bps
      - GigabitEthernet0/1: Status=down, Input Rate=0 bps
        Specific G0/1 status: down
      - Loopback0: Status=up, Input Rate=0 bps

    SwitchA CPU: 30%
    SwitchA G0/1 Input Rate: 5000000 bps

    Lab 2.2 complete.
    ```

---

## Lab 3: Building a Simple Monitoring Tool

**Objective:** Build a simple monitoring tool that periodically polls simulated data and checks thresholds.

### Task 3.1: Enhance Simulation for Dynamic Data

We'll modify `get_simulated_device_performance` to return slightly different data each time it's called, simulating real-time changes.

1.  Open `api_lab.py` in your code editor.
2.  **Modify** the `get_simulated_device_performance` function. Find it and change it to:
    ```python
    # ... (previous code) ...

    # Add this global variable to simulate changing CPU
    _simulated_cpu_counter = 0

    def get_simulated_device_performance(device_name):
        """
        Simulates an API call to get device performance data.
        Returns a dictionary with CPU, memory, and interface stats.
        CPU will change slightly each time for monitoring.
        """
        global _simulated_cpu_counter # We need to modify this global variable

        if device_name == "Router1":
            # Simulate CPU going up/down slowly
            _simulated_cpu_counter = (_simulated_cpu_counter + 5) % 100 # Increment and wrap around
            current_cpu = 60 + (_simulated_cpu_counter % 30) # CPU between 60 and 89
            
            # Simulate an interface sometimes going down
            g0_1_status = "up" if random.random() > 0.1 else "down" # 10% chance of being down

            return {
                "device_name": "Router1",
                "ip_address": "192.168.1.1",
                "cpu_utilization_percent": min(int(current_cpu), 95), # Cap at 95%
                "memory_total_mb": 4096,
                "memory_used_mb": 3072,
                "interfaces": [
                    {"name": "GigabitEthernet0/0", "status": "up", "input_rate_bps": 1000000, "output_rate_bps": 500000},
                    {"name": "GigabitEthernet0/1", "status": g0_1_status, "input_rate_bps": 0, "output_rate_bps": 0},
                    {"name": "Loopback0", "status": "up", "input_rate_bps": 0, "output_rate_bps": 0}
                ]
            }
        elif device_name == "SwitchA":
            # Simulate CPU for SwitchA
            current_cpu = 20 + (time.time() % 15) * 0.5
            return {
                "device_name": "SwitchA",
                "ip_address": "192.168.1.10",
                "cpu_utilization_percent": min(int(current_cpu), 60),
                "memory_total_mb": 2048,
                "memory_used_mb": 1024,
                "interfaces": [
                    {"name": "GigabitEthernet0/1", "status": "up", "input_rate_bps": 5000000, "output_rate_bps": 2000000},
                    {"name": "GigabitEthernet0/2", "status": "up", "input_rate_bps": 100000, "output_rate_bps": 50000}
                ]
            }
        else:
            return None # Device not found
    ```
    *Note: We added a global counter and `random.random()` to make the CPU and interface status change over time. Also, add `import random` at the top of your file with other imports.*

### Task 3.2: Build the Monitoring Logic

Now, create a function that monitors a device, checks thresholds, and prints alerts.

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 3.2: Build the Monitoring Logic ---")

    def monitor_device(device_name, cpu_threshold=80, interface_down_alert=True):
        """
        Monitors a device's performance data, checks thresholds, and prints alerts.
        """
        print(f"\nMonitoring {device_name}...")
        performance_data = get_simulated_device_performance(device_name)
        
        if performance_data:
            cpu = performance_data["cpu_utilization_percent"]
            mem_used = performance_data["memory_used_mb"]
            mem_total = performance_data["memory_total_mb"]
            interfaces = performance_data["interfaces"]
            
            print(f"  CPU: {cpu}%, Memory: {mem_used}/{mem_total}MB")
            
            # Check CPU threshold
            if cpu > cpu_threshold:
                print(f"  !!! ALERT: {device_name} CPU utilization ({cpu}%) is above threshold ({cpu_threshold}%).")
            
            # Check interface status
            for iface in interfaces:
                if iface['status'] == "down" and interface_down_alert:
                    print(f"  !!! ALERT: {device_name} Interface {iface['name']} is DOWN!")
        else:
            print(f"  Could not retrieve data for {device_name}.")

    # We will run this in the next task
    print("\nLab 3.2 complete. (Monitoring will run in next task)")
    ```

### Task 3.3: Run the Monitoring Tool

Finally, we'll put it all together in a loop to simulate continuous monitoring.

1.  Open `api_lab.py` in your code editor.
2.  Add the following code below the previous task:
    ```python
    # ... (previous code) ...

    print("\n--- Lab 3.3: Run the Monitoring Tool ---")

    # Main loop for continuous monitoring
    print("Starting continuous network monitoring (Ctrl+C to stop)...")
    try:
        for i in range(1, 11): # Run 10 monitoring cycles
            print(f"\n--- Monitoring Cycle {i} ---")
            monitor_device("Router1", cpu_threshold=75) # Set a CPU threshold for Router1
            monitor_device("SwitchA", cpu_threshold=50) # Set a CPU threshold for SwitchA
            time.sleep(3) # Wait 3 seconds before the next monitoring cycle
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"An error occurred during monitoring: {e}")

    print("\nLab 3.3 complete.")
    ```
3.  Save `api_lab.py`.
4.  **Run the script** from your `network_automation_labs` directory:
    ```bash
    python api_lab.py
    ```
    *Expected Output (output will change over time, and alerts will appear):*
    ```
    --- Lab 3.3: Run the Monitoring Tool ---
    Starting continuous network monitoring (Ctrl+C to stop)...

    --- Monitoring Cycle 1 ---

    Monitoring Router1...
      CPU: 60%, Memory: 3072/4096MB
      !!! ALERT: Router1 Interface GigabitEthernet0/1 is DOWN!

    Monitoring SwitchA...
      CPU: 20%, Memory: 1024/2048MB

    --- Monitoring Cycle 2 ---

    Monitoring Router1...
      CPU: 65%, Memory: 3072/4096MB
      !!! ALERT: Router1 Interface GigabitEthernet0/1 is DOWN!

    Monitoring SwitchA...
      CPU: 21%, Memory: 1024/2048MB

    --- Monitoring Cycle 3 ---

    Monitoring Router1...
      CPU: 70%, Memory: 3072/4096MB

    Monitoring SwitchA...
      CPU: 22%, Memory: 1024/2048MB

    --- Monitoring Cycle 4 ---

    Monitoring Router1...
      CPU: 75%, Memory: 3072/4096MB
      !!! ALERT: Router1 CPU utilization (75%) is above threshold (75%).

    Monitoring SwitchA...
      CPU: 23%, Memory: 1024/2048MB

    ... (continues for 10 cycles, or until Ctrl+C) ...

    Monitoring stopped by user.
    Lab 3.3 complete.
    ```
    *Observation:* You will see CPU values changing and alerts appearing when thresholds are met or interfaces go down (simulated). This demonstrates a basic monitoring loop.

---

## Conclusion

You've now completed Module 5 and gained practical experience with using APIs to retrieve data! You can now:

*   Understand the role of APIs in modern network automation.
*   Make basic GET requests to REST APIs using the `requests` library.
*   Work with structured data (JSON) returned by APIs.
*   Simulate device performance data.
*   Build a simple monitoring tool that polls data and checks thresholds.

APIs are a powerful and increasingly common way to interact with network devices and controllers. These foundational skills will serve you well as you explore more advanced automation topics.

**Keep Automating!**

---