import pytest


@pytest.fixture(autouse=True)
def setup_and_teardown_table():
    """Override parent fixture - infrastructure unit tests don't need DynamoDB."""
    yield
