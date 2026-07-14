import requests
import json
from requests.auth import HTTPBasicAuth

# Suppress SSL warnings for lab environments (use with caution in production)
requests.packages.urllib3.disable_warnings()

# Device details
HOST = '10.10.20.48'
PORT = 443  # Default HTTPS port for RESTCONF
USER = 'developer'
PASS = 'C1sco12345'

# RESTCONF URI for CPU utilization
# YANG Path: Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization
URI = f"https://{HOST}:{PORT}/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"

# Set up HTTP headers for JSON data
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

try:
    # Make the GET request
    response = requests.get(
        url=URI,
        headers=HEADERS,
        auth=HTTPBasicAuth(USER, PASS),
        verify=False  # Do not verify SSL certificate (for lab)
    )

    # Check for successful response
    response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

    # Parse the JSON response
    cpu_data = response.json()
    print(cpu_data['Cisco-IOS-XE-process-cpu-oper:cpu-utilization']['five-seconds'])

    # Print the raw JSON response (for inspection)
    # print("Raw JSON Response:")
    # print(json.dumps(cpu_data, indent=2))

    # Extract and display specific CPU utilization metrics
    if "Cisco-IOS-XE-process-cpu-oper:cpu-utilization" in cpu_data:
        cpu_util = cpu_data["Cisco-IOS-XE-process-cpu-oper:cpu-utilization"]
        print(f"\nCPU Utilization (5 seconds): {cpu_util.get('five-seconds')}%")
        print(f"CPU Utilization (1 minute): {cpu_util.get('one-minute')}%")
        print(f"CPU Utilization (5 minutes): {cpu_util.get('five-minutes')}%")
        # print(f"Total CPU Utilization: {cpu_util.get('cpu-total-utilization')}%")
    else:
        print("CPU utilization data not found in response.")

except requests.exceptions.RequestException as e:
    print(f"Error making RESTCONF request: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response status code: {e.response.status_code}")
        print(f"Response text: {e.response.text}")
except json.JSONDecodeError:
    print("Error decoding JSON response.")
    print(f"Response text: {response.text}")