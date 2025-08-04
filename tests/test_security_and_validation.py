import pytest
import requests
import socket
from utils.logger import get_logger
from utils.endpoints import Endpoints  # Assuming this is an Enum

logger = get_logger(__name__)

BASE_URL = "http://localhost:8000"


def is_server_up(host="localhost", port=8000):
    """
    Utility function to check if the local server is up and accepting connections.
    """
    try:
        socket.create_connection((host, port), timeout=1)
        return True
    except OSError:
        return False


class TestSecurity:

    @pytest.fixture(scope="class", autouse=True)
    def skip_if_server_off(self):
        """
        Skips all tests in this class if the server at localhost:8000 is not running.
        """
        if not is_server_up():
            logger.warning("Server is not running at http://localhost:8000 — skipping security tests.")
            pytest.skip("Server not running at localhost:8000")
        logger.info("Server is running. Proceeding with security tests.")

    @pytest.mark.parametrize("endpoint", [e.value for e in Endpoints])
    def test_endpoint_availability(self, endpoint):
        """
        Smoke test: Ensure each endpoint is reachable and returns a known response code.
        """
        url = f"{BASE_URL}{endpoint}"
        method = "GET" if "balance" in endpoint else "POST"
        logger.info(f"Testing endpoint availability: {method} {url}")

        if method == "GET":
            response = requests.get(url, params={"userId": 123})
        else:
            response = requests.post(url, json={"userId": 123})

        logger.debug(f"{method} {url} → Status: {response.status_code}")
        assert response.status_code in [200, 400, 403, 422], (
            f"Unexpected status code {response.status_code} for {method} {url}"
        )

    @pytest.mark.parametrize("endpoint", [
        "/user/balance?userId=123",
        "/payment/placeBet",
        "/slot/spin",
        "/notify"
    ])
    def test_unauthorized_access(self, endpoint):
        """
        Test: Send request without authentication headers.
        Expected: Server should respond with 401 or 403 to simulate access control enforcement.
        """
        url = BASE_URL + endpoint
        logger.info(f"Testing unauthorized access to: {url}")

        if "balance" in endpoint:
            response = requests.get(url)
        else:
            response = requests.post(url, json={})

        logger.debug(f"Unauthorized response: {response.status_code} | Body: {response.text}")
        assert response.status_code in (401, 403), (
            f"Expected 401/403 for unauthorized access to {endpoint}, got {response.status_code}"
        )

    def test_sql_injection_in_userid(self):
        """
        Test: Attempt SQL injection via userId query parameter.
        Expected: Server should return validation or security error, not success.
        """
        payload = "123 OR 1=1"
        logger.info(f"Testing SQL injection with payload: {payload}")

        response = requests.get(f"{BASE_URL}/user/balance", params={"userId": payload})

        logger.debug(f"SQL injection response: {response.status_code} | Body: {response.text}")
        assert response.status_code in (400, 422), (
            f"Expected 400/422 for SQL injection, got {response.status_code}"
        )
        assert "error" in response.text.lower() or response.status_code != 200, (
            "SQL injection attempt should not result in 200 OK"
        )

    def test_large_bet_amount(self):
        """
        Test: Submit an extremely large bet amount.
        Expected: Server should return validation error.
        """
        payload = {
            "userId": 123,
            "betAmount": 999_999_999
        }
        logger.info("Testing large bet amount for validation handling")

        response = requests.post(f"{BASE_URL}/payment/placeBet", json=payload)

        logger.debug(f"Large bet response: {response.status_code} | Body: {response.text}")
        assert response.status_code in (400, 422), (
            f"Expected 400/422 for large bet amount, got {response.status_code}"
        )
