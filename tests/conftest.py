import pytest
from unittest.mock import patch
from utils.logger import get_logger
import os
logger = get_logger(__name__)


def pytest_addoption(parser):
    parser.addoption("--user_id", action="store", default="123", help="User ID to test")


@pytest.fixture(scope="class", autouse=True)
def init_user_id(request):
    if request.cls is not None:
        request.cls.user_id = int(request.config.getoption("--user_id"))
        os.environ["user_id"] = str(request.cls.user_id)


@pytest.fixture(autouse=False, scope="function")
def mock_requests(request):
    with patch("utils.endpoints.requests") as mock:
        request.cls.mock = mock
        yield mock

