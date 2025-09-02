# Python Basics for Network Automation: Module 6 Theory Guide

## Infrastructure as Code (IaC) Automation with Python

**[Your Organization/Name]**
**September 01, 2025**

---

## 1. Introduction to Infrastructure as Code (IaC)

In previous modules, you've learned to automate tasks like sending commands, pushing configurations, and retrieving data from network devices. While effective, these were often direct, one-off operations. **Infrastructure as Code (IaC)** takes automation to the next level.

**What is IaC?**
IaC is the practice of managing and provisioning infrastructure (like networks, servers, databases) using code and software development techniques, rather than manual processes or interactive configurations. Instead of manually configuring a router via CLI, you write a text file (code) that describes the desired state of that router.

**Key Principles of IaC:**
*   **Declarative:** You describe *what* you want the infrastructure to look like, not *how* to achieve it. (e.g., "Interface GigabitEthernet1 should have IP 10.0.0.1," not "go to config mode, type interface Gi1, type ip address...").
*   **Version Control:** The infrastructure definition (the code) is stored in a version control system (like Git), allowing tracking changes, collaboration, and easy rollback.
*   **Automation:** Tools automatically apply the code to the infrastructure.
*   **Idempotence:** Applying the code multiple times yields the same result (no unintended side effects if the state is already correct).
*   **Single Source of Truth:** Your code repository becomes the definitive record of your network's configuration.

**Why IaC for Network Automation?**
*   **Consistency:** Eliminates configuration drift and human error.
*   **Speed:** Deploy changes rapidly and repeatedly.
*   **Reliability:** Changes are tested and versioned.
*   **Collaboration:** Teams can work together on network configurations.
*   **Auditability:** Every change is tracked, showing who did what and when.
*   **Rollback:** Easily revert to a previous working state if something goes wrong.

---

## 2. Describing Configuration Data with YAML

For IaC, you need a way to describe your network configuration in a structured, human-readable format. **YAML (YAML Ain't Markup Language)** is a popular choice.

*   **Why YAML?**
    *   **Human-readable:** Easy to read and write, using indentation for structure.
    *   **Machine-parsable:** Easily converted into Python dictionaries/lists.
    *   **Flexible:** Can represent complex data hierarchies.

*   **Example YAML Data for a Router:**
    ```yaml
    # network_data.yaml
    router_name: R1-Core
    loopback_ip: 1.1.1.1
    loopback_mask: 255.255.255.255
    ospf_process_id: 10
    ospf_network: 10.0.0.0
    ospf_wildcard: 0.0.0.255
    ospf_area: 0
    ```
    This YAML file defines the *variables* for your configuration.

---

## 3. Generating Configuration with Jinja2 Templates

Once you have your configuration data (in YAML), you need to turn it into actual device commands. **Jinja2** is a powerful templating engine used for this.

*   **What is Jinja2?**
    *   A templating language that allows you to embed variables, logic (like loops and conditions), and macros into text files (templates).
    *   It separates the data from the presentation (the configuration commands).

*   **How it works:**
    1.  You create a **Jinja2 template file** (e.g., `router_config.j2`) that contains your device configuration commands, but with placeholders for variables (e.g., `{{ router_name }}`).
    2.  You load your **data file** (e.g., `network_data.yaml`) into a Python dictionary.
    3.  You use Python to **render** the Jinja2 template, passing the data dictionary to it. Jinja2 then fills in the placeholders and executes any logic, producing the final configuration text.

*   **Example Jinja2 Template (`router_config.j2`):**
    ```jinja2
    hostname {{ router_name }}
    !
    interface Loopback0
     description Management Interface
     ip address {{ loopback_ip }} {{ loopback_mask }}
    !
    router ospf {{ ospf_process_id }}
     network {{ ospf_network }} {{ ospf_wildcard }} area {{ ospf_area }}
    !
    end
    ```

---

## 4. Pushing Configuration with NETCONF

After generating the configuration, you need a reliable way to push it to the network device. **NETCONF** is an excellent choice for IaC because it's transaction-based and uses structured data (XML).

*   **Why NETCONF for IaC?**
    *   **Transactional:** Changes are either fully applied or fully reverted. This prevents partial configurations.
    *   **Validation:** Devices can validate the configuration before applying it.
    *   **Rollback:** NETCONF has built-in mechanisms for rolling back configurations.
    *   **Structured:** Uses XML payloads, which are precise and machine-readable.
    *   **Python Library:** `ncclient` is a popular Python library for interacting with NETCONF.

*   **How it works (simplified):**
    1.  Establish a NETCONF session to the Cisco IOS XE router.
    2.  Build an XML payload containing the configuration you want to apply (often generated from your Jinja2 template).
    3.  Use `ncclient` to send an `edit-config` RPC (Remote Procedure Call) with your XML payload.
    4.  The device validates and applies the configuration.

*   **Example NETCONF XML Payload (for hostname change):**
    ```xml
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <hostname>NEW_ROUTER_HOSTNAME</hostname>
      </native>
    </config>
    ```
    This XML payload (which would be generated by Jinja2 from your YAML data) tells the device to set its hostname.

---

## 5. Version Control with Git

**Git** is a distributed version control system that tracks changes in any set of computer files. It is the cornerstone of IaC.

*   **Why Git for IaC?**
    *   **History:** Every change to your network configuration (the YAML data, Jinja2 templates) is recorded.
    *   **Collaboration:** Multiple engineers can safely work on the same network definitions.
    *   **Branching:** Create separate branches for new features or changes without affecting the main configuration.
    *   **Merging:** Combine changes from different branches.
    *   **Rollback:** Easily revert to any previous working state if a change causes issues. This is crucial for disaster recovery and maintaining network stability.

*   **Basic Git Workflow for IaC:**
    1.  `git clone <repository>`: Get the latest version of your network's code.
    2.  `git checkout -b <new-feature-branch>`: Create a new branch for your changes.
    3.  Modify YAML data or Jinja2 templates.
    4.  `git add .`: Stage your changes.
    5.  `git commit -m "Description of change"`: Save your changes to your local history.
    6.  `git push`: Upload your changes to the central repository.
    7.  Create a Pull Request (or Merge Request in GitLab) to merge your changes into the `main` (or `master`) branch.
    8.  `git revert <commit-hash>`: If a deployed change causes problems, use this to create a new commit that undoes the changes of a previous commit.

---

## 6. Verification with PyATS

After deploying a configuration, you need to verify that the network is in the desired state and that no unintended side effects occurred. **PyATS (Python Automated Test System)** is a powerful framework for network test automation.

*   **Why PyATS for IaC Verification?**
    *   **Network-aware:** Designed specifically for testing network devices.
    *   **Structured Output:** Can parse CLI output into structured Python objects, making verification easy.
    *   **Pre-checks/Post-checks:** Run tests *before* and *after* a change to ensure the network remains healthy.
    *   **Assertions:** Easily define conditions that must be met (e.g., "hostname should be X," "interface status should be up").

*   **Example PyATS Check:**
    You can use PyATS to connect to the device, run `show hostname`, and assert that the hostname matches the one defined in your YAML data.

---

## 7. Continuous Integration/Continuous Delivery (CI/CD) with GitLab

For fully automated IaC, you integrate all these tools into a CI/CD pipeline. **GitLab CI/CD** is a popular platform for this.

*   **What is CI/CD?**
    *   **Continuous Integration (CI):** Developers frequently merge their code changes into a central repository. Automated tests (like PyATS checks) are run after each merge to quickly detect integration issues.
    *   **Continuous Delivery/Deployment (CD):** Once changes pass automated tests, they are automatically prepared for release (delivery) or even automatically deployed to production (deployment).

*   **How GitLab CI/CD Works for IaC:**
    1.  **Code Commit:** An engineer pushes changes (YAML data, Jinja2 templates) to a Git repository in GitLab.
    2.  **Trigger Pipeline:** GitLab CI/CD automatically detects the change and triggers a predefined pipeline.
    3.  **Pipeline Stages:**
        *   **Linting/Validation:** Check YAML/Jinja2 syntax.
        *   **Generate Config:** Render Jinja2 templates with YAML data.
        *   **Pre-Checks (PyATS):** Verify current network state before change.
        *   **Deploy (NETCONF):** Push the generated configuration to the device.
        *   **Post-Checks (PyATS):** Verify the new network state and ensure no regressions.
        *   **Rollback (Optional):** If post-checks fail, automatically trigger a rollback to the previous configuration.
    4.  **Reporting:** Provide feedback on pipeline success/failure.

*   **Benefits of CI/CD for IaC:**
    *   Automated testing and deployment.
    *   Faster and more reliable change management.
    *   Reduced human error.
    *   Enables "GitOps" for network operations.

---

## 8. Summary and Key Takeaways

### Summary

Infrastructure as Code (IaC) transforms network management from manual processes to automated, version-controlled workflows. By describing network configurations in YAML, generating device-specific commands with Jinja2, and pushing them via transactional protocols like NETCONF, engineers gain consistency, speed, and reliability. Git provides essential version control, enabling collaboration and easy rollbacks. PyATS verifies the deployed state, and CI/CD platforms like GitLab automate the entire pipeline, from code commit to verified deployment, ushering in a "GitOps" approach for network operations.

### Key Takeaways

*   **IaC Core:** Manage infrastructure with code, enabling automation, version control, and idempotence.
*   **YAML:** Human-readable data format for defining network configurations.
*   **Jinja2:** Templating engine to generate device-specific configurations from YAML data.
*   **NETCONF:** Transactional protocol (XML-based) for pushing configurations reliably to devices.
*   **Git:** Essential for version control, collaboration, branching, merging, and especially for easy rollback.
*   **PyATS:** Network test automation framework for pre- and post-deployment verification.
*   **CI/CD (GitLab):** Automates the entire IaC workflow from code commit to deployment and verification, enabling a "GitOps" model.

---