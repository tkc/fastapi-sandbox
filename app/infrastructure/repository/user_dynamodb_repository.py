from typing import Any

from boto3.dynamodb.conditions import Key
from botocore.exceptions import BotoCoreError, ClientError

from app.core.decorators import log_action
from app.core.exceptions import RepositoryError
from app.core.types import UserId
from app.domain.user.entity import User
from app.domain.user.i_user_repository import IUserRepository


class UserDynamoDBRepository(IUserRepository):
    def __init__(self, table: Any) -> None:
        self._table = table

    @log_action()
    def save(self, user: User) -> None:
        try:
            self._table.put_item(Item=user.model_dump())
        except (ClientError, BotoCoreError) as err:
            raise RepositoryError(message=f"Failed to save user: {err}", operation="save") from err

    @log_action()
    def find_by_id(self, user_id: UserId) -> User | None:
        try:
            response = self._table.get_item(Key={"user_id": user_id})
        except (ClientError, BotoCoreError) as err:
            raise RepositoryError(message=f"Failed to find user: {err}", operation="find_by_id") from err
        item = response.get("Item")
        if not item:
            return None
        return User(**item)

    @log_action()
    def find_all(self) -> list[User]:
        try:
            response = self._table.scan()
        except (ClientError, BotoCoreError) as err:
            raise RepositoryError(message=f"Failed to list users: {err}", operation="find_all") from err
        return [User(**item) for item in response["Items"]]

    @log_action()
    def search_by_name(self, name: str) -> list[User]:
        try:
            response = self._table.query(
                IndexName="name-index",
                KeyConditionExpression=Key("name").eq(name),
            )
        except (ClientError, BotoCoreError) as err:
            raise RepositoryError(
                message=f"Failed to search by name: {err}",
                operation="search_by_name",
            ) from err
        return [User(**item) for item in response["Items"]]

    @log_action()
    def search_by_email(self, email: str) -> list[User]:
        try:
            response = self._table.query(
                IndexName="email-index",
                KeyConditionExpression=Key("email").eq(email),
            )
        except (ClientError, BotoCoreError) as err:
            raise RepositoryError(
                message=f"Failed to search by email: {err}",
                operation="search_by_email",
            ) from err
        return [User(**item) for item in response["Items"]]
