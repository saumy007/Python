import threading
import time

def daemon_function():
    while True:
        print("Daemon thread is doing something...")
        time.sleep(2)

# Create a daemon thread
daemon_thread = threading.Thread(target=daemon_function)
daemon_thread.setDaemon(True)  # Set as daemon

# Start the daemon thread
daemon_thread.start()

# Main program
print("Main program is doing something...")
time.sleep(5)
print("Main program is done.")
