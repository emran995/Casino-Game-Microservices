# Base image: lightweight Python 3.10
FROM python:3.10-slim

# Install required system packages:
# - gcc, python3-dev: for compiling Python packages with native code
# - librdkafka-dev: Kafka C client library for Python Kafka clients
# - netcat-openbsd: to check if Kafka is reachable (TCP port check)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    librdkafka-dev \
    netcat-openbsd \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy all project files into the container's /app directory
COPY . /app

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Start command:
# 1. Wait for Kafka to be ready on port 9092 (up to 10 attempts)
# 2. Start kafka_consumer.py in the background
# 3. Wait 5 seconds, then start kafka_producer.py
CMD sh -c "for i in {1..10}; do nc -z kafka 9092 && echo 'Kafka is ready' && break || echo 'Waiting for kafka...' && sleep 5; done && \
    python kafka_consumer.py & sleep 5 && python kafka_producer.py"
