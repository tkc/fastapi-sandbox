from injector import inject

from app.core.exceptions import UserNotFoundError
from app.domain.user.entity import User
from app.domain.user.i_user_repository import IUserRepository
from app.schemas.user import UserCreate, UserResponse


class UserService:
    @inject
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def create_user(self, user_create: UserCreate) -> UserResponse:
        user = User.create(
            name=user_create.name,
            email=user_create.email,
            age=user_create.age,
            address=user_create.address,
        )
        self._user_repository.save(user)
        return UserResponse.from_entity(user)

    def get_user(self, user_id: str) -> UserResponse:
        user = self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return UserResponse.from_entity(user)

    def list_users(self) -> list[UserResponse]:
        users = self._user_repository.find_all()
        return [UserResponse.from_entity(user) for user in users]

    def search_users(self, name: str | None, email: str | None) -> list[UserResponse]:
        if name and email:
            users = self._user_repository.search_by_name(name)
            users = [u for u in users if u.email == email]
        elif name:
            users = self._user_repository.search_by_name(name)
        elif email:
            users = self._user_repository.search_by_email(email)
        else:
            users = self._user_repository.find_all()
        return [UserResponse.from_entity(user) for user in users]
