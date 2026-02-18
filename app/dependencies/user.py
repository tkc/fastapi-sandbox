from app.usecase.user.create_user_usecase import CreateUserUseCase
from app.usecase.user.get_user_usecase import GetUserUseCase
from app.usecase.user.list_users_usecase import ListUsersUseCase
from app.usecase.user.search_users_usecase import SearchUsersUseCase

_create_user_usecase: CreateUserUseCase | None = None
_get_user_usecase: GetUserUseCase | None = None
_list_users_usecase: ListUsersUseCase | None = None
_search_users_usecase: SearchUsersUseCase | None = None


def init_usecases(
    create_user: CreateUserUseCase,
    get_user: GetUserUseCase,
    list_users: ListUsersUseCase,
    search_users: SearchUsersUseCase,
) -> None:
    global _create_user_usecase, _get_user_usecase
    global _list_users_usecase, _search_users_usecase
    _create_user_usecase = create_user
    _get_user_usecase = get_user
    _list_users_usecase = list_users
    _search_users_usecase = search_users


def get_create_user_usecase() -> CreateUserUseCase:
    assert _create_user_usecase is not None
    return _create_user_usecase


def get_get_user_usecase() -> GetUserUseCase:
    assert _get_user_usecase is not None
    return _get_user_usecase


def get_list_users_usecase() -> ListUsersUseCase:
    assert _list_users_usecase is not None
    return _list_users_usecase


def get_search_users_usecase() -> SearchUsersUseCase:
    assert _search_users_usecase is not None
    return _search_users_usecase
