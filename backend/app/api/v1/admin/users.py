"""
Admin API - User Management
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.administrators import AdminUser
from app.schemas.admin import (
    BanUserRequest,
    LockUserRequest,
    UserListResponse,
    UserResponse,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/users", tags=["Admin - Users"])


@router.get("", response_model=UserListResponse)
def list_users(
    status: Optional[str] = Query(None, description="Filter by user status"),
    search: Optional[str] = Query(None, description="Search by nickname or phone"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    List all users with pagination and filtering.
    
    - **status**: Filter by user status (ACTIVE, DISABLED, LOCKED, HIBERNATED)
    - **search**: Search by nickname or phone number
    """
    service = AdminService(db, admin)
    users, total = service.list_users(status=status, search=search, page=page, page_size=page_size)
    
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Get user details by ID.
    """
    service = AdminService(db, admin)
    user = service.get_user(user_id)
    
    if not user:
        from app.core.exceptions import BusinessException, ErrorCode
        raise BusinessException(ErrorCode.ADMIN_4004, "用户不存在")
    
    return UserResponse.model_validate(user)


@router.post("/{user_id}/ban", response_model=UserResponse)
def ban_user(
    user_id: str,
    request: BanUserRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Ban a user.
    
    - **reason**: Reason for banning
    - **duration_days**: Optional ban duration (None for permanent)
    """
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    user = service.ban_user(user_id, request, ip_address=ip_address)
    return UserResponse.model_validate(user)


@router.post("/{user_id}/unban", response_model=UserResponse)
def unban_user(
    user_id: str,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Unban a user.
    """
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    user = service.unban_user(user_id, ip_address=ip_address)
    return UserResponse.model_validate(user)


@router.post("/{user_id}/lock", response_model=UserResponse)
def lock_user(
    user_id: str,
    request: LockUserRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Lock a user account.
    
    - **reason**: Reason for locking
    """
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    user = service.lock_user(user_id, request, ip_address=ip_address)
    return UserResponse.model_validate(user)


@router.post("/{user_id}/unlock", response_model=UserResponse)
def unlock_user(
    user_id: str,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Unlock a user account.
    """
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    user = service.unlock_user(user_id, ip_address=ip_address)
    return UserResponse.model_validate(user)
