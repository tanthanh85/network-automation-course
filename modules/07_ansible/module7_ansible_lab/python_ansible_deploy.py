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