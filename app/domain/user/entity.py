import uuid
from datetime import UTC, datetime

from pydantic import BaseModel


class User(BaseModel):
    user_id: str
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
            user_id=str(uuid.uuid4()),
            name=name,
            email=email,
            age=age,
            address=address,
            created_at=datetime.now(UTC).isoformat(),
        )
