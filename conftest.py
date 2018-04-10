# content of conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption("--port", action="store", default="1234",
        help="appium port")

@pytest.fixture
def port(request):
    return request.config.getoption("--port")
