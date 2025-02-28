import zmq
import threading
import time
import sys
import json
import os
import random
import csv

# **1. Initialize Peer Identity**
peer_id = sys.argv[1] if len(sys.argv) > 1 else "P1"
peer_port = 6000 + int(peer_id[-1])  # Assign unique port

context = zmq.Context()

# **2. ROUTER Socket for Receiving Messages**
recv_socket = context.socket(zmq.ROUTER)
recv_socket.bind(f"tcp://*:{peer_port}")

# **3. DEALER Socket for Sending Messages**
send_socket = context.socket(zmq.DEALER)

# **4. Seed Nodes**
seed_nodes = {
    "P1": {"id": "P1", "ip": "localhost", "port": 6001},
    "P2": {"id": "P2", "ip": "localhost", "port": 6002},
    "P3": {"id": "P3", "ip": "localhost", "port": 6003},
    "P4": {"id": "P4", "ip": "localhost", "port": 6004},
}

# **5. Maintain Known Peers**
peers = {}
peer_list = set()

# **6. CSV Logging Setup**
log_file = f"logs/peer_{peer_id}.csv"
os.makedirs("logs", exist_ok=True)

# Initialize CSV log with structured headers
if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Peer ID", "Type", "Peer", "Message"])

print(f"[{peer_id}] ✅ Peer-to-Peer Node Active on port {peer_port}...")

# **7. Function to Write to CSV**
def log_event(event_type, peer, message):
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), peer_id, event_type, peer, message])

# **8. Connect to Known Peers (Bootstrapping)**
def bootstrap():
    if peer_id in seed_nodes:
        for seed_name, seed_info in seed_nodes.items():
            if seed_name != peer_id:
                connect_to_peer(seed_name, seed_info)
    else:
        first_seed = random.choice(list(seed_nodes.values()))
        connect_to_peer(first_seed["id"], first_seed)
        send_socket.send_json({
            "type": "NEW_PEER",
            "sender": peer_id,
            "peer_info": {"id": peer_id, "ip": "localhost", "port": peer_port}
        })
        request_known_peers(first_seed["id"])

# **9. Connect to a Peer**
def connect_to_peer(peer_name, peer_info):
    """Ensures connection to a peer and updates peer lists."""
    if peer_name not in peers:
        peers[peer_name] = peer_info
        peer_list.add(peer_name)
        send_socket.connect(f"tcp://{peer_info['ip']}:{peer_info['port']}")
        print(f"[{peer_id}] 🔗 Connected to {peer_name}")
        log_event("Connected", peer_name, "Established connection")

        send_socket.send_json({
            "type": "HELLO",
            "sender": peer_id,
            "message": f"Hello {peer_name}, I have now connected to you!"
        })

# **10. Request List of Known Peers**
def request_known_peers(target_peer):
    """Ask a peer for a full list of known nodes to ensure full connection."""
    send_socket.send_json({
        "type": "REQUEST_PEER_LIST",
        "sender": peer_id
    })
    print(f"[{peer_id}] 🔄 Requested peer list from {target_peer}")
    log_event("Requested Peers", target_peer, "Requested full peer list")

# **11. Broadcast New Peer to All Known Nodes**
def broadcast_new_peer(new_peer_id, new_peer_info):
    """Tell all peers about the new node."""
    msg = {
        "type": "GOSSIP",
        "sender": peer_id,
        "new_peer": new_peer_id,
        "peer_info": new_peer_info
    }

    for peer_name in peer_list:
        if peer_name != new_peer_id and peer_name != peer_id:
            send_socket.send_json(msg)
            print(f"[{peer_id}] 📢 Broadcasting {new_peer_id} to {peer_name}")
            log_event("Broadcast", peer_name, f"Informing about new peer {new_peer_id}")

# **12. Message Handling Loop**
def listen():
    while True:
        try:
            message_parts = recv_socket.recv_multipart()
            message = message_parts[-1].decode('utf-8')

            msg_data = json.loads(message)
            msg_type = msg_data.get("type")
            sender = msg_data["sender"]

            if msg_type == "NEW_PEER":
                new_peer_info = msg_data["peer_info"]
                new_peer_id = new_peer_info["id"]

                if new_peer_id not in peers:
                    connect_to_peer(new_peer_id, new_peer_info)
                    broadcast_new_peer(new_peer_id, new_peer_info)

            elif msg_type == "GOSSIP":
                new_peer_id = msg_data["new_peer"]
                new_peer_info = msg_data["peer_info"]

                if new_peer_id not in peers:
                    print(f"[{peer_id}] 🆕 Learned about {new_peer_id}, connecting...")
                    connect_to_peer(new_peer_id, new_peer_info)
                    broadcast_new_peer(new_peer_id, new_peer_info)

            elif msg_type == "REQUEST_PEER_LIST":
                """Send back the full list of known peers when requested."""
                send_socket.send_json({
                    "type": "PEER_LIST",
                    "sender": peer_id,
                    "peer_list": list(peers.keys())
                })
                print(f"[{peer_id}] 🔄 Sending full peer list to {sender}")
                log_event("Peer List Sent", sender, "Shared full peer list")

            elif msg_type == "PEER_LIST":
                """Update peer list based on received information."""
                received_peers = msg_data["peer_list"]
                for peer_name in received_peers:
                    if peer_name not in peers and peer_name != peer_id:
                        peer_info = {"id": peer_name, "ip": "localhost", "port": 6000 + int(peer_name[-1])}
                        connect_to_peer(peer_name, peer_info)

            elif msg_type == "MESSAGE":
                print(f"[{peer_id}] 📩 Received from {sender}: {msg_data['message']}")
                log_event("Received", sender, msg_data["message"])
                if sender not in peer_list:
                    connect_to_peer(sender, {"id": sender, "ip": "localhost", "port": 6000 + int(sender[-1])})

        except json.JSONDecodeError:
            print(f"[{peer_id}] ⚠️ Received a non-JSON message, ignoring it.")
        except UnicodeDecodeError:
            print(f"[{peer_id}] ⚠️ Received a corrupted message, ignoring it.")

# **13. Start Listening**
listener_thread = threading.Thread(target=listen, daemon=True)
listener_thread.start()

# **14. Bootstrap Peers**
bootstrap()

# **15. Periodically Send Messages to All Peers**
while True:
    for peer_name in list(peer_list):
        if peer_name == peer_id:
            continue  # Avoid sending to itself

        msg = {
            "type": "MESSAGE",
            "sender": peer_id,
            "message": f"Hello from {peer_id} at {time.strftime('%H:%M:%S')}"
        }
        send_socket.send_json(msg)
        print(f"[{peer_id}] 🚀 Sent message to {peer_name}")
        log_event("Sent", peer_name, msg["message"])

    time.sleep(2)
