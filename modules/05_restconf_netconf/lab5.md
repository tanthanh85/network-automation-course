---

## Document 2: Python Basics for Network Automation - Module 5 Lab Guide (Complete Markdown Block)

```markdown
# Python Basics for Network Automation: Module 5 Lab Guide

## Using APIs to Retrieve Data on Cisco Network Devices - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 5 of the Python Basics for Network Automation Lab Guide! In this module, you will gain hands-on experience with using APIs to retrieve data. We will focus on **RESTCONF on Cisco IOS XE routers** and the `requests` Python library. We will then use **Python Flask** to build a simple web-based monitoring tool.

**It is crucial that you replace the dummy values for your IOS XE router with its actual IP address, username, and password to make the code functional.**

**Lab Objectives:**
*   Install the `requests` and `Flask` libraries.
*   Query Cisco IOS XE router's performance data (CPU, memory, interfaces) using RESTCONF.
*   Build a simple monitoring tool using Python Flask to display this data.

**Prerequisites:**
*   Completion of Module 1, Module 2, Module 3, and Module 4 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   An active internet connection.
*   **Access to a Cisco IOS XE router with RESTCONF enabled (e.g., Cisco DevNet Sandboxes).** You will need its IP, username, and password.

Let's start exploring APIs and Flask!

---

## Lab Setup: Project Structure

For this module, we will structure our project for better organization.

1.  **Navigate** to your main `network_automation_labs` directory.
2.  **Create a new directory** for this module's labs:
    ```bash
    mkdir module5_api_lab
    cd module5_api_lab
    ```
3.  **Inside `module5_api_lab`, create the following directories:**
    ```bash
    mkdir templates
    mkdir static
    ```
4.  **Inside `module5_api_lab`, create the following empty Python files:**
    ```bash
    touch __init__.py
    touch config.py
    touch iosxe_api_functions.py
    touch app.py
    ```
5.  **Inside the `templates` directory, create an empty HTML file:**
    ```bash
    touch templates/index.html
    ```
6.  **Inside the `static` directory, create an empty CSS file:**
    ```bash
    touch static/style.css
    ```

Your directory structure should now look like this:
Your Python script would then easily access `data['Cisco-IOS-XE-process-cpu-oper:cpu-usage']['cpu-utilization'][0]['cpu-total-utilization']`.

* * *

3\. Building a Simple Monitoring Tool with Python Flask
-------------------------------------------------------

Python Flask is a lightweight web framework. It allows you to create simple web applications that can display data in a web browser. This is perfect for building a basic monitoring dashboard.

How it works:

1.  Flask Application: A Python script that runs a small web server.
2.  Routes: Define specific URLs (e.g., `/`, `/metrics`) that trigger Python functions.
3.  Data Retrieval: Inside these functions, you'll use `requests` to query your Cisco IOS XE router's RESTCONF API.
4.  HTML/JSON Response: Flask sends back either an HTML page (for the dashboard view) or JSON data (for a data API endpoint).
5.  Web Browser: Users open the Flask app's URL in their browser to see the monitoring data. The browser can periodically refresh the page or fetch new data using JavaScript.

* * *

4\. Summary and Key Takeaways
-----------------------------

### Summary

APIs provide a powerful, structured way to interact with network devices and controllers, moving beyond the limitations of CLI parsing. RESTCONF (HTTP + YANG) offers structured access directly to devices like Cisco IOS XE routers. These APIs enable programmatic access to performance data (CPU, memory, interfaces) and are ideal for building monitoring tools, which can be easily displayed using a web framework like Python Flask.

### Key Takeaways

*   APIs vs. CLI: APIs offer structured data, more reliable automation.
*   REST APIs: Standard web methods (GET, POST), JSON data.
*   NETCONF/YANG: Protocol (NETCONF) and data model (YANG) for structured device management.
*   RESTCONF: RESTful interface to YANG-modeled data (HTTP, JSON/XML), found directly on IOS XE.
*   `requests` Library: Your primary tool for making HTTP requests to REST APIs.
*   Python Flask: A lightweight web framework for building simple web applications, ideal for displaying monitoring data.
*   Monitoring: APIs enable polling, thresholding, and displaying real-time network health data.