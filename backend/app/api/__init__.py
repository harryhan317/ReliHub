"""
Central API router – mounts all v1 sub-routers.
"""
from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.users.router import router as users_router
from app.api.v1.resources.router import router as resources_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["认证鉴权"])
api_router.include_router(users_router, prefix="/users", tags=["用户"])
api_router.include_router(resources_router, prefix="/resources", tags=["资源"])
