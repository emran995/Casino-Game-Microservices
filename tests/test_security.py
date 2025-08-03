import pytest
import requests
import socket

BASE_URL = "http://localhost:8000"


def is_server_up(host="localhost", port=8000):
    try:
        socket.create_connection((host, port), timeout=1)
        return True
    except Exception:
        return False


class TestSecurity:

    @pytest.fixture(scope="class", autouse=True)
    def skip_if_server_off(self):
        if not is_server_up():
            pytest.skip("Server not running at localhost:8000")

    @pytest.mark.parametrize("endpoint", [
        "/user/balance?userId=123",
        "/payment/placeBet",
        "/slot/spin",
        "/notify"
    ])
    def test_unauthorized_access(self, endpoint):
        """
        בדיקה שהמערכת מחזירה שגיאה כשאין הרשאות
        (בהנחה שבמערכת אמיתית דרושה הרשאה, כאן זה סימולציה)
        """
        url = BASE_URL + endpoint
        if "balance" in endpoint:
            response = requests.get(url)
        else:
            response = requests.post(url, json={})
        assert response.status_code in (401, 403)

    def test_sql_injection_in_userid(self):
        """
        ניסיון SQL Injection בפרמטר userId
        """
        response = requests.get(BASE_URL + "/user/balance", params={"userId": "123 OR 1=1"})
        assert response.status_code in (400, 422)
        assert "error" in response.text.lower() or response.status_code != 200

    def test_large_bet_amount(self):
        """
        בדיקה שסכום הימור קיצוני נחסם כראוי
        """
        response = requests.post(BASE_URL + "/payment/placeBet", json={
            "userId": 123,
            "betAmount": 999999999
        })
        assert response.status_code in (400, 422)
