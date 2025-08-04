"""
Kafka Consumer Test Runner

This script consumes user ID events from the Kafka topic 'qa_user_ids'
and triggers pytest runs for each user ID.

For each consumed userId:
- Runs the test suite 'tests/full_game_flow.py' with --user_id argument
- Captures the result and extracts the final test summary line
- Logs the results to a CSV file: results/user_test_results.csv

Usage:
- Requires Kafka running and messages published to 'qa_user_ids'
- Messages must be in JSON format: {"userId": <int>}
"""

import csv
import os
import json
import subprocess
from confluent_kafka import Consumer

# Initialize Kafka consumer
consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'qa-consumer',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['qa_user_ids'])
print("Waiting for user IDs from Kafka...")

# Create results directory if it doesn't exist
os.makedirs("results", exist_ok=True)

# Open CSV file for writing test results
with open("results/user_test_results.csv", mode="w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["User ID", "Test Result", "Last Line"])

    while True:
        msg = consumer.poll(timeout=3)
        if msg is None:
            break

        event = json.loads(msg.value().decode("utf-8"))
        user_id = event["userId"]
        print(f"\nRunning tests for user_id={user_id}")

        result = subprocess.run(
            ["pytest", "tests/full_game_flow.py", "-q", "--tb=short", f"--user_id={user_id}"],
            capture_output=True, text=True
        )

        status = "Passed" if result.returncode == 0 else "Failed"
        last_line = result.stdout.strip().split("\n")[-1]
        writer.writerow([user_id, status, last_line])

consumer.close()
