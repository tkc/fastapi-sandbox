from app.core.constants import ERROR_USER_NOT_FOUND
from app.core.types import UserId


class AppError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class UserNotFoundError(AppError):
    def __init__(self, user_id: UserId) -> None:
        self.user_id = user_id
        super().__init__(f"{ERROR_USER_NOT_FOUND}: {user_id}")


class RepositoryError(AppError):
    def __init__(self, message: str, operation: str) -> None:
        self.operation = operation
        super().__init__(message)
