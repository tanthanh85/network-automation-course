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

This module focuses on automating security policies, specifically using **Cisco Firepower Threat Defense (FTD)**, which is managed via the **Firepower Management Center (FMC) API**.

---

## 2. Automating Access Control List (ACL) Configurations

ACLs are fundamental security mechanisms. Automating their configuration ensures consistent application and reduces errors.

*   **Traditional CLI vs. API for ACLs:**
    *   **CLI:** Text-based, sequential commands. Difficult to verify rule order or conflicts programmatically.
    *   **API:** Structured data (JSON) for rules, allowing programmatic creation, modification, deletion, and reordering. The API handles the underlying CLI translation.

*   **Cisco Firepower Threat Defense (FTD) Access Control Policies:**
    *   FTD devices (like Firepower 1000/2100/4100/9300 series) are managed centrally by the Firepower Management Center (FMC).
    *   Access Control Lists (ACLs) on FTD are part of a larger **Access Control Policy (ACP)** configured on the FMC. An ACP is a set of ordered rules that determine if traffic is allowed or denied.
    *   When you automate FTD ACLs, you typically interact with the FMC API to manage these Access Control Policies and their rules.

---

## 3. Managing Firewall Rules Across Network Devices (Cisco FTD with FMC API)

The **Cisco Firepower Management Center (FMC) API** is a RESTful API that allows programmatic interaction with all aspects of FMC, including:
*   Access Control Policies (ACP) and rules
*   Network objects (IP addresses, networks, ports)
*   Interfaces, devices, deployments
*   Intrusion Policies, File Policies, etc.

### 3.1 FMC API Authentication

The FMC API uses a token-based authentication:
1.  Send a `POST` request to the `/api/fmc_platform/v1/auth/generatetoken` endpoint with username/password in the body.
2.  The response contains an `X-auth-access-token` in the header, which you use for subsequent requests in the `X-auth-access-token` header.
3.  The response also provides a `DOMAIN_UUID` and `X-token-expiration` (timestamp).

### 3.2 Key FMC API Endpoints for ACL Automation

*   **Access Control Policies (ACP):**
    *   `GET /api/fmc_config/v1/domain/{domainUUID}/policy/accesspolicies`
        *   Retrieves a list of all Access Control Policies. You'll need the `id` of the specific ACP you want to modify.
*   **Access Rules (within an ACP):**
    *   `GET /api/fmc_config/v1/domain/{domainUUID}/policy/accesspolicies/{accessPolicyId}/accessrules`
        *   Retrieves all rules within a specific ACP.
    *   `POST /api/fmc_config/v1/domain/{domainUUID}/policy/accesspolicies/{accessPolicyId}/accessrules`
        *   Creates a new access rule. The request body is JSON defining the rule (source/destination networks, ports, action, etc.).
    *   `PUT /api/fmc_config/v1/domain/{domainUUID}/policy/accesspolicies/{accessPolicyId}/accessrules/{accessRuleId}`
        *   Modifies an existing access rule.
    *   `DELETE /api/fmc_config/v1/domain/{domainUUID}/policy/accesspolicies/{accessPolicyId}/accessrules/{accessRuleId}`
        *   Deletes an access rule.
*   **Network Objects:**
    *   `GET /api/fmc_config/v1/domain/{domainUUID}/object/networks`
        *   Retrieves existing network objects (IPs, ranges, networks).
    *   `POST /api/fmc_config/v1/domain/{domainUUID}/object/networks`
        *   Creates new network objects. These objects are then referenced by their `id` in access rules.

### 3.3 Deployment

After making changes to an ACP via the API, the changes are staged on the FMC. They need to be **deployed** to the actual FTD devices for them to take effect.
*   `POST /api/fmc_platform/v1/domain/{domainUUID}/deployment/deploymentrequests`
    *   This endpoint is used to initiate a deployment. The payload specifies which devices to deploy to.

### 3.4 Example: Creating a Firewall Rule (Conceptual Flow)

1.  **Authenticate** to FMC API to get `X-auth-access-token` and `DOMAIN_UUID`.
2.  **Find the Access Control Policy ID:** `GET /api/fmc_config/.../accesspolicies` to get the `id` of your target ACP (e.g., "Default Access Policy").
3.  **Create Network Objects (if needed):** If your rule needs new IP addresses or networks not already defined, `POST` to `/api/fmc_config/.../object/networks` to create them. Note their `id`s.
4.  **Create the Access Rule:** `POST` to `/api/fmc_config/.../accessrules` with a JSON payload defining the rule. This payload will reference the `id`s of network objects, ports, etc.
    *   The rule JSON will specify `sourceNetworks`, `destinationNetworks`, `sourcePorts`, `destinationPorts`, `action` (e.g., `ALLOW`, `BLOCK`).
    *   You can also specify `newPosition` (e.g., `FIRST`, `LAST`, `BEFORE: <ruleId>`) to control rule order.
5.  **Deploy Changes:** `POST` to `/api/fmc_platform/.../deploymentrequests` to push the changes to the FTD device(s).

---

## 4. Detecting Unauthorized Devices using Python Scripts

While not directly part of FTD configuration, detecting unauthorized devices is a critical security automation task. Python can integrate with various network sources to achieve this.

*   **How it works:**
    1.  **Data Collection:** Python script collects MAC addresses/IPs from trusted sources (e.g., ARP tables from switches via Netmiko, DHCP server logs, RADIUS authentication logs, network access control (NAC) systems like Cisco ISE API).
    2.  **Baseline/Whitelist:** Compare collected data against a known list of authorized devices (e.g., a database, a YAML file).
    3.  **Detection:** Identify devices present on the network that are not in the whitelist.
    4.  **Action:** Log the unauthorized device, send an alert, or even trigger an automated quarantine action (e.g., disable switch port via Netmiko, block IP via firewall API).

*   **Example (Conceptual):**
    ```python
    # Conceptual Python script for unauthorized device detection
    import requests # For NAC/API
    # from netmiko import ConnectHandler # For CLI

    AUTHORIZED_DEVICES = ["AA:BB:CC:DD:EE:F1", "AA:BB:CC:DD:EE:F2"] # Example whitelist

    def get_mac_addresses_from_switch(device_ip, creds):
        # In reality, use Netmiko to 'show mac address-table'
        # For now, simulate
        print(f"Collecting MACs from {device_ip}...")
        return ["AA:BB:CC:DD:EE:F1", "DD:EE:FF:11:22:33"] # Simulated MACs

    def detect_unauthorized_devices(switch_ip, creds):
        detected_macs = get_mac_addresses_from_switch(switch_ip, creds)
        unauthorized_macs = []
        for mac in detected_macs:
            if mac not in AUTHORIZED_DEVICES:
                unauthorized_macs.append(mac)
        
        if unauthorized_macs:
            print(f"UNAUTHORIZED DEVICES DETECTED on {switch_ip}: {unauthorized_macs}")
            # Trigger alert (e.g., email, Slack)
            # Trigger quarantine (e.g., disable port via Netmiko)
            # Trigger FTD rule to block unauthorized MAC/IP (via CLI or API)
        else:
            print(f"No unauthorized devices detected on {switch_ip}.")

    # Example usage:
    # switch_creds = {"host": "192.168.1.1", "username": "admin", "password": "cisco"}
    # detect_unauthorized_devices("192.168.1.1", switch_creds)
    ```

---

## 5. Summary and Key Takeaways

### Summary

Automating network security policies, particularly Access Control Lists and firewall rules, is essential for consistency, speed, and compliance. Cisco Firepower Threat Defense (FTD) devices are managed via the Firepower Management Center (FMC) API, a RESTful interface that allows programmatic control over Access Control Policies, network objects, and deployments. Python's `requests` library is key for interacting with this API, handling authentication and JSON payloads. Beyond configuration, Python scripts can also play a vital role in detecting unauthorized devices by integrating data from various network sources and comparing it against baselines.

### Key Takeaways

*   **Security Automation Benefits:** Consistency, speed, accuracy, scalability, compliance.
*   **Cisco FTD/FMC API:** RESTful API for managing Firepower Threat Defense security policies.
*   **FMC API Authentication:** Token-based (POST to get token, use `X-auth-access-token` header).
*   **Key FMC API Endpoints:** For Access Control Policies, Access Rules, Network Objects, and Deployment.
*   **Rule Management:** APIs allow programmatic creation, modification, deletion, and ordering of firewall rules.
*   **Deployment:** Changes made via API must be deployed to FTD devices to take effect.
*   **Unauthorized Device Detection:** Python scripts can collect network data (MACs/IPs), compare against whitelists, and trigger alerts/actions.
*   **`requests` Library:** Your primary tool for interacting with RESTful APIs like FMC.

---