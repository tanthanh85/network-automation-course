# Python Basics for Network Automation: Module 2 Lab Guide

## Data Synchronization and Asynchronous Mechanisms in Python - Hands-on Exercises

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

## Lab 1: Data Synchronization with Threading

**Objective:** Observe race conditions and use `threading.Lock` to protect shared resources.

### Task 1.1: Observe a Race Condition

In this task, you'll create a simple multi-threaded program that increments a shared counter without any synchronization, demonstrating a race condition.

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `threading_sync_lab.py`.
3.  Add the following code:
    ```python
    # threading_sync_lab.py
    import threading
    import time

    # Shared global variable
    shared_counter = 0

    def increment_counter(iterations):
        global shared_counter
        for _ in range(iterations):
            # Read, modify, write - this is a critical section
            current_value = shared_counter
            time.sleep(0.0001) # Simulate some work/delay
            new_value = current_value + 1
            shared_counter = new_value

    print("--- Observing Race Condition ---")
    num_threads = 5
    iterations_per_thread = 10000 # Each thread increments 10,000 times
    expected_total = num_threads * iterations_per_thread

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=increment_counter, args=(iterations_per_thread,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join() # Wait for all threads to complete

    print(f"Expected final counter value: {expected_total}")
    print(f"Actual final counter value:   {shared_counter}")

    if shared_counter != expected_total:
        print("!!! Race condition observed: Actual value is less than expected. !!!")
    else:
        print("No race condition observed (this is rare, try running multiple times).")

    ```
4.  Save and run `threading_sync_lab.py`.
5.  Run it multiple times. You should consistently see the "Race condition observed" message, where the actual final value is less than the expected total. This is because threads are interfering with each other's updates to `shared_counter`.

### Task 1.2: Fix Race Condition with `threading.Lock`

Now, you'll use a `threading.Lock` to protect the `shared_counter` and ensure atomic updates.

1.  In the same `threading_sync_lab.py` file, modify the code as follows:
    ```python
    # ... (previous code) ...

    # Shared global variable
    shared_counter_locked = 0
    # Create a Lock object
    counter_lock = threading.Lock()

    def increment_counter_locked(iterations):
        global shared_counter_locked
        for _ in range(iterations):
            # Acquire the lock before entering the critical section
            with counter_lock: # 'with' statement ensures lock is released
                current_value = shared_counter_locked
                # time.sleep(0.0001) # No need for sleep here, lock protects it
                new_value = current_value + 1
                shared_counter_locked = new_value

    print("\n--- Fixing Race Condition with Lock ---")
    num_threads_locked = 5
    iterations_per_thread_locked = 10000
    expected_total_locked = num_threads_locked * iterations_per_thread_locked

    threads_locked = []
    for i in range(num_threads_locked):
        thread = threading.Thread(target=increment_counter_locked, args=(iterations_per_thread_locked,))
        threads_locked.append(thread)
        thread.start()

    for thread in threads_locked:
        thread.join()

    print(f"Expected final counter value (with lock): {expected_total_locked}")
    print(f"Actual final counter value (with lock):   {shared_counter_locked}")

    if shared_counter_locked == expected_total_locked:
        print("!!! Race condition prevented: Actual value matches expected. !!!")
    else:
        print("Race condition still observed (something is wrong).")
    ```
2.  Save and run `threading_sync_lab.py`.
3.  Run it multiple times. You should now consistently see the "Race condition prevented" message, with the actual value matching the expected total.

### Task 1.3: Limit Concurrent Access with `threading.Semaphore`

You'll simulate limiting the number of concurrent network connections using a `threading.Semaphore`.

1.  In `threading_sync_lab.py`, add the following code:
    ```python
    # ... (previous code) ...

    import random

    # Create a Semaphore that allows a maximum of 3 concurrent "connections"
    max_concurrent_connections = 3
    connection_semaphore = threading.Semaphore(max_concurrent_connections)

    def simulate_network_connection(device_ip):
        # Acquire the semaphore. This will block if max_concurrent_connections are already active.
        with connection_semaphore:
            # Indicate how many "slots" are left
            print(f"[{threading.current_thread().name}] Acquiring connection to {device_ip}. Available slots: {connection_semaphore._value}")
            
            # Simulate connection time
            connection_time = random.uniform(1, 3) # Random time between 1 and 3 seconds
            time.sleep(connection_time)
            
            print(f"[{threading.current_thread().name}] Finished connection to {device_ip}. Releasing slot.")

    print("\n--- Limiting Concurrent Connections with Semaphore ---")
    device_ips_to_connect = [f"192.168.1.{i}" for i in range(100, 110)] # 10 devices

    connection_threads = []
    for i, ip in enumerate(device_ips_to_connect):
        thread_name = f"ConnThread-{i+1}"
        thread = threading.Thread(target=simulate_network_connection, args=(ip,), name=thread_name)
        connection_threads.append(thread)
        thread.start()

    for thread in connection_threads:
        thread.join()

    print("\nAll simulated network connections completed.")
    ```
2.  Save and run `threading_sync_lab.py`. Observe how the `Available slots` count changes and how only a maximum of 3 connections are active at any given time.

### Task 1.4: Thread-Safe Communication with `queue.Queue`

You'll implement a simple producer-consumer pattern using `queue.Queue` for thread-safe task distribution.

1.  In `threading_sync_lab.py`, add the following code:
    ```python
    # ... (previous code) ...

    import queue

    print("\n--- Thread-Safe Communication with Queue ---")

    # Create a thread-safe Queue
    task_queue = queue.Queue()

    def device_config_producer(num_configs):
        for i in range(num_configs):
            config_data = f"interface Loopback{i}\n ip address 10.0.0.{i} 255.255.255.255"
            task_queue.put(config_data)
            print(f"[Producer] Added config for Loopback{i} to queue.")
            time.sleep(0.1) # Simulate time to generate config

    def config_worker(worker_id):
        while True:
            config_task = task_queue.get() # Blocks until an item is available
            if config_task is None: # Check for sentinel value to stop worker
                print(f"[Worker {worker_id}] Received stop signal. Exiting.")
                task_queue.task_done() # Mark the sentinel as done
                break
            
            print(f"[Worker {worker_id}] Processing config: {config_task.splitlines()}...")
            time.sleep(random.uniform(0.5, 1.5)) # Simulate applying config
            print(f"[Worker {worker_id}] Finished processing config.")
            task_queue.task_done() # Mark the task as done

    num_configs_to_generate = 10
    num_workers = 3

    # Start producer thread
    producer_thread = threading.Thread(target=device_config_producer, args=(num_configs_to_generate,))
    producer_thread.start()

    # Start worker threads
    worker_threads = []
    for i in range(num_workers):
        worker_thread = threading.Thread(target=config_worker, args=(i+1,))
        worker_threads.append(worker_thread)
        worker_thread.start()

    producer_thread.join() # Wait for producer to finish adding all configs

    # Add a 'None' sentinel for each worker to signal them to stop
    for _ in range(num_workers):
        task_queue.put(None)

    # Wait for all tasks in the queue to be processed (including sentinels)
    task_queue.join() 

    print("\nAll configuration tasks completed via queue.")
    ```
2.  Save and run `threading_sync_lab.py`. Observe how the producer adds tasks and multiple workers process them concurrently.

---

## Lab 2: Asynchronous Programming with `asyncio`

**Objective:** Write and execute basic `asyncio` coroutines for non-blocking I/O operations.

### Task 2.1: Basic `async` and `await`

You'll create simple coroutines and run them using `asyncio.run()`.

1.  Activate your `na_env` virtual environment.
2.  Create a new Python file named `asyncio_lab.py`.
3.  Add the following code:
    ```python
    # asyncio_lab.py
    import asyncio
    import time

    async def simulate_network_fetch(device_ip, delay):
        """
        A coroutine that simulates fetching data from a network device.
        It uses asyncio.sleep() to simulate non-blocking I/O.
        """
        print(f"[{time.strftime('%H:%M:%S')}] Starting fetch from {device_ip} (delay: {delay}s)...")
        await asyncio.sleep(delay) # This is a non-blocking pause
        print(f"[{time.strftime('%H:%M:%S')}] Finished fetch from {device_ip}.")
        return f"Data from {device_ip}"

    async def main_sequential():
        """
        Main coroutine to run network fetches sequentially.
        """
        print("--- Running Network Fetches Sequentially (Blocking Simulation) ---")
        start_time = time.time()

        result1 = await simulate_network_fetch("192.168.1.1", 3) # Will wait 3 seconds
        result2 = await simulate_network_fetch("192.168.1.2", 2) # Will wait 2 seconds after the first one finishes

        print(f"\nSequential results: {result1}, {result2}")
        end_time = time.time()
        print(f"Total sequential time: {end_time - start_time:.2f} seconds")

    # To run the sequential example:
    if __name__ == "__main__":
        asyncio.run(main_sequential())
    ```
4.  Save and run `asyncio_lab.py`. Observe that the total time is approximately the sum of the individual delays (3s + 2s = 5s). This demonstrates the blocking nature of `await` when used sequentially.

### Task 2.2: Running Multiple Coroutines Concurrently with `asyncio.gather`

Now, you'll run the same network fetch coroutines concurrently using `asyncio.gather`.

1.  In the same `asyncio_lab.py` file, add the following coroutine:
    ```python
    # ... (previous code) ...

    async def main_concurrent():
        """
        Main coroutine to run network fetches concurrently.
        """
        print("\n--- Running Network Fetches Concurrently (Non-Blocking Simulation) ---")
        start_time = time.time()

        # Create coroutine objects (they don't start executing yet)
        task1 = simulate_network_fetch("192.168.1.10", 3)
        task2 = simulate_network_fetch("192.168.1.11", 2)
        task3 = simulate_network_fetch("192.168.1.12", 4)

        # Run tasks concurrently and wait for all of them to complete
        results = await asyncio.gather(task1, task2, task3)

        print(f"\nConcurrent results: {results}")
        end_time = time.time()
        print(f"Total concurrent time: {end_time - start_time:.2f} seconds")

    # To run the concurrent example, modify the __main__ block:
    if __name__ == "__main__":
        # asyncio.run(main_sequential()) # Comment out or remove this line
        asyncio.run(main_concurrent()) # Run the concurrent example
    ```
2.  Save and run `asyncio_lab.py`.
3.  Observe that the total time is now approximately the duration of the *longest* task (4 seconds), because they are running concurrently.

### Task 2.3: Concurrent Device Configuration Simulation

You'll expand on the concurrent fetching to simulate configuring multiple devices.

1.  In `asyncio_lab.py`, add the following coroutines:
    ```python
    # ... (previous code) ...

    async def configure_device(device_ip, config_commands):
        """
        Simulates sending configuration commands to a device.
        """
        print(f"[{time.strftime('%H:%M:%S')}] Configuring {device_ip}...")
        await asyncio.sleep(random.uniform(1, 3)) # Simulate variable config time
        print(f"[{time.strftime('%H:%M:%S')}] Configuration complete for {device_ip}.")
        return f"Configured {device_ip} with {len(config_commands)} commands."

    async def main_config_automation():
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
            config_tasks.append(configure_device(ip, commands))

        # Run all configuration tasks concurrently
        config_results = await asyncio.gather(*config_tasks)

        print("\nAll device configurations completed:")
        for res in config_results:
            print(f"- {res}")

        end_time = time.time()
        print(f"Total configuration time: {end_time - start_time:.2f} seconds")

    # Modify the __main__ block to run this new example:
    if __name__ == "__main__":
        # asyncio.run(main_sequential())
        # asyncio.run(main_concurrent())
        asyncio.run(main_config_automation())
    ```
2.  Save and run `asyncio_lab.py`. You'll see the configuration messages interleaved, and the total time will be dictated by the longest individual configuration simulation.

---

## Conclusion

You've now completed the labs for Data Synchronization and Asynchronous Mechanisms! You've experienced the challenges of race conditions and learned how to mitigate them with `threading.Lock` and `threading.Semaphore`. More importantly for network automation, you've seen the power of `asyncio` to perform I/O-bound tasks concurrently, leading to significant time savings.

These are fundamental concepts that will empower you to write highly efficient and scalable network automation solutions.

**Keep Learning!**

---