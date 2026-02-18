import pytest


@pytest.fixture(autouse=True)
def setup_and_teardown_table():
    """Override parent fixture - usecase tests don't need DynamoDB."""
    yield
