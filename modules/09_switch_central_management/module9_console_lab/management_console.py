# management_console.py
from switch_ops import get_switch_connection, get_vlan_brief, create_vlan, assign_port_to_vlan, get_interface_vlan_assignment
from config import MANAGED_SWITCHES
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def display_menu():
    """Displays the main menu options to the admin."""
    print("\n--- Switch Management Console ---")
    print("1. Select Switch")
    print("2. List Available VLANs on Selected Switch")
    print("3. List Ports Belonging to a VLAN on Selected Switch")
    print("4. Create New VLAN on Selected Switch")
    print("5. Assign Port(s) to VLAN on Selected Switch")
    print("6. Exit")
    print("---------------------------------")

def select_switch():
    """Allows the admin to choose a switch from the managed list."""
    if not MANAGED_SWITCHES:
        print("No switches defined in config.py.")
        return None

    print("\n--- Available Switches ---")
    for i, switch in enumerate(MANAGED_SWITCHES):
        print(f"{i+1}. {switch['host']}")
    print("--------------------------")

    while True:
        try:
            choice = int(input("Enter number of switch to select: "))
            if 1 <= choice <= len(MANAGED_SWITCHES):
                selected = MANAGED_SWITCHES[choice-1]
                print(f"Selected switch: {selected['host']}")
                return selected
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def list_vlans(selected_switch_info):
    """Lists all VLANs on the selected switch."""
    if not selected_switch_info:
        print("No switch selected.")
        return

    net_conn = get_switch_connection(selected_switch_info)
    if net_conn:
        print(f"\n--- VLANs on {selected_switch_info['host']} ---")
        vlans = get_vlan_brief(net_conn)
        if vlans:
            for vlan in vlans:
                print(f"  ID: {vlan['id']}, Name: {vlan['name']}, Status: {vlan['status']}, Ports: {', '.join(vlan['ports'])}")
        else:
            print("  No VLANs found or error retrieving.")
        net_conn.disconnect()
    else:
        print(f"Failed to connect to {selected_switch_info['host']}.")

def list_ports_in_vlan(selected_switch_info):
    """Lists ports belonging to a specific VLAN on the selected switch."""
    if not selected_switch_info:
        print("No switch selected.")
        return

    vlan_id = input("Enter VLAN ID to list ports for: ")
    net_conn = get_switch_connection(selected_switch_info)
    if net_conn:
        print(f"\n--- Ports in VLAN {vlan_id} on {selected_switch_info['host']} ---")
        vlans = get_vlan_brief(net_conn)
        found_vlan = False
        for vlan in vlans:
            if vlan['id'] == vlan_id:
                print(f"  VLAN {vlan_id} ({vlan['name']}) Ports: {', '.join(vlan['ports'])}")
                found_vlan = True
                break
        if not found_vlan:
            print(f"  VLAN {vlan_id} not found or has no assigned ports.")
        net_conn.disconnect()
    else:
        print(f"Failed to connect to {selected_switch_info['host']}.")

def handle_create_vlan(selected_switch_info):
    """Handles creating a new VLAN."""
    if not selected_switch_info:
        print("No switch selected.")
        return

    vlan_id = input("Enter new VLAN ID (e.g., 100): ")
    vlan_name = input("Enter new VLAN Name (e.g., DATA_VLAN): ")

    net_conn = get_switch_connection(selected_switch_info)
    if net_conn:
        if create_vlan(net_conn, vlan_id, vlan_name):
            print(f"Successfully sent commands to create VLAN {vlan_id}.")
        else:
            print(f"Failed to create VLAN {vlan_id}.")
        net_conn.disconnect()
    else:
        print(f"Failed to connect to {selected_switch_info['host']}.")

def handle_assign_port_to_vlan(selected_switch_info):
    """Handles assigning port(s) to a VLAN."""
    if not selected_switch_info:
        print("No switch selected.")
        return

    interface_name = input("Enter interface name (e.g., FastEthernet0/1 or GigabitEthernet1/0/1): ")
    vlan_id = input("Enter VLAN ID to assign port(s) to: ")

    net_conn = get_switch_connection(selected_switch_info)
    if net_conn:
        if assign_port_to_vlan(net_conn, interface_name, vlan_id):
            print(f"Successfully sent commands to assign {interface_name} to VLAN {vlan_id}.")
            # Optional: Verify assignment
            time.sleep(2) # Give switch time to update
            assigned_vlan_info = get_interface_vlan_assignment(net_conn, interface_name)
            if assigned_vlan_info and assigned_vlan_info.get("access_vlan") == vlan_id:
                print(f"Verification: {interface_name} is now in VLAN {vlan_id} (Access Mode).")
            else:
                print(f"Verification: Could not confirm {interface_name} in VLAN {vlan_id}.")
        else:
            print(f"Failed to assign {interface_name} to VLAN {vlan_id}.")
        net_conn.disconnect()
    else:
        print(f"Failed to connect to {selected_switch_info['host']}.")

def main():
    """Main function to run the management console."""
    selected_switch = None
    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            selected_switch = select_switch()
        elif choice == '2':
            list_vlans(selected_switch)
        elif choice == '3':
            list_ports_in_vlan(selected_switch)
        elif choice == '4':
            handle_create_vlan(selected_switch)
        elif choice == '5':
            handle_assign_port_to_vlan(selected_switch)
        elif choice == '6':
            print("Exiting console. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()