# app.py
from flask import Flask, render_template
import time
from iosxe_api_functions import (
    get_cpu_utilization_restconf, get_memory_utilization_restconf,
    get_gigabitethernet1_utilization_netconf
)

app = Flask(__name__)

@app.route('/')
def index():
    """
    Main dashboard route. Fetches metrics from RESTCONF and NETCONF and renders the HTML template.
    """
    # --- Fetch RESTCONF Data (CPU & Memory) ---
    cpu_rc = get_cpu_utilization_restconf()
    mem_used_rc, mem_total_rc = get_memory_utilization_restconf()
    
    # --- Fetch NETCONF Data (GigabitEthernet1 Utilization) ---
    gigabit_stats_nc = get_gigabitethernet1_utilization_netconf()

    # Render the HTML template with the fetched data
    return render_template(
        'index.html',
        # RESTCONF Data
        cpu_util_rc=cpu_rc,
        memory_used_rc=mem_used_rc,
        memory_total_rc=mem_total_rc,
        # NETCONF Data
        gig1_in_octets=gigabit_stats_nc['in_octets'],
        gig1_out_octets=gigabit_stats_nc['out_octets'],
        gig1_in_pkts=gigabit_stats_nc['in_pkts'],
        gig1_out_pkts=gigabit_stats_nc['out_pkts'],
        current_time=time.strftime("%Y-%m-%d %H:%M:%S")
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)