from enum import Enum
import requests
import os
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


class Endpoints(Enum):
    BALANCE = "/user/balance"
    UPDATE_BALANCE = "/user/update-balance"
    PLACE_BET = "/payment/placeBet"
    PAYOUT = "/payment/payout"
    SPIN = "/slot/spin"
    NOTIFY = "/notify"


def get_balance(user_id):
    return requests.get(f"{BASE_URL}{Endpoints.BALANCE.value}?userId={user_id}")


def update_balance(user_id, new_balance):
    return requests.post(f"{BASE_URL}{Endpoints.UPDATE_BALANCE.value}", json={"userId": user_id, "newBalance": new_balance})


def place_bet(user_id, bet_amount):
    return requests.post(f"{BASE_URL}{Endpoints.PLACE_BET.value}", json={"userId": user_id, "betAmount": bet_amount})


def payout(user_id, transaction_id, win_amount):
    return requests.post(f"{BASE_URL}{Endpoints.PAYOUT.value}", json={"userId": user_id, "transactionId": transaction_id, "winAmount": win_amount})


def spin(user_id, bet_amount, transaction_id):
    return requests.post(f"{BASE_URL}{Endpoints.SPIN.value}", json={"userId": user_id, "betAmount": bet_amount, "transactionId": transaction_id})


def notify(user_id, transaction_id, message):
    return requests.post(f"{BASE_URL}{Endpoints.NOTIFY.value}", json={"userId": user_id, "transactionId": transaction_id, "message": message})


# utility methods + mock response generator
class MockHelper:
    @staticmethod
    def make_mock_response(data, status_code=200):
        return type("MockResponse", (), {
            "status_code": status_code,
            "json": lambda self: data
        })()
