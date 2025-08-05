import pytest
from utils.mock import MockHelper
from utils.logger import get_logger
from tests.common_tests.base_game_test import BaseGameTest
from utils.endpoints import spin

logger = get_logger(__name__)


@pytest.mark.usefixtures("mock_requests")
class TestEdgeCase(BaseGameTest):

    def test_bet_with_exact_balance_and_validate_3_reels(self):
        """
        Positive Edge Case:
        User has exactly enough balance to place a bet (10 USD), receives a WIN,
        and goes through the full spin-payout-notify flow successfully.

        Purpose:
        - Validate edge condition: balance == bet
        - Ensure newBalance is 0 after bet
        - Confirm WIN response contains exactly 3 reels
        - Assert data types and structural correctness
        - Ensure payout and notification work as expected
        - Validate currency consistency
        """
        user_id = self.user_id
        bet_amount = 10
        transaction_id = "txn_555"
        expected_reels = ["Cherry", "Cherry", "Cherry"]

        # Step 1: Mock balance to exactly the bet amount
        self._mock_balance(bet_amount)

        # Step 2: Setup all expected responses
        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": transaction_id, "newBalance": 0}),
            MockHelper.make_mock_response({
                "Win": {
                    "userId": user_id,
                    "outcome": "WIN",
                    "winAmount": 30,
                    "message": "You won!",
                    "reels": expected_reels
                }
            }),
            MockHelper.make_mock_response({"newBalance": 30, "currency": "USD"}),
            MockHelper.make_mock_response({"status": "SENT"})
        ]

        # Step 3: Place Bet
        bet_resp = self._place_bet_and_assert(bet_amount, transaction_id)
        assert bet_resp.json()["newBalance"] == 0, "Expected balance to be 0 after full bet"

        # Step 4: Spin
        spin_resp = spin(user_id, bet_amount, transaction_id)
        assert spin_resp.status_code == 200
        spin_result = spin_resp.json()["Win"]

        # Step 5: Validate spin result
        assert isinstance(spin_result.get("winAmount"), (int, float)), "winAmount should be numeric"
        assert isinstance(spin_result.get("message"), str), "Message should be a string"
        assert isinstance(spin_result.get("reels"), list), "Reels should be a list"
        assert len(spin_result["reels"]) == 3, f"Expected 3 reels, got {len(spin_result['reels'])}"
        assert spin_result.get("userId") == user_id, "User ID in response does not match request"

        # Step 6: Payout and Notification
        self._payout_and_assert(transaction_id, spin_result["winAmount"], 30)
        self._notify_and_assert(transaction_id, spin_result["message"])

        logger.info("Test passed: exact balance bet with full WIN flow and structure validation")
