# Python Basics for Network Automation: Module 4 Theory Guide

## Programming Device Automation with Paramiko Library

**[Your Organization/Name]**
**September 01, 2025**

---

## 1. Introduction to Paramiko

In Module 3, you learned about Netmiko, a high-level library for network automation. Netmiko is excellent because it handles many complexities of CLI interaction for you. However, sometimes you need more control, or you might be working with a device or a specific SSH feature that Netmiko doesn't fully support or abstract away. This is where **Paramiko** comes in.

**What is Paramiko?**
Paramiko is a pure Python implementation of the SSHv2 protocol. This means it allows your Python scripts to act like an SSH client, connecting to remote servers and devices, executing commands, and transferring files securely. It essentially provides the raw building blocks for SSH communication.

**Why use Paramiko (compared to Netmiko)?**
*   **Lower-Level Control:** Paramiko gives you direct access to the SSH protocol. This means you can do things that Netmiko might not expose easily, or that require more fine-grained control:
    *   **Interactive Shells:** Building custom terminal emulators or handling complex, multi-step interactive prompts that Netmiko's `send_command` or `send_config_set` might not fully cover.
    *   **File Transfer (SFTP):** Paramiko includes an SFTP client, allowing you to upload and download files to/from network devices or servers. This is crucial for tasks like firmware upgrades, transferring configuration files, or collecting logs directly.
    *   **Advanced Authentication:** Support for various SSH key types, agent forwarding, or custom authentication flows.
    *   **Port Forwarding:** Setting up secure tunnels for other services.
    *   **Multiple Channels:** Opening several concurrent command channels over a single SSH connection.
*   **Building Block:** Many higher-level libraries (including Netmiko!) are built on top of Paramiko. Understanding Paramiko helps you understand how these libraries work under the hood, giving you deeper insight into SSH communication.
*   **Flexibility:** If you encounter a device or a scenario where Netmiko's abstractions get in the way, Paramiko offers the flexibility to implement custom solutions.
*   **Not just for Network Devices:** Paramiko can connect to any SSH server (Linux servers, cloud instances, etc.), making it a versatile tool beyond just network automation.

**When to choose Paramiko over Netmiko:**
*   You need very specific SSH features not exposed by Netmiko (e.g., direct SFTP, complex interactive sessions).
*   You are building a custom SSH-based tool or a specialized automation framework.
*   You are connecting to non-network SSH servers (e.g., Linux servers).
*   You want to understand the underlying SSH communication for debugging or learning purposes.

**When to choose Netmiko over Paramiko:**
*   For most common network device interactions (sending `show` commands, pushing configurations).
*   When you want simplicity and speed of development, as Netmiko handles many complexities automatically.
*   When you need robust, out-of-the-box handling of device prompts, pagination, and error messages (Netmiko excels here).

---

## 2. Paramiko Basics: Getting Started

*   **2.1 Installation:**
    *   Always install Paramiko within your project's virtual environment.
    *   Open your terminal (with your virtual environment activated) and run:
        ```bash
        pip install paramiko
        ```

*   **2.2 Key Paramiko Components:**

    *   **`paramiko.SSHClient`:** This is the most common and easiest way to connect to an SSH server. It acts like a standard SSH client, handling the connection, authentication, and command execution.
    *   **`paramiko.Transport`:** A lower-level component that handles the actual SSH connection setup (encryption, authentication). You typically use `SSHClient` unless you need very fine-grained control over the connection's establishment.
    *   **`paramiko.Channel`:** Once an SSH `Transport` is established, you can open one or more `Channel` objects. Each channel represents a logical connection for a specific purpose (e.g., executing commands, interactive shell, SFTP). `SSHClient.exec_command()` automatically creates a channel for you behind the scenes.

*   **2.3 Connecting to a Device using `SSHClient`**
    *   The `SSHClient` object is your primary interface.
    *   You need to tell Paramiko how to handle unknown host keys (the unique identifier of the remote server).
        *   `client.load_system_host_keys()`: (Recommended for production) Trusts host keys already known by your system.
        *   `client.set_missing_host_key_policy(paramiko.AutoAddPolicy())`: (Convenient for labs, less secure for production) Automatically adds new host keys to your `known_hosts` file. This means the first time you connect to a new host, Paramiko will trust it without asking.
        *   `client.set_missing_host_key_policy(paramiko.RejectPolicy())`: (Most secure) Rejects connections to unknown hosts.
    *   Then, use the `connect()` method with device details.
    *   Finally, call `close()` when done.

    **Example Connection Flow:**
    ```python
    import paramiko
    from paramiko.ssh_exception import AuthenticationException, SSHException
    import socket # For handling network-related errors

    client = paramiko.SSHClient()
    # Automatically add the remote host's key. Good for labs, be cautious in production.
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

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
    except AuthenticationException:
        print("Error: Authentication failed. Check username/password.")
    except socket.timeout:
        print("Error: Connection timed out. Device might be unreachable or SSH is not enabled.")
    except SSHException as e:
        print(f"Error: SSH connection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if client: # Ensure client object exists before trying to close
            client.close()
            print("Connection closed.")
    ```
    **Expected Output (if connection is successful):**
    ```
    Successfully connected!
    Connection closed.
    ```

---

## 3. Executing Commands Remotely

Once connected, Paramiko offers different ways to execute commands depending on whether the commands are interactive or not.

*   **3.1 `exec_command()`: Running Non-Interactive Commands**
    *   This method is best for commands that don't require user interaction (e.g., `show version`, `show ip interface brief`, `ping`).
    *   It executes a command on the remote device and returns three file-like objects: `stdin`, `stdout`, and `stderr`.
        *   `stdin`: This is the input stream to the remote command. You can `write()` to it if the command expects further input (less common for basic `show` commands).
        *   `stdout`: This is the standard output stream from the remote command. You `read()` from this to get the command's result.
        *   `stderr`: This is the standard error stream. Any error messages generated by the remote command will appear here.
    *   **Important:** You *must* read from `stdout` and `stderr` to prevent the remote process from blocking (waiting for you to read its output).
    *   The output from `stdout.read()` and `stderr.read()` will be in bytes. You need to `decode()` them (typically using `'utf-8'`) to convert them into readable Python strings.

    **Example:**
    ```python
    # Assuming 'client' is an active SSHClient connection
    command = "show version"
    stdin, stdout, stderr = client.exec_command(command)

    # Read the output from stdout and decode it to a string
    output = stdout.read().decode('utf-8').strip() # .strip() removes leading/trailing whitespace
    print(f"Command '{command}' output:\n{output}")

    # Read any errors from stderr and decode them
    errors = stderr.read().decode('utf-8').strip()
    if errors:
        print(f"Command '{command}' errors:\n{errors}")
    ```
    **Expected Output (example for `show version`):**
    ```
    Command 'show version' output:
    Cisco IOS Software, IOS-XE Software, Version 16.9.4
    ... (actual version output) ...
    ```

*   **3.2 `invoke_shell()`: Handling Interactive Sessions (Configuration, Paging)**
    *   For commands that require interaction (like entering configuration mode, responding to prompts, or handling paginated output), `exec_command()` is not suitable.
    *   `invoke_shell()` creates an interactive pseudo-terminal (PTY) session, similar to what you get when you SSH directly into a device.
    *   You interact with this shell by reading from and writing to its `recv()` and `send()` methods. This is more complex than `exec_command()` because you have to:
        1.  Send a command.
        2.  Wait for the prompt or expected output.
        3.  Send the next command or response.
    *   Netmiko handles this complexity for you, which is why it's often preferred for configuration tasks. However, Paramiko gives you the flexibility to build custom interactive logic.

    **Conceptual Example (Simplified interactive shell):**
    ```python
    # Assuming 'client' is an active SSHClient connection
    shell = client.invoke_shell()
    
    # Read initial prompt
    time.sleep(1) # Give device time to send prompt
    output = shell.recv(65535).decode('utf-8')
    print(f"Initial shell output: {output}")

    # Send a command to enter config mode
    shell.send("conf t\n")
    time.sleep(1)
    output = shell.recv(65535).decode('utf-8')
    print(f"After 'conf t': {output}")

    # Send a config command
    shell.send("hostname MY_PARAMIKO_ROUTER\n")
    time.sleep(1)
    output = shell.recv(65535).decode('utf-8')
    print(f"After hostname command: {output}")

    # Exit config mode
    shell.send("end\n")
    time.sleep(1)
    output = shell.recv(65535).decode('utf-8')
    print(f"After 'end': {output}")

    shell.close()
    ```
    *Note: Implementing robust interactive shell automation requires careful handling of prompts, delays, and error checking, which can be complex.*

*   **3.3 File Transfer (SFTPClient)**
    *   Paramiko includes an SFTP (SSH File Transfer Protocol) client, allowing you to securely upload and download files.
    *   You get an `SFTPClient` object from your `SSHClient` connection.

    **Example (Upload and Download):**
    ```python
    # Assuming 'client' is an active SSHClient connection
    sftp_client = client.open_sftp()

    # Upload a local file
    local_path = "my_config_template.txt"
    remote_path = "/flash/my_config_template.txt"
    print(f"Uploading {local_path} to {remote_path}...")
    sftp_client.put(local_path, remote_path)
    print("Upload complete.")

    # Download a remote file
    remote_log_path = "/var/log/syslog" # Example path on a Linux server
    local_download_path = "downloaded_syslog.log"
    print(f"Downloading {remote_log_path} to {local_download_path}...")
    sftp_client.get(remote_log_path, local_download_path)
    print("Download complete.")

    sftp_client.close()
    ```

---

## 4. Integrating with Python Automation Scripts

Paramiko can be a core part of your automation scripts, especially for specialized tasks.

*   **4.1 Device Inventory:**
    *   Store device details (hostname, username, password, port) in a structured format (like a list of dictionaries, similar to what you did for Netmiko).
*   **4.2 Functions for Reusability:**
    *   Wrap Paramiko connection, command execution, and file transfer logic into reusable functions. This makes your main script cleaner and easier to read.
*   **4.3 Error Handling:**
    *   Always use `try-except` blocks to catch Paramiko-specific exceptions (`AuthenticationException`, `SSHException`, `BadHostKeyException`, `socket.timeout`) for robust scripts. This is critical for network operations where connectivity issues are common.

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
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=device_info['host'],
            username=device_info['username'],
            password=device_info['password'],
            port=device_info.get('port', 22),
            timeout=10
        )
        print(f"Connected to {device_info['host']}. Executing '{command}'...")
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        errors = stderr.read().decode('utf-8').strip()
        
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