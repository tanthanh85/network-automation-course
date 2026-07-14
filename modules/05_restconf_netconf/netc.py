from ncclient import manager
import xmltodict
import json # Used for pretty printing the dictionary

# Device details
HOST = '10.10.20.48'
PORT = 830  # Default NETCONF port
USER = 'developer'
PASS = 'C1sco12345'

# XML filter to retrieve operational status of GigabitEthernet1
# Using ietf-interfaces YANG model
# NETCONF_FILTER = """
#     <filter type="subtree" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
#       <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
#         <interface>
#           <name>GigabitEthernet1</name>
#         </interface>
#       </interfaces-state>
#     </filter>
# """


NETCONF_FILTER = """
<filter type="subtree" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>GigabitEthernet1</name>
      <oper-status/>
    </interface>
  </interfaces>
</filter>
"""

try:
    # Establish NETCONF session
    with manager.connect(host=HOST,
                         port=PORT,
                         username=USER,
                         password=PASS,
                         hostkey_verify=False, # Set to True in production with proper host keys
                         device_params={'name': 'csr'}) as m: # 'csr' for Cisco IOS XE devices
        print(f"Connected to {HOST} via NETCONF.")

        # Perform a 'get' operation with the filter
        # The 'get' operation retrieves both configuration and operational data
        # 'get_config' would only retrieve configuration data
        result = m.get(NETCONF_FILTER)

        # Print the raw XML response (for inspection)
        print("\nRaw XML Response:")
        # print(result.xml_pretty())
        print(result)

        # Parse the XML response to a Python dictionary using xmltodict
        data_dict = xmltodict.parse(result.xml)

        # Print the dictionary (for inspection)
        print("\nParsed Dictionary Response:")
        print(json.dumps(data_dict, indent=2))

        # Extract operational status from the dictionary
        # Navigating through the dictionary structure based on the YANG model
        # Note: xmltodict often adds ordereddict keys like 'rpc-reply', 'data', etc.
        # It also handles XML namespaces by default, often prefixing with '@' or just using the tag name.
        oper_status = None
        try:
            # Adjust path based on actual XML structure and namespaces
            # Example path for ietf-interfaces:
            # rpc-reply -> data -> interfaces-state -> interface (which is a list) -> oper-status
            interfaces = data_dict['rpc-reply']['data']['interfaces-state']['interface']
            # If there's only one interface matching the filter, it might not be a list
            if isinstance(interfaces, list):
                for iface in interfaces:
                    if iface['name'] == 'GigabitEthernet1':
                        oper_status = iface['oper-status']
                        break
            else: # Single interface returned
                if interfaces['name'] == 'GigabitEthernet1':
                    oper_status = interfaces['oper-status']

        except KeyError as ke:
            print(f"Could not find key in dictionary: {ke}. Check XML structure.")
            
        if oper_status:
            print(f"\nOperational status of GigabitEthernet1: {oper_status}")
        else:
            print("Operational status not found for GigabitEthernet1.")

except Exception as e:
    print(f"Error connecting or retrieving data via NETCONF: {e}")