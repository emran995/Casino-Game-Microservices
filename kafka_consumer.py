from confluent_kafka import Consumer
import subprocess
import json
import os

# ודא שתקיית results קיימת
os.makedirs("results", exist_ok=True)

# צרכן Kafka
consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'qa-consumer',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['qa_user_ids'])

print("Waiting for user IDs from Kafka...")

with open("results/report.txt", "w", encoding="utf-8") as f:
    while True:
        msg = consumer.poll(timeout=3)
        if msg is None:
            break

        event = json.loads(msg.value().decode("utf-8"))
        user_id = event["userId"]

        f.write(f"\n=== Running tests for user_id={user_id} ===\n")
        print(f"\nRunning tests for user_id={user_id}")

        result = subprocess.run(
            ["pytest", "tests/test_negative_cases.py", "--user_id", str(user_id)],
            capture_output=True, text=True
        )

        f.write(result.stdout + "\n")
        if result.returncode != 0:
            f.write(f"Tests failed for user {user_id}\n")
            print(f"Tests failed for user {user_id}")
        else:
            f.write(f"Tests passed for user {user_id}\n")
            print(f"Tests passed for user {user_id}")

consumer.close()
