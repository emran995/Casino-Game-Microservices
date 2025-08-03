import pytest
from casino_tests.utils import MockHelper
from casino_tests.utils import place_bet, spin, payout, notify


@pytest.mark.usefixtures("mock_requests")
class TestPositiveCases:

    def setup_method(self):
        self.user_id = 123

    def test_regular_win(self):
        # Mock GET response for balance
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": 150})

        # Mock POST responses in correct order:
        # 1. place_bet → transactionId + newBalance
        # 2. spin → WIN with winAmount
        # 3. payout → updated balance
        # 4. notify → status=SENT
        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": "txn_001", "newBalance": 140}),
            MockHelper.make_mock_response({"Win": {"winAmount": 50, "message": "Congratulations! You won $50!"}}),
            MockHelper.make_mock_response({"newBalance": 190}),
            MockHelper.make_mock_response({"status": "SENT"})
        ]

        # Simulate the actual flow so each response is used in order
        place_bet(self.user_id, 10)
        spin(self.user_id, 10, "txn_001")
        payout(self.user_id, "txn_001", 50)
        notify_response = notify(self.user_id, "txn_001", "Congratulations! You won $50!")

        # Assertion
        assert notify_response.status_code == 200
        assert notify_response.json()["status"] == "SENT"

    def test_regular_loss(self):
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": 150})
        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": "txn_002", "newBalance": 140}),  # place_bet
            MockHelper.make_mock_response({"Lose": {"message": "Better luck next time!"}}),  # spin
            MockHelper.make_mock_response({"status": "SENT"})  # notify
        ]

        # חייבים להריץ את הקריאות לפי הסדר כדי שה-side_effect יעבוד כמו שצריך
        place_bet(self.user_id, 10)
        spin(self.user_id, 10, "txn_002")
        notify_response = notify(self.user_id, "txn_002", "Better luck next time!")

        assert notify_response.status_code == 200
        assert notify_response.json()["status"] == "SENT"

    def test_multiple_rounds(self):
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": 200})

        # נשתמש באותה תגובה ריקה לשני הקריאות (place_bet + spin)
        self.mock.post.return_value = MockHelper.make_mock_response({})

        for i, bet in enumerate([5, 10, 15]):
            txn_id = f"txn_{i + 1}"
            response = place_bet(self.user_id, bet)
            assert response.status_code == 200
            response = spin(self.user_id, bet, txn_id)
            assert response.status_code == 200

    def test_notify_format(self):
        self.mock.post.return_value = MockHelper.make_mock_response({"status": "SENT"})

        response = notify(self.user_id, "txn_777", "Congratulations! You won $50!")
        assert response.status_code == 200
        assert response.json()["status"] == "SENT"

    def test_balance_after_win(self):
        self.mock.get.return_value = MockHelper.make_mock_response({"balance": 100})

        self.mock.post.side_effect = [
            MockHelper.make_mock_response({"transactionId": "txn_003", "newBalance": 90}),  # place_bet
            MockHelper.make_mock_response({"Win": {"winAmount": 50, "message": "You won!"}}),  # spin
            MockHelper.make_mock_response({"newBalance": 140})  # payout
        ]

        place_bet(self.user_id, 10)
        spin(self.user_id, 10, "txn_003")
        payout_response = payout(self.user_id, "txn_003", 50)

        assert payout_response.status_code == 200
        assert payout_response.json()["newBalance"] == 140
