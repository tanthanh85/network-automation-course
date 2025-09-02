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
network_automation_labs/
└── module5_api_lab/
├── init.py
├── config.py
├── iosxe_api_functions.py
├── app.py
├── templates/
│ └── index.html
└── static/
└── style.css