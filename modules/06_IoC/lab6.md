
# Lab 6 – Infrastructure as Code with Netmiko, YAML, Jinja2, pyATS and Git Version Control

## Objective

In this lab, learners will manage **OSPF configuration** on a Cisco IOS XE router using **YAML + Jinja2 + Netmiko**. The configuration is version-controlled with **Git**, and learners will simulate a typical IaC process: update config, push to device, test with pyATS, and rollback on failure.

## Estimated Time
2–3 hours

---

## Prerequisites

- DevNet Sandbox: IOS XE on CSR1000v Always-On
- Tools installed:
  - Python 3.9+
  - `netmiko`, `pyats`, `jinja2`, `pyyaml`
- Git + GitHub or GitLab
- VSCode

🔐 **IOS XE Sandbox Info**  
- Hostname: `sandbox-iosxe-latest-1.cisco.com`  
- SSH Port: `22`  
- Username: `developer`  
- Password: `C1sco12345`  

---

## Lab Scenario Overview

You are provided with a working Git-based IaC repository containing:

- `ospf_base.yaml` – the original OSPF config
- `ospf_template.j2` – Jinja2 template to render OSPF config
- `deploy_ospf.py` – deploy script (Netmiko)
- `test_ospf.py` – verify script (pyATS)
- `rollback_ospf.py` – rollback script to remove OSPF
- `.gitignore` – to exclude `.venv`, log files

Your task: **add new networks to OSPF**, commit the change, deploy, test, and rollback if needed.

---

## Step-by-Step Instructions

### Step 1 – Clone the Lab Repo and Setup

```bash
git clone https://gitlab.com/<your-username>/ospf-netmiko-lab.git
cd ospf-netmiko-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

✅ **Git Check**

```bash
git status
git log --oneline
```

---

### Step 2 – Add New OSPF Networks

Open the file: `data/ospf_base.yaml`

```yaml
ospf:
  process_id: 1
  router_id: 1.1.1.1
  networks:
    - ip: 192.168.0.0
      wildcard: 0.0.255.255
      area: 0
    - ip: 10.10.10.0
      wildcard: 0.0.0.255
      area: 1
    - ip: 172.16.0.0
      wildcard: 0.0.255.255
      area: 2    # <--- YOU ADD THIS NEW NETWORK
```

✅ Git Commit

```bash
git checkout -b feature/add-area2
git status
git add data/ospf_base.yaml
git commit -m "Added OSPF area 2 with 172.16.0.0 network"
```

---

### Step 3 – Deploy to Device

Run:

```bash
python3 scripts/deploy_ospf.py
```

✅ **Expected Output**

```bash
[INFO] Connecting to sandbox-iosxe-latest-1.cisco.com
[INFO] Sending OSPF config via SSH...
[OK] Configuration applied successfully!
```

✅ Git Commit:

```bash
git add scripts/deploy_ospf.py
git commit -m "Deployed updated OSPF config with area 2"
```

---

### Step 4 – Validate with pyATS

Run:

```bash
genie learn ospf --testbed-file testbed.yaml --output ospf_validation
cat ospf_validation/ospf/ops/ospf/ospf.txt
```

✅ **Expected Output:** OSPF neighbor up, area 2 is active

If the new config causes an issue (e.g., neighbor down), continue to rollback.

---

### Step 5 – Rollback Configuration

Run rollback script:

```bash
python3 scripts/rollback_ospf.py
```

✅ **Expected Output**

```bash
[INFO] Removed OSPF networks in area 2
[OK] Rollback successful
```

✅ Git Commit:

```bash
git revert HEAD
# OR
git checkout main
git merge --no-ff feature/add-area2
# Then:
git revert <commit-id-of-bad-change>
```

---

## Homework Challenges

1. Add two more OSPF areas (area 3, 4)
2. Write a function to backup current config before pushing
3. Create a GitLab CI/CD pipeline to validate YAML, deploy via Netmiko, test with pyATS
4. Practice using Git:
   - `git fetch`, `git pull`, `git merge`, `git revert`
   - Branch naming: `feature/`, `fix/`, `rollback/`
   - Add a `README.md` describing this lab

---

## Takeaway Summary

✅ This lab reinforces:

- IaC with YAML + Jinja2 + Netmiko + pyATS
- Git for change tracking, rollback, branching
- Real-world process: modify → commit → deploy → test → rollback

