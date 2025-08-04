FROM python:3.10-slim

# התקנת כל התלויות הדרושות
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    librdkafka-dev \
    netcat-openbsd \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# העתקת קבצי הפרויקט
WORKDIR /app
COPY . /app

# התקנת ספריות פייתון
RUN pip install --no-cache-dir -r requirements.txt

# הפקודה שתרוץ בתוך הקונטיינר
CMD sh -c "for i in {1..10}; do nc -z kafka 9092 && echo 'Kafka is ready' && break || echo 'Waiting for kafka...' && sleep 5; done && \
    python kafka_consumer.py & sleep 5 && python kafka_producer.py"
