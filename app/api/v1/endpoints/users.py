from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query

from app.container.container import Container
from app.core.exceptions import UserNotFoundError
from app.schemas.user import UserCreate, UserResponse
from app.usecase.user.create_user_usecase import CreateUserUseCase
from app.usecase.user.get_user_usecase import GetUserUseCase
from app.usecase.user.list_users_usecase import ListUsersUseCase
from app.usecase.user.search_users_usecase import SearchUsersUseCase

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=201)
@inject
def create_user(
    user: UserCreate,
    usecase: CreateUserUseCase = Depends(Provide[Container.create_user_usecase]),
):
    return usecase.execute(user)


@router.get("/search", response_model=list[UserResponse])
@inject
def search_users(
    name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    usecase: SearchUsersUseCase = Depends(Provide[Container.search_users_usecase]),
):
    return usecase.execute(name=name, email=email)


@router.get("/{user_id}", response_model=UserResponse)
@inject
def get_user(
    user_id: str,
    usecase: GetUserUseCase = Depends(Provide[Container.get_user_usecase]),
):
    try:
        return usecase.execute(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("", response_model=list[UserResponse])
@inject
def list_users(
    usecase: ListUsersUseCase = Depends(Provide[Container.list_users_usecase]),
):
    return usecase.execute()
