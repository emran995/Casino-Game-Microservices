from confluent_kafka import Producer
import json

producer = Producer({'bootstrap.servers': 'localhost:9092'})

for user_id in range(1, 1001):
    event = {"userId": user_id}
    producer.produce("qa_user_ids", value=json.dumps(event))
    print(f"Sent user {user_id}")

producer.flush()
