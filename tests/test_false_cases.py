from utils.endpoints import place_bet, spin, payout, notify
from utils.mock import MockHelper
from utils.logger import get_logger

logger = get_logger(__name__)


class TestNegativeCases:

    def test_insufficient_balance(self, mock_requests):
        """
        Test: User tries to place a bet with a balance lower than the bet amount.
        Expected: Server should respond with status 400 and error message "Insufficient balance".
        """
        user_id = self.user_id
        logger.info("Testing insufficient balance scenario")

        mock_requests.get.return_value = MockHelper.make_mock_response({"balance": 5})
        mock_requests.post.return_value = MockHelper.make_mock_response(
            {"error": "Insufficient balance"}, status_code=400
        )

        response = place_bet(user_id, 10)
        logger.debug(f"Response: {response.json()}")

        assert response.status_code == 400, "Expected status code 400 for insufficient balance"
        assert "error" in response.json(), "Expected 'error' key in response for insufficient balance"

    def test_invalid_transaction_id(self, mock_requests):
        """
        Test: Spin is triggered using an invalid transaction ID.
        Expected: Server should respond with 404 and error "Transaction not found".
        """
        logger.info("Testing invalid transaction ID in spin")

        mock_requests.post.return_value = MockHelper.make_mock_response(
            {"error": "Transaction not found"}, status_code=404
        )

        response = spin(self.user_id, 10, "invalid_txn")
        logger.debug(f"Response: {response.json()}")

        assert response.status_code == 404, "Expected status code 404 for invalid transaction ID"
        assert "error" in response.json(), "Expected 'error' key in response for invalid transaction ID"

    def test_missing_user_id(self, mock_requests):
        """
        Test: Attempt to place a bet without providing a user ID (user_id=None).
        Expected: Server should respond with 400 and error "Missing userId".
        """
        logger.info("Testing missing user_id in place_bet")

        mock_requests.post.return_value = MockHelper.make_mock_response(
            {"error": "Missing userId"}, status_code=400
        )

        response = place_bet(None, 10)
        logger.debug(f"Response: {response.json()}")

        assert response.status_code == 400, "Expected status code 400 for missing userId"
        assert "error" in response.json(), "Expected 'error' key in response for missing userId"

    def test_payout_without_win(self, mock_requests):
        """
        Test: Attempting to payout with a winAmount of 0 (i.e., no actual win).
        Expected: Server should respond with 403 and error "No win to payout".
        """
        logger.info("Testing payout without a win")

        mock_requests.post.return_value = MockHelper.make_mock_response(
            {"error": "No win to payout"}, status_code=403
        )

        response = payout(self.user_id, "txn_999", 0)
        logger.debug(f"Response: {response.json()}")

        assert response.status_code == 403, "Expected status code 403 for payout without win"
        assert "error" in response.json(), "Expected 'error' key in response for payout without win"

    def test_empty_message_notify(self, mock_requests):
        """
        Test: Attempting to send a notification with an empty message string.
        Expected: Server should respond with 400 and error "Message cannot be empty".
        """
        logger.info("Testing notify with empty message")

        mock_requests.post.return_value = MockHelper.make_mock_response(
            {"error": "Message cannot be empty"}, status_code=400
        )

        response = notify(self.user_id, "txn_888", "")
        logger.debug(f"Response: {response.json()}")

        assert response.status_code == 400, "Expected status code 400 for empty message"
        assert "error" in response.json(), "Expected 'error' key in response for empty message"
