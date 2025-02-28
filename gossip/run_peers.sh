#!/bin/bash

# Function to gracefully stop peers
cleanup() {
    echo "🛑 Stopping all peers..."
    pkill -f peer.py
    echo "✅ All peers stopped."
    exit 0
}

# Handle CTRL+C
trap cleanup SIGINT

echo "✅ Starting peers..."
python3 peer.py P1 & 
PID1=$!
python3 peer.py P2 & 
PID2=$!
python3 peer.py P3 & 
PID3=$!
python3 peer.py P4 & 
PID4=$!

echo "⏳ Peers running. Collecting messages for 3 minutes..."
sleep 180  

cleanup  # Gracefully stop peers after 3 mins
