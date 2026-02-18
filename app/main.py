from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import v1_router
from app.container.container import Container
from app.infrastructure.datasource.dynamodb import create_users_table


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_users_table()
    yield


def create_app() -> FastAPI:
    container = Container()
    app = FastAPI(title="User API", lifespan=lifespan)
    app.container = container
    app.include_router(v1_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
