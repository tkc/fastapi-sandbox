from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.exceptions import UserNotFoundError
from app.dependencies.user import (
    get_create_user_usecase,
    get_get_user_usecase,
    get_list_users_usecase,
    get_search_users_usecase,
)
from app.schemas.user import UserCreate, UserResponse
from app.usecase.user.create_user_usecase import CreateUserUseCase
from app.usecase.user.get_user_usecase import GetUserUseCase
from app.usecase.user.list_users_usecase import ListUsersUseCase
from app.usecase.user.search_users_usecase import SearchUsersUseCase

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    usecase: CreateUserUseCase = Depends(get_create_user_usecase),
):
    return usecase.execute(user)


@router.get("/search", response_model=list[UserResponse])
def search_users(
    name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    usecase: SearchUsersUseCase = Depends(get_search_users_usecase),
):
    return usecase.execute(name=name, email=email)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    usecase: GetUserUseCase = Depends(get_get_user_usecase),
):
    try:
        return usecase.execute(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("", response_model=list[UserResponse])
def list_users(
    usecase: ListUsersUseCase = Depends(get_list_users_usecase),
):
    return usecase.execute()
