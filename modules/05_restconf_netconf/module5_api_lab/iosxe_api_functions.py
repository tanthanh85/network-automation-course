# iosxe_api_functions.py
import requests
import json
from ncclient import manager
from ncclient.operations import RPCError
# import xml.etree.ElementTree as ET
import xmltodict # For easier XML to dict conversion
import logging
import urllib3
urllib3.disable_warnings()

ncclient_logger = logging.getLogger('ncclient')
ncclient_logger.setLevel(logging.WARNING)

from config import IOSXE_DEVICE_INFO # Import device info from config.py

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- RESTCONF Base URLs ---
RESTCONF_BASE_URL = f"https://{IOSXE_DEVICE_INFO['host']}:{IOSXE_DEVICE_INFO['restconf_port']}/restconf/data"
# This is the well-known URI for RESTCONF capability discovery
#RESTCONF_MONITORING_URL = f"https://{IOSXE_DEVICE_INFO['host']}:{IOSXE_DEVICE_INFO['restconf_port']}/restconf/data/ietf-restconf-monitoring:restconf-state/capabilities"


# --- Generic API Helper Functions (used by discovery and data retrieval) ---
def _make_restconf_get_request(path):
    """Internal helper to make a RESTCONF GET request."""
    full_url = f"{RESTCONF_BASE_URL}/{path}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    try:
        response = requests.get(
            full_url,
            headers=headers,
            auth=(IOSXE_DEVICE_INFO['username'], IOSXE_DEVICE_INFO['password']),
            verify=IOSXE_DEVICE_INFO['verify_ssl']
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"RESTCONF Request Error for {path}: {e}")
        return None
    except json.JSONDecodeError:
        logging.error(f"RESTCONF JSON Decode Error for {path} response.")
        return None
    except Exception as e:
        logging.error(f"RESTCONF Unexpected Error for {path}: {e}")
        return None

def _make_netconf_get_request(xml_filter):
    """Internal helper to make a NETCONF GET request."""
    host = IOSXE_DEVICE_INFO['host']
    username = IOSXE_DEVICE_INFO['username']
    password = IOSXE_DEVICE_INFO['password']
    port = IOSXE_DEVICE_INFO['netconf_port']

    try:
        logging.info(f"Connecting to {host}:{port} via NETCONF...")
        with manager.connect(host=host,
                             port=port,
                             username=username,
                             password=password,
                             hostkey_verify=False, # Set to True in production with proper host keys
                             device_params={'name': 'iosxe'},
                             allow_agent=False,
                             look_for_keys=False) as m:
            logging.info(f"Successfully connected to {host} via NETCONF. Sending GET request.")
            
            netconf_reply = m.get(filter=('subtree', xml_filter))
            raw_xml = netconf_reply.xml
            parsed_data = xmltodict.parse(raw_xml)
            
            return parsed_data

    except RPCError as e:
        logging.error(f"NETCONF RPC Error for {host}: {e.info}")
        logging.error(f"Error message: {e.message}")
        return None
    except Exception as e:
        logging.error(f"NETCONF An unexpected error occurred connecting or fetching data from {host}: {e}")
        return None


# --- Capability Discovery Functions ---

# def discover_restconf_capabilities():
#     """Discovers and returns supported YANG modules via RESTCONF."""
#     headers = {
#         "Accept": "application/yang-data+json"
#     }
#     try:
#         response = requests.get(
#             RESTCONF_MONITORING_URL,
#             headers=headers,
#             auth=(IOSXE_DEVICE_INFO['username'], IOSXE_DEVICE_INFO['password']),
#             verify=IOSXE_DEVICE_INFO['verify_ssl']
#         )
#         response.raise_for_status()
#         data = response.json()

#         # print("Restconf respose: " + str(data))
        
#         modules = []
#         # The capabilities are usually under 'ietf-restconf-monitoring:capabilities'
#         # and then 'capability' is a list of URIs
#         capabilities_list = data.get('ietf-restconf-monitoring:capabilities', {}).get('capability', [])
#         for cap_uri in capabilities_list:
#             # Extract module name from URI (e.g., urn:ietf:params:xml:ns:yang:ietf-interfaces?module=ietf-interfaces&revision=2018-02-20)
#             if 'module=' in cap_uri:
#                 module_name = cap_uri.split('module=')[1].split('&')[0]
#                 modules.append(module_name)
#         return sorted(list(set(modules))) # Return unique sorted module names
#     except Exception as e:
#         logging.error(f"Error discovering RESTCONF capabilities: {e}")
#         return []

def discover_netconf_capabilities():
    """Discovers and returns supported YANG modules via NETCONF."""
    host = IOSXE_DEVICE_INFO['host']
    username = IOSXE_DEVICE_INFO['username']
    password = IOSXE_DEVICE_INFO['password']
    port = IOSXE_DEVICE_INFO['netconf_port']

    try:
        logging.info(f"Connecting to {host}:{port} for NETCONF capabilities discovery...")
        with manager.connect(host=host,
                             port=port,
                             username=username,
                             password=password,
                             hostkey_verify=False,
                             device_params={'name': 'iosxe'},
                             allow_agent=False,
                             look_for_keys=False) as m:
            logging.info(f"Successfully connected to {host} for NETCONF capabilities. Retrieving capabilities.")
            
            modules = []
            # ncclient's manager object holds the server capabilities
            for capability in m.server_capabilities:
                # Capabilities are typically in the format:
                # urn:ietf:params:xml:ns:netconf:base:1.0
                # urn:ietf:params:xml:ns:yang:ietf-interfaces?module=ietf-interfaces&revision=2018-02-20
                
                if 'module=' in capability:
                    module_name = capability.split('module=')[1].split('&')[0]
                    modules.append(module_name)
            return sorted(list(set(modules))) # Return unique sorted module names
    except Exception as e:
        logging.error(f"Error discovering NETCONF capabilities: {e}")
        return []


# --- Data Retrieval Functions (for CPU, Memory, and GigabitEthernet1 utilization) ---
# (These functions will be fully detailed in the next section, but are included here for completeness
# if you are copying the entire file at once)

def get_cpu_utilization_restconf():
    """Queries and returns CPU utilization from IOS XE via RESTCONF."""
    path = "Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"
    data = _make_restconf_get_request(path)
    if data:
        try:
            cpu_total = data.get('Cisco-IOS-XE-process-cpu-oper:cpu-utilization', {}).get('five-seconds')
            return int(cpu_total) if cpu_total is not None else "N/A"
        except (TypeError, ValueError) as e:
            logging.error(f"Error parsing RESTCONF CPU data: {e}")
            return "N/A"
    return "N/A"

def get_memory_utilization_restconf():
    """Queries and returns memory utilization from IOS XE via RESTCONF."""
    path = "Cisco-IOS-XE-memory-oper:memory-statistics"
    data = _make_restconf_get_request(path)
    if data:
        try:
            mem_stats = data.get('Cisco-IOS-XE-memory-oper:memory-statistics', {}).get('memory-statistic', [{}])
            if mem_stats and isinstance(mem_stats, list) and len(mem_stats) > 0:
                mem_stats = mem_stats[0]
            
            used = mem_stats.get('used-memory')
            total = mem_stats.get('total-memory')
            return int(used) if used is not None else "N/A", int(total) if total is not None else "N/A"
        except (TypeError, ValueError, IndexError) as e:
            logging.error(f"Error parsing RESTCONF Memory data: {e}")
            return "N/A", "N/A"
    return "N/A", "N/A"

def get_gigabitethernet1_utilization_netconf():
    """Queries and returns GigabitEthernet1 input/output utilization via NETCONF."""
    interface_filter = """
    <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>GigabitEthernet1</name>
            <statistics>
                <in-octets/>
                <out-octets/>
                <in-unicast-pkts/>
                <out-unicast-pkts/>
            </statistics>
        </interface>
    </interfaces-state>
    """
    data = _make_netconf_get_request(interface_filter)
    stats = {
        "in_octets": "N/A",
        "out_octets": "N/A",
        "in_pkts": "N/A",
        "out_pkts": "N/A"
    }
    if data:
        try:
            iface_data = data.get('rpc-reply', {}).get('data', {}).get('interfaces-state', {}).get('interface', {})
            if isinstance(iface_data, list):
                iface_data = iface_data[0] if iface_data else {}

            statistics = iface_data.get('statistics', {})
            
            stats["in_octets"] = statistics.get('in-octets', "N/A")
            stats["out_octets"] = statistics.get('out-octets', "N/A")
            stats["in_pkts"] = statistics.get('in-unicast-pkts', "N/A")
            stats["out_pkts"] = statistics.get('out-unicast-pkts', "N/A")
            
        except (TypeError, ValueError, IndexError) as e:
            logging.error(f"Error parsing NETCONF GigabitEthernet1 stats: {e}")
    return stats


# Standalone test for functions (only runs when this file is executed directly)
if __name__ == '__main__':
    print("--- Testing iosxe_api_functions.py (Capabilities, RESTCONF & NETCONF) ---")
    print("Note: This will attempt to connect to the IOS XE router defined in config.py.")
    
    print("\nNETCONF Supported Modules:")
    netconf_caps = discover_netconf_capabilities()
    for module in netconf_caps:
        print(f"  - {module}")

    print("\n--- RESTCONF Data (CPU & Memory) ---")
    # Test CPU
    cpu_rc = get_cpu_utilization_restconf()
    print(f"RESTCONF CPU Utilization (5-sec): {cpu_rc}%")

    # Test Memory
    mem_used_rc, mem_total_rc = get_memory_utilization_restconf()
    print(f"RESTCONF Memory: {mem_used_rc} used / {mem_total_rc} total bytes")

    print("\n--- NETCONF Data (GigabitEthernet1 Utilization) ---")
    # Test GigabitEthernet1 Utilization
    gigabit_stats_nc = get_gigabitethernet1_utilization_netconf()
    print(f"NETCONF GigabitEthernet1 In-Octets: {gigabit_stats_nc['in_octets']}")
    print(f"NETCONF GigabitEthernet1 Out-Octets: {gigabit_stats_nc['out_octets']}")
    print(f"NETCONF GigabitEthernet1 In-Packets: {gigabit_stats_nc['in_pkts']}")
    print(f"NETCONF GigabitEthernet1 Out-Packets: {gigabit_stats_nc['out_pkts']}")

    print("\n--- Test Complete ---")