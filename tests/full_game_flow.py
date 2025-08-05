import pytest
from utils.endpoints import get_balance, spin
from utils.mock import MockHelper
from utils.logger import get_logger
from tests.common_tests.base_game_test import BaseGameTest

logger = get_logger(__name__)


@pytest.mark.full_game_flow_test
@pytest.mark.usefixtures("mock_requests")
class TestPositiveCases(BaseGameTest):

    @pytest.mark.parametrize("bet_amount, outcome", [
        (10, "WIN"),
        (10, "LOSE")
    ])
    def test_full_game_flow_with_mock(self, bet_amount, outcome):
        """
        Full Slot Game Flow (WIN and LOSE)

        Verifies:
        - Balance retrieval and currency
        - Bet deduction and transaction ID
        - WIN or LOSE outcome structure
        - Payout processing (if WIN)
        - Final balance correctness
        - Notification delivery
        """
        starting_balance = 150
        txn_id = f"txn_{self.user_id}"
        logger.info(f"Starting test | User={self.user_id}, Bet={bet_amount}, Outcome={outcome}, Txn={txn_id}")

        self._mock_balance(starting_balance)

        self.mock.post.side_effect = self._build_post_side_effect(txn_id, starting_balance, bet_amount, outcome)
        self._place_bet_and_assert(bet_amount, txn_id)

        logger.info("Spinning the slot...")
        spin_resp = spin(self.user_id, bet_amount, txn_id)
        assert spin_resp.status_code == 200, "[SPIN] Failed to spin"
        spin_result = spin_resp.json()
        logger.info(f"Spin result: {spin_result}")

        if "Win" in spin_result:
            msg = self._validate_result("WIN", spin_result["Win"], txn_id, starting_balance, bet_amount)
        else:
            msg = self._validate_result("LOSE", spin_result["Lose"], txn_id, starting_balance, bet_amount)

        self._notify_and_assert(txn_id, msg)

        logger.info(f"Test passed successfully for User={self.user_id} | Outcome={outcome}")

    def _build_post_side_effect(self, txn_id, starting_balance, bet_amount, outcome):
        responses = [
            MockHelper.make_mock_response({
                "transactionId": txn_id,
                "newBalance": starting_balance - bet_amount
            })
        ]

        if outcome == "WIN":
            win_amount = 50
            responses.extend([
                MockHelper.make_mock_response({
                    "Win": {
                        "userId": self.user_id,
                        "outcome": "WIN",
                        "winAmount": win_amount,
                        "message": f"Congratulations! You won ${win_amount}!",
                        "reels": ["Cherry", "Cherry", "Cherry"]
                    }
                }),
                MockHelper.make_mock_response({
                    "newBalance": starting_balance - bet_amount + win_amount,
                    "currency": "USD"
                })
            ])
        else:
            responses.append(MockHelper.make_mock_response({
                "Lose": {
                    "userId": self.user_id,
                    "outcome": "LOSE",
                    "winAmount": 0,
                    "message": "Better luck next time!",
                    "reels": ["Lemon", "Bell", "Cherry"]
                }
            }))

        responses.append(MockHelper.make_mock_response({"status": "SENT"}))
        return responses

    def _validate_result(self, outcome, data, txn_id, starting_balance, bet_amount):
        msg = data["message"]
        expected_balance = starting_balance - bet_amount

        logger.info(f"Validating outcome: {outcome} | message='{msg}'")

        assert data["userId"] == self.user_id, f"[{outcome}] userId mismatch"
        assert data["outcome"] == outcome, f"[{outcome}] Outcome mismatch"
        assert isinstance(msg, str), f"[{outcome}] Message should be string"
        assert isinstance(data["reels"], list), f"[{outcome}] Reels should be a list"
        assert len(data["reels"]) == 3, f"[{outcome}] Expected 3 reels, got {len(data['reels'])}"

        if outcome == "WIN":
            win_amount = data["winAmount"]
            assert isinstance(win_amount, (int, float)), "winAmount should be numeric"
            expected_balance += win_amount
            logger.info(f"WIN detected! Amount={win_amount}, Expected balance={expected_balance}")
            self._payout_and_assert(txn_id, win_amount, expected_balance)

        logger.info(f"Mocking GET /balance to reflect expected_balance={expected_balance}")
        self.mock.get.return_value = MockHelper.make_mock_response({
            "balance": expected_balance,
            "currency": "USD"
        })

        self._assert_final_balance(expected_balance, context=outcome)
        return msg

    def _assert_final_balance(self, expected_balance, context=""):
        logger.info("Validating final balance...")
        resp = get_balance(self.user_id)
        assert resp.status_code == 200, f"[{context}] Balance GET failed"
        actual_balance = resp.json()["balance"]
        actual_currency = resp.json()["currency"]

        assert actual_currency == "USD", f"[{context}] Currency mismatch: expected 'USD', got '{actual_currency}'"
        assert actual_balance == expected_balance, f"[{context}] Final balance mismatch: expected {expected_balance}, got {actual_balance}"
        logger.info(f"Final balance validated: {actual_balance} USD")
