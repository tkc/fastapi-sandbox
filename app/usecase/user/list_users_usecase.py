from injector import inject

from app.domain.user.i_user_repository import IUserRepository
from app.schemas.user import UserResponse


class ListUsersUseCase:
    @inject
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def execute(self) -> list[UserResponse]:
        users = self._user_repository.find_all()
        return [UserResponse.from_entity(user) for user in users]
