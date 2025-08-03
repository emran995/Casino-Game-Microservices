import pytest
import requests
from casino_tests.utils import Endpoints, BASE_URL
import socket


def is_port_open(host, port):
    try:
        socket.create_connection((host, port), timeout=1)
        return True
    except Exception:
        return False


@pytest.mark.parametrize("endpoint", [e.value for e in Endpoints])
def test_endpoint_availability(endpoint):
    if not is_port_open("localhost", 8000):
        pytest.skip("Server not running on localhost:8000")

    url = f"{BASE_URL}{endpoint}"
    method = "get" if "balance" in endpoint else "post"
    if method == "get":
        response = requests.get(url, params={"userId": 123})
    else:
        response = requests.post(url, json={"userId": 123})
    assert response.status_code in [200, 400, 403, 422]
