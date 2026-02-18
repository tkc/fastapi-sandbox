from boto3.dynamodb.conditions import Key

from app.domain.user.entity import User
from app.domain.user.i_user_repository import IUserRepository


class UserDynamoDBRepository(IUserRepository):
    def __init__(self, table) -> None:
        self._table = table

    def save(self, user: User) -> None:
        self._table.put_item(Item=user.model_dump())

    def find_by_id(self, user_id: str) -> User | None:
        response = self._table.get_item(Key={"user_id": user_id})
        item = response.get("Item")
        if not item:
            return None
        return User(**item)

    def find_all(self) -> list[User]:
        response = self._table.scan()
        return [User(**item) for item in response["Items"]]

    def search_by_name(self, name: str) -> list[User]:
        response = self._table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(name),
        )
        return [User(**item) for item in response["Items"]]

    def search_by_email(self, email: str) -> list[User]:
        response = self._table.query(
            IndexName="email-index",
            KeyConditionExpression=Key("email").eq(email),
        )
        return [User(**item) for item in response["Items"]]
