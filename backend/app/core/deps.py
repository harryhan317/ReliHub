"""
FastAPI dependency injection utilities.
Aligned with: API_认证鉴权.md §2 (JWT bearer), §4 (RBAC).
"""
from fastapi import Depends, Header
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ErrorCode
from app.core.security import decode_token
from app.db.session import get_db
from app.models.administrators import AdminUser
from app.models.users import User


def get_current_user(
    authorization: str = Header(
        ...,
        description="Bearer token for authentication. Format: Bearer <JWT>",
        examples=["Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    ),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and validate the user from the JWT Bearer token.

    Args:
        authorization: The 'Authorization' header containing the Bearer token.
        db: Database session.

    Returns:
        The User object associated with the token.

    Raises:
        BusinessException(AUTH_4000): If the token is missing, malformed, or invalid.
        BusinessException(AUTH_4001): If the token has expired.
    """
    if not authorization.startswith("Bearer "):
        raise BusinessException(ErrorCode.AUTH_4000, "Token 缺失或无效格式")

    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        # Audit Requirement: Distinguish expired token (AUTH_4001) from invalid (AUTH_4000)
        raise BusinessException(ErrorCode.AUTH_4001, "Token 已过期")
    except JWTError:
        raise BusinessException(ErrorCode.AUTH_4000, "Token 缺失或无效格式")

    if payload.get("type") != "access":
        raise BusinessException(ErrorCode.AUTH_4000, "无效的 Token 类型")

    user_id: str = payload.get("sub", "")
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise BusinessException(ErrorCode.AUTH_4000, "用户不存在")

    return user


def require_admin(
    authorization: str = Header(
        ...,
        description="Bearer token for authentication. Format: Bearer <JWT>",
        examples=["Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    ),
    db: Session = Depends(get_db),
) -> AdminUser:
    """
    Require admin privileges.
    
    Args:
        authorization: The 'Authorization' header containing the Bearer token.
        db: Database session.
    
    Returns:
        The AdminUser object.
    
    Raises:
        BusinessException: If token is invalid or user is not admin.
    """
    if not authorization.startswith("Bearer "):
        raise BusinessException(ErrorCode.AUTH_4000, "Token 缺失或无效格式")
    
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise BusinessException(ErrorCode.AUTH_4001, "Token 已过期")
    except JWTError:
        raise BusinessException(ErrorCode.AUTH_4000, "Token 缺失或无效格式")
    
    if payload.get("type") != "access":
        raise BusinessException(ErrorCode.AUTH_4000, "无效的 Token 类型")
    
    user_id: str = payload.get("sub", "")
    admin = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    
    if admin is None:
        raise BusinessException(ErrorCode.AUTH_4000, "管理员不存在或权限不足")
    
    if not admin.is_active:
        raise BusinessException(ErrorCode.ADMIN_4001, "管理员账号已被禁用")
    
    return admin


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """
    Ensure the current user is active and not locked/disabled.

    Args:
        user: The user object injected by get_current_user.

    Returns:
        The validated active User object.

    Raises:
        BusinessException(USER_4010): If the account is locked or disabled.
    """
    if user.status == "DISABLED":
        raise BusinessException(
            ErrorCode.USER_4010,
            "您的账号已被安全锁定",
            {"ban_until": None, "reason": "账号已被封禁"},
        )
    if user.status == "LOCKED":
        raise BusinessException(
            ErrorCode.USER_4010,
            "您的账号已被安全锁定",
            {"reason": "资产冻结"},
        )
    if user.status == "HIBERNATED":
        raise BusinessException(
            ErrorCode.USER_4011,
            "您的账号已进入休眠状态，请重新激活",
        )
    return user
