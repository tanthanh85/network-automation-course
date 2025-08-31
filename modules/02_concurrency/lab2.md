# Lab 2 – Data Synchronization and Asynchronous Mechanisms in Python

> 🕒 Estimated Time: 2 hours

## 🎯 Objective
This lab introduces learners to concurrent programming using Python in a network automation context, using **VSCode** for code development. You will:

- Write multithreaded and asynchronous scripts to simulate concurrent device connections
- Practice real-world applications like log collection and device polling
- Get hands-on with Python’s `threading`, `concurrent.futures`, and `asyncio`

---

## 🔧 Prerequisites
- Python 3.10+ installed
- Virtual environment created and activated (see Lab 1)
- VSCode with Python extension installed

> Ensure VSCode is opened in your `lab2` folder.

```bash
mkdir -p network-automation-nasp/lab2
cd network-automation-nasp/lab2
code .  # Opens VSCode in this folder
```

---

## 🧪 Task 1: Simulate CLI Device Access Using `threading`

### Step 1: Create a new file
In VSCode, click **File > New File**, save it as:
```
cli_threading_simulation.py
```

### Step 2: Add this code
```python
import threading
import time

def connect_device(device):
    print(f"Connecting to {device}...")
    time.sleep(2)
    print(f"{device} connected successfully.")

devices = ["R1", "R2", "SW1", "SW2"]
threads = []

for device in devices:
    thread = threading.Thread(target=connect_device, args=(device,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print("All devices connected.")
```

### Step 3: Run the script
In VSCode:
- Right-click in the editor → **Run Python File in Terminal**

### ✅ Expected Output
```
Connecting to R1...
Connecting to R2...
Connecting to SW1...
Connecting to SW2...
R1 connected successfully.
...
All devices connected.
```

---

## 🧪 Task 2: Use `asyncio` for REST-like Polling

### Step 1: Create a new file
```
async_polling_sim.py
```

### Step 2: Paste this code
```python
import asyncio

async def poll_device(device):
    print(f"Polling {device}...")
    await asyncio.sleep(1)
    print(f"{device} responded.")

async def main():
    devices = ["SW1", "SW2", "R1", "R2"]
    await asyncio.gather(*(poll_device(d) for d in devices))

asyncio.run(main())
```

### Step 3: Run it in terminal
Right-click → Run Python File in Terminal

### ✅ Expected Output
```
Polling SW1...
Polling SW2...
...
SW1 responded.
...
```

> 💡 Takeaway: `asyncio` allows polling multiple endpoints concurrently using cooperative multitasking.

---

## 🧪 Task 3: Use `ThreadPoolExecutor` for Log Collection

### Step 1: Create a file
```
log_collector_threadpool.py
```

### Step 2: Add code below
```python
from concurrent.futures import ThreadPoolExecutor
import time

def collect_logs(device):
    print(f"Collecting logs from {device}...")
    time.sleep(1)
    return f"{device}: logs collected."

devices = ["FW1", "R3", "SW5", "SW6"]
with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(collect_logs, devices)

for result in results:
    print(result)
```

### ✅ Expected Output
```
Collecting logs from FW1...
Collecting logs from R3...
...
FW1: logs collected.
R3: logs collected.
```

---

## 🔍 Troubleshooting Tips
- 🐍 Use the VSCode terminal to see output clearly
- 🔁 If output is jumbled, rerun to observe thread concurrency
- ❌ If errors occur: ensure proper indenting and that you saved the file

---

## 🏡 Homework Exercises
These exercises reinforce concurrency by challenging learners to create real-world simulations.

### 📝 Exercise 1: VLAN Collector with Threads
- Devices = 10 simulated switches
- Each returns random VLANs
- Use `threading` to connect and print the VLAN info

### 📝 Exercise 2: REST Monitoring Dashboard (Async)
- Use `asyncio` to simulate API responses from 8 routers
- Each returns CPU/memory values
- Print a dashboard-like output

### 📝 Exercise 3: Performance Comparison
- Write 3 versions:
  1. Sequential log collection (1 device at a time)
  2. Using threads
  3. Using `asyncio`
- Time each script and compare total execution time

### 📝 Bonus: Combine Threads + Async
- Create a multithreaded script where each thread runs an async polling function

---

## ✅ Takeaway Notes
- You now understand **how concurrency boosts automation performance**
- You practiced both **multithreading** and **asyncio** for real use cases
- You learned how to manage device access, simulate logs, and improve script execution speed


