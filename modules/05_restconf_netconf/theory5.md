# Python Basics for Network Automation: Module 5 Theory Guide

## Using APIs to Retrieve Data on Cisco Network Devices

**[Your Organization/Name]**
**September 01, 2025**

---

## 1. Introduction to APIs in Network Automation

You've learned to automate network devices using the Command Line Interface (CLI). While powerful, CLI automation has limitations:
*   **Text-based:** Output is unstructured text, which is hard for programs to parse reliably. If Cisco changes a `show` command's output format, your script might break.
*   **Interactive:** Often requires sending commands and waiting for prompts (e.g., `more`, `confirm`).
*   **Vendor-specific:** Commands vary greatly between different device vendors.

**APIs (Application Programming Interfaces)** offer a modern, more efficient way to interact with network devices and controllers. Think of an API as a specialized "menu" or "service counter" that a device or software offers. Your program sends a clear, structured request (like ordering a specific item from the menu) and receives a structured response (like a neatly printed receipt).

**Why use APIs for Network Automation?**
*   **Structured Data:** APIs give data in JSON or XML, easy for Python to use.
*   **Built for Programs:** Reliable communication, less prone to breaking.
*   **Consistent:** Can offer a unified way to get data across different systems.

### 1.1 Cisco APIs: REST, NETCONF/YANG, RESTCONF

Cisco provides various APIs:

*   **REST APIs (Representational State Transfer):**
    *   **What:** The most common type of API. Uses standard web methods (HTTP GET, POST) via URLs.
    *   **Data:** Primarily **JSON**.
    *   **Cisco Examples:** Cisco DNA Center (Catalyst Center), Meraki Dashboard API.
    *   **Focus:** We will use `requests` for RESTCONF on IOS XE.

*   **NETCONF/YANG:**
    *   **NETCONF:** A protocol (often over SSH) for managing network devices. Uses **XML** for data exchange. It's designed for robust, transactional configuration changes.
    *   **YANG:** A data modeling language. Think of YANG as the blueprint or schema that defines the structure and hierarchy of configuration and operational data on network devices. It tells you exactly what data looks like and where it belongs.

*   **RESTCONF:**
    *   **What:** A "REST-like" API that uses standard HTTP methods to access data defined by **YANG** models. It typically runs directly on the network device (e.g., Cisco IOS XE routers).
    *   **Data:** Can use **JSON** or **XML**.
    *   **Comparison: RESTCONF vs. NETCONF for Monitoring:**
        *   **NETCONF for Monitoring:** Can be used for polling operational data. More importantly, it supports **NETCONF Notifications** (also known as "push telemetry"), where the device can stream data to a collector without being polled. This is very efficient for high-volume, real-time data. However, setting up NETCONF clients and collectors can be more complex than simple HTTP requests.
        *   **RESTCONF for Monitoring:** Ideal for polling operational data using simple HTTP GET requests. Easier to integrate with web-based tools and dashboards due to its HTTP nature. While it can also support event streams (like Server-Sent Events), its primary strength for monitoring is often simpler polling of YANG-modeled data.
        *   **Choice:** For simple, periodic polling, RESTCONF is often easier to implement. For high-volume, event-driven telemetry, NETCONF (or gRPC-based telemetry, which is a newer evolution) is generally more powerful.

---

## 2. Understanding YANG Data Models

YANG models are the core of NETCONF and RESTCONF. They define the structure of the data you interact with.

### 2.1 Brief Introduction to YANG Syntax

YANG models are human-readable text files that define a hierarchical tree structure for data. Key components include:
*   **`module`:** The top-level container for a YANG model, defining its name and namespace.
*   **`container`:** An interior node in the tree that groups related data nodes. It's like a folder.
*   **`list`:** An ordered sequence of list entries, each uniquely identified by a `key`. It's like a table where each row is a list entry.
*   **`leaf`:** A data node that has a single value of a specific type (e.g., string, integer, boolean). It's like a file.
*   **`type`:** Defines the data type of a `leaf` (e.g., `string`, `int32`, `boolean`, `empty`).
*   **`config`:** A statement that indicates whether a node is configuration data (`true`) or state/operational data (`false`). Operational data is read-only.
*   **`description`:** Provides human-readable text explaining the node.

**Example YANG Snippet (Conceptual):**
```yang
module example-interfaces {
  namespace "urn:example:interfaces";
  prefix "ex-if";

  container interfaces {
    list interface {
      key "name";
      leaf name {
        type string;
        description "Interface name.";
      }
      leaf description {
        type string;
        description "Interface description.";
      }
      leaf enabled {
        type boolean;
        config true; // This is configuration data
        description "Interface enabled state.";
      }
      leaf oper-status {
        type enumeration { // Operational data, read-only
          enum "up";
          enum "down";
          enum "testing";
        }
        config false; // This is operational data
        description "Interface operational status.";
      }
    }
  }
}
```
### 2.2 Available YANG Models: Native, IETF, OpenConfig

YANG models are categorized by their origin and purpose:

*   Native YANG Models (Vendor-Specific):
    
    *   What: Developed by the device vendor (e.g., `Cisco-IOS-XE-native`). These models typically reflect the device's traditional CLI configuration and operational commands. They often expose almost every configurable parameter and operational state.
    *   When to use: When you need to access specific, vendor-proprietary features or configurations that are not covered by standard models. Often used for deep dives into vendor-specific operational data.
    *   Pros: Access to full device capabilities.
    *   Cons: Not portable; code written for one vendor's native model won't work on another's. If the vendor changes their internal CLI structure, the native YANG model might also change, potentially breaking your automation.
*   IETF YANG Models (Standardized):
    
    *   What: Developed by the Internet Engineering Task Force (IETF). These are standardized models for common network functionalities (e.g., `ietf-interfaces` for interface configuration and status, `ietf-routing` for routing protocols). They define common network concepts in a vendor-agnostic way.
    *   When to use: For basic, common network elements and operations that are standardized across vendors. This is your go-to for portable automation.
    *   Pros: Highly portable; code written for IETF models can work across any vendor supporting those models. Stable and well-documented.
    *   Cons: May not cover all vendor-specific features or advanced operational data. They focus on common denominators, so you might miss some vendor-specific details.
*   OpenConfig YANG Models (Industry-Driven):
    
    *   What: Developed by a collaboration of network operators (like Google, Microsoft) and vendors. OpenConfig aims to create vendor-neutral, operationally focused YANG models for common network services and telemetry. They often provide a more "opinionated" and operationally useful view of network data than IETF models, focusing on the data operators actually need.
    *   When to use: Ideal for multi-vendor environments where you need consistent, rich operational data and configuration across different platforms, especially for telemetry (streaming data).
    *   Pros: Vendor-neutral, operationally rich, designed for large-scale deployments. Provides a unified view across diverse hardware.
    *   Cons: Adoption is growing but not universal across all devices/features yet. Some vendors might have partial implementations.

* * *

3\. Querying Cisco IOS XE Router Performance Data
-------------------------------------------------

To query performance data from a Cisco IOS XE router, you'll use RESTCONF with specific YANG models.

### 3.1 Building RESTCONF URIs (Uniform Resource Identifiers)

A RESTCONF URI is constructed to point to a specific node in the YANG data tree. The basic structure is: `https:/{host}/:{port}/restconf/data/{yangpath}`

*   {host}: The IP address or hostname of your router.
*   {port}: Usually 443 for HTTPS.
*   `/restconf/data/`: This is the base path for accessing data nodes defined by YANG models.
*   {yangpath}: This is the critical part. It specifies the path to the desired data within the YANG model hierarchy. It uses a specific format:
    *   `module-name:top-level-container/list-name=key-value/leaf-name`
    *   `module-name:` is the prefix defined in the YANG model (e.g., `Cisco-IOS-XE-process-cpu-oper:`, `ietf-interfaces:`).
    *   List entries are identified by `list-name=key-value` (e.g., `interface=GigabitEthernet1`).

### 3.2 Applying YANG Filters (Querying Specific Data)

YANG filtering allows you to retrieve only the specific data you need, reducing the amount of data transferred and processed.

*   For RESTCONF URIs: Filtering is primarily done by specifying the exact path in the URI. If you want a specific interface's status, you build the URI directly to that interface's status leaf.
    
    *   Example: `/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1/oper-status`
*   For NETCONF Payloads (XML Filters): NETCONF uses an XML `` element within a `` or `` RPC (Remote Procedure Call) to specify the desired data. This filter can use XPath-like expressions.
    
    Example NETCONF `` Payload (XML): To get CPU utilization:
```xml
    <filter type="subtree">
    <cpu-usage xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-process-cpu-oper">
        <cpu-utilization/>
    </cpu-usage>
    </filter>
```
To get a specific interface's operational status:
```xml
    <filter type="subtree">
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
        <name>GigabitEthernet1</name>
        <oper-status/>
        </interface>
    </interfaces>
    </filter>
```
### 3.3 Querying Performance Data Examples

Here are common YANG paths and their corresponding RESTCONF URIs for Cisco IOS XE performance data:

*   CPU Utilization:
    
    *   YANG Path: `Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization`
    *   RESTCONF URI: `https://:/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization`
    *   Response (JSON):
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
*   *   You'd extract `cpu-total-utilization`.
*   Memory Utilization:
    
    *   YANG Path: `Cisco-IOS-XE-memory-oper:memory-statistics`
    *   RESTCONF URI: `https://:/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics`
    *   Response (JSON - simplified):
    ```json
        {
    "Cisco-IOS-XE-memory-oper:memory-statistics": {
        "memory-statistic": [
        {
            "name": "Processor",
            "total-memory": 100000000,
            "used-memory": 50000000,
            "free-memory": 50000000
        }
        ]
    }
    }
    ```
    *   *   You'd extract `total-memory` and `used-memory` from the relevant `memory-statistic` entry (e.g., "Processor" pool).
*   Interface Operational Status:
    
    *   YANG Path: `ietf-interfaces:interfaces/interface=/oper-status`
    *   RESTCONF URI: `https://:/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1/oper-status`
    *   Response (JSON):
        ```json
        {
        "ietf-interfaces:oper-status": "up"
        }
        ```
4\. Cisco YangSuite: Your YANG Companion
----------------------------------------

Working with YANG models and building complex filters or URIs can be challenging. Cisco YangSuite is an invaluable tool for this.

*   What it is: A web-based application that helps you explore, validate, and test YANG models and their corresponding data.
*   How it helps:
    *   Browse Models: Visually explore the hierarchical structure of various YANG models (Native, IETF, OpenConfig) supported by your device.
    *   Build Filters/URIs: It provides a graphical interface to select specific data nodes and automatically generates the correct NETCONF XML filters or RESTCONF URIs.
    *   Test API Calls: You can directly test `get`, `get-config`, `edit-config` operations against your live devices from within YangSuite, seeing the exact request and response.
    *   Validate Data: Ensure your data payloads conform to the YANG model.

YangSuite simplifies the process of understanding YANG models and constructing API calls, making your automation development much faster.

* * *

5\. Building a Simple Monitoring Tool with Python Flask
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

6\. Summary and Key Takeaways
-----------------------------

### Summary

APIs provide a powerful, structured way to interact with network devices and controllers, moving beyond the limitations of CLI parsing. RESTCONF (HTTP + YANG) offers structured access directly to devices like Cisco IOS XE routers. These APIs enable programmatic access to performance data (CPU, memory, interfaces) and are ideal for building monitoring tools, which can be easily displayed using a web framework like Python Flask or integrated into larger monitoring systems like Grafana. Understanding YANG models and tools like YangSuite is key to effective API interaction.

### Key Takeaways

*   APIs vs. CLI: APIs offer structured data, more reliable automation.
*   REST APIs: Standard web methods (GET, POST), JSON data.
*   NETCONF/YANG: Protocol (NETCONF) and data model (YANG) for structured device management (XML).
*   RESTCONF: RESTful interface to YANG-modeled data (HTTP, JSON/XML), found directly on IOS XE.
*   YANG Syntax: Defines data hierarchy using `module`, `container`, `list`, `leaf`, `type`, `config`, `description`.
*   YANG Model Types:
    *   Native: Vendor-specific, reflects CLI, not portable.
    *   IETF: Standardized, basic functions, portable.
    *   OpenConfig: Industry-driven, operationally rich, vendor-neutral.
*   Building RESTCONF URIs: Use `https:/{host}/:{port}/restconf/data/{yangpath}`. YANG path uses `module-name:container/list=key/leaf` format.
*   YANG Filtering: Done by precise URI path for RESTCONF; XML `` for NETCONF.
*   Cisco YangSuite: Tool to explore YANG models, build filters/URIs, and test API calls.
*   `requests` Library: Your primary tool for making HTTP requests to REST APIs.
*   Python Flask: A lightweight web framework for building simple web applications, ideal for displaying monitoring data.
*   Monitoring Tools: APIs enable polling, thresholding, and displaying real-time network health data. Consider Grafana for advanced visualization.