import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from app.core.constants import (
    ERROR_INTERNAL_SERVER,
    ERROR_USER_NOT_FOUND,
    LOG_APP_ERROR,
    LOG_REPOSITORY_ERROR,
    LOG_USER_NOT_FOUND,
)
from app.core.exceptions import AppError, RepositoryError, UserNotFoundError

logger = structlog.stdlib.get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserNotFoundError)
    async def handle_user_not_found(request: Request, exc: UserNotFoundError) -> JSONResponse:
        logger.warning(
            LOG_USER_NOT_FOUND,
            user_id=exc.user_id,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": ERROR_USER_NOT_FOUND},
        )

    @app.exception_handler(RepositoryError)
    async def handle_repository_error(request: Request, exc: RepositoryError) -> JSONResponse:
        logger.error(
            LOG_REPOSITORY_ERROR,
            operation=exc.operation,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": ERROR_INTERNAL_SERVER},
        )

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.error(
            LOG_APP_ERROR,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": ERROR_INTERNAL_SERVER},
        )
