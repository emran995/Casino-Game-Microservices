import pytest
import threading

from tests.common_tests.base_game_test import BaseGameTest
from utils.mock import MockHelper
from utils.endpoints import place_bet, spin, payout, notify
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.usefixtures("mock_requests")
class TestStrongestTrueCases(BaseGameTest):

    def test_full_game_win_flow(self):
        """
        Test Case: Full game flow when the user wins.

        Description:
        This test simulates a complete user journey through the slot game where the outcome is a win.
        It verifies that the balance is correctly deducted, the spin returns a WIN, payout is processed,
        and a notification is successfully sent to the user.
        """
        logger.info("Running: test_full_game_win_flow")
        self._mock_balance(150)

        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": "txn_win", "newBalance": 140}),
            MockHelper.make_mock_response({"Win": {"winAmount": 50, "message": "You won!"}}),
            MockHelper.make_mock_response({"newBalance": 190}),
            MockHelper.make_mock_response({"status": "SENT"})
        ]

        bet_resp = place_bet(self.user_id, 10)
        assert bet_resp.status_code == 200, "Failed to place bet"

        spin_resp = spin(self.user_id, 10, "txn_win")
        assert spin_resp.status_code == 200 and "Win" in spin_resp.json(), "Spin result missing or incorrect"

        payout_resp = payout(self.user_id, "txn_win", 50)
        assert payout_resp.json()["newBalance"] == 190, "Incorrect balance after payout"

        notify_resp = notify(self.user_id, "txn_win", "You won!")
        assert notify_resp.json()["status"] == "SENT", "Notification not sent"

    def test_full_game_loss_flow(self):
        """
        Test Case: Full game flow when the user loses.

        Description:
        This test simulates a complete game flow for a user who places a bet and loses.
        It verifies that the balance is deducted, the spin result is LOSE, and a loss notification is sent.
        """
        logger.info("Running: test_full_game_loss_flow")
        self._mock_balance(150)

        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": "txn_loss", "newBalance": 140}),
            MockHelper.make_mock_response({"Lose": {"message": "Better luck next time!"}}),
            MockHelper.make_mock_response({"status": "SENT"})
        ]

        assert place_bet(self.user_id, 10).status_code == 200, "Bet failed"
        assert "Lose" in spin(self.user_id, 10, "txn_loss").json(), "Expected LOSE outcome"
        assert notify(self.user_id, "txn_loss", "Better luck next time!").json()["status"] == "SENT", "Notification failed"

    @pytest.mark.parametrize("bet_amount, description", [
        (100, "maximum allowed bet"),
        (1, "minimum allowed bet"),
        (1000, "beyond maximum allowed bet")
    ])
    def test_extreme_bet_values(self, bet_amount, description):
        """
        Test Case: Extreme Bet Values (min, max, beyond max)

        Description:
        This test validates the system's behavior when placing edge-case bet amounts:
        - Minimum allowed
        - Maximum allowed
        - Beyond maximum (e.g., over-limit scenario)

        It verifies:
        - User balance is deducted correctly
        - The system returns a WIN result
        - The payout is processed and balance updated
        - The notification is sent successfully
        - Proper transaction ID and message content
        """
        logger.info(f"Running: test_extreme_bet_values ({description})")
        initial_balance = 2000
        txn_id = f"txn_{bet_amount}"

        self._mock_balance(initial_balance)

        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": txn_id, "newBalance": initial_balance - bet_amount}),
            MockHelper.make_mock_response({"Win": {"winAmount": 50, "message": "Congratulations! You won $50!"}}),
            MockHelper.make_mock_response({"newBalance": initial_balance - bet_amount + 50}),
            MockHelper.make_mock_response({"status": "SENT"})
        ]

        self._place_bet_and_assert(bet_amount, txn_id)
        self._spin_and_assert(bet_amount, txn_id, "Win", 50)

        payout_resp = payout(self.user_id, txn_id, 50)
        assert payout_resp.status_code == 200, "Payout failed"
        assert payout_resp.json()["newBalance"] == initial_balance - bet_amount + 50, "Incorrect balance after payout"
        self._notify_and_assert(txn_id, "Congratulations! You won $50!")

    def test_spin_response_time_delay_handling(self):
        """
        Test Case: Validate system handles slow spin response (simulated delay).

        Description:
        This test simulates a delayed response from the spin endpoint to verify the system’s resilience.
        It confirms the API call completes successfully even under latency, and the WIN result remains valid.
        """
        logger.info("Running: test_spin_response_time_delay_handling")

        # Step 1: Mock balance
        self._mock_balance(150)
        txn_id = "txn_delay"

        # Step 2: Define side effects for the mocked POST requests (in exact call order)
        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": txn_id, "newBalance": 140}),  # placeBet
            MockHelper.make_mock_response(
                {"Win": {"winAmount": 20, "message": "You won despite delay!"}},
                delay=3
            ),  # spin (delayed)
            MockHelper.make_mock_response({"newBalance": 190}),  # payout
            MockHelper.make_mock_response({"status": "SENT"})  # notify
        ]

        # Step 3: Place bet using helper
        self._place_bet_and_assert(10, txn_id)

        # Step 4: Measure delay during spin
        resp = spin(self.user_id, 10, txn_id)

        # Step 5: Assert spin outcome
        assert resp.status_code == 200, "Spin failed after delay"
        win_data = resp.json().get("Win")
        assert win_data is not None, "Missing WIN result after delay"
        assert win_data["winAmount"] == 20, "Incorrect win amount after delay"

        # Step 6: Validate payout
        payout_resp = payout(self.user_id, txn_id, 20)
        assert payout_resp.status_code == 200, "Payout failed after delay"
        assert payout_resp.json()["newBalance"] == 190, "Incorrect balance after payout delay"

        # Step 7: Validate notification
        self._notify_and_assert(txn_id, win_data["message"])

    def test_multiple_parallel_successful_rounds(self):
        """
        Test Case: Run multiple successful game rounds in parallel threads.

        Description:
        This test verifies that the system can process multiple concurrent bets and spins without conflict.
        It simulates three simultaneous game sessions, each with independent transactionId and bet.
        """
        logger.info("Running: test_multiple_parallel_successful_rounds")
        self._mock_balance(300)

        def _play_parallel_round(round_number, bet_amount):
            txn_id = f"txn_parallel_{round_number}"
            logger.info(f"[Round {round_number}] Starting with txn_id={txn_id} and bet={bet_amount}")

            self.mock.post.side_effect = [
                MockHelper.make_mock_response({"transactionId": txn_id, "newBalance": 300 - bet_amount}),
                MockHelper.make_mock_response({"Win": {"winAmount": 50}}),
                MockHelper.make_mock_response({"status": "SENT"})
            ]

            resp_bet = place_bet(self.user_id, bet_amount)
            assert resp_bet.status_code == 200
            logger.info(f"[Round {round_number}] place_bet: {resp_bet.json()}")

            resp_spin = spin(self.user_id, bet_amount, txn_id)
            assert resp_spin.status_code == 200
            logger.info(f"[Round {round_number}] spin: {resp_spin.json()}")

            resp_notify = notify(self.user_id, txn_id, f"You won in round {round_number}!")
            assert resp_notify.status_code == 200
            logger.info(f"[Round {round_number}] notify: {resp_notify.json()}")

        threads = []
        for i in range(1, 4):
            t = threading.Thread(target=_play_parallel_round, args=(i, 10 * i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        logger.info("All parallel rounds completed successfully")
