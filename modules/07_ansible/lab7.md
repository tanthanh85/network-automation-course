# Python Basics for Network Automation: Module 7 Lab Guide

## Identification of Workflows Automated using Ansible - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 7 of the Python Basics for Network Automation Lab Guide! In this module, you will get hands-on with **Ansible** for network automation. You will learn to use Ansible playbooks for configuration management and see how Python scripts can integrate with Ansible. We will also compare a simple task done with Netmiko versus Ansible.

**It is crucial that you replace the dummy values for your IOS XE router with its actual IP address, username, and password to make the code functional.**

**Lab Objectives:**
*   Install Ansible.
*   Create an Ansible inventory file.
*   Write a basic Ansible playbook to configure a Cisco IOS XE router.
*   Run an Ansible playbook.
*   Integrate Python with Ansible by calling a playbook from a Python script.
*   Compare a configuration task using Netmiko vs. Ansible.

**Prerequisites:**
*   Completion of Module 1 through Module 6 Labs.
*   Your `na_env` virtual environment activated.
*   A code editor (VS Code recommended).
*   An active internet connection.
*   **Access to a Cisco IOS XE router with SSH enabled (e.g., Cisco DevNet Sandboxes).** You will need its IP, username, and password.

Let's automate with Ansible!

---

## Lab Setup: Project Structure

For this module, we will create a dedicated project structure.

1.  **Navigate** to your main `network_automation_labs` directory.
2.  **Create a new directory** for this module's labs:
    ```bash
    mkdir module7_ansible_lab
    cd module7_ansible_lab
    ```
3.  **Inside `module7_ansible_lab`, create the following empty files:**
    ```bash
    touch config.py
    touch inventory.yaml
    touch playbook_hostname.yaml
    touch playbook_loopback.yaml
    touch playbook_full_config.yaml
    touch python_ansible_deploy.py
    touch python_netmiko_workflow.py
    ```

Your directory structure should now look like this:
```
network_automation_labs/
└── module7_ansible_lab/
├── config.py
├── inventory.yaml
├── playbook_hostname.yaml
├── playbook_loopback.yaml
├── playbook_full_config.yaml
├── python_ansible_deploy.py
└── python_netmiko_workflow.py
```
### Task 0.1: Install Ansible and Netmiko

1.  Ensure your `na_env` virtual environment is active (from `network_automation_labs` directory).
2.  Navigate into your `module7_ansible_lab` directory:
    ```bash
    cd module7_ansible_lab
    ```
3.  Install Ansible and Netmiko:
    ```bash
    pip install ansible netmiko
    ```
    *Expected Observation:* Ansible, Netmiko, and their dependencies will be installed. You should see "Successfully installed..." messages.

### Task 0.2: Populate `config.py`

This file will store your IOS XE device credentials for both Netmiko and Ansible.

1.  Open `config.py` in your code editor.
2.  Add the following Python code. **REPLACE THE DUMMY VALUES WITH YOUR ACTUAL LAB IOS XE ROUTER DETAILS!**
    ```python
    # config.py

    # --- IOS XE Device Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
    # This router should be reachable and have SSH enabled.
    IOSXE_DEVICE_INFO = {
        "host": "YOUR_IOSXE_IP", # e.g., 10.10.20.40 (from Cisco DevNet Sandbox)
        "username": "YOUR_IOSXE_USERNAME", # e.g., developer
        "password": "YOUR_IOSXE_PASSWORD", # e.g., C!sco12345
        "secret": "YOUR_IOSXE_ENABLE_PASSWORD", # For enable mode if needed (Netmiko)
        "port": 22, # Default SSH port
    }
    ```
3.  Save `config.py`.

### Task 0.3: Populate `inventory.yaml`

This file will define your network devices for Ansible.

1.  Open `inventory.yaml` in your code editor.
2.  Add the following YAML content. **REPLACE THE DUMMY IP WITH YOUR ACTUAL LAB IOS XE ROUTER IP.**
    ```yaml
    # inventory.yaml
    all:
      hosts:
        YOUR_IOSXE_IP: # Replace with your router's IP
          ansible_host: YOUR_IOSXE_IP # Redundant but good for clarity
          # Using environment variables for credentials is more secure.
          # Ansible will look for ANSIBLE_USER, ANSIBLE_PASSWORD, ANSIBLE_ENABLE_PASS
          # in the environment where ansible-playbook is run.
          # Fallback to dummy values if env vars are not set (for testing purposes).
          ansible_user: "{{ lookup('env', 'ANSIBLE_USER') | default('dummy_user') }}"
          ansible_password: "{{ lookup('env', 'ANSIBLE_PASSWORD') | default('dummy_password') }}"
          ansible_become: yes # Use 'enable' mode for configuration
          ansible_become_method: enable
          ansible_become_pass: "{{ lookup('env', 'ANSIBLE_ENABLE_PASS') | default('dummy_enable') }}"
          ansible_network_os: ios # Specify network OS for Cisco IOS devices
          ansible_connection: network_cli # Use network_cli connection plugin
          ansible_port: 22 # Explicitly define SSH port
    ```
3.  Save `inventory.yaml`.

---

## Lab 1: Basic Ansible Playbook for Configuration Management

**Objective:** Use Ansible to change the hostname of your Cisco IOS XE router.

### Task 1.1: Create Ansible Playbook to Change Hostname

1.  Open `playbook_hostname.yaml` in your code editor.
2.  Add the following YAML content:
    ```yaml
    # playbook_hostname.yaml
    ---
    - name: Configure hostname on Cisco IOS XE
      hosts: all # Apply to all hosts in inventory
      gather_facts: false # No need to gather facts for this simple task
      
      vars:
        new_hostname: "Ansible-Managed-Router" # Define the desired hostname

      tasks:
        - name: Set router hostname
          ios_config:
            lines:
              - hostname {{ new_hostname }} # Use the variable
            provider: "{{ lookup('vars', 'ansible_network_cli_connection') }}" # Use connection details from inventory
            save_when: changed # Save config if changes are made
          register: hostname_result # Store task result for inspection
          
        - name: Print hostname change result
          debug:
            msg: "Hostname configuration result: {{ hostname_result }}"
    ```
3.  Save `playbook_hostname.yaml`.

### Task 1.2: Run the Ansible Playbook

1.  **Set environment variables for credentials** (if you haven't already). Replace with your actual credentials.
    ```bash
    export ANSIBLE_USER="YOUR_IOSXE_USERNAME"
    export ANSIBLE_PASSWORD="YOUR_IOSXE_PASSWORD"
    export ANSIBLE_ENABLE_PASS="YOUR_IOSXE_ENABLE_PASSWORD"
    ```
2.  **Run the playbook** from your `module7_ansible_lab` directory:
    ```bash
    ansible-playbook -i inventory.yaml playbook_hostname.yaml
    ```
    *Expected Output (if successful):*
    ```
    PLAY [Configure hostname on Cisco IOS XE] **************************************

    TASK [Set router hostname] *****************************************************
    changed: [YOUR_IOSXE_IP] => {"ansible_facts": {"discovered_interpreter_python": "/usr/bin/python"}, "changed": true, "commands": ["hostname Ansible-Managed-Router"], "diff": [...], "invocation": {...}, "stderr": "", "stderr_lines": [], "stdout": "configure terminal\nhostname Ansible-Managed-Router\nend\n", "stdout_lines": ["configure terminal", "hostname Ansible-Managed-Router", "end"]}

    TASK [Print hostname change result] ********************************************
    ok: [YOUR_IOSXE_IP] => {
        "msg": "Hostname configuration result: {'changed': True, 'stdout': 'configure terminal\\nhostname Ansible-Managed-Router\\nend\\n', ...}"
    }

    PLAY RECAP *********************************************************************
    YOUR_IOSXE_IP              : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
    ```
    *Expected Output (if failed, e.g., connection/auth error):*
    ```
    PLAY [Configure hostname on Cisco IOS XE] **************************************

    TASK [Set router hostname] *****************************************************
    fatal: [YOUR_IOSXE_IP]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh: ...", "unreachable": true}

    PLAY RECAP *********************************************************************
    YOUR_IOSXE_IP              : ok=0    changed=0    unreachable=1    failed=0    skipped=0    rescued=0    ignored=0   
    ```
3.  **Manual Verification:** Log in to your IOS XE router via SSH/console and verify that its hostname is now `Ansible-Managed-Router`.
    ```
    Router# show hostname
    Ansible-Managed-Router
    ```

---

## Lab 2: Integrating Python with Ansible

**Objective:** Learn how to trigger an Ansible playbook from a Python script.

### Task 2.1: Create Python Script to Deploy Ansible Playbook

1.  Open `python_ansible_deploy.py` in your code editor.
2.  Add the following Python code:
    ```python
    # python_ansible_deploy.py
    import subprocess
    import os
    from config import IOSXE_DEVICE_INFO # Import device info for host IP

    def run_ansible_playbook(playbook_path, inventory_path, extra_vars=None):
        """
        Runs an Ansible playbook using subprocess.
        extra_vars: dictionary of variables to pass to the playbook.
        """
        command = ["ansible-playbook", "-i", inventory_path, playbook_path]
        
        # Pass extra variables using -e flag
        if extra_vars:
            for key, value in extra_vars.items():
                command.extend(["-e", f"{key}={value}"])
        
        # Set environment variables for Ansible credentials
        # This is a good practice for security and flexibility
        env = os.environ.copy()
        env['ANSIBLE_HOST_KEY_CHECKING'] = 'False' # Disable host key checking for lab (be cautious in prod)
        env['ANSIBLE_USER'] = IOSXE_DEVICE_INFO['username']
        env['ANSIBLE_PASSWORD'] = IOSXE_DEVICE_INFO['password']
        env['ANSIBLE_ENABLE_PASS'] = IOSXE_DEVICE_INFO['secret']
        
        print(f"Running command: {' '.join(command)}")
        try:
            # Run the command, capture output, and check for errors
            result = subprocess.run(command, capture_output=True, text=True, check=True, env=env)
            print("\n--- Ansible Playbook Output ---")
            print(result.stdout)
            if result.stderr:
                print("\n--- Ansible Playbook Errors ---")
                print(result.stderr)
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n--- Ansible Playbook Failed ---")
            print(f"Error code: {e.returncode}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"\n--- An unexpected error occurred ---")
            print(e)
            return False

    if __name__ == "__main__":
        print("--- Lab 2.1: Deploy Ansible Playbook from Python ---")
        
        # Define the path to our playbook and inventory
        playbook_to_run = "playbook_hostname.yaml"
        inventory_file = "inventory.yaml"
        
        # Define new hostname to pass as an extra variable
        new_hostname_from_python = "Python-Ansible-Router"
        
        # Run the playbook
        success = run_ansible_playbook(
            playbook_to_run,
            inventory_file,
            extra_vars={"new_hostname": new_hostname_from_python}
        )
        
        if success:
            print(f"\nSuccessfully deployed hostname '{new_hostname_from_python}' via Ansible playbook from Python.")
            print("Please verify the hostname on your router.")
        else:
            print(f"\nFailed to deploy hostname '{new_hostname_from_python}' via Ansible playbook from Python.")
        
        print("\nLab 2.1 complete.")
    ```

### Task 2.2: Run the Python Integration Script

1.  **Ensure you have updated `config.py` with your real device details.**
2.  **Run the Python script** from your `module7_ansible_lab` directory:
    ```bash
    python python_ansible_deploy.py
    ```
    *Expected Output (if successful):*
    ```
    --- Lab 2.1: Deploy Ansible Playbook from Python ---
    Running command: ansible-playbook -i inventory.yaml playbook_hostname.yaml -e new_hostname=Python-Ansible-Router

    --- Ansible Playbook Output ---
    PLAY [Configure hostname on Cisco IOS XE] **************************************

    TASK [Set router hostname] *****************************************************
    changed: [YOUR_IOSXE_IP] => {"ansible_facts": {"discovered_interpreter_python": "/usr/bin/python"}, "changed": true, "commands": ["hostname Python-Ansible-Router"], "diff": [...], "invocation": {...}, "stderr": "", "stderr_lines": [], "stdout": "configure terminal\nhostname Python-Ansible-Router\nend\n", "stdout_lines": ["configure terminal", "hostname Python-Ansible-Router", "end"]}

    TASK [Print hostname change result] ********************************************
    ok: [YOUR_IOSXE_IP] => {
        "msg": "Hostname configuration result: {'changed': True, 'stdout': 'configure terminal\\nhostname Python-Ansible-Router\\nend\\n', ...}"
    }

    PLAY RECAP *********************************************************************
    YOUR_IOSXE_IP              : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

    Successfully deployed hostname 'Python-Ansible-Router' via Ansible playbook from Python.
    Please verify the hostname on your router.

    Lab 2.1 complete.
    ```
3.  **Manual Verification:** Log in to your IOS XE router via SSH/console and verify that its hostname is now `Python-Ansible-Router`.

---

## Lab 3: Workflows Automated with Ansible (Full Configuration)

**Objective:** Use Ansible to configure multiple services (hostname, NTP, OSPF) on your Cisco IOS XE router in one playbook.

### Task 3.1: Create Ansible Playbook for Full Configuration

1.  Open `playbook_full_config.yaml` in your code editor.
2.  Add the following YAML content:
    ```yaml
    # playbook_full_config.yaml
    ---
    - name: Configure Router with Hostname, NTP, and OSPF
      hosts: all
      gather_facts: false
      
      vars:
        router_hostname: "Full-Config-Router"
        ntp_server_ip: "10.0.0.254"
        ospf_process_id: 10
        ospf_network: "10.0.0.0"
        ospf_wildcard: "0.0.0.255"
        ospf_area: 0

      tasks:
        - name: Set router hostname
          ios_config:
            lines:
              - hostname {{ router_hostname }}
            provider: "{{ lookup('vars', 'ansible_network_cli_connection') }}"
            save_when: changed

        - name: Configure NTP server
          ios_config:
            lines:
              - ntp server {{ ntp_server_ip }}
            provider: "{{ lookup('vars', 'ansible_network_cli_connection') }}"
            save_when: changed

        - name: Configure OSPF
          ios_config:
            lines:
              - router ospf {{ ospf_process_id }}
              -   network {{ ospf_network }} {{ ospf_wildcard }} area {{ ospf_area }}
            provider: "{{ lookup('vars', 'ansible_network_cli_connection') }}"
            save_when: changed
    ```
3.  Save `playbook_full_config.yaml`.

### Task 3.2: Run the Full Configuration Playbook

1.  **Ensure you have updated `config.py` with your real device details and set environment variables for credentials.**
2.  **Run the playbook** from your `module7_ansible_lab` directory:
    ```bash
    ansible-playbook -i inventory.yaml playbook_full_config.yaml
    ```
    *Expected Output (if successful):*
    ```
    PLAY [Configure Router with Hostname, NTP, and OSPF] ***************************

    TASK [Set router hostname] *****************************************************
    changed: [YOUR_IOSXE_IP] => {"changed": true, "commands": ["hostname Full-Config-Router"], ...}

    TASK [Configure NTP server] ****************************************************
    changed: [YOUR_IOSXE_IP] => {"changed": true, "commands": ["ntp server 10.0.0.254"], ...}

    TASK [Configure OSPF] **********************************************************
    changed: [YOUR_IOSXE_IP] => {"changed": true, "commands": ["router ospf 10", "network 10.0.0.0 0.0.0.255 area 0"], ...}

    PLAY RECAP *********************************************************************
    YOUR_IOSXE_IP              : ok=3    changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
    ```
3.  **Manual Verification:** Log in to your IOS XE router via SSH/console and verify the configurations:
    *   `show hostname` (should be `Full-Config-Router`)
    *   `show run | section ntp` (should show `ntp server 10.0.0.254`)
    *   `show run | section ospf` (should show `router ospf 10` and `network 10.0.0.0 0.0.0.255 area 0`)

---

## Lab 4: Comparison: Netmiko-based vs. Ansible-based Workflows

**Objective:** Perform the same configuration task (adding a Loopback interface) using both Netmiko and Ansible, and compare their approaches.

### Task 4.1: Configure Loopback with Netmiko

1.  Open `python_netmiko_workflow.py` in your code editor.
2.  Add the following Python code:
    ```python
    # python_netmiko_workflow.py
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoException
    import logging
    from config import IOSXE_DEVICE_INFO # Import device info

    # Configure logging for better visibility
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def configure_loopback_netmiko(loopback_id, ip_address, mask):
        """
        Configures a loopback interface using Netmiko.
        Returns True on success, False on failure.
        """
        host = IOSXE_DEVICE_INFO['host']
        
        config_commands = [
            f"interface Loopback{loopback_id}",
            f"description Configured_by_Netmiko",
            f"ip address {ip_address} {mask}",
            "no shutdown"
        ]
        
        try:
            logging.info(f"Connecting to {host} via Netmiko to configure Loopback{loopback_id}...")
            with ConnectHandler(**IOSXE_DEVICE_INFO) as net_connect:
                logging.info(f"Connected to {host}. Pushing configuration...")
                output = net_connect.send_config_set(config_commands)
                logging.info(f"Netmiko config output:\n{output}")
                logging.info(f"Successfully configured Loopback{loopback_id} on {host}.")
                return True
        except (NetmikoTimeoutException, NetmikoAuthenticationException, NetmikoException) as e:
            logging.error(f"Netmiko Error configuring Loopback{loopback_id} on {host}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected Error configuring Loopback{loopback_id} on {host}: {e}")
            return False

    if __name__ == "__main__":
        print("--- Lab 4.1: Configure Loopback with Netmiko ---")
        
        loopback_id = 100
        ip_address = "10.0.0.100"
        mask = "255.255.255.255"
        
        success = configure_loopback_netmiko(loopback_id, ip_address, mask)
        
        if success:
            print(f"\nNetmiko: Loopback{loopback_id} configured successfully.")
            print("Please verify the configuration on your router.")
        else:
            print(f"\nNetmiko: Failed to configure Loopback{loopback_id}.")
        
        print("\nLab 4.1 complete.")
    ```
2.  Save `python_netmiko_workflow.py`.
3.  **Run the script** from your `module7_ansible_lab` directory:
    ```bash
    python python_netmiko_workflow.py
    ```
    *Expected Output (if successful):*
    ```
    --- Lab 4.1: Configure Loopback with Netmiko ---
    Connecting to YOUR_IOSXE_IP via Netmiko to configure Loopback100...
    Connected to YOUR_IOSXE_IP. Pushing configuration...
    Netmiko config output:
    configure terminal
    Enter configuration commands, one per line.  End with CNTL/Z.
    YOUR_IOSXE_PROMPT(config)#interface Loopback100
    YOUR_IOSXE_PROMPT(config-if)#description Configured_by_Netmiko
    YOUR_IOSXE_PROMPT(config-if)#ip address 10.0.0.100 255.255.255.255
    YOUR_IOSXE_PROMPT(config-if)#no shutdown
    YOUR_IOSXE_PROMPT(config-if)#end
    YOUR_IOSXE_PROMPT#
    Successfully configured Loopback100 on YOUR_IOSXE_IP.

    Netmiko: Loopback100 configured successfully.
    Please verify the configuration on your router.

    Lab 4.1 complete.
    ```
4.  **Manual Verification:** Log in to your router and check `show run interface Loopback100`.

### Task 4.2: Configure Loopback with Ansible

1.  Open `playbook_loopback.yaml` in your code editor.
2.  Add the following YAML content:
    ```yaml
    # playbook_loopback.yaml
    ---
    - name: Configure Loopback Interface with Ansible
      hosts: all
      gather_facts: false
      
      vars:
        loopback_id: 101
        ip_address: "10.0.0.101"
        mask: "255.255.255.255"

      tasks:
        - name: Configure Loopback interface
          ios_config:
            lines:
              - "interface Loopback{{ loopback_id }}"
              - "description Configured_by_Ansible"
              - "ip address {{ ip_address }} {{ mask }}"
              - "no shutdown"
            provider: "{{ lookup('vars', 'ansible_network_cli_connection') }}"
            save_when: changed
          register: loopback_config_result
          
        - name: Print Loopback configuration result
          debug:
            msg: "Loopback configuration result: {{ loopback_config_result }}"
    ```
3.  Save `playbook_loopback.yaml`.
4.  **Run the playbook** from your `module7_ansible_lab` directory:
    ```bash
    ansible-playbook -i inventory.yaml playbook_loopback.yaml
    ```
    *Expected Output (if successful):*
    ```
    PLAY [Configure Loopback Interface with Ansible] *******************************

    TASK [Configure Loopback interface] ********************************************
    changed: [YOUR_IOSXE_IP] => {"ansible_facts": {"discovered_interpreter_python": "/usr/bin/python"}, "changed": true, "commands": ["interface Loopback101", "description Configured_by_Ansible", "ip address 10.0.0.101 255.255.255.255", "no shutdown"], "diff": [...], "invocation": {...}, "stderr": "", "stderr_lines": [], "stdout": "configure terminal\ninterface Loopback101\ndescription Configured_by_Ansible\nip address 10.0.0.101 255.255.255.255\nno shutdown\nend\n", "stdout_lines": ["configure terminal", "interface Loopback101", "description Configured_by_Ansible", "ip address 10.0.0.101 255.255.255.255", "no shutdown", "end"]}

    TASK [Print Loopback configuration result] *************************************
    ok: [YOUR_IOSXE_IP] => {
        "msg": "Loopback configuration result: {'changed': True, 'stdout': 'configure terminal\\ninterface Loopback101\\ndescription Configured_by_Ansible\\nip address 10.0.0.101 255.255.255.255\\nno shutdown\\nend\\n', ...}"
    }

    PLAY RECAP *********************************************************************
    YOUR_IOSXE_IP              : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
    ```
5.  **Manual Verification:** Log in to your router and check `show run interface Loopback101`.

### Task 4.3: Comparison and Discussion

*   **Netmiko (Python Script):**
    *   **Pros:** Direct Python code, full control over logic, good for complex conditional flows, direct integration with other Python libraries.
    *   **Cons:** Requires more lines of code for basic configuration, error handling is explicit, less readable for non-programmers.
*   **Ansible (Playbook):**
    *   **Pros:** Declarative (describe desired state), very concise for common tasks, human-readable YAML, built-in idempotence, handles SSH connection details, easy for multi-device.
    *   **Cons:** Less flexible for complex programmatic logic, requires learning Ansible-specific YAML syntax and modules.

This comparison highlights that Netmiko is a powerful *library* for programmatic control, while Ansible is a powerful *engine* for declarative automation and orchestration. Often, they are used together, with Python scripts orchestrating Ansible playbooks.

---

## Conclusion

You've now completed Module 7 and gained valuable experience with Ansible! You can now:

*   Understand Ansible's core components (inventory, playbooks, modules).
*   Automate basic device configuration using Ansible playbooks.
*   Integrate Ansible playbooks into your Python scripts.
*   Compare and contrast Netmiko-based and Ansible-based automation workflows.

Ansible is an indispensable tool in the network automation landscape, complementing your Python scripting skills for scalable and declarative infrastructure management.

**Keep Automating!**

---