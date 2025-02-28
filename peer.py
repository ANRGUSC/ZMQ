import zmq
import threading
import time
import sys
import csv
import os

# **1. Initialize Peer Identity**
peer_id = sys.argv[1] if len(sys.argv) > 1 else "P1"

context = zmq.Context()

# **2. DEALER Socket for Receiving Messages**
recv_socket = context.socket(zmq.DEALER)
recv_port = 6000 + int(peer_id[-1])  # Assign a unique port for each peer
recv_socket.bind(f"tcp://*:{recv_port}")

# **3. DEALER Socket for Sending Messages**
send_socket = context.socket(zmq.DEALER)
peers = [6001, 6002, 6003, 6004]  # List of peer ports

for port in peers:
    if port != recv_port:  # Avoid connecting to self
        send_socket.connect(f"tcp://localhost:{port}")

print(f"[{peer_id}] Peer-to-Peer Node Active on port {recv_port}...")

# **4. CSV Logging Setup (ONE FILE PER PEER)**
log_file = f"logs/peer_{peer_id}.csv"
os.makedirs("logs", exist_ok=True)

# Initialize CSV with headers if empty
if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Type", "Peer", "Message", "Source Peer"])

# **5. Function to Listen for Incoming Messages**
def listen():
    while True:
        try:
            message = recv_socket.recv_string(flags=zmq.NOBLOCK)
            sender = message.split()[2]  # Extract sender ID
            print(f"[{peer_id}] Received from {sender}: {message}")

            # Log received message
            with open(log_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), "Received", sender, message, peer_id])

        except zmq.Again:
            time.sleep(0.1)  # No message, sleep briefly

# Start listening in a separate thread
listener_thread = threading.Thread(target=listen, daemon=True)
listener_thread.start()

# **6. Sending Messages in a Loop**
start_time = time.time()  # Record start time

while time.time() - start_time < 180:  # Run for 3 minutes (180 seconds)
    message = f"Hello from {peer_id} at {time.strftime('%H:%M:%S')}"
    print(f"[{peer_id}] Sending: {message}")

    for port in peers:
        if port != recv_port:
            send_socket.send_string(message)
            # Log sent message
            with open(log_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), "Sent", f"P{port - 6000}", message, peer_id])

    time.sleep(2)

# **7. Stop the Process After 3 Minutes**
print(f"[{peer_id}] Stopping after 3 minutes.")
