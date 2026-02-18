import uuid
from datetime import UTC, datetime

from pydantic import BaseModel

from app.core.types import UserId


class User(BaseModel):
    user_id: UserId
    name: str
    email: str
    age: int
    address: str
    created_at: str

    @classmethod
    def create(
        cls,
        name: str,
        email: str,
        age: int,
        address: str,
    ) -> "User":
        return cls(
            user_id=UserId(str(uuid.uuid4())),
            name=name,
            email=email,
            age=age,
            address=address,
            created_at=datetime.now(UTC).isoformat(),
        )
