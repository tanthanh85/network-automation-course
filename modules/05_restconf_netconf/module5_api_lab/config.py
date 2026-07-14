# config.py

# --- IOS XE API Information (REPLACE WITH YOUR ACTUAL LAB DETAILS) ---
# This router should be reachable and have RESTCONF and NETCONF enabled.
# We use a single set of credentials for both APIs on the same device.
IOSXE_DEVICE_INFO = {
    "host": "10.10.20.48", # e.g., 10.10.20.40 (from Cisco DevNet Sandbox)
    "username": "developer", # e.g., developer
    "password": "C1sco12345", # e.g., C!sco12345
    "restconf_port": 443, # Default HTTPS port for RESTCONF
    "netconf_port": 830, # Default NETCONF over SSH port
    "verify_ssl": False # Set to True in production for RESTCONF if you have proper CA certificates
}