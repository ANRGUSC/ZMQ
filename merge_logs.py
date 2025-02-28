import csv
import os

LOGS_DIR = "logs"
FINAL_FILE = os.path.join(LOGS_DIR, "combined_logs.csv")  # Ensure naming consistency
PEERS = ["P1", "P2", "P3", "P4"]

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

print("✅ Merging logs...")  # Debugging print

# **1. Combine all peer logs into one final CSV**
with open(FINAL_FILE, "w", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["Timestamp", "Type", "Peer", "Message", "Source Peer"])  # Header

    for peer in PEERS:
        log_file = os.path.join(LOGS_DIR, f"peer_{peer}.csv")
        
        if os.path.exists(log_file):
            print(f"🔹 Found {log_file}, merging...")  # Debugging print
            with open(log_file, "r") as infile:
                reader = csv.reader(infile)
                next(reader, None)  # Skip header
                for row in reader:
                    # Ensure row has all required fields (5 columns)
                    while len(row) < 5:
                        row.append("")  # Fill missing values with empty strings
                    writer.writerow(row)  # Append source peer info
        else:
            print(f"⚠️ Missing log file: {log_file}")  # Debugging print

print(f"✅ Logs saved in {FINAL_FILE}")
