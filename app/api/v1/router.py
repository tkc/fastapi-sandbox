from fastapi import APIRouter

from app.api.v1.endpoints import users

v1_router = APIRouter()
v1_router.include_router(users.router, prefix="/users", tags=["users"])
