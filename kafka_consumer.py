import csv
import os
from confluent_kafka import Consumer
import subprocess
import json

consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'qa-consumer',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['qa_user_ids'])

print("Waiting for user IDs from Kafka...")

# יצירת תיקייה לקבצים אם לא קיימת
os.makedirs("results", exist_ok=True)

# פתיחת קובץ CSV לכתיבה
with open("results/user_test_results.csv", mode="w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["User ID", "Test Result", "Details"])

    while True:
        msg = consumer.poll(timeout=3)
        if msg is None:
            break

        event = json.loads(msg.value().decode("utf-8"))
        user_id = event["userId"]
        print(f"\nRunning tests for user_id={user_id}")

        result = subprocess.run(
            ["pytest", "tests/full_game_flow.py", "--user_id", str(user_id)],
            capture_output=True, text=True
        )

        status = "Passed" if result.returncode == 0 else "Failed"
        details = result.stdout.strip().split("\n")[-1]  # השורה האחרונה
        writer.writerow([user_id, status, details])

consumer.close()
