from unittest.mock import MagicMock

from app.domain.user.entity import User
from app.domain.user.i_user_repository import IUserRepository
from app.schemas.user import UserCreate
from app.usecase.user.create_user_usecase import CreateUserUseCase
from app.usecase.user.get_user_usecase import GetUserUseCase
from app.usecase.user.list_users_usecase import ListUsersUseCase
from app.usecase.user.search_users_usecase import SearchUsersUseCase


def _make_user(**overrides) -> User:
    defaults = {
        "user_id": "test-uuid",
        "name": "Taro",
        "email": "taro@example.com",
        "age": 30,
        "address": "Tokyo",
        "created_at": "2026-01-01T00:00:00+00:00",
    }
    defaults.update(overrides)
    return User(**defaults)


class TestCreateUserUseCase:
    def test_creates_and_saves_user(self):
        repo = MagicMock(spec=IUserRepository)
        usecase = CreateUserUseCase(user_repository=repo)

        result = usecase.execute(
            UserCreate(name="Taro", email="taro@example.com", age=30, address="Tokyo")
        )

        repo.save.assert_called_once()
        saved_user = repo.save.call_args[0][0]
        assert saved_user.name == "Taro"
        assert saved_user.email == "taro@example.com"
        assert result.name == "Taro"
        assert result.user_id is not None


class TestGetUserUseCase:
    def test_returns_user_when_found(self):
        repo = MagicMock(spec=IUserRepository)
        user = _make_user()
        repo.find_by_id.return_value = user
        usecase = GetUserUseCase(user_repository=repo)

        result = usecase.execute("test-uuid")

        assert result.user_id == "test-uuid"
        assert result.name == "Taro"

    def test_raises_when_not_found(self):
        repo = MagicMock(spec=IUserRepository)
        repo.find_by_id.return_value = None
        usecase = GetUserUseCase(user_repository=repo)

        import pytest
        with pytest.raises(Exception):
            usecase.execute("nonexistent")


class TestListUsersUseCase:
    def test_returns_all_users(self):
        repo = MagicMock(spec=IUserRepository)
        repo.find_all.return_value = [_make_user(), _make_user(name="Hanako")]
        usecase = ListUsersUseCase(user_repository=repo)

        result = usecase.execute()

        assert len(result) == 2


class TestSearchUsersUseCase:
    def test_search_by_name(self):
        repo = MagicMock(spec=IUserRepository)
        repo.search_by_name.return_value = [_make_user()]
        usecase = SearchUsersUseCase(user_repository=repo)

        result = usecase.execute(name="Taro", email=None)

        assert len(result) == 1
        repo.search_by_name.assert_called_once_with("Taro")

    def test_search_by_email(self):
        repo = MagicMock(spec=IUserRepository)
        repo.search_by_email.return_value = [_make_user()]
        usecase = SearchUsersUseCase(user_repository=repo)

        result = usecase.execute(name=None, email="taro@example.com")

        assert len(result) == 1
        repo.search_by_email.assert_called_once_with("taro@example.com")

    def test_search_by_name_and_email(self):
        repo = MagicMock(spec=IUserRepository)
        repo.search_by_name.return_value = [
            _make_user(),
            _make_user(email="other@example.com"),
        ]
        usecase = SearchUsersUseCase(user_repository=repo)

        result = usecase.execute(name="Taro", email="taro@example.com")

        assert len(result) == 1
        assert result[0].email == "taro@example.com"

    def test_search_no_params_returns_all(self):
        repo = MagicMock(spec=IUserRepository)
        repo.find_all.return_value = [_make_user()]
        usecase = SearchUsersUseCase(user_repository=repo)

        result = usecase.execute(name=None, email=None)

        assert len(result) == 1
        repo.find_all.assert_called_once()
