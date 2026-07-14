# devices.py

# --- SINGLE DEVICE FOR LAB 1 & 2 ---
# REPLACE THESE DUMMY VALUES WITH YOUR ACTUAL LAB DEVICE DETAILS!
# This device should be reachable and have SSH enabled with the provided credentials.
single_device = {
    "device_type": "cisco_ios",
    "host": "10.10.20.48", # DUMMY IP - REPLACE WITH YOUR DEVICE'S IP
    "username": "developer", # DUMMY USERNAME - REPLACE WITH YOUR DEVICE'S USERNAME
    "password": "C1sco12345", # DUMMY PASSWORD - REPLACE WITH YOUR DEVICE'S PASSWORD
    "secret": "dummy_enable", # DUMMY ENABLE PASSWORD - REPLACE IF YOUR DEVICE USES ONE
    "port": 22, # Default SSH port
    # "session_log": "device_session.log", # Uncomment to log SSH session
}

# --- MULTIPLE DEVICES FOR LAB 3 ---
# REPLACE THESE DUMMY VALUES WITH YOUR ACTUAL LAB DEVICE DETAILS!
# Add as many devices as you have available in your lab.
multi_devices = [
    {
        "device_type": "cisco_ios",
        "host": "10.10.20.48", # DUMMY IP 1 (can be the same as single_device if you only have one)
        "username": "developer",
        "password": "C1sco12345",
        "secret": "dummy_enable",
    },
    {
        "device_type": "cisco_xr", # in Cisco Sandbox, this is a IOS XR router
        "host": "10.10.20.35", # DUMMY IP 2
        "username": "developer",
        "password": "C1sco12345",
        "secret": "dummy_enable",
    }

    # Add more device dictionaries here if you have more lab devices
    # Example:
    # {
    #     "device_type": "cisco_ios",
    #     "host": "192.168.1.13",
    #     "username": "dummy_user",
    #     "password": "dummy_password",
    #     "secret": "dummy_enable",
    # },
]