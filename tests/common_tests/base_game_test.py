from utils.endpoints import get_balance, place_bet, spin, payout, notify
from utils.mock import MockHelper
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseGameTest:

    def _mock_balance(self, amount):
        user = self.user_id
        self.mock.get.return_value = MockHelper.make_mock_response({
            "balance": amount,
            "currency": "USD"
        })
        resp = get_balance(user)
        assert resp.status_code == 200, f"[{user}] Failed to get balance"
        assert resp.json()["currency"] == "USD", f"[{user}] Currency mismatch"
        logger.info(f"[{user}] Balance mocked to ${amount} USD")
        return resp

    def _place_bet_and_assert(self, amount, txn_id):
        user = self.user_id
        resp = place_bet(user, amount)
        assert resp.status_code == 200, f"[{user}] Failed to place bet"
        logger.info(f"[{user}] Placed bet of ${amount}, transactionId={txn_id}")
        return resp

    def _spin_and_assert(self, amount, txn_id, expected_key, win_amount):
        user = self.user_id
        self.mock.post.return_value = MockHelper.make_mock_response({
            expected_key: {"winAmount": win_amount}
        })
        resp = spin(user, amount, txn_id)
        assert resp.status_code == 200, f"[{user}] Spin request failed"
        assert expected_key in resp.json(), f"[{user}] Expected '{expected_key}' in spin result"
        logger.info(f"[{user}] Spin result: {expected_key} with winAmount=${win_amount}")
        return resp

    def _payout_and_assert(self, txn_id, win_amount, expected_balance):
        user = self.user_id
        self.mock.post.return_value = MockHelper.make_mock_response({
            "newBalance": expected_balance,
            "currency": "USD"
        })
        resp = payout(user, txn_id, win_amount)
        assert resp.status_code == 200, f"[{user}] Payout failed"
        assert resp.json()["newBalance"] == expected_balance, f"[{user}] Incorrect balance after payout"
        assert resp.json()["currency"] == "USD", f"[{user}] Currency mismatch in payout"
        logger.info(f"[{user}] Payout of ${win_amount} processed. New balance: ${expected_balance}")
        return resp

    def _notify_and_assert(self, txn_id, message):
        user = self.user_id
        self.mock.post.return_value = MockHelper.make_mock_response({"status": "SENT"})
        resp = notify(user, txn_id, message)
        assert resp.status_code == 200, f"[{user}] Notification failed"
        assert resp.json()["status"] == "SENT", f"[{user}] Notification status incorrect"
        logger.info(f"[{user}] Notification sent successfully: '{message}'")
        return resp
