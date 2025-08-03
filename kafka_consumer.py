from confluent_kafka import Consumer
import subprocess
import json

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'qa-consumer',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['qa_user_ids'])

print("Waiting for user IDs from Kafka...")

while True:
    msg = consumer.poll(timeout=3)
    if msg is None:
        break

    event = json.loads(msg.value().decode("utf-8"))
    user_id = event["userId"]

    print(f"\nRunning tests for user_id={user_id}")
    result = subprocess.run(
        ["pytest", "tests/test_negative_cases.py", "--user_id", int(user_id)],
        capture_output=True, text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print(f"Tests failed for user {user_id}")
    else:
        print(f"teTests passed for user {user_id}")

consumer.close()
