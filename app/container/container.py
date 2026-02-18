from dependency_injector import containers, providers

from app.infrastructure.datasource.dynamodb import get_table
from app.infrastructure.repository.user_dynamodb_repository import (
    UserDynamoDBRepository,
)
from app.usecase.user.create_user_usecase import CreateUserUseCase
from app.usecase.user.get_user_usecase import GetUserUseCase
from app.usecase.user.list_users_usecase import ListUsersUseCase
from app.usecase.user.search_users_usecase import SearchUsersUseCase


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.api.v1.endpoints.users"],
    )

    dynamodb_table = providers.Singleton(get_table)

    user_repository = providers.Singleton(
        UserDynamoDBRepository,
        table=dynamodb_table,
    )

    create_user_usecase = providers.Factory(
        CreateUserUseCase,
        user_repository=user_repository,
    )

    get_user_usecase = providers.Factory(
        GetUserUseCase,
        user_repository=user_repository,
    )

    list_users_usecase = providers.Factory(
        ListUsersUseCase,
        user_repository=user_repository,
    )

    search_users_usecase = providers.Factory(
        SearchUsersUseCase,
        user_repository=user_repository,
    )
