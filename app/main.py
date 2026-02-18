from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import v1_router
from app.infrastructure.datasource.dynamodb import create_users_table


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_users_table()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="User API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(v1_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
