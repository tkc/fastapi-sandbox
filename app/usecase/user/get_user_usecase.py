from injector import inject

from app.core.exceptions import UserNotFoundError
from app.domain.user.i_user_repository import IUserRepository
from app.schemas.user import UserResponse


class GetUserUseCase:
    @inject
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def execute(self, user_id: str) -> UserResponse:
        user = self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return UserResponse.from_entity(user)
