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

## 4. Configuration Push: Deploying the Desired State

After generating the configuration, the next crucial step in IaC is to push it to the network devices. This is the "Deploy" stage of your pipeline. The choice of tool depends on your network's capabilities, scale, and existing automation ecosystem.

*   **Common Tools and Protocols for Configuration Push:**

    *   **Netmiko (CLI over SSH/Telnet):**
        *   **How it works:** Connects via SSH/Telnet and sends CLI commands directly to the device.
        *   **When to use:** Ideal for brownfield (existing) networks, devices without API support, or when direct CLI control is preferred. Simple to implement.
        *   **Example:** `net_connect.send_config_set(config_commands)`
        *   **Pros:** Works with almost any device, familiar CLI syntax.
        *   **Cons:** Text-based output, not inherently transactional.

    *   **RESTCONF (API over HTTPS):**
        *   **How it works:** Uses standard HTTP methods (PUT/POST) to send YANG-modeled configuration data (JSON/XML) to the device's RESTCONF API.
        *   **When to use:** Modern devices with RESTCONF enabled. Good for structured, API-driven configuration.
        *   **Example:** `requests.put(restconf_url, json=yang_payload)`
        *   **Pros:** Structured data, programmatic, uses standard web protocols.
        *   **Cons:** Requires device to have RESTCONF enabled, can be complex to build YANG payloads directly.

    *   **NETCONF (Protocol over SSH):**
        *   **How it works:** A dedicated, XML-based protocol designed for transactional configuration management. Uses `edit-config` operations.
        *   **When to use:** When strong transactional integrity, validation, and rollback capabilities are paramount.
        *   **Example:** `ncclient.edit_config(target='running', config=xml_payload)`
        *   **Pros:** Transactional (all or nothing), schema validation, robust error handling.
        *   **Cons:** XML-based (can be verbose), requires specific client libraries.

    *   **Ansible (Configuration Management Tool):**
        *   **How it works:** Agentless tool that uses YAML playbooks to define tasks. Can use Netmiko or other plugins to push configurations.
        *   **When to use:** Orchestrating complex workflows across many devices, multi-vendor environments.
        *   **Pros:** Very popular, large module ecosystem, human-readable playbooks.
        *   **Cons:** Can be slower for very large-scale deployments compared to pure Python.

    *   **Terraform (Infrastructure as Code Tool):**
        *   **How it works:** Declarative tool that manages infrastructure state. Uses providers (plugins) to interact with network devices/APIs.
        *   **When to use:** Managing entire infrastructure stacks (network, compute, cloud) in a state-based manner.
        *   **Pros:** Excellent for managing infrastructure lifecycle, strong state management.
        *   **Cons:** Can be complex for network-only configurations, not designed for granular CLI commands.

    *   **Network Service Orchestrators (NSO) / Network Automation Platforms (Itential):**
        *   **How it works:** Centralized platforms that abstract device details, manage service models, and orchestrate complex workflows. They use various underlying protocols (NETCONF, CLI, API) to interact with devices.
        *   **When to use:** Large enterprises requiring end-to-end service automation, multi-domain orchestration, and advanced workflow capabilities.
        *   **Pros:** High level of abstraction, multi-vendor, service-oriented.
        *   **Cons:** Significant investment in licensing and implementation.

---

## 5. Version Control with Git: The Foundation of IaC

**Git** is a distributed version control system that tracks changes in any set of computer files. It is the cornerstone of IaC.

### 5.1 Core Git Concepts and Commands

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
        git merge feature/new-hostname
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
    *   **Continuous Integration (CI):** Developers frequently merge their code changes into a central repository. Automated processes (builds, tests) run after each merge to quickly detect integration issues.
    *   **Continuous Delivery (CD):** Once changes pass automated tests, they are automatically prepared for release.
    *   **Continuous Deployment:** Changes that pass all tests are automatically deployed to production.

*   **CI/CD Pipeline Stages (Typical Flow for Network IaC):**
    1.  **Source (Trigger):**
        *   **What triggers it:** A code push to a Git repository (e.g., to a `dev` or `main` branch), a scheduled job, or a manual trigger.
    2.  **Build/Validate:**
        *   **What happens:** Linting (YAML, Python), syntax checks, template rendering (Jinja2).
        *   **Tools:** `yamllint`, `pylint`, Python scripts.
    3.  **Test (Pre-Deployment):**
        *   **What happens:** Run automated tests against the *current* network state.
        *   **Tools:** PyATS (pre-checks), Python `unittest`/`pytest` (for code logic).
    4.  **Approval Gate (Manual/Automated):**
        *   **What happens:** A pause in the pipeline.
        *   **Approval Flow:**
            *   **Manual:** Requires a human (e.g., network engineer, manager) to review and click "Approve" before deployment proceeds. This is common for production changes.
            *   **Automated:** All previous tests must pass with 100% success.
        *   **Purpose:** To prevent unapproved or untested changes from reaching critical environments.
    5.  **Deploy:**
        *   **What happens:** The generated configuration is pushed to the network devices. This might happen first in a lab/staging environment, then in production.
        *   **Tools:** Netmiko, RESTCONF, NETCONF, Ansible, Terraform, NSO, etc.
    6.  **Test (Post-Deployment):**
        *   **What happens:** Run automated tests against the *new* network state to confirm changes were applied correctly and no regressions occurred.
        *   **Tools:** PyATS (post-checks), ThousandEyes (end-to-end performance verification).
    7.  **Rollback (Automated/Manual Trigger):**
        *   **What triggers it:**
            *   **Automated:** If post-deployment tests fail, or if a critical monitoring alert is received shortly after deployment.
            *   **Manual:** A human decides to revert.
        *   **How it works:** Git allows reverting to a previous commit. The CI/CD pipeline can then automatically deploy the configuration from that reverted commit.
        *   **Purpose:** To quickly restore network stability if a change introduces issues.

*   **Benefits of CI/CD for IaC:**
    *   Automated testing and deployment.
    *   Faster and more reliable change management.
    *   Reduced human error.
    *   Enables "GitOps" for network operations, where Git is the single source of truth and the central control point.

---

## 8. Summary and Key Takeaways

### Summary

Infrastructure as Code (IaC) transforms network management from manual processes to automated, version-controlled workflows. By describing network configurations in YAML, generating device-specific commands with Jinja2, and pushing them via Netmiko, engineers gain consistency, speed, and reliability. Git provides essential version control, enabling collaboration and easy rollbacks. Automated testing (using tools like PyATS and ThousandEyes) ensures quality, and CI/CD pipelines orchestrate the entire workflow from code commit to verified deployment, often incorporating approval gates and automated rollback mechanisms. This comprehensive approach ushers in a "GitOps" model for network operations.

### Key Takeaways

*   **IaC Core:** Manage infrastructure with code, enabling automation, version control, and idempotence.
*   **YAML:** Human-readable data format for defining network configurations.
*   **Jinja2:** Templating engine to generate device-specific configurations from YAML data.
*   **Configuration Push Tools:** Diverse options like Netmiko, RESTCONF, NETCONF, Ansible, Terraform, NSO, chosen based on needs.
*   **Git:** Essential for version control, collaboration, branching, merging, and especially for easy rollback.
*   **Testing is Multi-layered:**
    *   **Built-in Python/Linters:** For code/syntax quality.
    *   **PyATS:** For network state pre-checks and post-checks (CLI verification).
    *   **ThousandEyes:** For end-to-end performance and application impact verification.
*   **CI/CD Pipeline:** Orchestrates the entire IaC workflow (Source -> Build -> Test -> Deploy -> Test -> Rollback).
*   **CI/CD Triggers:** Code pushes, schedules, manual.
*   **Approval Flow:** Critical for controlled deployments, can be manual or automated.
*   **Rollback:** Automated or manual process to revert to a known good state, triggered by test failures or monitoring alerts.
*   **GitOps:** Git repository is the central control for network operations.

---