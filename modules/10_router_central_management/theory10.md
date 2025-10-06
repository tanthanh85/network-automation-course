# Python Basics for Network Automation: Module 10 Theory Guide

## Creating a Centralized Configuration Management Console for Cisco Routers

**[Your Organization/Name]**
**September 01, 2025**

---

## 1. Introduction to Centralized Network Management Consoles

In previous modules, you've learned to automate individual tasks on single or multiple devices using Netmiko, Paramiko, Ansible, and APIs. While effective, running separate scripts for each task can become cumbersome. A **centralized configuration management console** brings these capabilities together into a single, user-friendly interface.

**What is a Centralized Console?**
It's a web-based (or sometimes CLI-based) application that allows network administrators to:
*   Manage an inventory of network devices.
*   Perform common operational tasks (e.g., reboot, backup, collect logs,...).
*   Monitor device status and performance.
*   Receive automated alerts.
*   Trigger external API calls (Webex, Slack, Zalo...)

**Why build a Python Flask-based Console?**
*   **Unified Interface:** A single pane of glass for multiple tasks.
*   **User-Friendly:** A graphical user interface (GUI) is often easier to use than command-line scripts for non-technical staff.
*   **Automation Orchestration:** Python acts as the orchestrator, calling Netmiko, `requests`, etc., behind the scenes.
*   **Accessibility:** Accessible from any web browser.
*   **Customization:** Tailor the console exactly to your organization's needs.
*   **Scalability (Basic):** Can manage a small to medium-sized network. For enterprise scale, more robust platforms are typically used.

---

## 2. Console Architecture Overview

Our console for this course will be built using **Python Flask**, a lightweight web framework.

*   **Flask Application:** The core Python script that acts as a web server.
*   **Routes:** Specific URLs (e.g., `/`, `/reboot`, `/backup`,...) that trigger Python functions when accessed by a web browser.
*   **HTML Templates:** Flask uses Jinja2 (which you've seen in Module 6) to render dynamic HTML pages. These define the layout and display data fetched by the Python backend.
*   **Static Files:** CSS for styling, JavaScript for interactive elements.
*   **Backend Logic:** Python functions (using Netmiko, `requests`, `sqlite3`) to perform network operations, manage inventory, and process data.
*   **Background Tasks:** For long-running operations (like backups or reboots), it's crucial to run them in the background (e.g., using Python's `threading` module) to keep the web GUI responsive.
```

+-------------------+ +-----------------------+ +-------------------+
| Web Browser | <---> | Flask Web App | <---> | Python Backend |
| (User Interface) | | (Routes, Templates) | | (Netmiko, Requests,|
+-------------------+ +-----------------------+ | sqlite3, Threading)|
                            ^ | |
                            | v v
                    +----------------------+-------------------+
                    | Network Devices |
                    | (Cisco IOS XE) |
                    +-------------------+

```
---

## 3. Inventory Management

A centralized console needs a robust way to store and manage information about the network devices it controls. In this course, we will be storing the network inventory in SQLite.

*   **Why SQLite?**
    *   **File-based Database:** SQLite is a self-contained, serverless, zero-configuration, transactional SQL database engine. It stores data in a single `.db` file, making it easy to set up and manage for smaller applications.
    *   **Structured Data:** Stores data in tables with defined columns and data types, ensuring data integrity.
    *   **Queryable:** Allows powerful SQL queries to retrieve, filter, and manipulate data.
    *   **Scalability (Local):** Excellent for local, single-user applications or small-scale deployments. For multi-user or high-traffic scenarios, a client-server database (like PostgreSQL or MySQL) would be more appropriate.
*   **Data Storage:** We will store device inventory in an SQLite database file (`inventory.db`).
*   **Python Integration:** Python has a built-in `sqlite3` module, making database interactions straightforward.
*   **CRUD Operations (Create, Read, Update, Delete):** The GUI will allow administrators to:
    *   **Add:** Input new device details, which are then inserted into the database table.
    *   **List/Read:** Query all devices from the database table to display on the dashboard.
    *   **Delete:** Remove a device entry from the database table.

---

## 4. Router Control - Automating Operations

We'll leverage Netmiko (from Module 3) for CLI-based operations.

*   **4.1 Reboot a Router:**
    *   **Netmiko Command:** `net_connect.send_command("reload", expect_string=r"\[confirm\]", strip_prompt=False)` followed by `net_connect.send_command("y", strip_prompt=False)`.
    *   **GUI Interaction:** Admin selects a router (or multiple), clicks "Reboot."
    *   **Background Task:** Rebooting is a long-running, blocking task. It must be executed in a separate thread to prevent the Flask web server from freezing.

*   **4.2 Backup Configuration:**
    *   **Netmiko Command:** `net_connect.send_command("show running-config")`.
    *   **GUI Interaction:** Admin selects routers, clicks "Backup Config."
    *   **Background Task:** Backups can take time, especially for many devices. Run in a separate thread.
    *   **File Storage:** Save backups to a designated directory on the server running the Flask app.

*   **4.3 Retrieve "show logging" Output:**
    *   **Netmiko Command:** `net_connect.send_command("show logging")`.
    *   **GUI Interaction:** Admin selects routers, clicks "Get Logs."
    *   **Display/Download:** Display the logs directly on a web page or provide a download link.
    *   **Background Task:** Fetching logs can be quick but for many devices, a background thread is still advisable.

---

## 5. Monitoring Device Status and Bandwidth Utilization

For monitoring, we'll use RESTCONF (from Module 5) for structured data.

*   **5.1 Bandwidth Utilization:**
    *   **RESTCONF Path:** `ietf-interfaces:interfaces-state/interface=<interface_name>/statistics` (for interface counters).
    *   **Calculation:** Bandwidth utilization is calculated by taking the difference between `in-octets` (bytes received) or `out-octets` (bytes sent) over a period of time, then converting to bits per second (bps) and dividing by the interface's bandwidth.
    *   **GUI Display:** A dashboard page will display current bandwidth utilization for selected interfaces. This will require periodic fetching of data.

*   **5.2 Dashboard Design:**
    *   Simple HTML tables for current metrics.
    *   For "nice design," CSS will be used.
    *   For real-time graphs and historical data, this would typically involve:
        *   Storing data in a time-series database (e.g., InfluxDB, Prometheus).
        *   Using JavaScript charting libraries (e.g., Chart.js, D3.js) on the frontend.
        *   Or integrating with dedicated monitoring platforms like Grafana.
    *   For this lab, we'll focus on displaying current values in a table format.

---

## 6. Automated Alerts via Email, Telegram, Slack or Zalo

Integrating alerts is crucial for proactive management. When a monitored metric crosses a threshold (e.g., CPU > 90%, interface utilization > 80%), the system should notify administrators.

*   **How it works (Conceptual):**
    1.  **Monitoring Loop:** A background process (e.g., a separate Python script or a dedicated thread in the Flask app) continuously fetches metrics.
    2.  **Threshold Check:** Compares current metrics against predefined thresholds.
    3.  **Alert Trigger:** If a threshold is exceeded, an alert function is called.
    4.  **Notification Service:**
        *   **Email:** Use Python's `smtplib` module to send emails.
        *   **Telegram:** Use `python-telegram-bot` library to send messages to a Telegram chat.
        *   **Slack:** Use `slack_sdk` library to post messages to a Slack channel.
        *   **Zalo:** Use python `requests` library to send messages to a Zalo user via Zalo Official Account API
    *   **Alert Suppression:** Implement logic to avoid alert storms (e.g., don't send an alert every 5 seconds if the CPU is continuously high; send one, then wait 30 minutes before sending another if it's still high).

**Send alerts to Email, Telegram, and Slack**

This example provides basic functions for sending notifications. Remember to replace the placeholder values (e.g., YOUR_EMAIL, YOUR_PASSWORD, YOUR_BOT_TOKEN, YOUR_CHAT_ID, YOUR_SLACK_WEBHOOK_URL) with your actual credentials and details.


**Send alerts to Zalo**

To send alerts to Zalo, you'll typically use the Zalo Official Account (OA) API. This requires setting up a Zalo Official Account, creating an application on Zalo for Developers, and obtaining an access_token. The process for getting an access_token is an OAuth 2.0 flow and usually involves user interaction to grant permissions to your OA. Once you have the access_token and the user_id of the recipient (who must have interacted with your OA), you can send messages.

Prerequisites for Zalo Integration:

Create a Zalo Official Account (OA): Go to oa.zalo.me and create an Official Account. It needs to be verified.
Register an Application on Zalo for Developers: Visit developers.zalo.me, create a new application, and link it to your OA. You will get an App ID and Secret Key.
Obtain an access_token: This is the most complex step.
You need to implement an OAuth 2.0 flow to get an authorization code, which is then exchanged for an access_token and a refresh_token. The access_token is usually valid for 1 hour, and the refresh_token can be used to get a new access_token when the current one expires (refresh token is valid for 3 months).
For testing or simple cases, you might be able to generate a temporary access_token directly from the Zalo API Explorer (developers.zalo.me -> Tools -> API Explorer -> OA Access Token). However, for a production system, you'll need to manage the token refresh mechanism.
Get Recipient user_id: The user_id is the Zalo ID of the user you want to send the message to. This user must have interacted with your Zalo OA (e.g., followed it, sent a message) for your OA to be able to send them messages.

Given the complexity of the OAuth flow for access_token generation, the example below assumes you have already obtained a valid ZALO_ACCESS_TOKEN and ZALO_RECIPIENT_ID.

```python
import smtplib
from email.mime.text import MIMEText
import requests
import threading
import time
import json # Import json for Zalo payload

# --- Configuration for Alerts ---
# Email Configuration
EMAIL_SENDER = "your_email@example.com"  # Replace with your sender email
EMAIL_PASSWORD = "your_email_password"    # Replace with your email password (use app-specific passwords if available)
EMAIL_RECEIVER = "recipient_email@example.com" # Replace with recipient email
SMTP_SERVER = "smtp.gmail.com"           # Example for Gmail
SMTP_PORT = 465                          # SSL port for Gmail

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" # Replace with your Telegram Bot Token
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"     # Replace with your Telegram Chat ID (e.g., from @userinfobot)

# Slack Configuration
SLACK_WEBHOOK_URL = "YOUR_SLACK_WEBHOOK_URL"   # Replace with your Slack Incoming Webhook URL

# Zalo Configuration
# IMPORTANT: You need to obtain these values from your Zalo Official Account (OA) setup.
# The ACCESS_TOKEN has a limited lifespan (e.g., 1 hour) and needs to be refreshed.
# The RECIPIENT_ID is the Zalo user ID of the person who will receive the alert.
ZALO_ACCESS_TOKEN = "YOUR_ZALO_OA_ACCESS_TOKEN" # Replace with your Zalo OA Access Token
ZALO_RECIPIENT_ID = "YOUR_ZALO_RECIPIENT_USER_ID" # Replace with the Zalo User ID to send messages to

# --- Alert Functions ---

def send_email_alert(subject, message):
    """Sends an email alert."""
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"Email alert sent: '{subject}'")
    except Exception as e:
        print(f"Failed to send email alert: {e}")

def send_telegram_alert(message):
    """Sends a Telegram message alert."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram configuration missing. Cannot send alert.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown' # Optional: allows Markdown formatting in message
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        print(f"Telegram alert sent: '{message}'")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram alert: {e}")

def send_slack_alert(message):
    """Sends a Slack message alert via webhook."""
    if not SLACK_WEBHOOK_URL:
        print("Slack webhook URL missing. Cannot send alert.")
        return

    payload = {
        'text': message
    }
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        print(f"Slack alert sent: '{message}'")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Slack alert: {e}")

def send_zalo_alert(message):
    """Sends a message to a Zalo user via Zalo Official Account API."""
    if not ZALO_ACCESS_TOKEN or not ZALO_RECIPIENT_ID:
        print("Zalo configuration (ACCESS_TOKEN or RECIPIENT_ID) missing. Cannot send alert.")
        print("Please ensure your Zalo OA is set up and you have a valid access token and recipient user ID.")
        return

    zalo_api_url = "https://openapi.zalo.me/v2.0/oa/message" # Zalo OA message API endpoint [10]
    headers = {
        "Content-Type": "application/json",
        "access_token": ZALO_ACCESS_TOKEN # Authentication header [10]
    }
    payload = {
        "recipient": {
            "user_id": ZALO_RECIPIENT_ID # The Zalo user ID to send the message to [10]
        },
        "message": {
            "text": message # The message content [10]
        }
    }

    try:
        response = requests.post(zalo_api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for HTTP errors
        response_data = response.json()
        if response_data.get('error') == 0: # Zalo API typically returns 'error': 0 for success
            print(f"Zalo alert sent successfully: '{message}'")
        else:
            print(f"Failed to send Zalo alert. Zalo API response: {response_data}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Zalo alert: {e}")
    except json.JSONDecodeError:
        print(f"Failed to decode Zalo API response: {response.text}")


# --- Example Monitoring Loop (Conceptual) ---

def monitor_device_metrics():
    """
    Conceptual function to simulate monitoring device metrics and triggering alerts.
    In a real application, this would fetch actual data from network devices.
    """
    cpu_threshold = 80
    interface_util_threshold = 70
    alert_sent_cpu = False
    alert_sent_interface = False

    print("Starting device monitoring loop...")
    while True:
        # Simulate fetching metrics (replace with actual Netmiko/RESTCONF calls)
        current_cpu = 85 # Example: CPU is high
        current_interface_util = 65 # Example: Interface utilization is normal

        print(f"Monitoring: CPU={current_cpu}%, InterfaceUtil={current_interface_util}%")

        # Check CPU threshold
        if current_cpu > cpu_threshold and not alert_sent_cpu:
            alert_message = f"ALERT: Router R1 CPU utilization is at {current_cpu}% (threshold: {cpu_threshold}%)!"
            send_email_alert("High CPU Alert - R1", alert_message)
            send_telegram_alert(alert_message)
            send_slack_alert(alert_message)
            send_zalo_alert(alert_message) # Added Zalo alert
            alert_sent_cpu = True # Suppress further alerts until condition clears or timer resets

        elif current_cpu <= cpu_threshold and alert_sent_cpu:
            print("CPU back to normal.")
            alert_sent_cpu = False # Reset alert flag

        # Check Interface Utilization threshold
        if current_interface_util > interface_util_threshold and not alert_sent_interface:
            alert_message = f"ALERT: Router R1 Gi0/1 interface utilization is at {current_interface_util}% (threshold: {interface_util_threshold}%)!"
            send_email_alert("High Interface Util Alert - R1", alert_message)
            send_telegram_alert(alert_message)
            send_slack_alert(alert_message)
            send_zalo_alert(alert_message) # Added Zalo alert
            alert_sent_interface = True

        elif current_interface_util <= interface_util_threshold and alert_sent_interface:
            print("Interface utilization back to normal.")
            alert_sent_interface = False

        time.sleep(30) # Check every 30 seconds (adjust as needed)

# --- Main execution block ---
if __name__ == "__main__":
    print("This script demonstrates alert functions, including Zalo.")
    print("Please configure your email, Telegram, Slack, and Zalo details in the 'Configuration' section.")
    print("\n--- Testing individual alert functions ---")

    # Test Email
    # send_email_alert("Test Alert from Python", "This is a test email alert from your network automation console.")

    # Test Telegram
    # send_telegram_alert("This is a *test* Telegram alert from your network automation console. _Markdown supported_.")

    # Test Slack
    # send_slack_alert("This is a test Slack alert from your network automation console.")

    # Test Zalo
    # send_zalo_alert("This is a test Zalo alert from your network automation console.")

    print("\n--- Starting conceptual monitoring loop (run in background for Flask app) ---")
    # In a Flask application, this monitoring loop would typically run in a separate thread or process
    # to avoid blocking the web server.
    # For demonstration, we'll run it directly. Uncomment to start.
    # monitoring_thread = threading.Thread(target=monitor_device_metrics)
    # monitoring_thread.daemon = True # Allow the main program to exit even if thread is running
    # monitoring_thread.start()
    # monitoring_thread.join() # Keep main thread alive for demonstration, remove in Flask context

    print("\nExample complete. In a real Flask app, these functions would be called based on monitoring results.")
    print("Ensure you have installed 'requests' library: pip install requests")
    print("For email, ensure your email provider allows 'less secure app access' or use app passwords.")
```


---

## 7. Summary and Key Takeaways

### Summary

Building a centralized configuration management console with Python Flask empowers network administrators with a unified, user-friendly interface for router management. This involves managing device inventory using SQLite, performing CLI-based operations (reboot, backup, log collection) via Netmiko, and monitoring performance (CPU, memory, bandwidth) via RESTCONF. Background tasks ensure GUI responsiveness for long-running operations. The console can be extended to include automated alerting, transforming reactive troubleshooting into proactive network management.

### Key Takeaways

*   **Centralized Console:** A single web GUI (Flask) for managing network devices.
*   **Inventory Management:** Store device details in an **SQLite database**.
*   **Router Control (Netmiko):** Automate reboots, config backups, and log collection.
*   **Monitoring (RESTCONF):** Collect CPU, memory, and interface utilization data.
*   **Flask UI:** Display real-time data in a web browser.
*   **Background Tasks:** Use `threading` for long-running operations to keep Flask responsive.
*   **Automated Alerts:** Integrate with Email, Telegram, or Slack for proactive notifications.
*   **Scalability:** This is a basic console; enterprise-grade solutions often use client-server databases, message queues, and more robust web frameworks.

---