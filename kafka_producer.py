"""
Kafka Producer Script

This script sends 1000 mock user ID events (userId 1 to 1000) to the Kafka topic 'qa_user_ids'.

Each event is a JSON object in the form:
{
    "userId": <number>
}

Details:
- Uses confluent_kafka.Producer to connect to Kafka on 'kafka:9092'
- Produces messages to the topic 'qa_user_ids'
- Sends events sequentially from userId 1 to 1000
- Uses producer.flush() to ensure all messages are delivered before exiting

This script is intended for automated testing or populating test data in a QA environment.
"""

from confluent_kafka import Producer
import json

producer = Producer({'bootstrap.servers': 'kafka:9092'})

for user_id in range(1, 1001):
    event = {"userId": user_id}
    producer.produce("qa_user_ids", value=json.dumps(event))
    print(f"Sent user {user_id}")

producer.flush()
