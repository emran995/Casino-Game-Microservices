import pytest

from utils.endpoints import notify, payout, spin, place_bet
from utils.mock import MockHelper
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.usefixtures("mock_requests")
class TestExactBalanceEdgeCase:

    def test_exact_balance_bet(self):
        """
        Test Scenario: User with exact balance places a bet, wins, receives payout, and gets notified.

        Steps:
        1. Mock GET /balance to return 10 – simulates user with exact amount needed to bet.
        2. Mock the sequence of POST responses:
            - place_bet returns transaction ID and 0 balance
            - spin returns a WIN response
            - payout updates balance to 30
            - notify returns SENT status
        3. Call place_bet and assert status 200 and balance = 0
        4. Call spin and assert status 200
        5. Call payout and assert status 200 and newBalance = 30
        6. Call notify and assert status 200 and status = SENT
        """

        logger.info("Mocking balance to return 10")
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": 10})

        logger.info("Setting up mocked POST responses")
        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": "txn_555", "newBalance": 0}),
            MockHelper.make_mock_response({"Win": {"winAmount": 30, "message": "You won!"}}),
            MockHelper.make_mock_response({"newBalance": 30}),
            MockHelper.make_mock_response({"status": "SENT"})
        ]

        logger.info("Placing bet of 10 for user 123")
        bet_resp = place_bet(123, 10)
        assert bet_resp.status_code == 200, "place_bet failed: expected status 200"
        assert bet_resp.json()["newBalance"] == 0, "Expected newBalance to be 0 after full bet"
        logger.debug(f"place_bet response: {bet_resp.json()}")

        logger.info("Spinning with transaction ID 'txn_555'")
        spin_resp = spin(123, 10, "txn_555")
        assert spin_resp.status_code == 200, "spin failed: expected status 200"
        logger.debug(f"spin response: {spin_resp.json()}")

        logger.info("Processing payout of 30 for transaction 'txn_555'")
        payout_resp = payout(123, "txn_555", 30)
        assert payout_resp.status_code == 200, "payout failed: expected status 200"
        assert payout_resp.json()["newBalance"] == 30, "Expected newBalance to be 30 after payout"
        logger.debug(f"payout response: {payout_resp.json()}")

        logger.info("Sending notification with message 'You won!'")
        notify_resp = notify(123, "txn_555", "You won!")
        assert notify_resp.status_code == 200, "notify failed: expected status 200"
        assert notify_resp.json()["status"] == "SENT", "Expected notify status to be 'SENT'"
        logger.debug(f"notify response: {notify_resp.json()}")
