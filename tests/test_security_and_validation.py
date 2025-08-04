import pytest
import requests
import socket
from utils.logger import get_logger  # Assumes you have this in your project

logger = get_logger(__name__)

BASE_URL = "http://localhost:8000"


def is_server_up(host="localhost", port=8000):
    """
    Utility function to check if the local server is up.
    """
    try:
        socket.create_connection((host, port), timeout=1)
        return True
    except Exception:
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
        else:
            logger.info("Server is running. Proceeding with security tests.")

    @pytest.mark.parametrize("endpoint", [e.value for e in Endpoints])
    def test_endpoint_availability(self,endpoint):
        if not is_server_up("localhost", 8000):
            pytest.skip("Server not running on localhost:8000")

        url = f"{BASE_URL}{endpoint}"
        method = "get" if "balance" in endpoint else "post"
        if method == "get":
            response = requests.get(url, params={"userId": 123})
        else:
            response = requests.post(url, json={"userId": 123})
        assert response.status_code in [200, 400, 403, 422]

    @pytest.mark.parametrize("endpoint", [
        "/user/balance?userId=123",
        "/payment/placeBet",
        "/slot/spin",
        "/notify"
    ])
    def test_unauthorized_access(self, endpoint):
        """
        Test: Send request to endpoints without authentication headers.
        Expected: Server should respond with 401 or 403 to simulate protected endpoints.
        """
        url = BASE_URL + endpoint
        logger.info(f"Testing unauthorized access to endpoint: {url}")

        if "balance" in endpoint:
            response = requests.get(url)
        else:
            response = requests.post(url, json={})

        logger.debug(f"Response from {endpoint}: {response.status_code} | {response.text}")
        assert response.status_code in (401, 403), f"Expected 401/403, got {response.status_code} for {endpoint}"

    def test_sql_injection_in_userid(self):
        """
        Test: Try to perform SQL injection via userId parameter.
        Expected: Server should reject the input and not return 200.
        """
        logger.info("Testing SQL injection attempt in userId parameter")
        payload = "123 OR 1=1"
        response = requests.get(BASE_URL + "/user/balance", params={"userId": payload})

        logger.debug(f"SQLi response status: {response.status_code}, body: {response.text}")
        assert response.status_code in (400, 422), f"Expected 400/422 for SQLi input, got {response.status_code}"
        assert "error" in response.text.lower() or response.status_code != 200, "SQLi should not return success response"

    def test_large_bet_amount(self):
        """
        Test: Send an extremely large betAmount to check if system validates input.
        Expected: System should return a validation error (400 or 422).
        """
        logger.info("Testing large bet amount")
        payload = {
            "userId": 123,
            "betAmount": 999999999
        }
        response = requests.post(BASE_URL + "/payment/placeBet", json=payload)

        logger.debug(f"Large bet response: {response.status_code}, body: {response.text}")
        assert response.status_code in (400, 422), f"Expected 400/422 for large bet, got {response.status_code}"
