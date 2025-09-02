# Python Basics for Network Automation: Module 4 Theory Guide

## Programming Device Automation with Paramiko Library

**[Your Organization/Name]**
**September 01, 2025**

---

## 1. Introduction to Paramiko

In Module 3, you learned about Netmiko, a high-level library for network automation. Netmiko is great because it handles many complexities for you. However, sometimes you need more control, or you might be working with a device or a specific SSH feature that Netmiko doesn't fully support. This is where **Paramiko** comes in.

**What is Paramiko?**
Paramiko is a pure Python implementation of the SSHv2 protocol. This means it allows your Python scripts to act like an SSH client, connecting to remote servers and devices, executing commands, and transferring files securely.

**Why use Paramiko (compared to Netmiko)?**
*   **Lower-Level Control:** Paramiko gives you direct access to the SSH protocol. This means you can do things that Netmiko might not expose easily, like:
    *   Opening multiple SSH channels (e.g., for concurrent commands over one connection).
    *   Handling specific SSH key types or authentication methods.
    *   Building custom interactive SSH sessions (like a terminal emulator).
*   **Building Block:** Many higher-level libraries (including Netmiko!) are built on top of Paramiko. Understanding Paramiko helps you understand how these libraries work under the hood.
*   **Flexibility:** If you encounter a device or a scenario where Netmiko's abstractions get in the way, Paramiko offers the flexibility to implement custom solutions.
*   **Not just for Network Devices:** Paramiko can connect to any SSH server (Linux servers, cloud instances, etc.), making it a versatile tool beyond just network automation.

**When to choose Paramiko over Netmiko:**
*   You need very specific SSH features not exposed by Netmiko.
*   You are building a custom SSH-based tool.
*   You are connecting to non-network SSH servers.
*   You want to understand the underlying SSH communication.

**When to choose Netmiko over Paramiko:**
*   For most common network device interactions (sending commands, pushing configs).
*   When you want simplicity and speed of development.
*   When you need robust handling of device prompts, pagination, and error messages (Netmiko excels here).

---

## 2. Paramiko Basics: Getting Started

*   **2.1 Installation:**
    *   Install Paramiko within your project's virtual environment.
    *   Open your terminal (with your virtual environment activated) and run:
        ```bash
        pip install paramiko
        ```

*   **2.2 Key Paramiko Components:**

    *   **`paramiko.SSHClient`:** This is the most common and easiest way to connect to an SSH server. It acts like a standard SSH client, handling the connection, authentication, and command execution.
    *   **`paramiko.Transport`:** A lower-level component that handles the actual SSH connection setup (encryption, authentication). You typically use `SSHClient` unless you need very fine-grained control over the connection.
    *   **`paramiko.Channel`:** Once connected, an SSH session can have multiple "channels" for different purposes (e.g., executing commands, transferring files via SFTP). `SSHClient.exec_command()` automatically creates a channel for you.

*   **2.3 Connecting to a Device using `SSHClient`**
    *   The `SSHClient` object is your primary interface.
    *   You need to call `load_system_host_keys()` (to trust known hosts) or `set_missing_host_key_policy()` (to handle unknown hosts). For simplicity in labs, `AutoAddPolicy` is often used, but it's less secure for production.
    *   Then, use the `connect()` method with device details.
    *   Finally, call `close()` when done.

    **Example Connection Flow:**
    ```python
    import paramiko

    client = paramiko.SSHClient()
    client.load_system_host_keys() # Trust known hosts
    # OR (less secure for production, but simple for labs):
    # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname="192.168.1.1",
            username="admin",
            password="cisco",
            port=22,
            timeout=10 # Connection timeout in seconds
        )
        print("Successfully connected!")
        # Perform operations
    except paramiko.AuthenticationException:
        print("Authentication failed. Check username/password.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except Exception as e:
        print(f"General error: {e}")
    finally:
        if client:
            client.close()
            print("Connection closed.")
    ```

---

## 3. Executing Commands Remotely

Once connected, `SSHClient.exec_command()` is used to run commands.

*   **3.1 `exec_command()`: Running a Single Command**
    *   This method executes a command on the remote device and returns three file-like objects: `stdin`, `stdout`, and `stderr`.
    *   `stdin`: Used to send input to the remote command (less common for network devices).
    *   `stdout`: Contains the normal output of the command.
    *   `stderr`: Contains any error messages from the command.
    *   **Important:** You must read from `stdout` and `stderr` to prevent the remote process from blocking.

    **Example:**
    ```python
    # Assuming 'client' is an active SSHClient connection
    command = "show version"
    stdin, stdout, stderr = client.exec_command(command)

    # Read the output from stdout
    output = stdout.read().decode('utf-8')
    print(f"Command '{command}' output:\n{output}")

    # Read any errors from stderr
    errors = stderr.read().decode('utf-8')
    if errors:
        print(f"Command '{command}' errors:\n{errors}")
    ```
    **Expected Output (example for `show version`):**
    ```
    Command 'show version' output:
    Cisco IOS Software, IOS-XE Software, Version 16.9.4
    ...
    ```

*   **3.2 Handling Device Prompts and Interactive Sessions:**
    *   `exec_command()` is best for non-interactive commands (like `show` commands).
    *   Paramiko also supports more interactive sessions (like entering configuration mode, where the prompt changes) using `client.invoke_shell()`. This is more complex and involves reading/writing to a PTY (pseudo-terminal). Netmiko handles this complexity for you, which is why it's often preferred for configuration tasks. For this module, we'll focus on `exec_command()`.

---

## 4. Integrating with Python Automation Scripts

Paramiko can be a core part of your automation scripts.

*   **4.1 Device Inventory:**
    *   Store device details (hostname, username, password) in a structured format (like a list of dictionaries, similar to what you did for Netmiko).
*   **4.2 Functions for Reusability:**
    *   Wrap Paramiko connection and command execution logic into reusable functions. This makes your main script cleaner and easier to read.
*   **4.3 Error Handling:**
    *   Always use `try-except` blocks to catch Paramiko-specific exceptions (`AuthenticationException`, `SSHException`, `BadHostKeyException`, `NoValidConnectionsError`) for robust scripts.

**Conceptual Script Structure:**
```python
import paramiko
# ... other imports (time, etc.)

# Device list (from devices.py)
my_device = {
    "host": "192.168.1.1",
    "username": "admin",
    "password": "cisco"
}

def connect_and_execute(device_info, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Less secure, but simple for labs
    try:
        client.connect(
            hostname=device_info['host'],
            username=device_info['username'],
            password=device_info['password'],
            port=22,
            timeout=10
        )
        print(f"Connected to {device_info['host']}. Executing '{command}'...")
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        errors = stderr.read().decode('utf-8')
        
        if errors:
            return f"Error executing '{command}' on {device_info['host']}:\n{errors}"
        return f"Output from {device_info['host']} for '{command}':\n{output}"
    except Exception as e:
        return f"Failed to connect or execute command on {device_info['host']}: {e}"
    finally:
        if client:
            client.close()

# Main execution
if __name__ == "__main__":
    result = connect_and_execute(my_device, "show clock")
    print(result)