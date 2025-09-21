# Python Basics for Network Automation: Module 7 Theory Guide

## Identification of Workflows Automated using Ansible

**[Your Organization/Name]**
**September 01, 2025**

---

## 1. Introduction to Ansible

You've learned to automate network devices using Python libraries like Netmiko and Paramiko for CLI interaction, and `requests` for API communication. These are powerful tools for building custom automation scripts. Now, we introduce **Ansible**, a widely adopted automation engine that simplifies complex orchestration tasks, especially in multi-device and multi-vendor environments.

**What is Ansible?**
Ansible is an open-source automation engine that automates provisioning, configuration management, application deployment, orchestration, and many other IT processes. Unlike some other automation tools, Ansible is **agentless**, meaning it doesn't require any special software (agents) to be installed on the managed network devices. It communicates over standard SSH (for Linux/network devices) or WinRM (for Windows).

**Key Components of Ansible:**
*   **Inventory:** A list of managed hosts (network devices, servers) that Ansible can connect to.
*   **Modules:** Small programs that Ansible executes on managed nodes to perform specific tasks.
*   **Playbooks:** YAML files that define a set of automated tasks (plays) to be executed on specified hosts.
*   **Roles:** A way to organize playbooks and related files into reusable units.

---

## 2. Ansible Components and Concepts

### 2.1 Inventory - Defining Your Network Assets

The inventory tells Ansible *which* devices it should manage and *how* to connect to them.

*   **Purpose:** Lists your hosts, groups them, and stores connection variables.
*   **Formats:**
    *   **INI Format (Simple):** Traditional, easy to read for small inventories.
        ```ini
        # inventory.ini
        [routers]
        router1.example.com
        router2.example.com

        [switches]
        switch1.example.com
        switch2.example.com

        [all:vars] # Variables applying to all hosts
        ansible_user=admin
        ansible_password=cisco
        ansible_network_os=ios
        ansible_connection=network_cli
        ansible_become=yes
        ansible_become_method=enable
        ansible_become_pass=enable_pass
        ```
    *   **YAML Format (Structured):** Preferred for larger, more complex inventories as it supports more data structures and is more readable.
        ```yaml
        # inventory.yaml
        all:
          hosts:
            router1.example.com:
              ansible_host: 192.168.1.1
              ansible_user: admin
            router2.example.com:
              ansible_host: 192.168.1.2
              ansible_user: admin
          children:
            routers:
              hosts:
                router1.example.com:
                router2.example.com:
            switches:
              hosts:
                switch1.example.com:
                switch2.example.com:
          vars: # Variables applying to all hosts
            ansible_password: cisco
            ansible_network_os: ios
            ansible_connection: network_cli
            ansible_become: yes
            ansible_become_method: enable
            ansible_become_pass: enable_pass
        ```
*   **Dynamic Inventory:** Python scripts (or other executables) can generate inventory on the fly by printing a JSON representation. This is crucial for environments where devices are constantly added/removed (e.g., cloud, SDN controllers).

### 2.2 Modules - The Building Blocks of Automation

Ansible modules are small, reusable pieces of code that perform specific tasks on managed nodes.

*   **Agentless Execution:** Ansible copies the module to the remote host, executes it, and removes it.
*   **Idempotent:** Most modules are designed to be idempotent. Running a module multiple times with the same parameters will only make changes if the desired state is not already met.
*   **Network Modules:** Ansible has a rich set of modules specifically for network devices (e.g., `ios_config`, `ios_command`, `junos_interface`, `arista.eos.eos_facts`).
*   **General Modules:** Many modules are general-purpose (e.g., `copy` for file transfer, `template` for Jinja2 rendering, `debug` for printing messages).

### 2.3 Playbooks - Orchestrating Tasks

Playbooks are the heart of Ansible automation. They are YAML files that define a series of tasks to be executed on a group of hosts.

*   **Declarative:** Playbooks describe the *desired state* of your infrastructure. Ansible figures out the steps to achieve that state.
*   **Readability:** YAML syntax is human-readable, making playbooks easy to understand.
*   **Structure:**
    *   `---`: Start of a YAML document.
    *   `- name: `: A descriptive name for the playbook or a play.
    *   `hosts: `: Specifies which hosts from the inventory the play applies to.
    *   `gather_facts: false`: (Common for network devices) Prevents Ansible from trying to gather system facts, which can be slow or unsupported on network devices.
    *   `vars: `: Define variables specific to this playbook.
    *   `tasks: `: A list of tasks to execute. Each task uses an Ansible module.
        *   `- name: `: A descriptive name for the task.
        *   `module_name: `: The Ansible module to use.
        *   `module_parameters: `: Arguments passed to the module.
        *   `register: `: Stores the result of a task in a variable.
        *   `debug: `: A module to print messages or variable contents.

*   **Example Playbook Structure:**
    ```yaml
    ---
    - name: Configure Network Device
      hosts: routers # Group from inventory
      gather_facts: false
      vars:
        ntp_server_ip: 10.0.0.1
      tasks:
        - name: Set hostname
          ios_config:
            lines:
              - hostname MyRouter
        - name: Configure NTP
          ios_config:
            lines:
              - ntp server {{ ntp_server_ip }}
    ```

### 2.4 Roles - Reusability and Organization

Roles provide a standardized way to organize related playbooks, variables, templates, and files. They promote reusability and make complex projects manageable.

*   **Structure:** A role is a directory with a predefined structure (e.g., `tasks/`, `vars/`, `templates/`, `handlers/`).
*   **Usage:** You can apply a role to hosts in a playbook, and Ansible automatically finds the relevant files within the role.


### 2.5 Advanced Playbook Control: Loops and Conditionals

Ansible playbooks are declarative, but they also offer powerful control flow mechanisms like loops and conditionals to handle dynamic data and execute tasks selectively.

### 2.5.1 Loops in Ansible

Loops allow you to repeat a task multiple times, applying different input values each time. This is incredibly useful for configuring multiple interfaces, users, VLANs, or any repetitive configuration block.

Modern Loop Syntax (`loop` keyword): The `loop` keyword is the preferred and most flexible way to implement loops in Ansible. It can iterate over lists, dictionaries, sequences, and even the results of other tasks.

Example: Configuring Multiple Loopback Interfaces (as seen in the previous lab)
```yaml
- name: Configure multiple loopback interfaces with IP addresses
  cisco.ios.ios_config:
    parents: "interface Loopback{{ item.id }}"
    lines:
      - "ip address {{ item.ip }} 255.255.255.255"
      - "no shutdown"
  loop: "{{ loopback_interfaces }}" # Iterates over the list defined in 'vars'
  loop_control:
    label: "Loopback{{ item.id }}" # Customizes the output during playbook execution
```
In this example:

*   `loop: "{{ loopback_interfaces }}"` tells Ansible to iterate over the `loopback_interfaces` list.
*   During each iteration, the current item from the list is accessible via the special `item` variable.
*   `item.id` and `item.ip` are used to access the keys within each dictionary in the `loopback_interfaces` list.
*   `loop_control.label` provides more descriptive output in the terminal, making it easier to track which specific item is being processed.

### 2.5.2 Conditionals in Ansible

Conditionals allow you to execute tasks only when certain conditions are met. This is essential for creating intelligent and adaptive playbooks that can respond to different network states or requirements. The primary conditional keyword is `when`.

The `when` Clause: The `when` clause takes a Jinja2 expression. If the expression evaluates to `True`, the task is executed; otherwise, it's skipped.

Example: Apply configuration only if a variable is defined
```yaml
- name: Configure NTP server if ntp_server_ip is defined
  cisco.ios.ios_config:
    lines:
      - "ntp server {{ ntp_server_ip }}"
  when: ntp_server_ip is defined and ntp_server_ip != ""
```
Example: Apply configuration based on device hostname (using facts)
```yaml
- name: Set specific banner for router1
  cisco.ios.ios_config:
    lines:
      - "banner login ^CUnauthorized access prohibited^C"
  when: ansible_hostname == "router1" # Assumes facts were gathered or set
```
Example: Conditional based on task results
```yaml
- name: Check if interface GigabitEthernet1 is up
  cisco.ios.ios_command:
    commands: "show interface GigabitEthernet1 | include protocol"
  register: interface_status_output

- name: Send alert if interface is down
  debug:
    msg: "GigabitEthernet1 is down on {{ inventory_hostname }}!"
  when: "'down' in interface_status_output.stdout[0]"
```
### 2.6 Common Used Ansible Syntaxes
--------------------------------

Beyond modules and basic playbook structure, several common syntaxes and features are frequently used to build robust and dynamic Ansible playbooks.

### 2.6.1 Variables (`vars`, `{{ var_name }}`)

Variables are placeholders for values that can change. They make playbooks reusable and easier to maintain.

*   Definition:
    *   In `vars` section of a playbook, play, or task.
    *   In separate variable files (`group_vars/`, `host_vars/`).
    *   Passed via command line (`-e "key=value"`).
*   Usage: Accessed using Jinja2 templating syntax: `{{ var_name }}`.

Example:
```yaml
- name: Configure device with dynamic values
  hosts: my_devices
  vars:
    device_hostname: "MyRouter-{{ inventory_hostname }}"
    loopback_ip: "192.168.2.{{ ansible_loopback_id }}" # Example using a hypothetical fact
  tasks:
    - name: Set hostname
      cisco.ios.ios_config:
        lines:
          - "hostname {{ device_hostname }}"
```
### 2.6.2 Jinja2 Templating

Ansible uses the Jinja2 templating engine for processing variables and expressions. This allows for dynamic content generation within playbooks, templates, and conditional statements.

*   Syntax: `{{ variable_name }}` for variables, `{% expression %}` for control structures (like `if`, `for`).
*   Filters: Jinja2 provides filters to transform data (e.g., `| upper`, `| default('fallback')`).

Example:
```yaml
- name: Create a configuration file from a template
  ansible.builtin.template:
    src: router_config.j2
    dest: /tmp/{{ inventory_hostname }}_config.txt
```
Where router_config.j2 might contain:
```jinja2
hostname {{ device_hostname | upper }}
ip address {{ loopback_ip }} 255.255.255.255
{% if ntp_server_ip is defined %}
ntp server {{ ntp_server_ip }}
{% endif %}
```
### 2.6.3 Lists and Dictionaries

YAML, the language for playbooks, natively supports lists and dictionaries, which are fundamental for organizing data and iterating with loops.

*   Lists: Ordered collections of items. Used for `loop` iterations.
```yaml
my_list:
- item1
- item2
```
*   Dictionaries: Key-value pairs. Used for structured data, often within lists for complex loops.
```yaml
my_list:
    - item1
    - item2
```
*   Dictionaries: Key-value pairs. Used for structured data, often within lists for complex loops.
```yaml
my_dict:
    key1: value1
    key2: value2
```
### 2.7.4 register and debug
These are crucial for troubleshooting and understanding playbook execution.

*   `register`: Captures the output of a task into a variable. This variable can then be used in subsequent tasks, conditionals, or for debugging.
```yaml
- name: Get running configuration
cisco.ios.ios_command:
    commands: "show running-config"
register: running_config_output
```
*   `debug`: Prints messages or the contents of variables to the console during playbook execution. Invaluable for verifying data and task results.
```yaml
    - name: Display running config
    ansible.builtin.debug:
        var: running_config_output.stdout_lines
```

---

## 3. Ansible in the IaC

Ansible fits perfectly into the Infrastructure as Code paradigm.

*   **Declarative Nature:** You define the desired state of your network in playbooks. Ansible ensures the network matches this state.
*   **Version Control:** Playbooks, inventory, and variable files are all text-based and stored in Git.
*   **Automation Engine:** Ansible is the tool that reads your IaC definitions and applies them to the network.
*   **Agentless:** Simplifies deployment as no software needs to be pre-installed on network devices.

### 3.1 Ansible vs. Terraform

Both are IaC tools, but with different primary focuses:

| Feature           | Ansible                                     | Terraform                                   |
| :---------------- | :------------------------------------------ | :------------------------------------------ |
| **Primary Focus** | **Configuration Management**, Orchestration, Application Deployment | **Infrastructure Provisioning**, Lifecycle Management |
| **Approach**      | **Procedural/Declarative Hybrid** (tasks define steps, but modules are idempotent) | **Declarative** (defines desired end-state) |
| **State**         | Generally **Stateless** (checks current state, then acts) | **Stateful** (maintains a state file of deployed infra) |
| **Communication** | SSH, WinRM, API                             | API                                         |
| **Rollback**      | By re-running a previous playbook version or specific undo tasks | By applying a previous state file, or `terraform destroy` |
| **Best For**      | Post-provisioning config, app deployment, orchestration | Building new infrastructure, managing cloud resources, network device replacement |
| **Network Use**   | Configuring existing devices, automating operational tasks | Provisioning new devices, managing device lifecycle |

*   **Complementary:** Often used together. Terraform might provision a new router, and then Ansible steps in to configure it.

### 3.2 Ansible vs. Python (Netmiko)

You've already explored this in Module 4, but it's worth reiterating in the IaC context:

| Feature             | Python (Netmiko)                                     | Ansible                                          |
| :------------------ | :--------------------------------------------------- | :----------------------------------------------- |
| **Level of Abstraction** | Low-level (Python library for SSH/Telnet)            | High-level (Automation engine)                   |
| **Primary Use**     | Building custom Python scripts, complex logic, direct CLI interaction, API integration | Configuration management, orchestration, provisioning, multi-device management |
| **Language**        | Python (procedural/object-oriented)                  | YAML (declarative playbooks)                     |
| **Idempotence**     | Must be explicitly coded in Python                   | Built-in to most modules, core principle         |
| **Learning Curve**  | Requires Python programming knowledge                | Easier to start for non-programmers (YAML), but deeper Python knowledge for custom modules |
| **Role in IaC**     | The "engine" that executes specific CLI tasks. Can be orchestrated by Ansible. | The "orchestrator" that defines and applies the desired state across the network. |

*   **Synergy:** Python can generate dynamic inventories for Ansible, create custom Ansible modules, or act as the overarching orchestrator that calls Ansible playbooks.

---

## 4. Workflows Automated with Ansible

Ansible's versatility allows it to automate a wide range of network workflows:

*   **Configuration Management:**
    *   Standardizing configurations (e.g., NTP, logging, SNMP, AAA).
    *   Deploying new features (e.g., OSPF, BGP, VLANs, QoS policies).
    *   Ensuring compliance (auditing configurations against a golden standard).
*   **Device Provisioning (Basic):**
    *   Initial setup of new devices after they're racked and powered on (e.g., management IP, SSH, basic routing).
*   **Operational Tasks:**
    *   Collecting `show` command outputs from many devices (`ios_command` module).
    *   Upgrading IOS images (using `ios_system` module).
    *   Password rotations.
    *   Health checks and data collection.
*   **Orchestration:**
    *   Automating multi-step processes involving different network domains or even integrating with server/cloud teams.

---

## 5. Continuous Integration/Continuous Delivery (CI/CD) Pipeline for Network IaC

Ansible plays a central role in CI/CD pipelines for Network IaC.

*   **CI/CD Refresher:**
    *   **Continuous Integration (CI):** Developers frequently merge code changes. Automated tests run to detect integration issues early.
    *   **Continuous Delivery (CD):** Changes passing CI are automatically prepared for release.
    *   **Continuous Deployment:** Changes are automatically deployed to production after passing all tests.

*   **Ansible's Role in CI/CD:**
    *   **Build/Validate:** Ansible playbooks are themselves part of the code that gets linted and validated.
    *   **Deploy:** Ansible is the primary tool used in the "Deploy" stage to push configurations.
    *   **Test:** Ansible can run `show` commands (`ios_command`) for basic pre/post checks, or be integrated with more advanced testing tools.

*   **CI/CD Pipeline Stages (Typical Flow for Network IaC):**
    1.  **Source (Trigger):**
        *   **What triggers it:** A code push to a Git repository (e.g., to a `dev` or `main` branch), a scheduled job, or a manual trigger.
    2.  **Build/Validate:**
        *   **What happens:** Check YAML/Jinja2/Ansible playbook syntax. Render templates to ensure valid config output.
        *   **Tools:** `yamllint`, `ansible-lint`, Python scripts (for Jinja2 rendering).
        *   **Python's Built-in Test Frameworks:** `unittest` or `pytest` can be used here to test the Python scripts that generate data or render templates.
    3.  **Test (Pre-Deployment):**
        *   **What happens:** Run automated tests against the *current* network state to ensure it's healthy before applying changes.
        *   **Tools:**
            *   **Cisco PyATS (Python Automated Test System):** Connects to devices, gathers operational state, parses it, and makes assertions (e.g., "Is BGP neighbor up?"). This is crucial for pre-checks.
            *   **ThousandEyes (End-to-End Monitoring):** Can be triggered to run synthetic tests to verify application reachability or network performance *before* a change.
    4.  **Approval Gate (Manual/Automated):**
        *   **What happens:** A pause in the pipeline, often triggered when deploying to production.
        *   **Approval Flow:**
            *   **Manual:** Requires a human (e.g., network engineer, manager) to review the proposed changes and test results, then explicitly approve.
            *   **Automated:** All previous tests must pass with 100% success.
        *   **Purpose:** To prevent unapproved or untested changes from reaching critical environments.
    5.  **Deploy:**
        *   **What happens:** The validated configuration is pushed to the network devices. This might happen first in a lab/staging environment, then in production.
        *   **Tools:** Ansible playbooks (using `ios_config`, `ios_system`, etc.).
    6.  **Test (Post-Deployment):**
        *   **What happens:** Run automated tests against the *new* network state to confirm changes were applied correctly and no regressions occurred.
        *   **Tools:**
            *   **Cisco PyATS:** For post-checks, verifying the desired state (e.g., "Is the new hostname applied? Is the Loopback interface up?").
            *   **ThousandEyes:** Can be triggered again to run synthetic tests to verify the impact on user experience or application performance *after* the change. This validates the *business impact*.
    7.  **Rollback (Automated/Manual Trigger):**
        *   **What triggers it:**
            *   **Automated:** If post-deployment tests fail, or if a critical monitoring alert is received shortly after deployment.
            *   **Manual:** A human decides to revert.
        *   **How it works:** Git allows reverting to a previous commit. The CI/CD pipeline can then automatically deploy the configuration from that reverted commit. Ansible can be used to apply the reverted configuration.
        *   **Purpose:** To quickly restore network stability if a change introduces issues.

---

## 6. Summary and Key Takeaways

### Summary 

Ansible is a powerful, agentless automation engine that simplifies configuration management, provisioning, and orchestration using human-readable YAML playbooks. It leverages built-in modules for specific tasks and applies the principle of idempotence. Ansible plays a central role in CI/CD pipelines for Network IaC, where it's used for deployment, and integrated with various testing tools like PyATS for network state verification and ThousandEyes for end-to-end performance validation. This comprehensive approach, often orchestrated by CI/CD platforms like GitLab, enables a "GitOps" model for network operations, ensuring consistency, speed, and reliability.

### Key Takeaways

*   Ansible Core: Agentless automation engine using Inventory, Modules, and Playbooks (YAML).
*   IaC Big Picture: Ansible is the engine that applies the desired state defined in Git.
*   Dynamic Automation: Leverage loops (`loop` keyword) for repetitive tasks and conditionals (`when` clause) for intelligent, state-aware execution.
*   Precise Configuration with `ios_config`:
    *   `parents`: Essential for applying commands within specific hierarchical configuration modes (e.g., `interface`, `router ospf`).
    *   `save_when`: Controls when configuration changes are saved to startup (default `changed` is recommended).
    *   `state`: Defines the desired configuration state (`present`, `absent`, `merged`, `replaced`) for idempotent operations.
*   Flexible Playbook Syntax:
    *   Variables (`vars`, `{{ var_name }}`): Make playbooks reusable and maintainable.
    *   Jinja2 Templating: Enables dynamic content generation and powerful data manipulation.
    *   `register` and `debug`: Critical for capturing task output, troubleshooting, and verifying playbook execution.
    *   `delegate_to` and `run_once`: Control task execution location and frequency for advanced orchestration.
    *   `ignore_errors`: Allows tasks to proceed even if a non-critical error occurs (use with caution).
*   Ansible vs. Terraform: Ansible for config management/orchestration; Terraform for provisioning/lifecycle management. Often complementary.
*   Ansible vs. Python (Netmiko): Ansible is higher-level (orchestrator); Python/Netmiko is lower-level (granular control). Often used together.
*   Workflows Automated: Configuration management, basic provisioning, operational tasks, orchestration.
*   CI/CD Pipeline: Automates the entire IaC workflow (Source -> Build -> Test -> Deploy -> Test -> Rollback).
*   Testing is Multi-layered:
    *   Built-in Python/Linters: For code/syntax quality.
    *   PyATS: For network state pre-checks and post-checks (CLI verification).
    *   ThousandEyes: For end-to-end performance and application impact verification within the CI/CD pipeline.
*   CI/CD Triggers: Code pushes, schedules, manual.
*   Approval Flow: Critical for controlled deployments, can be manual or automated.
*   Rollback: Automated or manual process to revert to a known good state, triggered by test failures or monitoring alerts.
*   GitOps: Git repository is the central control for network operations.

---