# Python Basics for Network Automation: Module 2 Lab Guide

## Making Your Python Scripts Faster: Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 2 of the Python Basics for Network Automation Lab Guide! In this module, you'll get hands-on with concurrency concepts in Python, specifically focusing on data synchronization with `threading` and asynchronous programming with `asyncio`. These skills are vital for writing efficient network automation scripts that can handle multiple devices or operations concurrently.

**Lab Objectives:**
*   Understand and observe race conditions in multi-threaded programs.
*   Apply `threading.Lock` to prevent race conditions.
*   Use `threading.Semaphore` to limit concurrent access to resources (e.g., network devices).
*   Implement `queue.Queue` for thread-safe task distribution (e.g., for log processing).
*   Write and execute basic `asyncio` coroutines for non-blocking I/O.
*   Run multiple `asyncio` tasks concurrently using `asyncio.gather` for **concurrent network device connections**.
*   Apply asynchronous techniques to **log collection** and **real-time monitoring** simulations.

**Prerequisites:**
*   Completion of Module 1 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   **Optional (for real-world testing):** Access to a Cisco IOS XE routers sandbox (e.g., Cisco DevNet Sandbox) with SSH access. You will need to replace simulated IPs/credentials with real ones if you choose to test against live devices.

Let's dive into concurrent Python!

---

## Lab 1: Keeping Order with Threads (Data Synchronization)

**Objective:** Understand why we need to be careful when multiple threads work together, and how to use tools like Locks, Semaphores, and Queues to keep things organized.

### Task 1.1: See a "Race Condition" Happen

In this task, you'll create a simple multi-threaded program that increments a shared counter without any synchronization, demonstrating a race condition.

1.  Activate your `na_env` virtual environment in your terminal.
2.  Create a new Python file named `threading_sync_lab.py`.
3.  Add the following code to the file:
    ```python
    # threading_sync_lab.py
    import threading # This module helps us create and manage threads
    import time      # We'll use this to simulate delays

    # This is a number that all our threads will try to change.
    # It's a "shared resource."
    shared_counter = 0

    def increment_counter_problem(iterations):
        global shared_counter # Tell Python we want to use the global 'shared_counter'
        for _ in range(iterations):
            # --- This is the "critical section" where race conditions happen ---
            # 1. Read the current value
            current_value = shared_counter
            
            # 2. Simulate a tiny delay, like a thread getting distracted
            #    This makes the race condition more likely to appear.
            time.sleep(0.00001) 
            
            # 3. Calculate the new value
            new_value = current_value + 1
            
            # 4. Write the new value back
            shared_counter = new_value
            # --- End of critical section ---

    print("--- Observing a Race Condition ---")
    num_threads = 5 # We'll have 5 threads working
    iterations_per_thread = 10000 # Each thread will try to add 1 to the counter 10,000 times

    # If everything worked perfectly, what should the final number be?
    expected_total = num_threads * iterations_per_thread
    print(f"If all threads worked perfectly, the counter should be: {expected_total}")

    threads = []
    for i in range(num_threads):
        # Create a thread that will run our 'increment_counter_problem' function
        thread = threading.Thread(target=increment_counter_problem, args=(iterations_per_thread,))
        threads.append(thread)
        thread.start() # Start the thread (tell it to begin its work)

    # Wait for all threads to finish their work
    for thread in threads:
        thread.join() 

    print(f"Actual final counter value:   {shared_counter}")

    if shared_counter != expected_total:
        print("!!! Race condition observed: The actual value is NOT what we expected. !!!")
        print("This means threads interfered with each other's updates.")
    else:
        print("No race condition observed this time. (Try running it again, it's often random!)")

    ```
4.  Save and run `threading_sync_lab.py` from your terminal.
5.  **Expected Output/Observation:**
    *   The "Actual final counter value" will almost certainly be *less than* the "Expected final counter value" (which is 50000).
    *   You will see the message: `!!! Race condition observed: The actual value is NOT what we expected. !!!`
    *   The exact "Actual final counter value" will vary each time you run the script, but it will consistently be incorrect.

### Task 1.2: Fix the Race Condition with a "Lock"

Now, we'll use a `threading.Lock` to make sure that only one thread can access the `shared_counter` at a time. This is like putting a "Do Not Disturb" sign on the critical section of code.

1.  In the same `threading_sync_lab.py` file, add the following code below your previous task:
    ```python
    # ... (previous code from Task 1.1) ...

    # A new shared counter for this task
    shared_counter_locked = 0
    # Create a Lock object. This is our "Do Not Disturb" sign.
    counter_lock = threading.Lock()

    def increment_counter_fixed(iterations):
        global shared_counter_locked
        for _ in range(iterations):
            # Acquire the lock BEFORE entering the critical section.
            # The 'with' statement is best: it automatically acquires and releases the lock.
            with counter_lock: 
                # --- This is the "critical section" now protected by the lock ---
                current_value = shared_counter_locked
                # No need for time.sleep here; the lock ensures no interference
                new_value = current_value + 1
                shared_counter_locked = new_value
                # --- Lock is automatically released when exiting this 'with' block ---

    print("\n--- Fixing the Race Condition with a Lock ---")
    num_threads_fixed = 5
    iterations_per_thread_fixed = 10000
    expected_total_fixed = num_threads_fixed * iterations_per_thread_fixed
    print(f"Expected final counter value (with lock): {expected_total_fixed}")

    threads_fixed = []
    for i in range(num_threads_fixed):
        thread = threading.Thread(target=increment_counter_fixed, args=(iterations_per_thread_fixed,))
        threads_fixed.append(thread)
        thread.start()

    for thread in threads_fixed:
        thread.join()

    print(f"Actual final counter value (with lock):   {shared_counter_locked}")

    if shared_counter_locked == expected_total_fixed:
        print("!!! Race condition PREVENTED: The actual value now matches the expected. !!!")
        print("The lock successfully made threads take turns.")
    else:
        print("Race condition still observed (something is wrong).")
    ```
2.  Save and run `threading_sync_lab.py`.
3.  **Expected Output/Observation:**
    *   The "Actual final counter value (with lock)" will now consistently match the "Expected final counter value (with lock)" (which is 50000).
    *   You will see the message: `!!! Race condition PREVENTED: The actual value now matches the expected. !!!`

### Task 1.3: Limit Concurrent Network Device Connections with a "Semaphore"

You'll simulate limiting the number of concurrent network connections to avoid overwhelming devices, which is a common requirement when working with **Cisco IOS XE routers sandbox** or other live equipment.

1.  In `threading_sync_lab.py`, add the following code:
    ```python
    # ... (previous code) ...

    import random # For simulating random connection times
    # from netmiko import ConnectHandler # Conceptual: This would be used for real connections

    print("\n--- Limiting Concurrent Connections to Network Devices with a Semaphore ---")

    # Create a Semaphore that allows a maximum of 3 concurrent "connections" (parking spots)
    max_concurrent_connections = 3
    connection_semaphore = threading.Semaphore(max_concurrent_connections)

    # Conceptual: Replace with your Cisco IOS XE Sandbox details if you have one
    # SANDBOX_USERNAME = "developer"
    # SANDBOX_PASSWORD = "Cisco123!"
    # SANDBOX_ENABLE_PASSWORD = "Cisco123!"

    def connect_to_device_limited(device_ip, thread_name):
        # Acquire the semaphore. This will block if all 'max_concurrent_connections' are busy.
        with connection_semaphore:
            # Indicate how many "slots" are currently available
            # _value is for observation only, don't rely on it for logic
            print(f"[{thread_name}] Acquiring connection to {device_ip}. "
                  f"Active slots: {connection_semaphore._value}")
            
            # --- CONCEPTUAL REAL-WORLD NETMIKO CONNECTION ---
            # If you have a Cisco IOS XE Sandbox, uncomment and fill in details:
            # device_params = {
            #     "device_type": "cisco_ios",
            #     "host": device_ip,
            #     "username": SANDBOX_USERNAME,
            #     "password": SANDBOX_PASSWORD,
            #     "secret": SANDBOX_ENABLE_PASSWORD,
            #     "port": 22, # Default SSH port
            # }
            # try:
            #     with ConnectHandler(**device_params) as net_connect:
            #         # Example: Get hostname from the device
            #         hostname_output = net_connect.send_command("show hostname")
            #         print(f"[{thread_name}] Connected to {device_ip}. Hostname: {hostname_output.strip()}")
            #         # Or collect logs: log_output = net_connect.send_command("show logging")
            # except Exception as e:
            #     print(f"[{thread_name}] Error connecting to {device_ip}: {e}")
            # --- END CONCEPTUAL REAL-WORLD NETMIKO CONNECTION ---

            time.sleep(random.uniform(1, 3)) # Simulate connection time
            
            print(f"[{thread_name}] Finished connection to {device_ip}. Releasing slot.")

    # Using example IPs that might be in a Cisco IOS XE Sandbox (replace if needed)
    device_ips_to_connect = [
        "10.10.20.40", # Cisco IOS XE Always-On Sandbox
        "10.10.20.41", # Another potential sandbox IP
        "10.10.20.42",
        "10.10.20.43",
        "10.10.20.44",
        "10.10.20.45",
        "10.10.20.46",
        "10.10.20.47",
        "10.10.20.48",
        "10.10.20.49",
    ] # 10 conceptual device IPs

    connection_threads = []
    for i, ip in enumerate(device_ips_to_connect):
        thread_name = f"DeviceConn-{i+1}" # Give each thread a unique name
        thread = threading.Thread(target=connect_to_device_limited, args=(ip, thread_name), name=thread_name)
        connection_threads.append(thread)
        thread.start() # Start the thread

    # Wait for all connection threads to finish
    for thread in connection_threads:
        thread.join()

    print("\nAll simulated network connections completed.")
    ```
2.  Save and run `threading_sync_lab.py`.
3.  **Expected Output/Observation:**
    *   You will see print statements indicating threads acquiring and finishing connections.
    *   Crucially, you should observe that at any given moment, the `Active slots` count will not go below 0 (meaning no more than `max_concurrent_connections` (3) threads are actively "connecting" at the same time).
    *   The output will show threads waiting for a slot to become available before proceeding. If you uncommented the Netmiko code and used real sandbox credentials, you would see actual hostnames or version outputs from the devices.

### Task 1.4: Thread-Safe Task Distribution for Log Collection with a "Queue"

A `queue.Queue` is perfect for when one part of your program (a "producer") collects data (like logs), and other parts (the "workers" or "consumers") pick up and process those tasks. The queue handles all the tricky synchronization automatically.

1.  In `threading_sync_lab.py`, add the following code:
    ```python
    # ... (previous code) ...

    import queue # This module provides the thread-safe Queue

    print("\n--- Thread-Safe Task Distribution for Log Collection with a Queue ---")

    # Create a thread-safe Queue. This is our conveyor belt.
    log_queue = queue.Queue()

    def log_collector_producer(device_ips):
        """
        This function simulates collecting logs from devices and putting them on the queue.
        It's the "producer."
        """
        for i, ip in enumerate(device_ips):
            # Conceptual: In a real scenario, this would use Netmiko to get logs:
            # from netmiko import ConnectHandler
            # device_params = {"device_type": "cisco_ios", "host": ip, ...}
            # try:
            #     with ConnectHandler(**device_params) as net_connect:
            #         raw_log = net_connect.send_command("show logging")
            #         log_queue.put({"device_ip": ip, "log_data": raw_log})
            #         print(f"[Collector] Added logs from {ip} to queue.")
            # except Exception as e:
            #     print(f"[Collector] Error collecting logs from {ip}: {e}")
            
            # Simulated log data
            simulated_log = f"Log from {ip}: Interface Gi0/{i} changed state to up at {time.ctime()}"
            log_queue.put({"device_ip": ip, "log_data": simulated_log})
            print(f"[Collector] Added simulated log from {ip} to queue.")
            time.sleep(0.2) # Simulate time to collect log

        print("[Collector] Finished collecting all logs.")

    def log_processor_worker(worker_id):
        """
        This function simulates processing log data from the queue.
        It's a "worker" or "consumer."
        """
        while True:
            # Get a log task from the queue. This will wait (block) if the queue is empty.
            log_task = log_queue.get() 
            
            # We use 'None' as a special signal to tell the worker to stop
            if log_task is None: 
                print(f"[Processor {worker_id}] Received stop signal. Exiting.")
                log_queue.task_done() # Tell the queue this 'None' task is done
                break # Exit the loop, stopping the worker thread
            
            device_ip = log_task["device_ip"]
            log_data = log_task["log_data"]
            
            print(f"[Processor {worker_id}] Analyzing log from {device_ip}: {log_data.splitlines()}...") # Print only first line
            # Conceptual: Here you would parse, analyze, or store the log data
            # e.g., if "down" in log_data: alert_team(device_ip)
            time.sleep(random.uniform(0.5, 1.5)) # Simulate log analysis time
            print(f"[Processor {worker_id}] Finished analyzing log from {device_ip}.")
            log_queue.task_done() # Tell the queue that this task is done

    # Using example IPs that might be in a Cisco IOS XE Sandbox
    log_device_ips = [
        "10.10.20.40", "10.10.20.41", "10.10.20.42", "10.10.20.43", "10.10.20.44"
    ]
    num_log_processors = 2 # We'll have 2 worker threads processing logs

    # 1. Start log processor worker threads
    processor_threads = []
    for i in range(num_log_processors):
        processor_thread = threading.Thread(target=log_processor_worker, args=(i+1,))
        processor_threads.append(processor_thread)
        processor_thread.start()

    # 2. Start log collector producer thread
    collector_thread = threading.Thread(target=log_collector_producer, args=(log_device_ips,))
    collector_thread.start()

    # 3. Wait for the collector to finish adding all logs to the queue
    collector_thread.join() 

    # 4. Add a 'None' signal for EACH processor to tell them to stop.
    for _ in range(num_log_processors):
        log_queue.put(None)

    # 5. Wait for all tasks in the queue (including the 'None' signals) to be marked as done.
    log_queue.join() 

    print("\nAll log collection and analysis tasks completed via queue.")
    ```
2.  Save and run `threading_sync_lab.py`.
3.  **Expected Output/Observation:**
    *   You will see messages from the `[Collector]` adding simulated logs to the queue.
    *   You will then see messages from the `[Processor X]` threads analyzing these logs.
    *   The order of processing by processors will be interleaved and might vary, but all logs will be processed.
    *   Finally, you'll see the processors receive their stop signals and the "All log collection and analysis tasks completed via queue." message.

---

## Lab 2: Doing Many Things at Once with `asyncio` (The Smart Manager)

**Objective:** Learn how to use Python's `asyncio` to make your scripts run I/O-bound tasks (like network operations) concurrently, without getting stuck waiting.

### Task 2.1: Basic `async` and `await` - Sequential vs. Concurrent

We'll start by seeing how `asyncio` functions (`coroutines`) work when run one after another, then how they can run at the same time.

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `asyncio_lab.py`.
3.  Add the following code:
    ```python
    # asyncio_lab.py
    import asyncio # The module for asynchronous programming
    import time    # For measuring time and basic delays
    import random  # For simulating variable delays
    # import asyncssh # Conceptual: This would be used for real async connections

    async def simulate_network_fetch(device_ip, delay):
        """
        This is a 'coroutine' (an async function).
        It simulates fetching data from a network device.
        'await asyncio.sleep(delay)' is a NON-BLOCKING pause.
        """
        print(f"[{time.strftime('%H:%M:%S')}] Starting fetch from {device_ip} (delay: {delay}s)...")
        # --- CONCEPTUAL REAL-WORLD ASYNCHRONOUS CONNECTION ---
        # If you have a Cisco IOS XE Sandbox, you might use asyncssh here:
        # try:
        #     async with asyncssh.connect(device_ip, username='developer', password='Cisco123!') as conn:
        #         result = await conn.run("show version")
        #         print(f"[{time.strftime('%H:%M:%S')}] Connected to {device_ip}. Version: {result.stdout.splitlines()}")
        #         return result.stdout.splitlines()
        # except Exception as e:
        #     print(f"[{time.strftime('%H:%M:%S')}] Error fetching from {device_ip}: {e}")
        #     return f"Error from {device_ip}"
        # --- END CONCEPTUAL REAL-WORLD ASYNCHRONOUS CONNECTION ---
        await asyncio.sleep(delay) 
        print(f"[{time.strftime('%H:%M:%S')}] Finished fetch from {device_ip}.")
        return f"Data from {device_ip}"

    async def main_sequential():
        """
        This main coroutine will run our network fetches one after another (sequentially).
        """
        print("--- Running Network Fetches Sequentially (Blocking Simulation) ---")
        start_time = time.time()

        # We 'await' each fetch. This means the program will fully wait for the first one
        # to complete before starting the second one.
        result1 = await simulate_network_fetch("192.168.1.1", 3) # Will wait 3 seconds
        result2 = await simulate_network_fetch("192.168.1.2", 2) # Will wait 2 seconds AFTER the first one finishes

        print(f"\nSequential results: {result1}, {result2}")
        end_time = time.time()
        print(f"Total sequential time: {end_time - start_time:.2f} seconds")

    # This is the standard way to start an asyncio program.
    # It runs the 'main_sequential' coroutine and manages the asyncio event loop.
    if __name__ == "__main__":
        asyncio.run(main_sequential())
    ```
4.  Save and run `asyncio_lab.py`.
5.  **Expected Output/Observation:**
    *   The output will clearly show the first fetch starting, then finishing, *then* the second fetch starting and finishing.
    *   The "Total sequential time" will be approximately the sum of the individual delays (3s + 2s = around 5 seconds).
    ```
    --- Running Network Fetches Sequentially (Blocking Simulation) ---
    [HH:MM:SS] Starting fetch from 192.168.1.1 (delay: 3s)...
    [HH:MM:SS] Finished fetch from 192.168.1.1.
    [HH:MM:SS] Starting fetch from 192.168.1.2 (delay: 2s)...
    [HH:MM:SS] Finished fetch from 192.168.1.2.

    Sequential results: Data from 192.168.1.1, Data from 192.168.1.2
    Total sequential time: 5.xx seconds
    ```

### Task 2.2: Running Multiple Coroutines Concurrently with `asyncio.gather`

Now, we'll tell `asyncio` to start all the network fetches at the same time and wait for them all to finish. This is where the magic of concurrency happens for **concurrent network device connections**!

1.  In the same `asyncio_lab.py` file, add the following coroutine:
    ```python
    # ... (previous code) ...

    async def main_concurrent():
        """
        This main coroutine will run our network fetches concurrently (at the same time).
        """
        print("\n--- Running Network Fetches Concurrently (Non-Blocking Simulation) ---")
        start_time = time.time()

        # 1. Create coroutine objects (these are just "plans" for tasks, they don't run yet)
        task1 = simulate_network_fetch("192.168.1.10", 3)
        task2 = simulate_network_fetch("192.168.1.11", 2)
        task3 = simulate_network_fetch("192.168.1.12", 4)

        # 2. Use asyncio.gather() to run all these "plans" concurrently.
        #    It starts them all, and then waits for the *longest* one to finish.
        results = await asyncio.gather(task1, task2, task3)

        print(f"\nConcurrent results: {results}")
        end_time = time.time()
        print(f"Total concurrent time: {end_time - start_time:.2f} seconds")

    # IMPORTANT: Modify the '__main__' block at the bottom of your file
    # to run this new concurrent example instead of the sequential one.
    if __name__ == "__main__":
        # asyncio.run(main_sequential()) # Comment out or remove this line
        asyncio.run(main_concurrent()) # <--- UNCOMMENT THIS LINE
    ```
2.  Save and run `asyncio_lab.py`.
3.  **Expected Output/Observation:**
    *   You will see "Starting fetch..." messages for all three devices appear almost immediately one after another.
    *   Then, "Finished fetch..." messages will appear as each task completes, likely out of order (shortest delay finishes first).
    *   The "Total concurrent time" will be approximately the duration of the *longest* task (which is 4 seconds in this case), not the sum.
    ```
    --- Running Network Fetches Concurrently (Non-Blocking Simulation) ---
    [HH:MM:SS] Starting fetch from 192.168.1.10 (delay: 3s)...
    [HH:MM:SS] Starting fetch from 192.168.1.11 (delay: 2s)...
    [HH:MM:SS] Starting fetch from 192.168.1.12 (delay: 4s)...
    [HH:MM:SS] Finished fetch from 192.168.1.11.
    [HH:MM:SS] Finished fetch from 192.168.1.10.
    [HH:MM:SS] Finished fetch from 192.168.1.12.

    Concurrent results: ['Data from 192.168.1.10', 'Data from 192.168.1.11', 'Data from 192.168.1.12']
    Total concurrent time: 4.xx seconds
    ```

### Task 2.3: Concurrent Device Configuration Simulation

Let's apply this to a more realistic network automation scenario: configuring multiple devices concurrently.

1.  In `asyncio_lab.py`, add the following coroutines:
    ```python
    # ... (previous code) ...

    async def configure_device(device_ip, config_commands):
        """
        Simulates sending configuration commands to a device.
        """
        print(f"[{time.strftime('%H:%M:%S')}] Configuring {device_ip}...")
        # --- CONCEPTUAL REAL-WORLD ASYNCHRONOUS CONFIGURATION ---
        # If you have a Cisco IOS XE Sandbox, you might use asyncssh here:
        # try:
        #     async with asyncssh.connect(device_ip, username='developer', password='Cisco123!') as conn:
        #         await conn.run("config t")
        #         for cmd in config_commands:
        #             await conn.run(cmd)
        #         await conn.run("end")
        #     print(f"[{time.strftime('%H:%M:%S')}] Configuration successful for {device_ip}.")
        #     return f"Configured {device_ip} with {len(config_commands)} commands."
        # except Exception as e:
        #     print(f"[{time.strftime('%H:%M:%S')}] Error configuring {device_ip}: {e}")
        #     return f"Error configuring {device_ip}"
        # --- END CONCEPTUAL REAL-WORLD ASYNCHRONOUS CONFIGURATION ---
        await asyncio.sleep(random.uniform(1, 3)) 
        print(f"[{time.strftime('%H:%M:%S')}] Configuration complete for {device_ip}.")
        return f"Configured {device_ip} with {len(config_commands)} commands."

    async def main_config_automation():
        """
        This coroutine orchestrates concurrent configuration of multiple devices.
        """
        print("\n--- Concurrent Device Configuration Automation ---")
        start_time = time.time()

        # Using example IPs that might be in a Cisco IOS XE Sandbox (replace if needed)
        devices_to_configure = {
            "10.10.20.40": ["hostname R1-LAB", "interface Loopback0", "ip address 10.0.0.1 255.255.255.255"],
            "10.10.20.41": ["hostname R2-LAB", "interface GigabitEthernet0/1", "no shutdown"],
            "10.10.20.42": ["hostname R3-LAB", "line con 0", "logging synchronous"],
            "10.10.20.43": ["hostname R4-LAB", "interface Vlan1", "ip address 192.168.10.4 255.255.255.0"]
        }

        config_tasks = []
        for ip, commands in devices_to_configure.items():
            # Create a list of coroutine "plans" for each device
            config_tasks.append(configure_device(ip, commands))

        # Run all configuration tasks concurrently
        config_results = await asyncio.gather(*config_tasks)

        print("\nAll device configurations completed:")
        for res in config_results:
            print(f"- {res}")

        end_time = time.time()
        print(f"Total configuration time: {end_time - start_time:.2f} seconds")

    # IMPORTANT: Modify the '__main__' block at the bottom of your file
    # to run this new example.
    if __name__ == "__main__":
        # asyncio.run(main_sequential())
        # asyncio.run(main_concurrent())
        asyncio.run(main_config_automation()) # <--- UNCOMMENT THIS LINE
    ```
2.  Save and run `asyncio_lab.py`.
3.  **Expected Output/Observation:**
    *   You will see "Configuring..." messages for all devices appear quickly, interleaved with each other.
    *   "Configuration complete..." messages will appear as each device's simulated configuration finishes, likely out of order.
    *   The total time will be much less than if you configured each device one by one (it will be close to the time of the longest single configuration, which is about 3 seconds in this simulation).
    ```
    --- Concurrent Device Configuration Automation ---
    [HH:MM:SS] Configuring 10.10.20.40...
    [HH:MM:SS] Configuring 10.10.20.41...
    [HH:MM:SS] Configuring 10.10.20.42...
    [HH:MM:SS] Configuring 10.10.20.43...
    [HH:MM:SS] Configuration complete for 10.10.20.41.
    [HH:MM:SS] Configuration complete for 10.10.20.40.
    [HH:MM:SS] Configuration complete for 10.10.20.43.
    [HH:MM:SS] Configuration complete for 10.10.20.42.

    All device configurations completed:
    - Configured 10.10.20.40 with 3 commands.
    - Configured 10.10.20.41 with 3 commands.
    - Configured 10.10.20.42 with 3 commands.
    - Configured 10.10.20.43 with 3 commands.
    Total configuration time: 2.xx seconds
    ```

### Task 2.4: Concurrent Log Collection and Real-time Monitoring Simulation

This task demonstrates how `asyncio` can be used for efficiently collecting logs or monitoring status from multiple devices simultaneously, crucial for **real-time monitoring** and **log collection**.

1.  In `asyncio_lab.py`, add the following coroutine:
    ```python
    # ... (previous code) ...

    async def fetch_device_status(device_ip):
        """
        Simulates fetching status (e.g., interface status or CPU utilization) from a device.
        """
        print(f"[{time.strftime('%H:%M:%S')}] Monitoring {device_ip} status...")
        # --- CONCEPTUAL REAL-WORLD ASYNCHRONOUS MONITORING ---
        # If you have a Cisco IOS XE Sandbox, you might use asyncssh here:
        # try:
        #     async with asyncssh.connect(device_ip, username='developer', password='Cisco123!') as conn:
        #         status_output = await conn.run("show ip interface brief")
        #         # Or for logs: log_output = await conn.run("show logging | include %UP%")
        #         return {device_ip: status_output.stdout.splitlines()}
        # except Exception as e:
        #     print(f"[{time.strftime('%H:%M:%S')}] Error monitoring {device_ip}: {e}")
        #     return {device_ip: "Error"}
        # --- END CONCEPTUAL REAL-WORLD ASYNCHRONOUS MONITORING ---
        delay = random.uniform(0.5, 2.5) # Simulate variable monitoring time
        await asyncio.sleep(delay)
        status_data = f"Interface Gi0/1 on {device_ip} is {'up' if random.random() > 0.3 else 'down'}"
        print(f"[{time.strftime('%H:%M:%S')}] Finished monitoring {device_ip}.")
        return {device_ip: status_data}

    async def main_monitoring_and_logs():
        """
        Orchestrates concurrent monitoring and log collection simulation.
        """
        print("\n--- Concurrent Log Collection & Real-time Monitoring Simulation ---")
        start_time = time.time()

        # Using example IPs that might be in a Cisco IOS XE Sandbox (replace if needed)
        devices_to_monitor = [
            "10.10.20.40",
            "10.10.20.41",
            "10.10.20.42",
            "10.10.20.43",
            "10.10.20.44",
            "10.10.20.45",
            "10.10.20.46",
            "10.10.20.47",
        ] # 8 conceptual devices

        monitor_tasks = []
        for ip in devices_to_monitor:
            monitor_tasks.append(fetch_device_status(ip))

        # Run all monitoring tasks concurrently
        monitoring_results = await asyncio.gather(*monitor_tasks)

        print("\n--- All Monitoring Results ---")
        for res in monitoring_results:
            for ip, status in res.items():
                print(f"  {ip}: {status}")

        end_time = time.time()
        print(f"\nTotal monitoring time: {end_time - start_time:.2f} seconds")

    # IMPORTANT: Modify the '__main__' block at the bottom of your file
    # to run this new example.
    if __name__ == "__main__":
        # asyncio.run(main_sequential())
        # asyncio.run(main_concurrent())
        # asyncio.run(main_config_automation())
        asyncio.run(main_monitoring_and_logs()) # <--- UNCOMMENT THIS LINE
    ```
2.  Save and run `asyncio_lab.py`.
3.  **Expected Output/Observation:**
    *   You will see "Monitoring..." messages for all devices appear quickly.
    *   "Finished monitoring..." messages will appear as each device's simulated status fetch completes, likely out of order.
    *   The total time will be significantly less than if you monitored each device sequentially, demonstrating the efficiency for large-scale **log collection** and **real-time monitoring** tasks.
    ```
    --- Concurrent Log Collection & Real-time Monitoring Simulation ---
    [HH:MM:SS] Monitoring 10.10.20.40 status...
    [HH:MM:SS] Monitoring 10.10.20.41 status...
    [HH:MM:SS] Monitoring 10.10.20.42 status...
    [HH:MM:SS] Monitoring 10.10.20.43 status...
    [HH:MM:SS] Monitoring 10.10.20.44 status...
    [HH:MM:SS] Monitoring 10.10.20.45 status...
    [HH:MM:SS] Monitoring 10.10.20.46 status...
    [HH:MM:SS] Monitoring 10.10.20.47 status...
    [HH:MM:SS] Finished monitoring 10.10.20.42.
    [HH:MM:SS] Finished monitoring 10.10.20.45.
    [HH:MM:SS] Finished monitoring 10.10.20.40.
    [HH:MM:SS] Finished monitoring 10.10.20.47.
    [HH:MM:SS] Finished monitoring 10.10.20.44.
    [HH:MM:SS] Finished monitoring 10.10.20.41.
    [HH:MM:SS] Finished monitoring 10.10.20.43.
    [HH:MM:SS] Finished monitoring 10.10.20.46.

    --- All Monitoring Results ---
      10.10.20.40: Interface Gi0/1 on 10.10.20.40 is up
      10.10.20.41: Interface Gi0/1 on 10.10.20.41 is up
      10.10.20.42: Interface Gi0/1 on 10.10.20.42 is down
      10.10.20.43: Interface Gi0/1 on 10.10.20.43 is up
      10.10.20.44: Interface Gi0/1 on 10.10.20.44 is up
      10.10.20.45: Interface Gi0/1 on 10.10.20.45 is down
      10.10.20.46: Interface Gi0/1 on 10.10.20.46 is up
      10.10.20.47: Interface Gi0/1 on 10.10.20.47 is up

    Total monitoring time: 2.xx seconds
    ```

---

## Conclusion

You've now completed the labs for Data Synchronization and Asynchronous Mechanisms! You've experienced the challenges of race conditions and learned how to mitigate them with `threading.Lock` and `threading.Semaphore`. More importantly for network automation, you've seen the power of `asyncio` to perform I/O-bound tasks concurrently, leading to significant time savings, especially for **concurrent network device connections**, **log collection**, and **real-time monitoring** on devices like **Cisco IOS XE routers sandbox**.

These are fundamental concepts that will empower you to write highly efficient and scalable network automation solutions.

**Keep Learning!**

---