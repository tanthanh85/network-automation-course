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
*   Use `threading.Semaphore` to limit concurrent access.
*   Implement `queue.Queue` for thread-safe communication.
*   Write and execute basic `asyncio` coroutines.
*   Run multiple `asyncio` tasks concurrently using `asyncio.gather`.
*   Compare synchronous, threaded, and asynchronous approaches conceptually.

**Prerequisites:**
*   Completion of Module 1 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).

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

### Task 1.3: Limit Concurrent Access with a "Semaphore" (Limited Parking Spots)

Imagine you have a network device that can only handle 3 connections at once. A `threading.Semaphore` is perfect for this. It's like a parking lot with a limited number of spots. Threads can only proceed if there's a free spot.

1.  In `threading_sync_lab.py`, add the following code:
    ```python
    # ... (previous code) ...

    import random # For simulating random connection times

    print("\n--- Limiting Concurrent Connections with a Semaphore ---")

    # Create a Semaphore that allows a maximum of 3 concurrent "connections" (parking spots)
    max_concurrent_connections = 3
    connection_semaphore = threading.Semaphore(max_concurrent_connections)

    def simulate_network_connection(device_ip, thread_name):
        # Acquire the semaphore. This will block if all 'max_concurrent_connections' are busy.
        with connection_semaphore:
            # Indicate how many "slots" are currently available
            # _value is for observation only, don't rely on it for logic
            print(f"[{thread_name}] Acquiring connection to {device_ip}. "
                  f"Active slots: {connection_semaphore._value}")
            
            # Simulate connection time (random between 1 and 3 seconds)
            connection_time = random.uniform(1, 3) 
            time.sleep(connection_time)
            
            print(f"[{thread_name}] Finished connection to {device_ip}. Releasing slot.")

    device_ips_to_connect = [f"192.168.1.{i}" for i in range(100, 110)] # A list of 10 fake device IPs

    connection_threads = []
    for i, ip in enumerate(device_ips_to_connect):
        thread_name = f"DeviceConn-{i+1}" # Give each thread a unique name
        thread = threading.Thread(target=simulate_network_connection, args=(ip, thread_name), name=thread_name)
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
    *   The output will show threads waiting for a slot to become available before proceeding.

### Task 1.4: Thread-Safe Communication with a "Queue" (Safe Conveyor Belt)

A `queue.Queue` is perfect for when one part of your program (a "producer") creates tasks, and other parts (the "workers" or "consumers") pick up and process those tasks. The queue handles all the tricky synchronization automatically.

1.  In `threading_sync_lab.py`, add the following code:
    ```python
    # ... (previous code) ...

    import queue # This module provides the thread-safe Queue

    print("\n--- Thread-Safe Communication with a Queue ---")

    # Create a thread-safe Queue. This is our conveyor belt.
    task_queue = queue.Queue()

    def producer(num_tasks):
        """
        This function simulates creating configuration tasks and putting them on the queue.
        It's the "producer."
        """
        for i in range(num_tasks):
            config_data = f"interface Loopback{i}\n ip address 10.0.0.{i} 255.255.255.255"
            task_queue.put(config_data) # Put the config task onto the queue
            print(f"[Producer] Added: {config_data.splitlines()}...") # Print only first line
            time.sleep(0.1) # Simulate time to generate config
        print("[Producer] Finished adding tasks.")

    def worker(worker_id):
        """
        This function simulates processing configuration tasks from the queue.
        It's a "worker" or "consumer."
        """
        while True:
            # Get a task from the queue. This will wait (block) if the queue is empty.
            config_task = task_queue.get() 
            
            # We use 'None' as a special signal to tell the worker to stop
            if config_task is None: 
                print(f"[Worker {worker_id}] Received stop signal. Exiting.")
                task_queue.task_done() # Tell the queue that this 'None' task is done
                break # Exit the loop, stopping the worker thread
            
            print(f"[Worker {worker_id}] Processing: {config_task.splitlines()}...") # Print only first line
            time.sleep(random.uniform(0.5, 1.5)) # Simulate applying config to a device
            print(f"[Worker {worker_id}] Finished: {config_task.splitlines()}...") # Print only first line
            task_queue.task_done() # Tell the queue this task is done

    num_tasks_to_produce = 10 # We want to generate 10 config tasks
    num_workers = 3 # We'll have 3 worker threads processing these tasks

    # 1. Start the worker threads
    worker_threads = []
    for i in range(num_workers):
        worker_thread = threading.Thread(target=worker, args=(i+1,))
        worker_threads.append(worker_thread)
        worker_thread.start()

    # 2. Start the producer thread
    producer_thread = threading.Thread(target=producer, args=(num_tasks_to_produce,))
    producer_thread.start()

    # 3. Wait for the producer to finish adding all configs to the queue
    producer_thread.join() 

    # 4. Add a 'None' signal for EACH worker to tell them to stop.
    #    This is important so all workers eventually exit their loops.
    for _ in range(num_workers):
        task_queue.put(None)

    # 5. Wait for all tasks in the queue (including the 'None' signals) to be marked as done.
    #    This ensures all workers have finished processing their tasks before the main program exits.
    task_queue.join() 

    print("\nAll configuration tasks completed via queue.")
    ```
2.  Save and run `threading_sync_lab.py`.
3.  **Expected Output/Observation:**
    *   You will see messages from the `[Producer]` adding tasks to the queue.
    *   You will then see messages from the `[Worker X]` threads processing these tasks.
    *   The order of processing by workers will be interleaved and might vary, but all 10 tasks will be processed.
    *   Finally, you'll see the workers receive their stop signals and the "All configuration tasks completed via queue." message.

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

    async def simulate_network_fetch(device_ip, delay):
        """
        This is a 'coroutine' (an async function).
        It simulates fetching data from a network device.
        'await asyncio.sleep(delay)' is a NON-BLOCKING pause.
        """
        print(f"[{time.strftime('%H:%M:%S')}] Starting fetch from {device_ip} (delay: {delay}s)...")
        # When 'await' is used, this coroutine pauses and tells the asyncio manager:
        # "I'm waiting for {delay} seconds. While I wait, you can run other tasks!"
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

Now, we'll tell `asyncio` to start all the network fetches at the same time and wait for them all to finish. This is where the magic of concurrency happens!

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
        # Simulate variable config time for each device
        await asyncio.sleep(random.uniform(1, 3)) 
        print(f"[{time.strftime('%H:%M:%S')}] Configuration complete for {device_ip}.")
        return f"Configured {device_ip} with {len(config_commands)} commands."

    async def main_config_automation():
        """
        This coroutine orchestrates concurrent configuration of multiple devices.
        """
        print("\n--- Concurrent Device Configuration Automation ---")
        start_time = time.time()

        devices_to_configure = {
            "192.168.10.1": ["hostname R1", "interface Loopback0", "ip address 10.0.0.1 255.255.255.255"],
            "192.168.10.2": ["hostname R2", "interface GigabitEthernet0/1", "no shutdown"],
            "192.168.10.3": ["hostname R3", "line con 0", "logging synchronous"],
            "192.168.10.4": ["hostname R4", "interface Vlan1", "ip address 192.168.10.4 255.255.255.0"]
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
    [HH:MM:SS] Configuring 192.168.10.1...
    [HH:MM:SS] Configuring 192.168.10.2...
    [HH:MM:SS] Configuring 192.168.10.3...
    [HH:MM:SS] Configuring 192.168.10.4...
    [HH:MM:SS] Configuration complete for 192.168.10.2.
    [HH:MM:SS] Configuration complete for 192.168.10.1.
    [HH:MM:SS] Configuration complete for 192.168.10.4.
    [HH:MM:SS] Configuration complete for 192.168.10.3.

    All device configurations completed:
    - Configured 192.168.10.1 with 3 commands.
    - Configured 192.168.10.2 with 3 commands.
    - Configured 192.168.10.3 with 3 commands.
    - Configured 192.168.10.4 with 3 commands.
    Total configuration time: 2.xx seconds
    ```

---

## Conclusion

You've now completed the labs for Data Synchronization and Asynchronous Mechanisms! You've experienced the challenges of race conditions and learned how to mitigate them with `threading.Lock` and `threading.Semaphore`. More importantly for network automation, you've seen the power of `asyncio` to perform I/O-bound tasks concurrently, leading to significant time savings.

These are fundamental concepts that will empower you to write highly efficient and scalable network automation solutions.

**Keep Learning!**

---