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

## 2. Describing Complex Configuration Data with Nested YAML

For IaC, you need a way to describe your network configuration in a structured, human-readable format. **YAML (YAML Ain't Markup Language)** is a popular choice because it excels at representing complex, nested data.

*   **Why Nested YAML?**
    *   Simple flat YAML works for single parameters (like a hostname).
    *   For real-world network devices, configurations involve multiple interfaces, VLANs, routing protocols, and services, each with many parameters. Nested YAML allows you to logically group and organize this complex data.
    *   It maps directly to Python dictionaries and lists, making it easy to process.

*   **Example Nested YAML Data for Multiple Routers with Interfaces and OSPF:**
    ```yaml
    # network_data.yaml
    routers:
      - name: R1-Core
        mgmt_ip: 192.168.1.1
        interfaces:
          - name: GigabitEthernet0/0
            ip_address: 10.0.0.1
            subnet_mask: 255.255.255.0
            description: "Link to R2"
            is_trunk: false
          - name: Loopback0
            ip_address: 1.1.1.1
            subnet_mask: 255.255.255.255
            description: "Router ID Loopback"
            is_trunk: false
        routing:
          ospf:
            process_id: 10
            networks:
              - ip: 10.0.0.0
                wildcard: 0.0.0.255
                area: 0
              - ip: 1.1.1.1
                wildcard: 0.0.0.0
                area: 0

      - name: R2-Dist
        mgmt_ip: 192.168.1.2
        interfaces:
          - name: GigabitEthernet0/0
            ip_address: 10.0.0.2
            subnet_mask: 255.255.255.0
            description: "Link to R1"
            is_trunk: false
          - name: GigabitEthernet0/1
            ip_address: 10.0.1.1
            subnet_mask: 255.255.255.0
            description: "Link to SW1"
            is_trunk: true # Example of a trunk interface
        routing:
          ospf:
            process_id: 10
            networks:
              - ip: 10.0.0.0
                wildcard: 0.0.0.255
                area: 0
              - ip: 10.0.1.0
                wildcard: 0.0.0.255
                area: 0
    ```
    This YAML structure defines a list of routers, and for each router, it includes nested lists of interfaces and OSPF network statements.

---

## 3. Generating Configuration with Jinja2 Templates (Advanced)

Once you have your complex configuration data (in nested YAML), you need to turn it into actual device commands. **Jinja2** is perfectly suited for this, especially with its looping and conditional capabilities.

*   **Jinja2 Loops (`for`):**
    *   You can iterate over lists within your data structure. This is essential for configuring multiple interfaces, VLANs, or routing protocol networks.
    *   Syntax: `{% for item in list_variable %}` ... `{% endfor %}`

*   **Jinja2 Conditionals (`if`):**
    *   You can include or exclude configuration lines based on conditions in your data.
    *   Syntax: `{% if condition %}` ... `{% endif %}`

*   **Example Jinja2 Template (`router_full_config.j2`) for Nested Data:**
    ```jinja2
    !
    hostname {{ router.name }}
    !
    {% for interface in router.interfaces %}
    interface {{ interface.name }}
     description {{ interface.description }}
     ip address {{ interface.ip_address }} {{ interface.subnet_mask }}
     {% if interface.is_trunk %}
     switchport mode trunk
     {% else %}
     switchport mode access
     {% endif %}
     no shutdown
    !
    {% endfor %}
    !
    {% if router.routing.ospf %}
    router ospf {{ router.routing.ospf.process_id }}
    {% for network in router.routing.ospf.networks %}
     network {{ network.ip }} {{ network.wildcard }} area {{ network.area }}
    {% endfor %}
    !
    {% endif %}
    end
    ```
    *   This template loops through each `router` in the `routers` list (passed from YAML).
    *   Inside each router, it loops through its `interfaces` list.
    *   It uses an `if` condition to determine if an interface should be a trunk or access port.
    *   It also checks if OSPF configuration exists for a router before attempting to configure it.

---

## 4. Configuration Push: Deploying the Desired State with Netmiko

After generating the configuration, the next crucial step in IaC is to push it to the network devices. This is the "Deploy" stage of your pipeline. We will use **Netmiko** for this, as you've learned in Module 3.

*   **Why Netmiko for IaC (in this context)?**
    *   **Simplicity:** It's straightforward to use for pushing CLI configurations.
    *   **Familiarity:** You've already worked with it.
    *   **Common Use:** Many organizations use Netmiko (or similar libraries like NAPALM) to push configurations generated by IaC tools.
    *   **`send_config_set()`:** Netmiko's `send_config_set()` method is perfect for pushing a list of configuration commands to a device.

*   **How the whole process works in Python (YAML + Jinja2 + Netmiko):**

    1.  **Define Device Parameters:** Your Python script needs the device's connection details.
    2.  **Load Data:** Use Python's `PyYAML` library to load your `network_data.yaml` file into a Python dictionary.
    3.  **Load Template:** Use Python's `Jinja2` library to load your `router_full_config.j2` template file.
    4.  **Render Template:** Use Jinja2 to render the template, passing the loaded YAML data. This produces the final CLI configuration as a string.
    5.  **Push Configuration:** Use Netmiko to connect to the device and send the rendered configuration.

*   **Integrated Python Example Script (`deploy_full_config.py`):**

    ```python
    # deploy_full_config.py

    import yaml # For loading YAML data
    from jinja2 import Environment, FileSystemLoader # For Jinja2 templating
    from netmiko import ConnectHandler # For Netmiko device interaction
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException # For error handling
    import logging # For logging messages
    import os # For path operations

    # --- 1. Configure Logging ---
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # --- 2. Define Router Connection Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
    # This dictionary holds the connection parameters for your Cisco IOS XE router.
    # Ensure your router is reachable via SSH and has the correct credentials.
    ROUTER_CONNECTION_INFO = {
        "device_type": "cisco_ios",
        "host": "YOUR_ROUTER_IP",        # <<< REPLACE THIS
        "username": "YOUR_USERNAME",     # <<< REPLACE THIS
        "password": "YOUR_PASSWORD",     # <<< REPLACE THIS
        "secret": "YOUR_ENABLE_PASSWORD", # <<< REPLACE THIS (if your router uses enable password)
        "port": 22,                      # Default SSH port
    }

    # --- 3. Define File Paths ---
    DATA_FILE = "network_data.yaml"
    TEMPLATE_DIR = "templates" # Directory where Jinja2 templates are stored
    TEMPLATE_FILE = "router_full_config.j2" # The specific Jinja2 template to use

    # --- 4. Main Deployment Function ---
    def deploy_full_configuration():
        """
        Orchestrates the IaC deployment process for a single router:
        1. Loads network data for the specific router from YAML.
        2. Renders configuration using Jinja2.
        3. Pushes the generated configuration to the router via Netmiko.
        """
        logging.info(f"\n--- Starting IaC Deployment Workflow for {ROUTER_CONNECTION_INFO['host']} ---")

        # Load all network data from YAML file
        try:
            with open(DATA_FILE, 'r') as f:
                all_network_data = yaml.safe_load(f)
            logging.info(f"Successfully loaded data from {DATA_FILE}.")
        except Exception as e:
            logging.error(f"Error loading network data from {DATA_FILE}: {e}")
            return False

        # Find the specific router's data from the loaded YAML
        target_router_data = None
        for router_entry in all_network_data.get('routers', []):
            if router_entry.get('mgmt_ip') == ROUTER_CONNECTION_INFO['host']:
                target_router_data = router_entry
                break
        
        if not target_router_data:
            logging.error(f"Router with IP {ROUTER_CONNECTION_INFO['host']} not found in {DATA_FILE}. Aborting.")
            return False

        # Set up Jinja2 environment to load templates from the 'templates' directory
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template(TEMPLATE_FILE)
        
        # Render the template with the specific router's data
        rendered_config = template.render(router=target_router_data) # Pass the single router's data as 'router'
        logging.info(f"--- Rendered Configuration for {target_router_data['name']} ---")
        logging.info(f"\n{rendered_config}") # Display the generated config
        logging.info(f"------------------------------------")

        # Netmiko's send_config_set expects a list of configuration commands.
        # Split the rendered config string by lines and filter out empty ones.
        config_commands_list = [line for line in rendered_config.splitlines() if line.strip()]

        if not config_commands_list:
            logging.error("Generated configuration is empty. Aborting deployment.")
            return False

        # --- Push Configuration via Netmiko ---
        host = ROUTER_CONNECTION_INFO.get('host')
        try:
            logging.info(f"Connecting to {host} via Netmiko...")
            with ConnectHandler(**ROUTER_CONNECTION_INFO) as net_connect:
                logging.info(f"Connected to {host}. Pushing configuration...")
                
                # Use send_config_set to push the list of commands
                output = net_connect.send_config_set(config_commands_list)
                
                logging.info(f"Netmiko push output:\n{output}")
                logging.info(f"Configuration successfully pushed to {host}.")
                return True
        except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
            logging.error(f"Netmiko connection/authentication error to {host}: {e}")
            return False
        except Exception as e:
            logging.error(f"An unexpected error occurred during deployment to {host}: {e}")
            return False

# --- 5. Main Execution Block ---
if __name__ == "__main__":
    print("\n=== Starting IaC Deployment Script ===")
    
    success = deploy_full_configuration()
    
    if success:
        print(f"\nDeployment to {ROUTER_CONNECTION_INFO['host']} completed successfully!")
        print("Please log in to your router and verify the new configuration.")
    else:
        print(f"\nDeployment to {ROUTER_CONNECTION_INFO['host']} failed. Check logs for details.")
    
    print("\n=== Script Finished ===")
    ```

---

## 6. Version Control with Git: The Foundation of IaC

**Git** is a distributed version control system that tracks changes in any set of computer files. It is the cornerstone of IaC.

### 6.1 Core Git Concepts and Commands

Git manages your project's history by tracking changes to files. It operates on three main areas:
*   **Working Directory:** Where you make changes to your files.
*   **Staging Area (Index):** Where you prepare changes to be committed.
*   **Local Repository:** Where Git stores the committed history of your project.

Let's explore essential Git commands:

*   **`git init`**
    *   **Purpose:** Initializes a new Git repository in the current directory. This creates a hidden `.git` folder that Git uses to track changes.
    *   **Example:**
        ```bash
        cd my_network_iac_project
        git init
        ```
    *   **Output:** `Initialized empty Git repository in /path/to/my_network_iac_project/.git/`

*   **`git status`**
    *   **Purpose:** Shows the status of your working directory and staging area. It tells you which files are untracked, modified, or staged for commit.
    *   **Example:**
        ```bash
        # After creating network_data.yaml and templates/hostname.j2
        git status
        ```
    *   **Output (example):**
        ```
        On branch main
        No commits yet
        Untracked files:
          (use "git add <file>..." to include in what will be committed)
            network_data.yaml
            templates/
        nothing added to commit but untracked files present (use "git add" to track)
        ```

*   **`git add <file>` / `git add .`**
    *   **Purpose:** Adds changes from the working directory to the staging area. This prepares them for the next commit. `git add .` stages all changes in the current directory and its subdirectories.
    *   **Example:**
        ```bash
        git add network_data.yaml
        git add templates/hostname.j2
        # Or simply:
        git add .
        ```
    *   **Verify:** After `git add`, `git status` will show files in green, indicating they are staged.

*   **`git commit -m "Message"`**
    *   **Purpose:** Records the staged changes into the local repository as a new version (a "commit"). The message should be a concise summary of the changes.
    *   **Example:**
        ```bash
        git commit -m "Initial deployment of router hostname: MyRouter-Initial"
        ```
    *   **Output (example):**
        ```
        [main (root-commit) 5b7d9c1] Initial deployment of router hostname: MyRouter-Initial
         2 files changed, 5 insertions(+)
         create mode 100644 network_data.yaml
         create mode 100644 templates/hostname.j2
        ```
        (The `5b7d9c1` is a short version of the commit hash.)

*   **`git log`**
    *   **Purpose:** Shows the commit history. You can see who made changes, when, and their commit messages. `git log --oneline` shows a condensed version.
    *   **Example:**
        ```bash
        git log --oneline
        ```
    *   **Output (example):**
        ```
        5b7d9c1 (HEAD -> main) Initial deployment of router hostname: MyRouter-Initial
        ```

### 5.2 Git for Software Development Collaboration

In software development, Git is essential for teams.
*   **Feature Branches:** Developers create separate branches for new features or bug fixes. This isolates their work and prevents them from breaking the main codebase.
*   **Pull Requests (or Merge Requests):** Once a feature is complete on a branch, a developer opens a Pull Request. This is a formal request to merge their changes into a main branch. Pull Requests are critical for:
    *   **Code Review:** Other developers (or network engineers in IaC) review the changes for quality, correctness, and potential issues.
    *   **Automated Checks:** CI/CD pipelines (discussed later) are often triggered by Pull Requests to run automated tests (syntax checks, unit tests, network pre-checks) before merging.
*   **Staying Updated:** Developers frequently use `git pull` to fetch the latest changes from the central repository and integrate them into their local branches, ensuring they are always working with the most current version.

### 5.3 Applying Git in DevNetOps

The practices from software development translate directly to DevNetOps:

*   **Git as the Single Source of Truth:** Your Git repository becomes the definitive record of your network's desired state. Any change to the network *must* go through Git.
*   **Network Engineers as Developers:** Network engineers adopt developer workflows:
    *   Writing configuration as code (YAML, Jinja2).
    *   Committing changes to Git.
    *   Collaborating via branches and pull requests.
    *   Reviewing each other's network changes.
*   **IaC Changes are Code Changes:** A change to a router's hostname in `network_data.yaml` is treated with the same rigor as a code change in an application.
*   **The Power of Rollback:** Because every network state is versioned in Git, reverting to a previous working configuration is as simple as a `git revert` command followed by a re-deployment. This is a game-changer for network stability and disaster recovery.

### 5.4 Essential Git Commands for Collaboration

*   **`git branch <branch-name>`**
    *   **Purpose:** Creates a new branch.
    *   **Example:**
        ```bash
        git branch feature/new-hostname
        ```
*   **`git checkout <branch-name>`**
    *   **Purpose:** Switches to an existing branch. `git checkout -b <branch-name>` creates and switches.
    *   **Example:**
        ```bash
        git checkout feature/new-hostname
        ```
*   **`git merge <branch-name>`**
    *   **Purpose:** Integrates changes from a specified branch into the current branch.
    *   **Example:** (while on `main` branch)
        ```bash
        git merge feature/change-hostname
        ```
*   **`git push`**
    *   **Purpose:** Uploads your local commits to a remote repository (e.g., on GitLab, GitHub).
    *   **Example:**
        ```bash
        git push origin main # Push main branch to remote 'origin'
        ```
*   **`git pull`**
    *   **Purpose:** Fetches changes from a remote repository and merges them into your current local branch. Essential for keeping your local repository synchronized.
    *   **Example:**
        ```bash
        git pull origin main
        ```
*   **`git revert <commit-hash>`**
    *   **Purpose:** Creates a *new* commit that undoes the changes introduced by a specified commit. This is the safest way to undo changes in a shared history, as it doesn't rewrite history.
    *   **Example:** (after finding the commit hash from `git log`)
        ```bash
        git revert 5b7d9c1 # Revert the 'Initial deployment...' commit
        ```

---

## 6. Testing and Verification: Ensuring Network Health

Testing is paramount in IaC to ensure changes are correct and don't break the network. This involves multiple stages.

*   **6.1 Built-in Python Tests (Syntax, File Format):**
    *   **Purpose:** To catch basic errors in your automation code and data files *before* deployment.
    *   **Tools:**
        *   **Python `unittest` / `pytest`:** For testing the logic of your Python scripts (e.g., does `generate_config_from_template` produce the correct output for given data?).
        *   **Linters (e.g., `yamllint`, `pylint`):** Check for syntax errors, style guide violations, and potential bugs in YAML and Python files.
        *   **Schema Validation:** Ensure your YAML data conforms to a predefined structure.

*   **6.2 Network State Verification (Pre- & Post-Checks):**
    *   **Purpose:** To verify the actual state of the network devices.
    *   **Tools:**
        *   **Cisco PyATS (Python Automated Test System):**
            *   **Pre-checks:** Run tests *before* deploying a change to ensure the network is in a healthy, expected state. This prevents deploying to an already broken network.
            *   **Post-checks:** Run tests *after* deploying a change to confirm the desired configuration has been applied correctly and that no unintended side effects (regressions) have occurred. PyATS can connect, collect operational state (`show` commands), parse it into structured data, and make assertions.
        *   **ThousandEyes:**
            *   **Purpose:** Provides end-to-end network and application performance monitoring from an outside-in perspective.
            *   **Integration in CI/CD:** After a network change, ThousandEyes can be triggered to run synthetic tests (e.g., HTTP tests, network path visualization, voice quality tests) to verify the impact on user experience or application performance. This is crucial for validating the *business impact* of a network change.

---

## 7. Continuous Integration/Continuous Delivery (CI/CD) Pipeline

For fully automated IaC, you integrate all these tools into a CI/CD pipeline. **GitLab CI/CD** is a popular platform for this, but concepts apply to Jenkins, GitHub Actions, Azure DevOps, etc.

*   **What is CI/CD?**
    *   **Continuous Integration (CI):** Developers frequently merge code changes. Automated tests run to detect integration issues early.
    *   **Continuous Delivery (CD):** Changes passing CI are automatically prepared for release.
    *   **Continuous Deployment:** Changes are automatically deployed to production after passing all tests.

*   **CI/CD Pipeline Stages (Typical Flow for Network IaC):**
    1.  **Source (Trigger):**
        *   **What triggers it:** A code push to a Git repository (e.g., to a `dev` or `main` branch), a scheduled job, or a manual trigger.
    2.  **Build/Validate:**
        *   **What happens:** Linting (YAML, Python), syntax checks, template rendering (Jinja2).
        *   **Tools:** `yamllint`, `ansible-lint`, Python scripts (for Jinja2 rendering).
        *   **Python's Built-in Test Frameworks:** `unittest` or `pytest` can be used here to test the Python scripts that generate data or render templates.
    3.  **Test (Pre-Deployment):**
        *   **What happens:** Run automated tests against the *current* network state to ensure it's healthy before applying changes.
        *   **Tools:**
            *   **Cisco PyATS (Python Automated Test System):** Connects to devices, gathers operational state, parses it, and makes assertions (e.g., "Is BGP neighbor up?"). This is crucial for pre-checks.
            *   **ThousandEyes (End-to-End Monitoring):** Can be triggered to run synthetic tests (e.g., HTTP tests, network path visualization, voice quality tests) to verify the impact on user experience or application performance.
    4.  **Approval Gate (Manual/Automated):**
        *   **What happens:** A pause in the pipeline, often triggered when deploying to production.
        *   **Approval Flow:**
            *   **Manual:** Requires a human (e.g., network engineer, manager) to review the proposed changes and test results, then explicitly approve.
            *   **Automated:** All previous tests must pass with 100% success.
        *   **Purpose:** To prevent unapproved or untested changes from reaching critical environments.
    5.  **Deploy:**
        *   **What happens:** The validated configuration is pushed to the network devices. This might happen first in a lab/staging environment, then in production.
        *   **Tools:** Netmiko, RESTCONF, NETCONF, Ansible, Terraform, NSO, etc.
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

*   **Benefits of CI/CD for IaC:**
    *   Automated testing and deployment.
    *   Faster and more reliable change management.
    *   Reduced human error.
    *   Enables "GitOps" for network operations, where Git is the single source of truth and the central control point.

---

## 8. Summary and Key Takeaways

### Summary

Ansible is a powerful, agentless automation engine that simplifies configuration management, provisioning, and orchestration using human-readable YAML playbooks. It leverages built-in modules for specific tasks and applies the principle of idempotence. Ansible plays a central role in CI/CD pipelines for Network IaC, where it's used for deployment, and integrated with various testing tools like PyATS for network state verification and ThousandEyes for end-to-end performance validation. This comprehensive approach, often orchestrated by CI/CD platforms like GitLab, enables a "GitOps" model for network operations.

### Key Takeaways

*   **Ansible Core:** Agentless automation engine using Inventory, Modules, and Playbooks (YAML).
*   **IaC Big Picture:** Ansible is the engine that applies the desired state defined in Git.
*   **Ansible vs. Terraform:** Ansible for config management/orchestration; Terraform for provisioning/lifecycle management. Often complementary.
*   **Ansible vs. Python (Netmiko):** Ansible is higher-level (orchestrator); Python/Netmiko is lower-level (granular control). Often used together.
*   **Workflows Automated:** Configuration management, basic provisioning, operational tasks, orchestration.
*   **CI/CD Pipeline:** Automates the entire IaC workflow (Source -> Build -> Test -> Deploy -> Test -> Rollback).
*   **Testing is Multi-layered:**
    *   **Built-in Python/Linters:** For code/syntax quality.
    *   **PyATS:** For network state pre-checks and post-checks (CLI verification).
    *   **ThousandEyes:** For end-to-end performance and application impact verification within the CI/CD pipeline.
*   **CI/CD Triggers:** Code pushes, schedules, manual.
*   **Approval Flow:** Critical for controlled deployments, can be manual or automated.
*   **Rollback:** Automated or manual process to revert to a known good state, triggered by test failures or monitoring alerts.
*   **GitOps:** Git repository is the central control for network operations.

---