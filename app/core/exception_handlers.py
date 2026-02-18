import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError, RepositoryError, UserNotFoundError

logger = structlog.stdlib.get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserNotFoundError)
    async def handle_user_not_found(request: Request, exc: UserNotFoundError) -> JSONResponse:
        logger.warning(
            "user_not_found",
            user_id=exc.user_id,
            path=request.url.path,
        )
        return JSONResponse(status_code=404, content={"detail": "User not found"})

    @app.exception_handler(RepositoryError)
    async def handle_repository_error(request: Request, exc: RepositoryError) -> JSONResponse:
        logger.error(
            "repository_error",
            operation=exc.operation,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.error(
            "app_error",
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
