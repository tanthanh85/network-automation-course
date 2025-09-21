# Python Basics for Network Automation: Module 7 Lab Guide

## Identification of Workflows Automated using Ansible - Hands-on Exercises

**[Your Organization/Name]**
**September 01, 2025**

---

## Introduction

Welcome to Module 7 of the Python Basics for Network Automation Lab Guide! In this module, you will get hands-on with **Ansible** for network automation. You will learn to use Ansible playbooks for configuration management and see how Python scripts can integrate with Ansible.

**It is crucial that you replace the dummy values for your IOS XE router with its actual IP address, username, and password to make the code functional.**

**Lab Objectives:**
*   Install Ansible.
*   Create an Ansible inventory file.
*   Write a basic Ansible playbook to configure a Cisco IOS XE router.
*   Run an Ansible playbook.
*   Integrate Python with Ansible by calling a playbook from a Python script.
*   Configure several services (hostname, NTP, OSPF) using Ansible.

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
    touch playbook_full_config.yaml
    touch python_ansible_deploy.py
    touch playbook_loopback_ospf.yaml
    ```

Your directory structure should now look like this:
```
network_automation_labs/
└── module7_ansible_lab/
    ├── config.py
    ├── inventory.yaml
    ├── playbook_hostname.yaml
    ├── playbook_full_config.yaml
    ├── playbook_loopback_ospf.yaml
    └── python_ansible_deploy.py
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
        router1:
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


### Task 0.4: Setting Environment Variables for Ansible Credentials
-----------------------------------------------------

Ansible can securely retrieve sensitive information like usernames and passwords from environment variables. This is a recommended practice to avoid hardcoding credentials directly in your playbooks or inventory files.

You will need to set the following environment variables with your actual IOS XE router credentials:

*   `ANSIBLE_USER`: Your IOS XE username.
*   `ANSIBLE_PASSWORD`: Your IOS XE password.
*   `ANSIBLE_ENABLE_PASS`: Your IOS XE enable (secret) password.

How to set environment variables:

For Linux/macOS (Bash/Zsh): Open your terminal and run the following commands. Replace `YOUR_IOSXE_USERNAME`, `YOUR_IOSXE_PASSWORD`, and `YOUR_IOSXE_ENABLE_PASSWORD` with your actual credentials.
```bash
export ANSIBLE_USER="YOUR_IOSXE_USERNAME"
export ANSIBLE_PASSWORD="YOUR_IOSXE_PASSWORD"
export ANSIBLE_ENABLE_PASS="YOUR_IOSXE_ENABLE_PASSWORD"
```

_Note: These variables will only be set for the current terminal session. If you open a new terminal, you will need to set them again. For persistent settings, you can add these lines to your shell's profile file (e.g., `~/.bashrc`, `~/.zshrc`)._

For Windows (Command Prompt - CMD): Open Command Prompt and run:
```cmd
set ANSIBLE_USER=YOUR_IOSXE_USERNAME
set ANSIBLE_PASSWORD=YOUR_IOSXE_PASSWORD
set ANSIBLE_ENABLE_PASS=YOUR_IOSXE_ENABLE_PASSWORD
```
Note: These variables will only be set for the current CMD session.

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
      hosts: router1 # Apply to all hosts in inventory
      gather_facts: false # No need to gather facts for this simple task
      
      vars:
        new_hostname: "Ansible-Managed-Router" # Define the desired hostname

      tasks:
        - name: Set router hostname
          ios_config:
            lines:
              - hostname {{ new_hostname }} # Use the variable
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
    ok: [router1] => {
        "msg": "Hostname configuration result: {'changed': False, 'failed': False}"
    }

    PLAY RECAP *********************************************************************
    router1              : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
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

1.  **Ensure you have updated `config.py` with your real device details and set environment variables for credentials.**
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
    - name: Configure Router with Hostname, NTP, and OSPF
      hosts: router1
      gather_facts: false
      
      vars:
        router_hostname: "OSPF-Router"
        ntp_server_ip: "10.0.0.254"
        process_id: "10"

      tasks:
        - name: Set router hostname
          cisco.ios.ios_config:
            lines:
              - hostname {{ router_hostname }}
            save_when: changed

        - name: Configure NTP server
          cisco.ios.ios_config:
            lines:
              - ntp server {{ ntp_server_ip }}
            save_when: changed

        - name: Configure OSPF on GigabitEthernet2
          cisco.ios.ios_ospf_interfaces:
            config:
              - name: GigabitEthernet2
                address_family:
                  - afi: ipv4
                    process:
                      id: "{{ process_id }}"
                      area_id: 30
                    adjacency: true
                    bfd: true
                    cost:
                      interface_cost: 5
                    dead_interval:
                      time: 5
                    demand_circuit:
                      ignore: true
                    network:
                      broadcast: true
                    priority: 25
                    resync_timeout: 10
                    shutdown: true
                    ttl_security:
                      hops: 50
            state: merged
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
### Lab 4: Automating with Ansible Loops
------------------------------------

**Objective:** Learn how to use Ansible loops to configure multiple similar network objects efficiently, specifically creating multiple loopback interfaces and adding them to OSPF.

Ansible loops are a powerful feature that allows you to repeat a task multiple times, iterating over a list of items. This is incredibly useful for configuring repetitive elements like interfaces, VLANs, or routing entries. The `loop` keyword is the modern and preferred way to implement loops in Ansible playbooks. When using `loop`, each item in the list becomes available via the `item` variable within the task.

### Task 4.1: Create Ansible Playbook for Loopback and OSPF Configuration

In this task, you will create a new playbook that uses a loop to configure 10 new loopback interfaces (Loopback101 through Loopback110) with unique IP addresses (192.168.1.1/32 through 192.168.1.10/32). Subsequently, another loop will add these newly configured networks to OSPF process 1 in area 0.

Open `playbook_loopback_ospf.yaml` in your code editor. Add the following YAML content:

```yaml
# playbook_loopback_ospf.yaml
# playbook_loopback_ospf.yaml
---
- name: Configure multiple loopback interfaces and add them to OSPF on router1
  hosts: router1
  gather_facts: false # No need to gather facts for this configuration task

  vars:
    # Define the OSPF process ID and area as requested
    # ospf_process_id: 1
    # ospf_area: 0
    # Define a list of dictionaries for the loopback interfaces
    # Each dictionary contains the interface ID and its IP address
    loopback_interfaces:
      - { id: 101, ip: "192.168.100.1" }
      - { id: 102, ip: "192.168.100.2" }
      - { id: 103, ip: "192.168.100.3" }
      - { id: 104, ip: "192.168.100.4" }
      - { id: 105, ip: "192.168.100.5" }
      - { id: 106, ip: "192.168.100.6" }
      - { id: 107, ip: "192.168.100.7" }
      - { id: 108, ip: "192.168.100.8" }
      - { id: 109, ip: "192.168.100.9" }
      - { id: 110, ip: "192.168.100.10" }

  tasks:
    - name: Configure loopback interfaces with IP addresses
      ios_config:
        # The 'lines' parameter takes a list of configuration commands.
        # 'item.id' and 'item.ip' refer to the current item in the loopback_interfaces list.
        parents: "interface Loopback{{ item.id }}"
        lines:
          - "ip address {{ item.ip }} 255.255.255.255" # /32 subnet mask for loopbacks
        save_when: changed # Save configuration if any changes are made
      loop: "{{ loopback_interfaces }}" # Iterate over the 'loopback_interfaces' list
      loop_control:
        label: "Create loopback{{ item.id }} and assign ip {{ item.ip }}" # Provides more readable output during playbook execution

    - name: Configure OSPF on loopback interfaces
      cisco.ios.ios_ospf_interfaces:
        config:
          - name: Loopback{{ item.id }}
            address_family:
              - afi: ipv4
                process:
                  id: 10
                  area_id: 30
                adjacency: true
                bfd: true
                cost:
                  interface_cost: 5
                dead_interval:
                  time: 5
                demand_circuit:
                  ignore: true
                network:
                  broadcast: true
                priority: 25
                resync_timeout: 10
                shutdown: true
                ttl_security:
                  hops: 50
        state: merged
      loop: "{{ loopback_interfaces }}" # Iterate over the 'loopback_interfaces' list
      loop_control:
        label: "Config OSPF on Loopback{{ item.id }}" # Provides more readable output during playbook execution
```
Save `playbook_loopback_ospf.yaml`.

Explanation of the Playbook:

*   `vars` section: Defines `ospf_process_id`, `ospf_area`, and `loopback_interfaces`. The `loopback_interfaces` variable is a list of dictionaries, where each dictionary represents a single loopback interface and contains its `id` and `ip` address.
*   `Configure loopback interfaces` task:
    *   Uses the `ios_config` module to apply configuration to the Cisco IOS XE device.
    *   The `lines` parameter dynamically constructs the interface and IP address commands using `{{ item.id }}` and `{{ item.ip }}`, which are populated from the current item in the `loopback_interfaces` list during each iteration.
    *   `loop: "{{ loopback_interfaces }}"` tells Ansible to run this task once for each item in the `loopback_interfaces` list.
    *   `loop_control: label:` makes the output during playbook execution more informative.
*   `Add loopback networks to OSPF` task:
    *   Similar to the previous task, it uses `ios_config` and `loop` to iterate through the `loopback_interfaces`.
    *   It adds the `router ospf` command and then the `network` command for each loopback's IP address, using a `0.0.0.0` wildcard mask to advertise only the specific /32 host route, within OSPF process 1 and area 0.

### Task 4.2: Run the Loopback and OSPF Configuration Playbook

Ensure you have updated `config.py` with your real device details and set environment variables for credentials (as done in Task 1.2).

Run the playbook from your `module7_ansible_lab` directory:
```bash
ansible-playbook -i inventory.yaml playbook_loopback_ospf.yaml
```
Expected Output (if successful):

You will see output indicating that Ansible is configuring each loopback interface and adding each network statement to OSPF. The `changed` status should be true for each iteration if the configuration is new.
```bash
PLAY [Configure multiple loopback interfaces and add to OSPF] ******************

TASK [Configure loopback interfaces with IP addresses] *************************
changed: [YOUR_IOSXE_IP] => (item=Loopback101)
changed: [YOUR_IOSXE_IP] => (item=Loopback102)
...
changed: [YOUR_IOSXE_IP] => (item=Loopback110)

TASK [Add loopback networks to OSPF process 1 in area 0] ***********************
changed: [YOUR_IOSXE_IP] => (item=OSPF network 192.168.1.1)
changed: [YOUR_IOSXE_IP] => (item=OSPF network 192.168.1.2)
...
changed: [YOUR_IOSXE_IP] => (item=OSPF network 192.168.1.10)

PLAY RECAP *********************************************************************
YOUR_IOSXE_IP              : ok=2    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
Manual Verification:

Log in to your IOS XE router via SSH/console and verify the configurations:

1.  Verify Loopback Interfaces and IP Addresses:
```bash
show ip interface brief | include Loopback
```
You should see Loopback101 through Loopback110 listed with their assigned IP addresses.

2. Verify OSPF Configuration for Loopbacks:
```bash
show run | section router ospf 1
```
You should see the router ospf 1 block, including network 192.168.1.1 0.0.0.0 area 0 up to network 192.168.1.10 0.0.0.0 area 0.

3. Verify OSPF Neighbor Adjacencies (if applicable) and Interface Status:
```bash
show ip ospf interface brief
```
This command will show the OSPF status of all interfaces, including your new loopbacks.

## Conclusion

You've now completed Module 7 and gained valuable experience with Ansible! You can now:

*   Understand Ansible's core components (inventory, playbooks, modules).
*   Automate basic device configuration using Ansible playbooks.
*   Integrate Ansible playbooks into your Python scripts.
*   Configure multiple services on a Cisco IOS XE router using Ansible.
*   Leverage Ansible loops for efficient, repetitive network configurations.

Ansible is an indispensable tool in the network automation landscape, complementing your Python scripting skills for scalable and declarative infrastructure management.

**Keep Automating!**

---