# config.py

# --- Cisco Switch Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
# This switch should be reachable and have SSH enabled.
# You can add more switches to this list if you have them.
MANAGED_SWITCHES = [
    {
        "device_type": "cisco_ios", # Or 'cisco_nxos' if applicable
        "host": "devnetsandboxiosxec9k.cisco.com", # e.g., 192.168.1.10
        "username": "thandoan",
        "password": "YW3ja_ji4PN_t3G1",
        "secret": "YW3ja_ji4PN_t3G1", # If your switch uses enable password
        "port": 22, # Default SSH port
    },
    # {
    #     "device_type": "cisco_ios",
    #     "host": "YOUR_SWITCH_IP_2",
    #     "username": "YOUR_SWITCH_USERNAME",
    #     "password": "YOUR_SWITCH_PASSWORD",
    #     "secret": "YOUR_SWITCH_ENABLE_PASSWORD",
    #     "port": 22,
    # },
]