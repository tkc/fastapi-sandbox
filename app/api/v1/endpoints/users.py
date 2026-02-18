import structlog
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_user_service
from app.core.exceptions import UserNotFoundError
from app.schemas.user import UserCreate, UserResponse
from app.usecase.user.user_service import UserService

router = APIRouter()
logger = structlog.stdlib.get_logger()


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    logger.info("create_user called", name=user.name, email=user.email)
    try:
        result = service.create_user(user)
    except Exception:
        logger.exception("create_user failed")
        raise
    logger.info("create_user succeeded", user_id=result.user_id)
    return result


@router.get("/search", response_model=list[UserResponse])
def search_users(
    name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    logger.info("search_users called", name=name, email=email)
    try:
        results = service.search_users(name=name, email=email)
    except Exception:
        logger.exception("search_users failed")
        raise
    logger.info("search_users succeeded", count=len(results))
    return results


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    logger.info("get_user called", user_id=user_id)
    try:
        result = service.get_user(user_id)
    except UserNotFoundError as err:
        logger.warning("get_user not found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found") from err
    except Exception:
        logger.exception("get_user failed")
        raise
    logger.info("get_user succeeded", user_id=user_id)
    return result


@router.get("", response_model=list[UserResponse])
def list_users(
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    logger.info("list_users called")
    try:
        results = service.list_users()
    except Exception:
        logger.exception("list_users failed")
        raise
    logger.info("list_users succeeded", count=len(results))
    return results
