import time


class MockHelper:
    @staticmethod
    def make_mock_response(data, status_code=200, delay=0):
        return type("MockResponse", (), {
            "status_code": status_code,
            "json": lambda self: (time.sleep(delay) or data) if delay else data
        })()
