import pytest
from unittest.mock import patch
from utils.logger import get_logger
import os

logger = get_logger(__name__)


def pytest_addoption(parser):
    parser.addoption("--user_id", action="store", default="123", help="User ID to test")


@pytest.fixture(scope="class", autouse=True)
def init_user_id(request):
    user_id = request.config.getoption("--user_id")
    os.environ["user_id"] = user_id

    if request.cls is not None:
        request.cls.user_id = int(user_id)
        logger.info(f"[INIT] Set user_id for test class: {request.cls.__name__} => {user_id}")
    else:
        logger.warning("[INIT] Could not set user_id: request.cls is None")

    yield

    logger.info(f"[TEARDOWN] Finished test class: {request.cls.__name__ if request.cls else 'Unknown'}")


@pytest.fixture(autouse=False, scope="function")
def mock_requests(request):
    with patch("utils.endpoints.requests") as mock:
        request.cls.mock = mock
        logger.info(f"[MOCK] requests patched for test: {request.node.name}")
        yield mock
        logger.info(f"[MOCK] requests unpatched after test: {request.node.name}")
