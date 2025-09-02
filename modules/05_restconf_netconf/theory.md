# Python Basics for Network Automation: Module 5 Theory Guide

## Using APIs to Retrieve Data on Cisco Network Devices

**[Your Organization/Name]**
**September 01, 2025**

---

## 1. Introduction to APIs in Network Automation

You've learned to automate network devices using the Command Line Interface (CLI) with Netmiko and Paramiko. While powerful, CLI automation has limitations:
*   **Text-based:** Output is unstructured text, which is hard for programs to parse reliably. If Cisco changes a `show` command's output format, your script might break.
*   **Interactive:** Often requires sending commands and waiting for prompts (e.g., `more`, `confirm`).
*   **Vendor-specific:** Commands vary greatly between different device vendors and even different OS versions.

**APIs (Application Programming Interfaces)** offer a modern, more efficient way to interact with network devices and controllers. Think of an API as a specialized "menu" or "service counter" that a device or software offers. Your program sends a clear, structured request (like ordering a specific item from the menu) and receives a structured response (like a neatly printed receipt).

**Why use APIs for Network Automation?**
*   **Structured Data:** APIs usually give you data in easy-to-read formats like JSON or XML. Your Python script can then easily pick out exactly what it needs (e.g., "CPU usage is 75%"). This is much more reliable than parsing text.
*   **Built for Programs:** APIs are designed for software to talk to software, making automation more reliable and less prone to breaking from minor CLI changes.
*   **Consistent:** APIs can offer a more consistent way to get data, even from different types of devices or software, compared to parsing varied CLI outputs.

### 1.1 Cisco APIs: REST, NETCONF/YANG, RESTCONF

Cisco, like many network vendors, provides different types of APIs.

*   **REST APIs (Representational State Transfer):**
    *   **What it is:** The most common type of API you'll encounter. It uses standard web communication methods (like visiting a website to get information). You send requests using standard HTTP methods (like GET to get data, POST to send data).
    *   **Data Format:** Primarily exchanges data in **JSON** (JavaScript Object Notation) format, sometimes XML.
    *   **Cisco Examples:** Cisco DNA Center (Catalyst Center), Meraki Dashboard API.
    *   **Focus for this module:** We will primarily focus on REST APIs, especially RESTCONF on Cisco IOS XE.

*   **NETCONF/YANG:**
    *   **NETCONF:** A protocol (a set of rules for communication) specifically designed for managing network devices. It typically runs over SSH and uses **XML** for data exchange. It's designed for robust, transactional configuration changes.
    *   **YANG:** A data modeling language. Think of YANG as the blueprint or schema that defines the structure and hierarchy of configuration and operational data on network devices. It tells you exactly what data looks like and where it belongs.

*   **RESTCONF:**
    *   **What it is:** Think of RESTCONF as a way to use the simple ideas of REST (HTTP methods, URLs) but apply them to the structured data defined by **YANG** models. It's a "REST-like" API for YANG data. It typically runs directly on the network device (e.g., Cisco IOS XE routers).
    *   **Data Format:** Can use either **JSON** or **XML** for data exchange. JSON is often preferred for its simplicity.
    *   **Comparison: RESTCONF vs. NETCONF for Monitoring:**
        *   **NETCONF for Monitoring:** Can be used for polling operational data. More importantly, it supports **NETCONF Notifications** (also known as "push telemetry"), where the device can stream data to a collector without being polled. This is very efficient for high-volume, real-time data. However, setting up NETCONF clients and collectors can be more complex than simple HTTP requests.
        *   **RESTCONF for Monitoring:** Ideal for polling operational data using simple HTTP GET requests. Easier to integrate with web-based tools and dashboards due to its HTTP nature. While it can also support event streams (like Server-Sent Events), its primary strength for monitoring is often simpler polling of YANG-modeled data.
        *   **Choice:** For simple, periodic polling, RESTCONF is often easier to implement. For high-volume, event-driven telemetry, NETCONF (or gRPC-based telemetry, which is a newer evolution) is generally more powerful.

---

## 2. YANG Models: The Blueprint for Network Data

YANG models are crucial for understanding how data is structured in NETCONF and RESTCONF. They define the hierarchy, data types, and relationships of configuration and operational data.

*   **2.1 Native YANG Models (Vendor-Specific):**
    *   **What it is:** Developed by the device vendor (e.g., `Cisco-IOS-XE-native`). These models typically reflect the device's traditional CLI configuration and operational commands. They expose almost every configurable parameter and operational state that you would find via CLI.
    *   **When to use:** When you need to access specific, vendor-proprietary features or configurations that are not covered by standard models. Often used for deep dives into vendor-specific operational data.
    *   **Pros:** Access to full device capabilities, familiar to CLI users.
    *   **Cons:** Not portable; code written for one vendor's native model won't work on another's. If the vendor changes their internal CLI structure, the native YANG model might also change, potentially breaking your automation.

*   **2.2 IETF YANG Models (Standardized):**
    *   **What it is:** Developed by the Internet Engineering Task Force (IETF). These are standardized models for common network functionalities (e.g., `ietf-interfaces` for interface configuration and status, `ietf-routing` for routing protocols). They define common network concepts in a vendor-agnostic way.
    *   **When to use:** For basic, common network elements and operations that are standardized across vendors. This is your go-to for portable automation.
    *   **Pros:** Highly portable; code written for IETF models can work across any vendor supporting those models. Stable and well-documented.
    *   **Cons:** May not cover all vendor-specific features or advanced operational data. They focus on common denominators, so you might miss some vendor-specific details.

*   **2.3 OpenConfig YANG Models (Industry-Driven):**
    *   **What it is:** Developed by a collaboration of network operators (like Google, Microsoft) and vendors. OpenConfig aims to create vendor-neutral, operationally focused YANG models for common network services and telemetry. They often provide a more "opinionated" and operationally useful view of network data than IETF models, focusing on the data operators actually need.
    *   **When to use:** Ideal for multi-vendor environments where you need consistent, rich operational data and configuration across different platforms, especially for telemetry (streaming data).
    *   **Pros:** Vendor-neutral, operationally rich, designed for large-scale deployments and telemetry. Provides a unified view across diverse hardware.
    *   **Cons:** Adoption is growing but not universal across all devices/features yet. Some vendors might have partial implementations.

---

## 3. Querying Cisco IOS XE Router Performance Data via RESTCONF

Cisco IOS XE routers expose their operational data (like CPU, memory, interfaces) through RESTCONF, defined by various YANG models.

*   **CPU Utilization:** How busy the device's processor is.
*   **Memory Usage:** How much RAM is being used versus how much is available.
*   **Interface Statistics:** Bytes in/out, packets in/out, errors, discards, operational status, speed.

These metrics are typically exposed through specific YANG models.

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
```

Your Python script would then easily access `data['Cisco-IOS-XE-process-cpu-oper:cpu-usage']['cpu-utilization'][0]['cpu-total-utilization']`.

* * *

4\. Building a Simple Monitoring Tool with Python Flask
-------------------------------------------------------

Python Flask is a lightweight web framework. It allows you to create simple web applications that can display data in a web browser. This is perfect for building a basic monitoring dashboard.

How it works:

1.  Flask Application: A Python script that runs a small web server.
2.  Routes: Define specific URLs (e.g., `/`, `/metrics`) that trigger Python functions.
3.  Data Retrieval: Inside these functions, you'll use `requests` to query your Cisco IOS XE router's RESTCONF API.
4.  HTML/JSON Response: Flask sends back either an HTML page (for the dashboard view) or JSON data (for a data API endpoint).
5.  Web Browser: Users open the Flask app's URL in their browser to see the monitoring data. The browser can periodically refresh the page or fetch new data using JavaScript.

Displaying Data with Other Tools (e.g., Grafana): For more advanced, scalable, and visually rich monitoring, organizations often use dedicated monitoring stacks. Your Python script can be a crucial part of this by acting as a data collector.

*   Data Collection: Your Python script (using `requests` for RESTCONF, or other libraries for NETCONF/gRPC telemetry) fetches metrics.
*   Data Storage: The collected metrics are then pushed to a time-series database (e.g., Prometheus, InfluxDB). These databases are optimized for storing and querying time-stamped data.
*   Data Visualization: Tools like Grafana connect to these time-series databases. Grafana allows you to build highly customizable, interactive dashboards with graphs, charts, and alerts. Your Python script feeds the data, and Grafana makes it beautiful and actionable.

* * *

5\. Summary and Key Takeaways
-----------------------------

### Summary

APIs provide a powerful, structured way to interact with network devices and controllers, moving beyond the limitations of CLI parsing. RESTCONF (HTTP + YANG) offers structured access directly to devices like Cisco IOS XE routers. These APIs enable programmatic access to performance data (CPU, memory, interfaces) and are ideal for building monitoring tools, which can be easily displayed using a web framework like Python Flask or integrated into larger monitoring systems like Grafana.

### Key Takeaways

*   APIs vs. CLI: APIs offer structured data, more reliable automation.
*   REST APIs: Standard web methods (GET, POST), JSON data.
*   NETCONF/YANG: Protocol (NETCONF) and data model (YANG) for structured device management (XML).
*   RESTCONF: RESTful interface to YANG-modeled data (HTTP, JSON/XML), found directly on IOS XE.
*   YANG Models:
    *   Native: Vendor-specific, reflects CLI, full device capability, not portable.
    *   IETF: Standardized, basic functions, portable across vendors.
    *   OpenConfig: Industry-driven, operationally rich, vendor-neutral, good for multi-vendor environments and telemetry.
*   `requests` Library: Your primary tool for making HTTP requests to REST APIs.
*   Python Flask: A lightweight web framework for building simple web applications, ideal for displaying monitoring data.
*   Monitoring Tools: APIs enable polling, thresholding, and displaying real-time network health data. For advanced visualization, consider tools like Grafana.


