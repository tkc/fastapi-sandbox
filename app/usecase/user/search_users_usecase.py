from injector import inject

from app.domain.user.i_user_repository import IUserRepository
from app.schemas.user import UserResponse


class SearchUsersUseCase:
    @inject
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def execute(
        self, name: str | None, email: str | None
    ) -> list[UserResponse]:
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
