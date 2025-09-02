# Python Basics for Network Automation: Module 5 Theory Guide

## Using APIs to Retrieve Data on Cisco Network Devices

**[Your Organization/Name]**
**September 01, 2025**

---

## 1. Introduction to APIs in Network Automation

You've learned to automate network devices using the Command Line Interface (CLI). While powerful, CLI automation has limitations:
*   **Text-based:** Output is unstructured text, hard for programs to parse reliably.
*   **Interactive:** Often requires user input.
*   **Vendor-specific:** Commands vary greatly between different device vendors.

**APIs (Application Programming Interfaces)** offer a modern, more efficient way to interact with network devices and controllers. Think of an API as a specialized "menu" that a device or software offers. Your program sends a clear, structured request and receives a structured response (like JSON).

**Why use APIs for Network Automation?**
*   **Structured Data:** APIs give data in JSON/XML, easy for Python to use.
*   **Built for Programs:** Reliable communication, less prone to breaking.
*   **Consistent:** Can offer a unified way to get data across different systems.

### 1.1 Cisco APIs: REST, NETCONF/YANG, RESTCONF

Cisco provides various APIs:

*   **REST APIs:**
    *   **What:** Most common type. Uses standard web methods (HTTP GET, POST) via URLs.
    *   **Data:** Primarily **JSON**.
    *   **Cisco Examples:** Cisco DNA Center (Catalyst Center), Meraki Dashboard API.
    *   **Focus:** We will use `requests` for RESTCONF on IOS XE.

*   **NETCONF/YANG:**
    *   **NETCONF:** A protocol (often over SSH) for managing network devices. Uses **XML**.
    *   **YANG:** A language that defines the structure of network data. Think of it as the blueprint for network information.
    *   **Why:** Provides a precise, standardized way to configure and get data, often vendor-agnostic.

*   **RESTCONF:**
    *   **What:** A "REST-like" API that uses standard HTTP methods to access data defined by **YANG** models. It typically runs directly on the network device (e.g., Cisco IOS XE routers).
    *   **Data:** Can use **JSON** or **XML**.
    *   **Comparison: RESTCONF vs. NETCONF:** Both use YANG. NETCONF is a dedicated protocol (often for robust configuration), RESTCONF uses HTTP (easier for web integration and data retrieval).

---

## 2. Querying Cisco IOS XE Router Performance Data via RESTCONF

Cisco IOS XE routers expose their operational data (like CPU, memory, interfaces) through RESTCONF, defined by various YANG models.

*   **CPU Utilization:** How busy the device's processor is.
*   **Memory Usage:** How much RAM is being used versus how much is available.
*   **Interface Statistics:** Bytes in/out, packets in/out, errors, discards, operational status, speed.

These metrics are typically exposed through specific YANG models (e.g., `Cisco-IOS-XE-process-cpu-oper` for CPU, `Cisco-IOS-XE-memory-oper` for memory, `ietf-interfaces` for interfaces).

**Example (RESTCONF GET Request for CPU Data):**
To get CPU utilization from a Cisco IOS XE router, you might send a GET request to a URL like:
`https://<IOSXE_IP>/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization`

The router would respond with JSON data similar to this:
```json
{
  "Cisco-IOS-XE-process-cpu-oper:cpu-usage": {
    "cpu-utilization": [
      {
        "five-seconds": 5,
        "one-minute": 10,
        "five-minutes": 15,
        "cpu-total-utilization": 12
      }
    ]
  }
}