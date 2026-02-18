from fastapi import APIRouter, HTTPException, Query

from app.container.container import DIContainer
from app.core.exceptions import UserNotFoundError
from app.schemas.user import UserCreate, UserResponse
from app.usecase.user.user_service import UserService

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate) -> UserResponse:
    service = DIContainer.resolve(UserService)
    return service.create_user(user)


@router.get("/search", response_model=list[UserResponse])
def search_users(
    name: str | None = Query(default=None),
    email: str | None = Query(default=None),
) -> list[UserResponse]:
    service = DIContainer.resolve(UserService)
    return service.search_users(name=name, email=email)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str) -> UserResponse:
    service = DIContainer.resolve(UserService)
    try:
        return service.get_user(user_id)
    except UserNotFoundError as err:
        raise HTTPException(status_code=404, detail="User not found") from err


@router.get("", response_model=list[UserResponse])
def list_users() -> list[UserResponse]:
    service = DIContainer.resolve(UserService)
    return service.list_users()
