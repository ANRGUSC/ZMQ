import subprocess
import time
import os

# List of peers
peers = ["P1", "P2", "P3", "P4"]
processes = []

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# **1️⃣ Start Peers**
for peer in peers:
    log_file = f"logs/{peer}.log"
    print(f"✅ Starting {peer}...")

    with open(log_file, "w") as log:
        process = subprocess.Popen(["python", "peer.py", peer], stdout=log, stderr=log)
        processes.append(process)
    
    time.sleep(1)  # Small delay to avoid port conflicts

print("✅ All peers are running. Collecting logs...")

# **2️⃣ Allow Some Time to Collect Messages**
time.sleep(10)  # Adjust as needed

# **3️⃣ Merge Logs**
print("✅ Merging logs...")
subprocess.run(["python", "combine_logs.py"])

print("✅ Logs merged. Check `logs/combined_P1.csv`, `combined_P2.csv`, etc.")

# **4️⃣ Graceful Shutdown on CTRL+C**
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Stopping all peers...")
    for process in processes:
        process.terminate()
