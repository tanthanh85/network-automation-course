# Python Basics for Network Automation: Module 6 Lab Guide

## Infrastructure as Code (IaC) Automation with Python - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 6 of the Python Basics for Network Automation Lab Guide! In this module, you will get hands-on with Infrastructure as Code (IaC) principles. You will learn to define network configurations in YAML, generate device commands using Jinja2, and push them via Netmiko. We will then use Git for version control to simulate a full IaC workflow, including a rollback scenario.

**It is crucial that you replace the dummy values for your IOS XE router with its actual IP address, username, and password to make the code functional.**

**Lab Objectives:**
*   Describe configuration data using a YAML file.
*   Use a Jinja2 template to generate configuration.
*   Use Netmiko to push configuration to a Cisco IOS XE router.
*   Use Git for version control of your configuration data.
*   Simulate a complete IaC workflow: branch, modify data, push config, and rollback.

**Prerequisites:**
*   Completion of Module 1, Module 2, Module 3, Module 4, and Module 5 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   An active internet connection.
*   **Access to a Cisco IOS XE router with SSH enabled (e.g., Cisco DevNet Sandboxes).** You will need its IP, username, and password.
*   **Git installed** on your local machine.

Let's build some IaC!

---

## Lab Setup: Project Structure

For this module, we will create a dedicated project structure.

1.  **Navigate** to your main `network_automation_labs` directory.
2.  **Create a new directory** for this module's labs:
    ```bash
    mkdir module6_iac_lab
    cd module6_iac_lab
    ```
3.  **Inside `module6_iac_lab`, create the following directories:**
    ```bash
    mkdir templates
    ```
4.  **Inside `module6_iac_lab`, create the following empty Python files:**
    ```bash
    touch __init__.py
    touch config.py
    touch netmiko_iac_ops.py
    touch main_iac_workflow.py
    ```
5.  **Inside `module6_iac_lab`, create the following data and template files:**
    ```bash
    touch network_data.yaml
    touch templates/hostname.j2
    ```

Your directory structure should now look like this:
```
network_automation_labs/
└── module6_iac_lab/
├── init.py
├── config.py
├── netmiko_iac_ops.py
├── main_iac_workflow.py
├── network_data.yaml
└── templates/
└── hostname.j2
```
### Task 0.1: Populate `config.py`

This file will store your IOS XE Netmiko connection details.

1.  Open `config.py` in your code editor.
2.  Add the following Python code. **REPLACE THE DUMMY VALUES WITH YOUR ACTUAL LAB IOS XE ROUTER DETAILS!**
    ```python
    # config.py

    # --- IOS XE Netmiko Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
    # This router should be reachable and have SSH enabled.
    IOSXE_NETMIKO_INFO = {
        "device_type": "cisco_ios",
        "host": "YOUR_IOSXE_IP", # e.g., 10.10.20.40 (from Cisco DevNet Sandbox)
        "username": "YOUR_IOSXE_USERNAME", # e.g., developer
        "password": "YOUR_IOSXE_PASSWORD", # e.g., C!sco12345
        "secret": "YOUR_IOSXE_ENABLE_PASSWORD", # For enable mode if needed
        "port": 22, # Default SSH port
    }
    ```
3.  Save `config.py`.

### Task 0.2: Populate `network_data.yaml`

This file will define the desired hostname for your router.

1.  Open `network_data.yaml` in your code editor.
2.  Add the following YAML content:
    ```yaml
    # network_data.yaml
    router_hostname: MyRouter-Initial
    ```
3.  Save `network_data.yaml`.

### Task 0.3: Populate `templates/hostname.j2`

This Jinja2 template will generate the CLI commands to change the hostname.

1.  Open `templates/hostname.j2` in your code editor.
2.  Add the following Jinja2 template code:
    ```jinja2
    hostname {{ router_hostname }}
    ```
3.  Save `templates/hostname.j2`.

### Task 0.4: Populate `netmiko_iac_ops.py`

This file will contain functions for Netmiko operations (push config and get hostname).

1.  Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).
2.  Navigate into your `module6_iac_lab` directory:
    ```bash
    cd module6_iac_lab
    ```
3.  Install `netmiko` and `PyYAML` (if not already installed from previous modules):
    ```bash
    pip install netmiko PyYAML Jinja2
    ```
4.  Open `netmiko_iac_ops.py` in your code editor.
5.  Add the following Python code:
    ```python
    # netmiko_iac_ops.py
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoException
    import logging
    from .config import IOSXE_NETMIKO_INFO # Import device info

    # Configure logging for better visibility
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def push_config_netmiko(config_commands):
        """
        Pushes a list of configuration commands to the IOS XE router via Netmiko.
        Returns True on success, False on failure.
        """
        host = IOSXE_NETMIKO_INFO['host']
        
        try:
            logging.info(f"Connecting to {host} via Netmiko...")
            with ConnectHandler(**IOSXE_NETMIKO_INFO) as net_connect:
                logging.info(f"Connected to {host}. Pushing configuration...")
                
                # send_config_set handles entering/exiting config mode
                output = net_connect.send_config_set(config_commands)
                
                logging.info(f"Configuration push output:\n{output}")
                logging.info(f"Configuration successfully pushed to {host}.")
                return True

        except (NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoException) as e:
            logging.error(f"Netmiko Error pushing config to {host}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected Error connecting or pushing config to {host}: {e}")
            return False

    def get_hostname_netmiko():
        """
        Retrieves the hostname from the IOS XE router via Netmiko.
        Returns the hostname string or None on failure.
        """
        host = IOSXE_NETMIKO_INFO['host']
        
        try:
            logging.info(f"Connecting to {host} via Netmiko to get hostname...")
            with ConnectHandler(**IOSXE_NETMIKO_INFO) as net_connect:
                logging.info(f"Connected to {host}. Getting hostname...")
                
                output = net_connect.send_command("show hostname")
                # For a simple 'show hostname', the output is usually just the hostname.
                # We strip whitespace to clean it up.
                hostname = output.strip()
                
                logging.info(f"Retrieved hostname: {hostname}")
                return hostname

        except (NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoException) as e:
            logging.error(f"Netmiko Error getting hostname from {host}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected Error connecting or getting hostname from {host}: {e}")
            return None
    ```
6.  Save `netmiko_iac_ops.py`.

### Task 0.5: Populate `main_iac_workflow.py`

This is the main orchestration script that ties everything together.

1.  Open `main_iac_workflow.py` in your code editor.
2.  Add the following Python code:
    ```python
    # main_iac_workflow.py
    import yaml
    from jinja2 import Environment, FileSystemLoader
    import logging
    import os
    import time

    from .netmiko_iac_ops import push_config_netmiko, get_hostname_netmiko

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_network_data(file_path="network_data.yaml"):
        """Loads network configuration data from a YAML file."""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            logging.info(f"Successfully loaded data from {file_path}.")
            return data
        except Exception as e:
            logging.error(f"Error loading network data from {file_path}: {e}")
            return None

    def generate_config_from_template(data, template_file="hostname.j2"):
        """Generates configuration from Jinja2 template and data."""
        try:
            # Set up Jinja2 environment to load templates from 'templates' directory
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template(template_file)
            
            # Render the template with the provided data
            config_payload = template.render(data)
            logging.info(f"Configuration generated from template {template_file}.")
            return config_payload
        except Exception as e:
            logging.error(f"Error generating config from template {template_file}: {e}")
            return None

    def run_iac_workflow(data_file="network_data.yaml"):
        """
        Executes the IaC workflow:
        1. Load network data.
        2. Generate configuration.
        3. Push configuration via Netmiko.
        4. Verify status (by getting hostname).
        """
        logging.info(f"\n--- Starting IaC Workflow for {data_file} ---")

        # 1. Load network data
        network_data = load_network_data(data_file)
        if not network_data:
            logging.error("Workflow aborted: Could not load network data.")
            return False

        expected_hostname = network_data.get('router_hostname')
        if not expected_hostname:
            logging.error("Workflow aborted: 'router_hostname' not found in network data.")
            return False

        # 2. Generate configuration
        # Netmiko needs a list of commands, so split the generated string by lines
        config_payload_cli = generate_config_from_template(network_data, "hostname.j2").splitlines()
        # Remove any empty strings from the list if splitting creates them
        config_payload_cli = [line for line in config_payload_cli if line.strip()]

        if not config_payload_cli:
            logging.error("Workflow aborted: Generated configuration is empty.")
            return False
        
        logging.info(f"Generated config payload (CLI):\n{config_payload_cli}")

        # 3. Push configuration via Netmiko
        push_success = push_config_netmiko(config_payload_cli)
        if not push_success:
            logging.error("Workflow aborted: Failed to push configuration via Netmiko.")
            return False

        # Give router some time to apply config and update state
        time.sleep(5) 

        # 4. Verify status (get hostname and compare)
        logging.info("Verifying current hostname on device...")
        actual_hostname = get_hostname_netmiko()
        
        if actual_hostname == expected_hostname:
            logging.info(f"--- IaC Workflow for {data_file} COMPLETED SUCCESSFULLY ---")
            logging.info(f"Verification: Hostname matches. Actual: '{actual_hostname}', Expected: '{expected_hostname}'")
            return True
        else:
            logging.error(f"--- IaC Workflow for {data_file} FAILED VERIFICATION ---")
            logging.error(f"Verification: Hostname MISMATCH! Actual: '{actual_hostname}', Expected: '{expected_hostname}'")
            return False

    if __name__ == '__main__':
        # --- Initial Run ---
        print("\n=== Phase 1: Initial Deployment ===")
        success = run_iac_workflow("network_data.yaml")
        if success:
            print("\nInitial deployment successful. Router hostname should now be 'MyRouter-Initial'.")
        else:
            print("\nInitial deployment failed. Check logs for errors.")
        
        # --- Git Simulation Steps (Manual) ---
        print("\n\n=== Phase 2: Simulate Git Workflow and Change ===")
        print("Please perform the following manual Git steps in your terminal inside 'module6_iac_lab':")
        print("1. Initialize Git:           git init")
        print("2. Add and commit initial:   git add . && git commit -m 'Initial hostname config'")
        print("3. Create new branch:        git checkout -b feature/new-hostname")
        print("4. >>> Now, MANUALLY EDIT 'network_data.yaml' and change 'MyRouter-Initial' to 'MyRouter-New' <<<")
        print("5. Add and commit change:    git add . && git commit -m 'Feature: Change hostname to new'")
        print("6. Merge to main:            git checkout main && git merge feature/new-hostname")
        print("7. >>> After completing these steps, press Enter to continue Python script... <<<")
        input() # Wait for user to complete Git steps

        print("\n=== Phase 3: Deploy New Hostname ===")
        success_new = run_iac_workflow("network_data.yaml")
        if success_new:
            print("\nNew hostname deployment successful. Router hostname should now be 'MyRouter-New'.")
        else:
            print("\nNew hostname deployment failed. Check logs.")
        
        # --- Simulate Rollback ---
        print("\n\n=== Phase 4: Simulate Rollback ===")
        print("Simulating an issue and reverting to previous working state.")
        print("Please perform the following manual Git steps in your terminal inside 'module6_iac_lab':")
        print("1. Find the commit hash for 'Initial hostname config': git log --oneline")
        print("   (It will be the first commit, copy its 7-char hash, e.g., 'a1b2c3d')")
        print("2. Revert to that commit:    git revert <paste-commit-hash-here>")
        print("   (Git will open an editor for commit message, save and close it.)")
        print("3. >>> After completing these steps, press Enter to continue Python script... <<<")
        input() # Wait for user to complete Git steps

        print("\n=== Phase 5: Re-deploy Rolled Back Configuration ===")
        print("This will push the hostname from the reverted commit back to the router.")
        success_rollback = run_iac_workflow("network_data.yaml")
        if success_rollback:
            print("\nRollback deployment successful. Router hostname should now be 'MyRouter-Initial' again.")
        else:
            print("\nRollback deployment failed. Check logs.")
        
        print("\n--- IaC Lab Workflow Complete ---")
    ```
3.  Save `main_iac_workflow.py`.

---

## Lab Workflow Execution

Now, let's run the entire IaC workflow. You will be interacting with both your terminal (for Git commands) and the Python script.

1.  **Ensure your `na_env` virtual environment is active.**
2.  **Navigate to your `module6_iac_lab` directory.**
3.  **Start the main workflow script:**
    ```bash
    python main_iac_workflow.py
    ```
4.  **Follow the on-screen instructions** in your terminal. The Python script will pause and wait for you to execute Git commands and press Enter to proceed.

This comprehensive lab will give you a hands-on feel for the entire IaC pipeline, from data definition and templating to deployment, verification, and rollback using Git and network automation tools.

---

## Conclusion

You've now completed Module 6 and gained practical experience with Infrastructure as Code (IaC) principles! You can now:

*   Describe network configurations using YAML.
*   Generate network configurations using Jinja2 templates.
*   Push configurations to Cisco IOS XE routers using Netmiko.
*   Utilize Git for version control of your network configurations.
*   Perform basic network status verification.
*   Understand and simulate a complete IaC workflow, including rollback.

IaC is a foundational practice for modern, scalable, and reliable network automation. This module has provided you with the core tools and concepts to start implementing IaC in your own environment.

**Keep Automating!**

---