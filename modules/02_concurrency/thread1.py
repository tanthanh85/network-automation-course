# threading_sync_lab.py
import threading # This module helps us create and manage threads
import time      # We'll use this to simulate delays

# This is a number that all our threads will try to change.
# It's a "shared resource."
shared_counter = 0

def increment_counter_problem(iterations):
    global shared_counter # Tell Python we want to use the global 'shared_counter'
    for _ in range(iterations):
        # --- This is the "critical section" where race conditions happen ---
        # 1. Read the current value
        current_value = shared_counter
        
        # 2. Simulate a tiny delay, like a thread getting distracted
        #    This makes the race condition more likely to appear.
        time.sleep(0.00001) 
        
        # 3. Calculate the new value
        new_value = current_value + 1
        
        # 4. Write the new value back
        shared_counter = new_value
        # --- End of critical section ---

print("--- Observing a Race Condition ---")
num_threads = 5 # We'll have 5 threads working
iterations_per_thread = 10000 # Each thread will try to add 1 to the counter 10,000 times

# If everything worked perfectly, what should the final number be?
expected_total = num_threads * iterations_per_thread
print(f"If all threads worked perfectly, the counter should be: {expected_total}")

threads = []
for i in range(num_threads):
    # Create a thread that will run our 'increment_counter_problem' function
    thread = threading.Thread(target=increment_counter_problem, args=(iterations_per_thread,))
    threads.append(thread)
    thread.start() # Start the thread (tell it to begin its work)

# Wait for all threads to finish their work
for thread in threads:
    thread.join() 

print(f"Actual final counter value:   {shared_counter}")

if shared_counter != expected_total:
    print("!!! Race condition observed: The actual value is NOT what we expected. !!!")
    print("This means threads interfered with each other's updates.")
else:
    print("No race condition observed this time. (Try running it again, it's often random!)")
