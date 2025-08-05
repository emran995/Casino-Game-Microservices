## Casino Game Microservices – QA Automation Project

### Overview

This project is a test automation solution for a simplified Slot Machine Game composed of four interconnected microservices:

* User Service – Manages player balance
* Payment Service – Handles bets and payouts
* Game Service (Slot) – Executes spin logic and generates outcomes
* Notification Service – Sends game result messages

The automation suite includes:

* True (positive) test cases
* Negative test cases
* Edge case
* Security & validation tests
* Full game flow tests (chained API calls)
* Kafka producer/consumer for multi-user flow
* Docker + Docker Compose setup
* GitLab CI/CD pipeline with 3 distinct stages

### Python Version Requirement

This project requires **Python 3.9 or 3.10**. Please make sure to install it from [https://www.python.org/downloads/](https://www.python.org/downloads/) if you're using an older version.

To check your version:

```bash
python --version
```

### Project Structure

```
emran_project/
├── .gitlab-ci.yml                 # CI/CD Pipeline (GitLab)
├── Dockerfile                     # Docker setup for Kafka services
├── docker-compose.yml            # Kafka + Test runner orchestration
├── kafka_producer.py             # Kafka message sender
├── kafka_consumer.py             # Kafka message consumer (results)
├── requirements.txt              # Python dependencies
├── STP_STD_docs.pdf # Attached test design document
├── tests/
│   ├── test_true_cases.py        # Strong positive cases
│   ├── test_false_cases.py       # Negative test scenarios
│   ├── test_edge_case.py         # Edge test scenario
│   ├── test_security_and_validation.py # Security-focused smoke tests
│   ├── full_game_flow.py         # End-to-end WIN/LOSE test
│   └── conftest.py               # Pytest fixtures
├── utils/
│   ├── endpoints.py              # Wrapper functions for all services
│   ├── mock.py                   # Mock helper for simulated API calls
│   ├── logger.py                 # Logging utility
│   └── base_game_test.py         # Shared test logic
```

### How to Run Tests Locally

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Run specific test groups

```bash
# True test cases
pytest tests/test_true_cases.py

# Negative test cases
pytest tests/test_false_cases.py

# Full game end-to-end flow
pytest tests/full_game_flow.py

# Security validations
pytest tests/test_security_and_validation.py

# Kafka multi-user flow
docker-compose up --abort-on-container-exit
```

### GitLab CI/CD Explained

This project includes full CI/CD automation using GitLab. The pipeline runs automatically on each push or merge request into `main`.

#### Stages Overview

| Stage | Purpose                            | Test Files                                                          |
| ----- | ---------------------------------- | ------------------------------------------------------------------- |
| smoke | Quick smoke tests (auth, security) | test\_security\_and\_validation.py                                  |
| test  | Main functional tests              | test\_true\_cases.py, test\_false\_cases.py, full\_game\_flow\.py   |
| kafka | Kafka-based multi-user simulation  | Runs kafka\_producer.py and kafka\_consumer.py using Docker Compose |

### Why Docker & Compose?

GitLab CI/CD does not support Kafka by default. To enable reliable test execution with Kafka, we used:

* Dockerfile: Defines a test runner image
* docker-compose.yml: Spins up Kafka broker, Zookeeper, test runner, and services in a shared network

This makes Kafka tests portable across local and CI environments.

### Test Summary

#### True Cases (Positive)

* Full game flow with WIN
* Full game flow with LOSE
* Maximum allowed bet
* Minimum allowed bet
* Consistent transactionId flow

#### False Cases (Negative)

* Missing userId
* Negative betAmount
* Invalid transactionId
* Unauthorized access simulation
* API call sequence violation (e.g., payout before spin)

#### Edge Case

* Simulating delayed response from /slot/spin to test resilience

### Kafka Test Scenario

* kafka\_producer.py sends multiple user bets
* kafka\_consumer.py listens and validates outcomes
* Designed to run in the CI kafka stage with Docker Compose

### Assumptions Made

* All services respond with predictable JSON structure (mocked or real)
* Kafka broker will run via Docker on CI/CD
* userId, betAmount, and transactionId are generated or mocked consistently

### Time Taken

* Analysis & Design: \~1 hour
* Test Automation: \~4 hours
* CI/CD, Docker, Kafka setup: \~2 hours
* Debugging & Reporting: \~1 hour
