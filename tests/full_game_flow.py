import pytest
from utils.endpoints import place_bet, get_balance, spin, payout, notify
from utils.mock import MockHelper
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.usefixtures("mock_requests")
class TestPositiveCases:

    @pytest.mark.parametrize("bet_amount, outcome", [
        (10, "WIN"),
        (10, "LOSE")
    ])
    def test_full_game_flow_with_mock(self, bet_amount, outcome):
        """
        Test Scenario: Full game flow for both WIN and LOSE cases using mocks.

        Steps:
        1. Mock GET /user/balance to return a fixed starting balance (150).
        2. Mock POST /payment/placeBet to deduct the bet and return a transaction ID.
        3. Mock POST /slot/spin to return a WIN or LOSE result based on the parameterized outcome.
           - WIN returns winAmount and message.
           - LOSE returns zero winAmount and different message.
        4. If WIN:
            - Mock POST /payment/payout to return updated balance.
        5. Mock POST /notify to confirm notification was sent.
        6. Run the full flow with:
           - get_balance() → assert balance
           - place_bet() → assert newBalance
           - spin() → assert status and capture outcome
           - payout() if WIN → assert updated balance
           - notify() → assert status SENT
        """

        starting_balance = 150
        txn_id = f"txn_{self.user_id}"
        win_amount = 50

        logger.info(f"Start test for user {self.user_id} with bet {bet_amount} and outcome '{outcome}'")

        # Step 1: Mock GET /user/balance
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": starting_balance})

        # Step 2–5: Setup mocked POST responses
        post_responses = []

        logger.debug("Mocking /payment/placeBet response")
        post_responses.append(MockHelper.make_mock_response({
            "transactionId": txn_id,
            "newBalance": starting_balance - bet_amount
        }))

        logger.debug("Mocking /slot/spin response")
        if outcome == "WIN":
            post_responses.append(MockHelper.make_mock_response({
                "Win": {
                    "winAmount": win_amount,
                    "message": f"Congratulations! You won ${win_amount}!"
                }
            }))
            logger.debug("Mocking /payment/payout response (WIN)")
            post_responses.append(MockHelper.make_mock_response({
                "newBalance": starting_balance - bet_amount + win_amount
            }))
        else:
            post_responses.append(MockHelper.make_mock_response({
                "Lose": {
                    "winAmount": 0,
                    "message": "Better luck next time!"
                }
            }))

        logger.debug("Mocking /notify response")
        post_responses.append(MockHelper.make_mock_response({"status": "SENT"}))
        self.mock.post.side_effect = post_responses

        # Step 6: Run test flow

        logger.info("Calling GET /user/balance")
        balance_resp = get_balance(self.user_id)
        assert balance_resp.status_code == 200, "Failed to get user balance"
        assert balance_resp.json()["balance"] == starting_balance, "Initial balance mismatch"

        logger.info("Calling POST /payment/placeBet")
        bet_resp = place_bet(self.user_id, bet_amount)
        assert bet_resp.status_code == 200, "Failed to place bet"
        assert bet_resp.json()["newBalance"] == starting_balance - bet_amount, "Balance after bet mismatch"

        logger.info("Calling POST /slot/spin")
        spin_resp = spin(self.user_id, bet_amount, txn_id)
        assert spin_resp.status_code == 200, "Spin request failed"
        result = spin_resp.json()

        if "Win" in result:
            msg = result["Win"]["message"]
            logger.info(f"User won! Message: {msg}")

            logger.info("Calling POST /payment/payout")
            payout_resp = payout(self.user_id, txn_id, win_amount)
            assert payout_resp.status_code == 200, "Payout request failed"
            expected_balance = starting_balance - bet_amount + win_amount
            assert payout_resp.json()["newBalance"] == expected_balance, "Balance after payout mismatch"
        else:
            msg = result["Lose"]["message"]
            logger.info(f"User lost. Message: {msg}")

        logger.info("Calling POST /notify")
        notify_resp = notify(self.user_id, txn_id, msg)
        assert notify_resp.status_code == 200, "Notify request failed"
        assert notify_resp.json()["status"] == "SENT", "Notification status not SENT"

        logger.info(f"Test completed successfully for user {self.user_id}")
