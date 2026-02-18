import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.infrastructure.datasource.dynamodb import (
    create_users_table,
    get_dynamodb_resource,
)
from app.main import app


@pytest.fixture(autouse=True)
def setup_and_teardown_table():
    """Create table before each test, delete after."""
    create_users_table()
    yield
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(settings.dynamodb_table_name)
    table.delete()


@pytest.fixture
def client():
    return TestClient(app)
