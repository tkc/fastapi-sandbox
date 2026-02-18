from pydantic import BaseModel, EmailStr, Field

from app.core.types import UserId
from app.domain.user.entity import User


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    address: str = Field(..., min_length=1, max_length=500)


class UserResponse(BaseModel):
    user_id: UserId
    name: str
    email: str
    age: int
    address: str
    created_at: str

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            age=user.age,
            address=user.address,
            created_at=user.created_at,
        )


class UserSearchQuery(BaseModel):
    name: str | None = None
    email: str | None = None
