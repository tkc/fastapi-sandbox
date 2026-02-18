from injector import inject

from app.domain.user.entity import User
from app.domain.user.i_user_repository import IUserRepository
from app.schemas.user import UserCreate, UserResponse


class CreateUserUseCase:
    @inject
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def execute(self, user_create: UserCreate) -> UserResponse:
        user = User.create(
            name=user_create.name,
            email=user_create.email,
            age=user_create.age,
            address=user_create.address,
        )
        self._user_repository.save(user)
        return UserResponse.from_entity(user)
