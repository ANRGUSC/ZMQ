import os
import csv
import glob

# Directory where logs are stored
log_dir = "logs"
output_file = "logs/merged_logs.csv"

# Get all peer log files
log_files = glob.glob(os.path.join(log_dir, "peer_*.csv"))

# Read headers from the first file
if not log_files:
    print("No log files found.")
    exit()

# Read and merge logs
merged_data = []
header = ["Timestamp", "Peer ID", "Type", "Peer", "Message"]

for file in log_files:
    with open(file, "r", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
        if rows:
            merged_data.extend(rows[1:])  # Skip header row

# Sort merged data by timestamp
merged_data.sort(key=lambda x: x[0])  # Sorts based on Timestamp

# Write to output CSV
with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(merged_data)

print(f"✅ Merged logs saved to {output_file}")
