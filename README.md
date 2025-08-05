## Casino Game Microservices – QA Automation Project

### Overview

This project is a test automation solution for a simplified Slot Machine Game composed of four interconnected microservices:

* **User Service** – Manages player balance
* **Payment Service** – Handles bets and payouts
* **Game Service (Slot)** – Executes spin logic and generates outcomes
* **Notification Service** – Sends game result messages

The automation suite includes:

* True (positive) test cases
* Negative test cases
* Edge case
* Security & validation tests
* Full game flow tests (chained API calls)
* Kafka producer/consumer for multi-user flow
* Docker + Docker Compose setup
* GitLab CI/CD pipeline with 3 distinct stages

### Logs and Debugging

All test run logs are automatically generated and saved under the `logs/` directory at the project root. These logs are useful for debugging failed tests and are collected as artifacts in the CI/CD pipeline.

### Python Version Requirement

This project requires Python 3.9 or 3.10. Please make sure to install it from [https://www.python.org/downloads/](https://www.python.org/downloads/) if you're using an older version.

To check your version:

```bash
python --version
```

### Project Structure

```
emran_project/
├── logs/                         # All test run logs are saved here
├── .gitlab-ci.yml               # CI/CD Pipeline (GitLab)
├── Dockerfile                   # Docker setup for Kafka services
├── docker-compose.yml          # Kafka + Test runner orchestration
├── kafka_producer.py           # Kafka message sender
├── kafka_consumer.py           # Kafka message consumer (results)
├── requirements.txt            # Python dependencies
├── STP_STD_docs.pdf            # Attached test design document
├── tests/
│   ├── test_true_cases.py      # Strong positive cases
│   ├── test_false_cases.py     # Negative test scenarios
│   ├── test_edge_case.py       # Edge test scenario
│   ├── test_security_and_validation.py # Security-focused smoke tests
│   ├── full_game_flow.py       # End-to-end WIN/LOSE test
│   └── conftest.py             # Pytest fixtures
├── utils/
│   ├── endpoints.py            # Wrapper functions for all services
│   ├── mock.py                 # Mock helper for simulated API calls
│   ├── logger.py               # Logging utility
│   └── base_game_test.py       # Shared test logic
```

### How to Run Tests Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run specific test groups:

```bash
# True test cases
pytest tests/test_true_cases.py

# Negative test cases
pytest tests/test_false_cases.py

# Full game end-to-end flow
pytest tests/full_game_flow.py

# Edge case
pytest tests/test_edge_case.py

# Security validations
pytest tests/test_security_and_validation.py

# Kafka multi-user flow
docker-compose up --abort-on-container-exit
```

Optional: Choose a Specific `user_id`
By default, the test suite uses `user_id = 123`. You can override it when running any test by passing the `--user_id` option to pytest:

```bash
pytest tests/test_true_cases.py --user_id=456
```

This value will be:

* Assigned to `self.user_id` in your test classes via the `init_user_id` fixture
* Stored in the environment as `user_id`
* Used dynamically by the application or mocks where needed

### Run by Pytest Marks

```bash
# Smoke tests
pytest -m smoke_tests

# Positive test suite
pytest -m positive_tests

# Negative test suite
pytest -m nigative_tests

# Edge test
pytest -m edge_test

# Full game flow
pytest -m full_game_flow_test
```

### Known Issue & Solution

If you encounter the following error while running tests:

```
ImportError: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'OpenSSL 1.1.0i'
```

This means your Python environment is using an outdated OpenSSL version incompatible with urllib3 v2.0+.

**Solution Options:**

* **Quick Fix:** Downgrade urllib3 to a compatible version:

```bash
pip install "urllib3<2.0"
```

* **Long-Term Fix:** Upgrade to Python 3.10+ which includes OpenSSL 1.1.1 or higher.

This issue often occurs in older or 32-bit Python environments.

### GitLab CI/CD Explained

This project includes full CI/CD automation using GitLab. The pipeline runs automatically on each push or merge request into `main`, and you can also run individual jobs by passing the `SYSTEM_TEST` variable manually.

#### Stages Overview

| Stage | Purpose                            | Pytest Marks                                                                                                               |
| ----- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| smoke | Quick smoke tests (auth, security) | `@pytest.mark.smoke_tests`                                                                                                 |
| test  | Main functional tests              | `@pytest.mark.positive_tests`, `@pytest.mark.nigative_tests`, `@pytest.mark.edge_test`, `@pytest.mark.full_game_flow_test` |
| kafka | Kafka-based multi-user simulation  | (Runs kafka\_producer + consumer)                                                                                          |

### Why Docker & Compose?

GitLab CI/CD does not support Kafka by default. To enable reliable test execution with Kafka, we used:

* **Dockerfile**: Defines a test runner image
* **docker-compose.yml**: Spins up Kafka broker, Zookeeper, test runner, and services in a shared network

This makes Kafka tests portable across local and CI environments.

### Test Summary

**True Cases (Positive)**

* Full game flow with WIN
* Full game flow with LOSE
* Maximum allowed bet
* Minimum allowed bet
* Consistent `transactionId` flow

**False Cases (Negative)**

* Missing `userId`
* Negative `betAmount`
* Invalid `transactionId`
* Unauthorized access simulation
* API call sequence violation (e.g., payout before spin)

**Edge Case**

* Simulating delayed response from `/slot/spin` to test resilience

**Kafka Test Scenario**

* `kafka_producer.py` sends multiple user bets
* `kafka_consumer.py` listens and validates outcomes
* Designed to run in the CI `kafka` stage with Docker Compose

### Assumptions Made

* All services respond with predictable JSON structure (mocked or real)
* Kafka broker will run via Docker on CI/CD
* `userId`, `betAmount`, and `transactionId` are generated or mocked consistently

### Time Taken

* Analysis & Design: \~1 hour
* Test Automation: \~4 hours
* CI/CD, Docker, Kafka setup: \~2 hours
* Debugging & Reporting: \~1 hour
