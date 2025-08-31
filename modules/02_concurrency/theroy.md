# Module 2 – Data Synchronization and Asynchronous Mechanisms

> Estimated Time: 2 hours theory + 2 hours lab

## Overview
In modern network automation, it’s common to interact with multiple devices simultaneously. This requires mastering Python’s capabilities in **multithreading**, **asynchronous I/O (asyncio)**, and **concurrent execution**. These tools help ensure that scripts don’t block while waiting for device responses, enabling real-time operations like log collection or device health monitoring at scale.

---

## 1. Why Asynchronous Programming in Network Automation?
When automating networks, engineers often:
- Connect to dozens or hundreds of devices
- Wait for CLI/API responses
- Collect logs or status periodically

Traditional sequential execution is inefficient in such cases. Asynchronous and concurrent techniques help:
- Speed up device polling
- Avoid blocking I/O
- Collect data in real-time

---

## 2. Concurrency vs. Parallelism
- **Concurrency**: tasks appear to run simultaneously (context switching). Suitable for I/O-bound tasks.
- **Parallelism**: tasks truly run at the same time on multiple cores (CPU-bound).

| Term | Python Library | Suitable For |
|------|----------------|---------------|
| Concurrency | `asyncio` | I/O-bound tasks (API, SSH) |
| Multithreading | `threading` | I/O-bound or legacy tools |
| Multiprocessing | `multiprocessing` | CPU-bound computation |

---

## 3. Multithreading in Python
Python’s `threading` module enables concurrent execution by using threads:

```python
import threading

def connect_device(device):
    print(f"Connecting to {device}...")

thread1 = threading.Thread(target=connect_device, args=("Switch1",))
thread2 = threading.Thread(target=connect_device, args=("Router1",))

thread1.start()
thread2.start()
```

✅ **Expected Output**:
```
Connecting to Switch1...
Connecting to Router1...
```
(The order may vary due to thread execution timing.)

✅ **Use Case**: Connect to multiple network devices simultaneously and run configuration or diagnostic commands.

---

## 4. Asynchronous Programming with `asyncio`
Python’s `asyncio` supports true asynchronous I/O with `async` and `await` syntax:

```python
import asyncio

async def poll_device(device):
    print(f"Polling {device}...")
    await asyncio.sleep(1)

async def main():
    await asyncio.gather(
        poll_device("Switch1"),
        poll_device("Router1")
    )

asyncio.run(main())
```

✅ **Expected Output**:
```
Polling Switch1...
Polling Router1...
```
(Both tasks run concurrently and complete after ~1 second.)

✅ **Use Case**: Query REST APIs of multiple devices at once.

---

## 5. Use Case: Concurrent Device Access
### Scenario:
You need to collect interface status from 50 devices simultaneously every 5 minutes.

### Solutions:
- Use `threading` to launch 50 Netmiko sessions
- Use `asyncio` for non-blocking data collection from APIs

✅ **Expected Result**: A significant reduction in total execution time compared to sequential device access.

---

## 6. Best Practices
- Use `threading` when interacting with CLI tools like Netmiko
- Use `asyncio` for REST APIs and file operations
- Use `concurrent.futures.ThreadPoolExecutor` for cleaner parallelism

Example:
```python
from concurrent.futures import ThreadPoolExecutor

def collect_logs(device):
    print(f"Collecting logs from {device}...")

devices = ["R1", "R2", "SW1"]
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(collect_logs, devices)
```

✅ **Expected Output**:
```
Collecting logs from R1...
Collecting logs from R2...
Collecting logs from SW1...
```
(The order may vary depending on thread scheduling.)

---

## 7. Summary
By the end of this module, learners should:
- Understand the difference between `threading`, `asyncio`, and `multiprocessing`
- Use threads to run CLI-based automations in parallel
- Use `asyncio` for concurrent API or log collection tasks
- Structure their automation code to scale beyond a single device

✅ **Real-World Benefits**:
- Reduce script run times drastically when dealing with many devices
- Improve responsiveness of scripts for monitoring and alerting
- Enable scalable automation designs with clean, maintainable code

👉 Next: [Lab Guide – Module 2](lab2.md)

