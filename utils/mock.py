class MockHelper:
    @staticmethod
    def make_mock_response(data, status_code=200):
        return type("MockResponse", (), {
            "status_code": status_code,
            "json": lambda self: data
        })()
