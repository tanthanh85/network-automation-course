# Module 2: Data Synchronization and Asynchronous Mechanisms

## Overview
In modern network automation, many tasks involve interacting with multiple devices, collecting telemetry, executing commands, and aggregating data. These tasks are often **I/O-bound**, such as SSH connections or API calls, and can greatly benefit from concurrency techniques to improve efficiency and responsiveness.

Python provides two primary mechanisms for handling such concurrent operations:
- `threading` for multi-threaded execution
- `asyncio` for asynchronous, event-driven programming

This module dives into both approaches with examples, use cases, and implementation guidelines. Learners will understand how to write efficient scripts that can connect to multiple devices concurrently and collect data in parallel.

---

## 1. Why Use Concurrency in Network Automation?

Imagine you need to log in to 100 routers, run the same command, and collect the output. If you do this **sequentially**, it could take minutes.

By using **concurrent programming**, you can:
- Reduce total execution time
- Increase automation scale (hundreds or thousands of devices)
- Improve responsiveness in real-time monitoring systems

Concurrency helps especially when:
- Each task involves waiting (e.g., SSH response)
- Tasks are independent (no need to wait for one to finish before the next starts)

---

## 2. Blocking vs Non-Blocking I/O

### What is I/O?
I/O (Input/Output) refers to operations that interact with external systems:
- Reading from or writing to disk
- Sending/receiving data over a network
- Waiting for a device response

### Blocking I/O
A **blocking** operation waits until the task is complete before allowing further execution.

#### Example:
```python
response = requests.get("https://example.com")
print("Done")  # This waits until the request is complete
```

Even if the request takes 5 seconds, the script halts execution until it finishes.

### Non-Blocking I/O
**Non-blocking** operations allow the program to continue while the task is being processed.

#### Example with Asyncio:
```python
async def get_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://example.com") as resp:
            return await resp.text()
```

Here, while waiting for the HTTP response, Python can switch to other tasks (e.g., fetching from another URL).

---

## 3. Python Threading

Threading uses OS-level threads to run multiple tasks in parallel.

### When to Use:
- When working with **blocking libraries** like Netmiko or Paramiko (SSH)
- When each task is independent (e.g., run a command on each router)

### Example:
```python
from netmiko import ConnectHandler
import threading

def collect_log(device):
    conn = ConnectHandler(**device)
    output = conn.send_command("show log")
    print(f"[{device['host']}] Output length: {len(output)}")
    conn.disconnect()

threads = []
for dev in device_list:
    t = threading.Thread(target=collect_log, args=(dev,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```

### Pros:
- Easy to implement
- Works with any blocking I/O libraries

### Cons:
- Consumes more memory (each thread has its own stack)
- Risk of too many threads for very large tasks

---

## 4. Python Asyncio

Asyncio uses a **single thread** with an **event loop** that switches between tasks when they’re waiting on I/O.

### When to Use:
- When working with **non-blocking I/O**, such as HTTP APIs
- When scaling to **hundreds or thousands of connections**

### Example:
```python
import aiohttp
import asyncio

async def fetch_data(session, url):
    async with session.get(url) as resp:
        data = await resp.text()
        print(f"[{url}] Data length: {len(data)}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in url_list]
        await asyncio.gather(*tasks)

asyncio.run(main())
```

### Pros:
- Lightweight and memory efficient
- Great for massive parallelism (e.g., 10k tasks)

### Cons:
- Requires all libraries to be async-compatible
- Can’t use blocking SSH libraries (without extra wrappers)

---

## 5. Performance Comparison

| Task | Sequential | Threading | Asyncio |
|------|------------|-----------|---------|
| Fetch config from 50 routers (SSH) | 250s | 30s | ❌ (not suitable) |
| REST API calls to 1000 devices | 1000s | 200s | ✅ 20s |

---

## 6. Hybrid Approach (Advanced)
Use `asyncio.run_in_executor()` to run blocking code inside async functions:
```python
import asyncio
import concurrent.futures
from netmiko import ConnectHandler

def get_config(device):
    conn = ConnectHandler(**device)
    return conn.send_command("show run")

async def main():
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        results = await asyncio.gather(*[
            loop.run_in_executor(pool, get_config, dev)
            for dev in device_list
        ])
        for res in results:
            print(res)

asyncio.run(main())
```

---

## 7. Key Differences: Threading vs Asyncio

| Feature | Threading | Asyncio |
|---------|-----------|---------|
| Model | Preemptive | Cooperative |
| Suitable for | SSH/CLI, Netmiko | HTTP APIs, sockets |
| Performance | Good (medium scale) | Excellent (large scale) |
| Memory | Higher | Lower |
| Complexity | Low | Medium |

---

## 8. Common Use Cases

| Use Case | Recommended |
|----------|-------------|
| SSH into 20 routers | Threading |
| Call REST API from 1000 sensors | Asyncio |
| Mix of both | Hybrid with `run_in_executor()` |

---

## 9. Sample Real-World Applications

- Threading:
  - Collect logs from Cisco devices (Netmiko)
  - Run same CLI command on 50 routers
- Asyncio:
  - Pull interface health from ThousandEyes API
  - Collect alerts from Cisco DNA Center streaming API

---

## ✅ Summary
By the end of this module, learners will:
- Understand blocking vs non-blocking I/O
- Compare threading and asyncio in detail
- Know when and how to use each
- Write concurrent Python scripts for device automation
- Compare runtime performance
- Be ready for lab practice involving real device interaction


