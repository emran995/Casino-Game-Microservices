
from casino_tests.utils import MockHelper, place_bet, spin, payout, notify


class TestNegativeCases:

    def test_insufficient_balance(self, mock_requests):
        mock_requests.get.return_value = MockHelper.make_mock_response({"balance": 5})
        mock_requests.post.return_value = MockHelper.make_mock_response({"error": "Insufficient balance"}, status_code=400)

        response = place_bet(self.user_id, 10)
        assert response.status_code == 400
        assert "error" in response.json()

    def test_invalid_transaction_id(self, mock_requests):
        mock_requests.post.return_value = MockHelper.make_mock_response({"error": "Transaction not found"}, status_code=404)

        response = spin(self.user_id, 10, "invalid_txn")
        assert response.status_code == 404
        assert "error" in response.json()

    def test_missing_user_id(self, mock_requests):
        mock_requests.post.return_value = MockHelper.make_mock_response(
            {"error": "Missing userId"}, status_code=400
        )
        response = place_bet(None, 10)  # user_id is None

        assert response.status_code == 400
        assert "error" in response.json()

    def test_payout_without_win(self, mock_requests):
        mock_requests.post.return_value = MockHelper.make_mock_response({"error": "No win to payout"}, status_code=403)

        response = payout(self.user_id, "txn_999", 0)
        assert response.status_code == 403
        assert "error" in response.json()

    def test_empty_message_notify(self, mock_requests):
        mock_requests.post.return_value = MockHelper.make_mock_response({"error": "Message cannot be empty"}, status_code=400)

        response = notify(self.user_id, "txn_888", "")
        assert response.status_code == 400
        assert "error" in response.json()
