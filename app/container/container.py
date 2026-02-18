from injector import Binder, Injector, Module, singleton

from app.domain.user.i_user_repository import IUserRepository
from app.infrastructure.datasource.dynamodb import get_table
from app.infrastructure.repository.user_dynamodb_repository import (
    UserDynamoDBRepository,
)


class RepositoryModule(Module):
    def configure(self, binder: Binder) -> None:
        table = get_table()
        binder.bind(
            IUserRepository,
            to=UserDynamoDBRepository(table=table),
            scope=singleton,
        )


class DIContainer:
    _injector: Injector | None = None

    @classmethod
    def get_injector(cls) -> Injector:
        if cls._injector is None:
            cls._injector = Injector([RepositoryModule])
        return cls._injector

    @classmethod
    def resolve(cls, klass: type) -> object:
        return cls.get_injector().get(klass)

    @classmethod
    def reset(cls) -> None:
        cls._injector = None
