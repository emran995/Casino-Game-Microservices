import pytest

from casino_tests.utils import MockHelper, notify, payout, spin, place_bet


@pytest.mark.usefixtures("mock_requests")
class TestExactBalanceEdgeCase:

    def test_exact_balance_bet(self):
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": 10})

        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": "txn_555", "newBalance": 0}),
            MockHelper.make_mock_response({"Win": {"winAmount": 30, "message": "You won!"}}),
            MockHelper.make_mock_response({"newBalance": 30}),
            MockHelper.make_mock_response({"status": "SENT"})
        ]

        bet_resp = place_bet(123, 10)
        assert bet_resp.status_code == 200
        assert bet_resp.json()["newBalance"] == 0

        spin_resp = spin(123, 10, "txn_555")
        assert spin_resp.status_code == 200

        payout_resp = payout(123, "txn_555", 30)
        assert payout_resp.status_code == 200
        assert payout_resp.json()["newBalance"] == 30

        notify_resp = notify(123, "txn_555", "You won!")
        assert notify_resp.status_code == 200
        assert notify_resp.json()["status"] == "SENT"
