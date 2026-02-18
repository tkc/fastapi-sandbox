from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import v1_router
from app.container.container import DIContainer
from app.dependencies.user import init_usecases
from app.infrastructure.datasource.dynamodb import create_users_table
from app.usecase.user.create_user_usecase import CreateUserUseCase
from app.usecase.user.get_user_usecase import GetUserUseCase
from app.usecase.user.list_users_usecase import ListUsersUseCase
from app.usecase.user.search_users_usecase import SearchUsersUseCase


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_users_table()
    init_usecases(
        create_user=DIContainer.resolve(CreateUserUseCase),
        get_user=DIContainer.resolve(GetUserUseCase),
        list_users=DIContainer.resolve(ListUsersUseCase),
        search_users=DIContainer.resolve(SearchUsersUseCase),
    )
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="User API", lifespan=lifespan)
    app.include_router(v1_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
