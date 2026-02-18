from abc import ABC, abstractmethod

from app.domain.user.entity import User


class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    def search_by_name(self, name: str) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    def search_by_email(self, email: str) -> list[User]:
        raise NotImplementedError
