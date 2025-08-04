import pytest
from utils.mock import MockHelper
from utils.endpoints import place_bet, spin, payout, notify
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.usefixtures("mock_requests")
class TestPositiveCases:

    def test_regular_win(self):
        """
        Test: Simulate a full game round where the user wins.
        Expected flow:
        - GET /balance returns 150
        - POST /placeBet deducts 10 → newBalance: 140
        - POST /spin returns WIN with 50
        - POST /payout updates balance to 190
        - POST /notify confirms success
        """
        logger.info("Running test_regular_win")
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": 150})

        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": "txn_001", "newBalance": 140}),
            MockHelper.make_mock_response({"Win": {"winAmount": 50, "message": "Congratulations! You won $50!"}}),
            MockHelper.make_mock_response({"newBalance": 190}),
            MockHelper.make_mock_response({"status": "SENT"})
        ]

        logger.info("Placing bet of 10")
        bet_resp = place_bet(self.user_id, 10)
        assert bet_resp.status_code == 200, "Expected status 200 from place_bet"
        logger.debug(f"place_bet response: {bet_resp.json()}")

        logger.info("Spinning with transaction ID txn_001")
        spin_resp = spin(self.user_id, 10, "txn_001")
        assert spin_resp.status_code == 200, "Expected status 200 from spin"
        logger.debug(f"spin response: {spin_resp.json()}")

        logger.info("Processing payout of 50")
        payout_resp = payout(self.user_id, "txn_001", 50)
        assert payout_resp.status_code == 200, "Expected status 200 from payout"
        assert payout_resp.json()["newBalance"] == 190, "Expected newBalance to be 190 after payout"
        logger.debug(f"payout response: {payout_resp.json()}")

        logger.info("Sending win notification")
        notify_resp = notify(self.user_id, "txn_001", "Congratulations! You won $50!")
        assert notify_resp.status_code == 200, "Expected status 200 from notify"
        assert notify_resp.json()["status"] == "SENT", "Expected status 'SENT' from notify"
        logger.debug(f"notify response: {notify_resp.json()}")

    def test_regular_loss(self):
        """
        Test: Simulate a loss after placing a bet.
        Expected flow:
        - bet deducted
        - spin result is LOSE
        - notify sent with correct message
        """
        logger.info("Running test_regular_loss")
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": 150})
        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": "txn_002", "newBalance": 140}),
            MockHelper.make_mock_response({"Lose": {"message": "Better luck next time!"}}),
            MockHelper.make_mock_response({"status": "SENT"})
        ]

        logger.info("Placing losing bet")
        bet_resp = place_bet(self.user_id, 10)
        assert bet_resp.status_code == 200, "Expected status 200 from place_bet"

        logger.info("Spinning with losing outcome")
        spin_resp = spin(self.user_id, 10, "txn_002")
        assert spin_resp.status_code == 200, "Expected status 200 from spin"
        logger.debug(f"spin response: {spin_resp.json()}")

        logger.info("Sending lose notification")
        notify_resp = notify(self.user_id, "txn_002", "Better luck next time!")
        assert notify_resp.status_code == 200, "Expected status 200 from notify"
        assert notify_resp.json()["status"] == "SENT", "Expected status 'SENT' from notify"
        logger.debug(f"notify response: {notify_resp.json()}")

    def test_multiple_rounds(self):
        """
        Test: Simulate 3 rounds of play with different bet amounts.
        Expected: All place_bet and spin calls succeed (200)
        """
        logger.info("Running test_multiple_rounds")
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": 200})
        self.mock.post.return_value = MockHelper.make_mock_response({})

        for i, bet in enumerate([5, 10, 15]):
            txn_id = f"txn_{i + 1}"
            logger.info(f"Round {i + 1}: Placing bet of {bet}")
            bet_resp = place_bet(self.user_id, bet)
            assert bet_resp.status_code == 200, f"Expected 200 from place_bet in round {i + 1}"

            logger.info(f"Round {i + 1}: Spinning with transaction ID {txn_id}")
            spin_resp = spin(self.user_id, bet, txn_id)
            assert spin_resp.status_code == 200, f"Expected 200 from spin in round {i + 1}"

    def test_notify_format(self):
        """
        Test: Validate that notify returns correct status when format is valid.
        """
        logger.info("Running test_notify_format")
        self.mock.post.return_value = MockHelper.make_mock_response({"status": "SENT"})

        notify_resp = notify(self.user_id, "txn_777", "Congratulations! You won $50!")
        assert notify_resp.status_code == 200, "Expected status 200 from notify"
        assert notify_resp.json()["status"] == "SENT", "Expected status 'SENT' from notify"
        logger.debug(f"notify response: {notify_resp.json()}")

    def test_balance_after_win(self):
        """
        Test: Ensure balance is updated correctly after winning.
        Start: 100 → Bet: 10 → Win: 50 → Expected: 140
        """
        logger.info("Running test_balance_after_win")
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": 100})
        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": "txn_003", "newBalance": 90}),
            MockHelper.make_mock_response({"Win": {"winAmount": 50, "message": "You won!"}}),
            MockHelper.make_mock_response({"newBalance": 140})
        ]

        logger.info("Placing bet of 10")
        bet_resp = place_bet(self.user_id, 10)
        assert bet_resp.status_code == 200, "Expected status 200 from place_bet"

        logger.info("Spinning and receiving WIN")
        spin_resp = spin(self.user_id, 10, "txn_003")
        assert spin_resp.status_code == 200, "Expected status 200 from spin"
        logger.debug(f"spin response: {spin_resp.json()}")

        logger.info("Processing payout of 50")
        payout_resp = payout(self.user_id, "txn_003", 50)
        assert payout_resp.status_code == 200, "Expected status 200 from payout"
        assert payout_resp.json()["newBalance"] == 140, "Expected final balance to be 140"
        logger.debug(f"payout response: {payout_resp.json()}")


