"""
Admin API - Authentication
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.models.administrators import AdminUser
from app.schemas.common import ApiResponse
from pydantic import BaseModel


router = APIRouter(tags=["Admin - Auth"])


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminInfoResponse(BaseModel):
    id: str
    username: str
    role: str


class AdminLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    admin_info: AdminInfoResponse


@router.post("/auth/login")
def admin_login(
    body: AdminLoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    admin = db.query(AdminUser).filter(AdminUser.username == body.username).first()
    if not admin:
        return ApiResponse(code="AUTH_4003", msg="用户名或密码错误", data={})
    if not admin.is_active:
        return ApiResponse(code="ADMIN_4001", msg="管理员账号已被禁用", data={})
    if not verify_password(body.password, admin.password_hash):
        return ApiResponse(code="AUTH_4003", msg="用户名或密码错误", data={})

    admin.last_login_at = datetime.utcnow()
    db.commit()

    access = create_access_token(admin.id)
    refresh = create_refresh_token(admin.id)

    return ApiResponse(
        code="000000",
        msg="ok",
        data=AdminLoginResponse(
            access_token=access,
            refresh_token=refresh,
            admin_info=AdminInfoResponse(
                id=admin.id,
                username=admin.username,
                role=admin.role,
            ),
        ),
    )
