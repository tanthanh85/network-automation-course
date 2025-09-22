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

## Lab Setup: Initial IaC Components

This section focuses on setting up the core IaC components (YAML data, Jinja2 template, and a Python script to deploy the configuration) and verifying they work.

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
    touch deploy_config.py
    touch .gitignore
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
    ├── __init__.py
    ├── config.py
    ├── netmiko_iac_ops.py
    ├── deploy_config.py
    ├── network_data.yaml
    ├── .gitignore
    └── templates/
        └── hostname.j2
```
### Task 0.0: Populate `.gitignore`
add the following text to the file
```
na_env
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
        "host": "10.10.20.48", # e.g., 10.10.20.48 (from Cisco DevNet Sandbox)
        "username": "developer", # e.g., developer
        "password": "C1sco12345", # e.g., C1sco12345
        "secret": "C1sco12345", # For enable mode if needed
        "port": 22, # Default SSH port
    }
    ```
3.  Save `config.py`.

### Task 0.2: Populate `network_data.yaml`

This file will define the initial desired hostname for your router.

1.  Open `network_data.yaml` in your code editor.
2.  Add the following YAML content:
    ```yaml
    # network_data.yaml
    router_hostname: MyRouter
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
3.  Install `netmiko`, `PyYAML`, `Jinja2` (if not already installed from previous modules):
    ```bash
    pip install netmiko PyYAML Jinja2
    ```
4.  Open `netmiko_iac_ops.py` in your code editor.
5.  Add the following Python code:
    ```python
    # netmiko_iac_ops.py
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoBaseException
    import logging
    from config import IOSXE_NETMIKO_INFO # Import device info

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

        except (NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoBaseException) as e:
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
                
                output = net_connect.send_command("show run | in hostname")
                # For a simple 'show hostname', the output is usually just the hostname.
                # We strip whitespace to clean it up.
                import re
                hostname = re.search(r"hostname\s+(.*)", output)    
                
                logging.info(f"Retrieved hostname: {hostname}")
                return hostname

        except (NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoBaseException) as e:
            logging.error(f"Netmiko Error getting hostname from {host}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected Error connecting or getting hostname from {host}: {e}")
            return None
    ```
6.  Save `netmiko_iac_ops.py`.

### Task 0.5: Populate `deploy_config.py`

This is the script that will load data, generate config, and push it to the router. This script will be run multiple times during the Git workflow.

1.  Open `deploy_config.py` in your code editor.
2.  Add the following Python code:
    ```python
    # deploy_config.py
    import yaml
    from jinja2 import Environment, FileSystemLoader
    import logging
    import os
    import time

    from netmiko_iac_ops import push_config_netmiko, get_hostname_netmiko

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

    def deploy_current_config():
        """
        Loads network data, generates config, and pushes it via Netmiko.
        Also performs a basic hostname verification.
        """
        logging.info(f"\n--- Starting Deployment Workflow ---")

        # 1. Load network data
        network_data = load_network_data("network_data.yaml")
        if not network_data:
            logging.error("Deployment aborted: Could not load network data.")
            return False

        expected_hostname = network_data.get('router_hostname')
        if not expected_hostname:
            logging.error("Deployment aborted: 'router_hostname' not found in network data.")
            return False

        # 2. Generate configuration
        # Netmiko needs a list of commands, so split the generated string by lines
        config_payload_cli = generate_config_from_template(network_data, "hostname.j2").splitlines()
        # Remove any empty strings from the list if splitting creates them
        config_payload_cli = [line for line in config_payload_cli if line.strip()]

        if not config_payload_cli:
            logging.error("Deployment aborted: Generated configuration is empty.")
            return False
        
        logging.info(f"Generated config payload (CLI):\n{config_payload_cli}")

        # 3. Push configuration via Netmiko
        push_success = push_config_netmiko(config_payload_cli)
        if not push_success:
            logging.error("Deployment aborted: Failed to push configuration via Netmiko.")
            return False

        # Give router some time to apply config and update state
        time.sleep(5) 

        # 4. Verify status (get hostname and compare)
        logging.info("Verifying current hostname on device...")
        actual_hostname = get_hostname_netmiko()
        
        if actual_hostname == expected_hostname:
            logging.info(f"--- Deployment COMPLETED SUCCESSFULLY ---")
            logging.info(f"Verification: Hostname matches. Actual: '{actual_hostname}', Expected: '{expected_hostname}'")
            return True
        else:
            logging.error(f"--- Deployment FAILED VERIFICATION ---")
            logging.error(f"Verification: Hostname MISMATCH! Actual: '{actual_hostname}', Expected: '{expected_hostname}'")
            return False

    if __name__ == '__main__':
        deploy_current_config()
    ```
3.  Save `deploy_config.py`.

---

## Lab Workflow Execution

This section guides you through the actual IaC workflow using Git and your Python script.

### Task 1.1: Initial Deployment

1.  **Ensure your `na_env` virtual environment is active.**
2.  **Navigate to your `module6_iac_lab` directory.**
3.  **Run the deployment script:**
    ```bash
    python deploy_config.py
    ```
    *Expected Output (console):*
    ```
    --- Starting Deployment Workflow ---
    Successfully loaded data from network_data.yaml.
    Configuration generated from template hostname.j2.
    Generated config payload (CLI):
    ['hostname MyRouter']
    Connecting to YOUR_IOSXE_IP via Netmiko...
    Connected to YOUR_IOSXE_IP. Pushing configuration...
    Configuration push output:
    config terminal
    Enter configuration commands, one per line.  End with CNTL/Z.
    YOUR_IOSXE_PROMPT(config)#hostname MyRouter
    YOUR_IOSXE_PROMPT(config)#end
    YOUR_IOSXE_PROMPT#
    Configuration successfully pushed to YOUR_IOSXE_IP.
    Verifying current hostname on device...
    Connecting to YOUR_IOSXE_IP via Netmiko to get hostname...
    Connected to YOUR_IOSXE_IP. Getting hostname...
    Retrieved hostname: MyRouter
    --- Deployment COMPLETED SUCCESSFULLY ---
    Verification: Hostname matches. Actual: 'MyRouter', Expected: 'MyRouter'
    ```
4.  **Manual Verification:** Log in to your IOS XE router via SSH/console and verify that its hostname is now `MyRouter`.
    ```
    MyRouter# show run | in hostname
    MyRouter
    ```

### Task 1.2: Git Initialization and Initial Commit

1.  **Initialize a Git repository** in your `module6_iac_lab` directory:
    ```bash
    git init
    ```
2.  **Tell git who you are (if you have not done so)**
    ```bash
    git config --global user.name "Your Name"
    git config --global user.email "your.email@example.com"
    ```
    Then check your config
    ```bash
    git config --list
    ```

3.  **Add all current files** to the Git staging area:
    ```bash
    git add .
    ```
4.  **Commit the initial state** of your IaC project:
    ```bash
    git commit -m "Initial deployment of router hostname: MyRouter"
    ```
    *Expected Output:* Git will report that it created a new commit and list the files added.

### Task 1.3: Change the hostname to MyRouter1
1.  Open `network_data.yaml` in your code editor.
2.  Add the following YAML content:
    ```yaml
    # network_data.yaml
    router_hostname: MyRouter1
    ```
3.  Save `network_data.yaml`.

4.  **Run the deployment script:**
    ```bash
    python deploy_config.py
    ```
    *Expected Output (console):*
    ```
    --- Starting Deployment Workflow ---
    Successfully loaded data from network_data.yaml.
    Configuration generated from template hostname.j2.
    Generated config payload (CLI):
    ['hostname MyRouter1']
    Connecting to YOUR_IOSXE_IP via Netmiko...
    Connected to YOUR_IOSXE_IP. Pushing configuration...
    Configuration push output:
    config terminal
    Enter configuration commands, one per line.  End with CNTL/Z.
    YOUR_IOSXE_PROMPT(config)#hostname MyRouter1
    YOUR_IOSXE_PROMPT(config)#end
    YOUR_IOSXE_PROMPT#
    Configuration successfully pushed to YOUR_IOSXE_IP.
    Verifying current hostname on device...
    Connecting to YOUR_IOSXE_IP via Netmiko to get hostname...
    Connected to YOUR_IOSXE_IP. Getting hostname...
    Retrieved hostname: MyRouter1
    --- Deployment COMPLETED SUCCESSFULLY ---
    Verification: Hostname matches. Actual: 'MyRouter1', Expected: 'MyRouter1'
    ```
5.  **Add all current files** to the Git staging area:
    ```bash
    git add .
    ```
6.  **Commit the the new change** of your IaC project:
    ```bash
    git commit -m "Change router hostname: MyRouter1"
    ```
    *Expected Output:* Git will report that it created a new commit and list the files added.


### Task 1.4: Create a New Feature Branch

It's good practice to make changes in a separate branch.

1.  **Create and switch to a new branch:**
    ```bash
    git checkout -b feature/change-hostname
    ```
    *Expected Output:* `Switched to a new branch 'feature/change-hostname'`

### Task 1.4: Modify Configuration Data

Now, let's change the desired hostname in your `network_data.yaml`.

1.  Open `network_data.yaml` in your code editor.
2.  **Change the hostname** from `MyRouter1` to `MyRouter2`:
    ```yaml
    # network_data.yaml
    router_hostname: MyRouter2
    ```
3.  Save `network_data.yaml`.

### Task 1.5: Commit the Change

1.  **Add the modified file** to the Git staging area:
    ```bash
    git add network_data.yaml
    ```
2.  **Commit the change** to your `feature/change-hostname` branch:
    ```bash
    git commit -m "Feature: Change router hostname to MyRouter2"
    ```
    *Expected Output:* Git will report that it created a new commit.

### Task 1.6: Merge to Main and Deploy New Configuration

In a real CI/CD pipeline, this merge would trigger automated deployment. Here, we'll merge and then manually run our deploy script.

1.  **Switch back to the `main` branch:**
    ```bash
    git checkout main
    ```
2.  **Merge your feature branch** into `main`:
    ```bash
    git merge feature/change-hostname
    ```
    *Expected Output:* Git will report that it fast-forwarded and merged the branch.

3.  **Run the deployment script again.** This will pick up the new hostname from `network_data.yaml` (which is now `MyRouter-New` in the `main` branch) and push it to the router.
    ```bash
    python deploy_config.py
    ```
    *Expected Output (console):*
    ```
    --- Starting Deployment Workflow ---
    Successfully loaded data from network_data.yaml.
    Configuration generated from template hostname.j2.
    Generated config payload (CLI):
    ['hostname MyRouter-New']
    Connecting to YOUR_IOSXE_IP via Netmiko...
    Connected to YOUR_IOSXE_IP. Pushing configuration...
    Configuration push output:
    config terminal
    Enter configuration commands, one per line.  End with CNTL/Z.
    YOUR_IOSXE_PROMPT(config)#hostname MyRouter2
    YOUR_IOSXE_PROMPT(config)#end
    YOUR_IOSXE_PROMPT#
    Configuration successfully pushed to YOUR_IOSXE_IP.
    Verifying current hostname on device...
    Connecting to YOUR_IOSXE_IP via Netmiko to get hostname...
    Connected to YOUR_IOSXE_IP. Getting hostname...
    Retrieved hostname: MyRouter2
    --- Deployment COMPLETED SUCCESSFULLY ---
    Verification: Hostname matches. Actual: 'MyRouter2', Expected: 'MyRouter2'
    ```
4.  **Manual Verification:** Log in to your IOS XE router via SSH/console and verify that its hostname is now `MyRouter2`.
    ```
    MyRouter2# show run | in hostname
    MyRouter2
    ```

### Task 1.7: Simulate Rollback

Imagine `MyRouter2` caused an unexpected issue. We need to revert to `MyRouter1`.

1.  **Find the commit hash** of the commit where you set the hostname to `MyRouter1`.
    ```bash
    git log --oneline
    ```
    *Expected Output:* You'll see a list of commits. Find the one with message "Feature: Change router hostname to MyRouter2". Copy its 7-character hash (e.g., `a1b2c3d`).

2.  **Revert to that commit:**
    ```bash
    git revert <paste_the_commit_hash_here>
    ```
    *Example:* `git revert a1b2c3d`
    *Expected Output:* Git will open your default text editor (like Vim or Nano) to allow you to edit the commit message for the revert. Just save and close the file without changes (or add a note like "Revert to initial hostname"). Git will then report that it created a new commit.
    *Observation:* If you now open `network_data.yaml`, you'll see its content has automatically changed back to `router_hostname: MyRouter1`.

### Task 1.8: Deploy Rolled Back Configuration

1.  **Run the deployment script again.** This will pick up the `MyRouter-Initial` hostname from the reverted `network_data.yaml` and push it to the router.
    ```bash
    python deploy_config.py
    ```
    *Expected Output (console):*
    ```
    --- Starting Deployment Workflow ---
    Successfully loaded data from network_data.yaml.
    Configuration generated from template hostname.j2.
    Generated config payload (CLI):
    ['hostname MyRouter-Initial']
    Connecting to YOUR_IOSXE_IP via Netmiko...
    Connected to YOUR_IOSXE_IP. Pushing configuration...
    Configuration push output:
    config terminal
    Enter configuration commands, one per line.  End with CNTL/Z.
    YOUR_IOSXE_PROMPT(config)#hostname MyRouter-Initial
    YOUR_IOSXE_PROMPT(config)#end
    YOUR_IOSXE_PROMPT#
    Configuration successfully pushed to YOUR_IOSXE_IP.
    Verifying current hostname on device...
    Connecting to YOUR_IOSXE_IP via Netmiko to get hostname...
    Connected to YOUR_IOSXE_IP. Getting hostname...
    Retrieved hostname: MyRouter1
    --- Deployment COMPLETED SUCCESSFULLY ---
    Verification: Hostname matches. Actual: 'MyRouter1', Expected: 'MyRouter1
    ```
2.  **Manual Verification:** Log in to your IOS XE router via SSH/console and verify that its hostname is now `MyRouter1` again.
    ```
    MyRouter# show run | in hostname
    MyRouter1
    ```

---

## Conclusion

You've now completed Module 6 and gained practical experience with Infrastructure as Code (IaC) principles! You can now:

*   Describe network configurations using YAML.
*   Generate network configurations using Jinja2 templates.
*   Push configurations to Cisco IOS XE routers using Netmiko.
*   Utilize Git for version control of your network configurations.
*   Simulate a complete IaC workflow, including deployment of changes and rollback to a previous state.

IaC is a foundational practice for modern, scalable, and reliable network automation. This module has provided you with the core tools and concepts to start implementing IaC in your own environment.

**Keep Automating!**

---