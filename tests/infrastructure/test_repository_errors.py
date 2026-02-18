from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from app.core.exceptions import RepositoryError
from app.domain.user.entity import User
from app.infrastructure.repository.user_dynamodb_repository import UserDynamoDBRepository


def _make_user() -> User:
    return User(
        user_id="test-uuid",
        name="Taro",
        email="taro@example.com",
        age=30,
        address="Tokyo",
        created_at="2026-01-01T00:00:00+00:00",
    )


def _make_client_error() -> ClientError:
    return ClientError(
        error_response={"Error": {"Code": "500", "Message": "DynamoDB error"}},
        operation_name="PutItem",
    )


def _make_repo_with_error(method: str) -> UserDynamoDBRepository:
    table = MagicMock()
    error = _make_client_error()
    getattr(table, method).side_effect = error

    # For query/scan that raise on the method call itself
    if method in ("get_item", "scan", "query"):
        getattr(table, method).side_effect = error
    elif method == "put_item":
        table.put_item.side_effect = error

    return UserDynamoDBRepository(table=table)


class TestRepositoryErrorWrapping:
    def test_save_wraps_client_error(self):
        repo = _make_repo_with_error("put_item")

        with pytest.raises(RepositoryError) as exc_info:
            repo.save(_make_user())

        assert exc_info.value.operation == "save"
        assert isinstance(exc_info.value.__cause__, ClientError)

    def test_find_by_id_wraps_client_error(self):
        repo = _make_repo_with_error("get_item")

        with pytest.raises(RepositoryError) as exc_info:
            repo.find_by_id("test-uuid")

        assert exc_info.value.operation == "find_by_id"
        assert isinstance(exc_info.value.__cause__, ClientError)

    def test_find_all_wraps_client_error(self):
        repo = _make_repo_with_error("scan")

        with pytest.raises(RepositoryError) as exc_info:
            repo.find_all()

        assert exc_info.value.operation == "find_all"
        assert isinstance(exc_info.value.__cause__, ClientError)

    def test_search_by_name_wraps_client_error(self):
        repo = _make_repo_with_error("query")

        with pytest.raises(RepositoryError) as exc_info:
            repo.search_by_name("Taro")

        assert exc_info.value.operation == "search_by_name"
        assert isinstance(exc_info.value.__cause__, ClientError)

    def test_search_by_email_wraps_client_error(self):
        repo = _make_repo_with_error("query")

        with pytest.raises(RepositoryError) as exc_info:
            repo.search_by_email("taro@example.com")

        assert exc_info.value.operation == "search_by_email"
        assert isinstance(exc_info.value.__cause__, ClientError)
