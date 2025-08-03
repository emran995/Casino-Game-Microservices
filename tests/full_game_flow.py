import pytest
from casino_tests.utils import place_bet, get_balance, spin, payout, notify, MockHelper

@pytest.mark.usefixtures("mock_requests")
class TestPositiveCases:

    @pytest.mark.parametrize("bet_amount, outcome", [
        (10, "WIN"),
        (10, "LOSE")
    ])
    def test_full_game_flow_with_mock(self, bet_amount, outcome):
        starting_balance = 150
        txn_id = f"txn_{self.user_id}"
        win_amount = 50

        # Mock GET /user/balance
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": starting_balance})

        # Mock POST responses in the order: place_bet → spin → payout (if win) → notify
        post_responses = []

        # /payment/placeBet
        post_responses.append(MockHelper.make_mock_response({
            "transactionId": txn_id,
            "newBalance": starting_balance - bet_amount
        }))

        # /slot/spin
        if outcome == "WIN":
            post_responses.append(MockHelper.make_mock_response({
                "Win": {
                    "winAmount": win_amount,
                    "message": f"Congratulations! You won ${win_amount}!"
                }
            }))
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

        # /notify
        post_responses.append(MockHelper.make_mock_response({"status": "SENT"}))
        self.mock.post.side_effect = post_responses

        # Run full flow
        balance_resp = get_balance(self.user_id)
        assert balance_resp.status_code == 200
        assert balance_resp.json()["balance"] == starting_balance

        bet_resp = place_bet(self.user_id, bet_amount)
        assert bet_resp.status_code == 200
        assert bet_resp.json()["newBalance"] == starting_balance - bet_amount

        spin_resp = spin(self.user_id, bet_amount, txn_id)
        assert spin_resp.status_code == 200
        result = spin_resp.json()

        if "Win" in result:
            msg = result["Win"]["message"]
            payout_resp = payout(self.user_id, txn_id, win_amount)
            assert payout_resp.status_code == 200
            assert payout_resp.json()["newBalance"] == starting_balance - bet_amount + win_amount
        else:
            msg = result["Lose"]["message"]

        notify_resp = notify(self.user_id, txn_id, msg)
        assert notify_resp.status_code == 200
        assert notify_resp.json()["status"] == "SENT"
