"""
Admin API - Authentication
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.models.administrators import AdminUser
from app.schemas.common import ApiResponse
from app.services.admin_service import AdminService
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

    client_ip = request.client.host if request.client else None
    admin_service = AdminService(db, admin)
    admin_service._create_audit_log(
        action="ADMIN_LOGIN",
        target_type="admin_user",
        target_id=admin.id,
        before_data={},
        after_data={"username": admin.username, "role": admin.role},
        ip_address=client_ip
    )
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


@router.post("/auth/logout")
def admin_logout(
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    from app.core.security import decode_token

    client_ip = request.client.host if request.client else None
    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    if token:
        admin_service = AdminService(db, admin)
        admin_service._create_audit_log(
            action="ADMIN_LOGOUT",
            target_type="admin_user",
            target_id=admin.id,
            before_data={},
            after_data={"username": admin.username},
            ip_address=client_ip
        )
        db.commit()

    return ApiResponse(code="000000", msg="ok", data={})
