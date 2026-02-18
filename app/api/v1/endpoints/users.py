from fastapi import APIRouter, Depends, Query
from starlette import status

from app.api.dependencies import get_user_service
from app.core.types import UserId
from app.schemas.user import UserCreate, UserResponse
from app.usecase.user.user_service import UserService

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return service.create_user(user)


@router.get("/search", response_model=list[UserResponse])
def search_users(
    name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    return service.search_users(name=name, email=email)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UserId,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return service.get_user(user_id)


@router.get("", response_model=list[UserResponse])
def list_users(
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    return service.list_users()
