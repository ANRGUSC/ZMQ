#!/bin/bash

echo "✅ Starting peers..."
python3 peer.py P1 & 
PID1=$!
python3 peer.py P2 & 
PID2=$!
python3 peer.py P3 & 
PID3=$!
python3 peer.py P4 & 
PID4=$!

echo "⏳ Peers running. Collecting messages for 1 minute..."
sleep 60  # Wait exactly 3 minutes

echo "🛑 Stopping all peers..."
kill $PID1 $PID2 $PID3 $PID4

echo "✅ Merging logs..."
python3 merge_logs.py

echo "✅ Logs saved in logs/combined_logs.csv"
