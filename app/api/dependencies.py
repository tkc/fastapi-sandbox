from app.container.container import DIContainer
from app.usecase.user.user_service import UserService


def get_user_service() -> UserService:
    return DIContainer.resolve(UserService)
