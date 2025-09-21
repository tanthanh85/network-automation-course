# config.py

# --- IOS XE Device Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
# This router should be reachable and have SSH enabled.
IOSXE_DEVICE_INFO = {
    "host": "10.10.20.48", # e.g., 10.10.20.40 (from Cisco DevNet Sandbox)
    "username": "developer", # e.g., developer
    "password": "C1sco12345", # e.g., C!sco12345
    "secret": "C1sco12345", # For enable mode if needed (Netmiko)
    "port": 22, # Default SSH port
}