# Python Basics for Network Automation: Module 8 Theory Guide

## Implementation of Security Policies using Python

**[Your Organization/Name]**
**September 01, 2025**

---

## 1. Introduction to Network Security Automation

Network security is paramount, but managing security policies (like Access Control Lists, firewall rules, intrusion prevention) can be complex, repetitive, and prone to human error, especially in large environments. Automating these tasks is crucial for:
*   **Consistency:** Ensuring policies are applied uniformly across devices.
*   **Speed:** Rapidly deploying new rules or responding to threats.
*   **Accuracy:** Reducing manual configuration mistakes.
*   **Scalability:** Managing hundreds or thousands of rules efficiently.
*   **Compliance:** Demonstrating adherence to security standards through automated audits.

This module focuses on automating security policies, specifically using **Cisco Firepower Threat Defense (FTD)**.

---

## 2. Automating Access Control List (ACL) Configurations

ACLs are fundamental security mechanisms. Automating their configuration ensures consistent application and reduces errors.

*   **Traditional CLI vs. API for ACLs:**
    *   **CLI:** Text-based, sequential commands. Difficult to verify rule order or conflicts programmatically.
    *   **API:** Structured data (JSON) for rules, allowing programmatic creation, modification, deletion, and reordering. The API handles the underlying CLI translation.

*   **Cisco Firepower Threat Defense (FTD) Management Options:**
    *   **Firepower Management Center (FMC):** The primary and recommended way to manage multiple FTD devices centrally. FMC exposes a comprehensive REST API for policy orchestration.
    *   **Firepower Device Manager (FDM):** A web-based GUI and **REST API** built directly into standalone FTD devices. It's used for managing a single FTD appliance when an FMC is not present.
    *   **CLI:** Command Line Interface over SSH. Used for basic configuration, troubleshooting, and when FDM/FMC are unavailable or insufficient.

*   **Focus for this Module: FDM REST API**
    Since we're assuming no FMC, we will automate FTD directly via its FDM REST API. This API allows programmatic control over a single FTD appliance's policies.

---

## 3. Managing Firewall Rules Across Network Devices (Cisco FTD with FDM API)

The **Firepower Device Manager (FDM) API** is a RESTful API built directly into standalone Cisco FTD devices. It allows programmatic interaction for managing access control, network objects, interfaces, and other device-specific configurations.

### 3.1 FDM API Authentication

The FDM API uses a token-based authentication:
1.  Send a `POST` request to the `/api/fdm/v6/token` endpoint with username/password in the JSON body. for example: https://10.10.20.65/api/fdm/v6/fdm/token
2.  The response contains an `access_token` in the JSON body, which you use for subsequent requests in the `Authorization: Bearer <access_token>` header.
    Response example:
    ```json
    {
    "access_token": "eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTg4NjM1NjksInN1YiI6ImFkbWluIiwianRpIjoiNzIzZTRjNzgtOWE5Ny0xMWYwLWI5NmQtNWY4Yzg2NTI3ZTY1IiwibmJmIjoxNzU4ODYzNTY5LCJleHAiOjE3NTg4NjUzNjksInJlZnJlc2hUb2tlbkV4cGlyZXNBdCI6MTc1ODg2NTk2OTU5MSwidG9rZW5UeXBlIjoiSldUX0FjY2VzcyIsInVzZXJVdWlkIjoiMjA2NjgzODQtOTk1Mi0xMWVjLWJlMjQtYTViMTQxNjFmMzA3IiwidXNlclJvbGUiOiJST0xFX0FETUlOIiwib3JpZ2luIjoicGFzc3dvcmQiLCJ1c2VybmFtZSI6ImFkbWluIn0.ZO7SPQmIYnUarBKsrzntLzFr_q-S45QTPfSb1kjQ3F4",
    "expires_in": 1800,
    "token_type": "Bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTg4NjM1NjksInN1YiI6ImFkbWluIiwianRpIjoiNzIzZTRjNzgtOWE5Ny0xMWYwLWI5NmQtNWY4Yzg2NTI3ZTY1IiwibmJmIjoxNzU4ODYzNTY5LCJleHAiOjE3NTg4NjU5NjksImFjY2Vzc1Rva2VuRXhwaXJlc0F0IjoxNzU4ODY1MzY5NTkxLCJyZWZyZXNoQ291bnQiOi0xLCJ0b2tlblR5cGUiOiJKV1RfUmVmcmVzaCIsInVzZXJVdWlkIjoiMjA2NjgzODQtOTk1Mi0xMWVjLWJlMjQtYTViMTQxNjFmMzA3IiwidXNlclJvbGUiOiJST0xFX0FETUlOIiwib3JpZ2luIjoicGFzc3dvcmQiLCJ1c2VybmFtZSI6ImFkbWluIn0.hD-Wqxm1_GL4k21NKSmLAsyxhPvyEnbaIV_AfCuvhx4",
    "refresh_expires_in": 2400
    }
    ```


3.  Tokens typically expire after a short period (e.g., 30 minutes), so you need to refresh them.

### 3.2 Key FDM API Endpoints for ACL Automation

FDM structures its access rules within an "Access Policy" (similar to FMC's ACP).

*   **Access Policies:**
    *   `GET /api/fdm/v6/accesspolicies`
        *   Retrieves a list of all Access Policies. FDM usually has a default one.
*   **Access Rules (within an Access Policy):**
    *   `GET /api/fdm/v6/accesspolicies/{policy_uuid}/accessrules`
        *   Retrieves all rules within a specific Access Policy.
    *   `POST /api/fdm/v6/accesspolicies/{policy_uuid}/accessrules`
        *   Creates a new access rule. The request body is JSON defining the rule (source/destination networks, ports, action, etc.).
    *   `DELETE /api/fdm/v6/accesspolicies/{policy_uuid}/accessrules/{rule_uuid}`
        *   Deletes an access rule.
*   **Network Objects:**
    *   `GET /api/fdm/v6/object/networks`
        *   Retrieves existing network objects (IPs, ranges, networks).
    *   `POST /api/fdm/v6/object/networks`
        *   Creates new network objects (e.g., Host, Network, Range). These objects are then referenced by their `id` (UUID) in access rules.

### 3.3 Deployment (FDM API)

Unlike FMC, FDM API changes are typically applied immediately or upon saving the configuration. There isn't a separate "deployment" step like in FMC. However, you often need to issue a "deploy" or "write memory" equivalent command via the API or CLI to make changes persistent across reboots. FDM API handles this implicitly with some operations or explicitly via a `deploy` endpoint.

### 3.4 Example: Creating a Firewall Rule (Conceptual Flow via FDM API)

1.  **Authenticate** to FDM API to get the `access_token`.
2.  **Find the Access Policy UUID:** `GET /api/fdm/v6/accesspolicies` to get the `uuid` of your target policy (e.g., "Default_Access_Policy").
3.  **Create Network Objects (if needed):** If your rule needs new IP addresses or networks not already defined, `POST` to `/api/fdm/v6/object/networks` to create them. Note their `uuid`s.
4.  **Create the Access Rule:** `POST` to `/api/fdm/v6/accesspolicies/{policy_uuid}/accessrules` with a JSON payload defining the rule. This payload will reference the `uuid`s of network objects, ports, etc.
    *   The rule JSON will specify `sourceNetworks`, `destinationNetworks`, `sourcePorts`, `destinationPorts`, `action` (e.g., `PERMIT`, `DENY`).
    *   You can also specify `newPosition` (e.g., `FIRST`, `LAST`, `BEFORE: <ruleUUID>`) to control rule order.
5.  **Save/Deploy:** FDM API often saves changes implicitly. For persistence, you might trigger a `deploy` or `write memory` equivalent via API if available, or just rely on the API's immediate application.

---

## 4. Using Postman for FDM API Testing

**Postman** is a popular API client that simplifies testing and developing with APIs. It allows you to construct HTTP requests, send them, and view responses without writing any code. It's an excellent tool for:
*   **Exploring APIs:** Quickly understand what endpoints are available and what data they expect/return.
*   **Debugging:** Easily test individual API calls and inspect responses.
*   **Generating Code Snippets:** Postman can generate code in various languages (including Python) based on your requests.
*   **Automating Authentication (Variables & Pre-request Scripts):** This is where Postman truly shines for token-based APIs like FDM.

### 4.1 Setting up Postman for FDM API

1.  **Download and Install Postman:** Get it from [postman.com/downloads](https://www.postman.com/downloads/).
2.  **Create a New Collection:** Organize your FDM API requests into a collection (e.g., "FTD FDM API Calls").
3.  **Define Environment Variables:**
    *   Go to your collection, click on the "Variables" tab (or create a new environment).
    *   Add variables for your FTD details:
        *   `ftd_host`: `YOUR_FTD_IP`
        *   `ftd_port`: `443`
        *   `fdm_username`: `YOUR_FDM_USERNAME`
        *   `fdm_password`: `YOUR_FDM_PASSWORD`
        *   `fdm_base_url`: `https://{{ftd_host}}:{{ftd_port}}/api/fdm/v6`
        *   `fdm_token`: (Initial value can be empty, will be set by script)
    *   Set "Current Value" for `ftd_host`, `fdm_username`, `fdm_password`, `ftd_port`.
    *   Click "Save".

### 4.2 Automating Token Generation and Storage

This is the most powerful feature for FDM API in Postman.

1.  **Create a New Request:** Add a `POST` request to your collection, named "Get FDM Token".
2.  **URL:** `{{fdm_base_url}}/token`
3.  **Headers:**
    *   `Content-Type`: `application/json`
4.  **Body (raw, JSON):**
    ```json
    {
        "username": "{{fdm_username}}",
        "password": "{{fdm_password}}"
    }
    ```
5.  **Tests Tab (Post-request Script):** This is a JavaScript code that runs *after* the request. It extracts the token from the JSON response body and saves it as an environment variable for subsequent requests.
    ```javascript
    // Get token from response body
    const token_data = pm.response.json();
    const token = token_data.access_token;

    // Set this as an environment variable
    if (token) {
        pm.environment.set("fdm_token", token);
        console.log("FDM Token set: " + token.substring(0, 10) + "...");
    } else {
        console.log("FDM Token not found in response.");
    }
    ```
6.  **Send the "Get FDM Token" request.** Check the Postman console (View -> Show Postman Console) to see the variables being set.

### 4.3 Making Subsequent Authenticated Requests

Now, for any other FDM API request (e.g., getting Access Policies):

1.  **Create a New Request:** Add a `GET` request, named "Get Access Policies".
2.  **URL:** `{{fdm_base_url}}/accesspolicies`
3.  **Headers:**
    *   `Content-Type`: `application/json`
    *   `Authorization`: `Bearer {{fdm_token}}` (This will automatically use the token set by the "Get FDM Token" request)
4.  **Send the request.** It should now be authenticated.

By using Postman's environment variables and test scripts, you can streamline your API testing workflow, avoiding manual copy-pasting of tokens.

---

## 5. Detecting Unauthorized Devices using Python Scripts

Detecting unauthorized devices is a critical security automation task. Python can integrate with various network sources to achieve this.

*   **How it works:**
    1.  **Data Collection:** Python script collects MAC addresses/IPs from trusted sources (e.g., ARP tables from switches via Netmiko, DHCP server logs, RADIUS authentication logs, network access control (NAC) systems like Cisco ISE API).
    2.  **Baseline/Whitelist:** Compare collected data against a known list of authorized devices (e.g., a database, a YAML file).
    3.  **Detection:** Identify devices present on the network that are not in the whitelist.
    4.  **Action:** Log the unauthorized device, send an alert, or even trigger an automated quarantine action (e.g., disable switch port via Netmiko, create a blocking rule on FTD via FDM API).

*   **Example (Conceptual):**
    ```python
    # Conceptual Python script for unauthorized device detection
    import requests 
    # from netmiko import ConnectHandler # For CLI data collection

    AUTHORIZED_DEVICES = ["AA:BB:CC:DD:EE:F1", "AA:BB:CC:DD:EE:F2"] # Example whitelist

    def get_mac_addresses_from_switch(device_ip, creds):
        # In reality, use Netmiko to 'show mac address-table' or query a NAC system.
        # For now, simulate
        print(f"Collecting MACs from {device_ip}...")
        return ["AA:BB:CC:DD:EE:F1", "DD:EE:FF:11:22:33"] # Simulated MACs

    def detect_unauthorized_devices(switch_ip):
        detected_macs = get_mac_addresses_from_switch(switch_ip)
        unauthorized_macs = []
        for mac in detected_macs:
            if mac not in AUTHORIZED_DEVICES:
                unauthorized_macs.append(mac)
        
        if unauthorized_macs:
            print(f"UNAUTHORIZED DEVICES DETECTED on {switch_ip}: {unauthorized_macs}")
            # Trigger alert (e.g., email, Slack)
            # Trigger quarantine (e.g., disable switch port via Netmiko)
            # Trigger FTD rule to block unauthorized MAC/IP (via FDM API)
        else:
            print(f"No unauthorized devices detected on {switch_ip}.")

    # Example usage:
    # detect_unauthorized_devices("192.168.1.1")
    ```

---

## 6. Summary and Key Takeaways

### Summary

Automating network security policies, particularly Access Control Lists and firewall rules, is essential for consistency, speed, and compliance. Cisco Firepower Threat Defense (FTD) devices, when managed directly without FMC, can be automated via the **Firepower Device Manager (FDM) API**. This RESTful API allows programmatic control over access control policies, network objects, and rule deployment. Python's `requests` library is key for interacting with this API, handling authentication and JSON payloads. Postman is an invaluable tool for testing and exploring these APIs. Beyond configuration, Python scripts can also play a vital role in detecting unauthorized devices by integrating data from various network sources and comparing it against baselines.

### Key Takeaways

*   **Security Automation Benefits:** Consistency, speed, accuracy, scalability, compliance.
*   **FTD Management without FMC:** Use **Firepower Device Manager (FDM) API** for direct RESTful automation of a single FTD appliance.
*   **FDM API Authentication:** Token-based (POST to `/api/fdm/v6/token`, use `access_token` in `Authorization: Bearer` header).
*   **Key FDM API Endpoints:** For Access Policies, Access Rules, Network Objects.
*   **Rule Management:** APIs allow programmatic creation, modification, and deletion of firewall rules.
*   **Deployment (FDM):** Changes are typically applied directly via API calls.
*   **Postman for API Testing:** Use Postman to explore, debug, and automate authentication for FDM API calls using environment variables and test scripts.
*   **Unauthorized Device Detection:** Python scripts can collect network data (MACs/IPs), compare against whitelists, and trigger alerts/actions.
*   **`requests` Library:** Your primary tool for interacting with RESTful APIs like FDM.

---