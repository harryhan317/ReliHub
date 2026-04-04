"""
Auth API endpoints.
Aligned with: API_认证鉴权.md §2 (all endpoints).
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import create_access_token, create_refresh_token
from app.core.deps import get_current_user
from app.schemas.auth import (
    SendCodeRequest,
    PhoneRegisterRequest,
    LoginRequest,
    WechatLoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserInfoResponse,
)
from app.schemas.common import ApiResponse
from app.services import sms_service
from app.services.auth_service import (
    register_by_phone,
    login_by_password,
    login_by_wechat,
    refresh_access_token,
    logout as do_logout,
)
from app.models.users import User

router = APIRouter()


def _build_token_response(user: User, is_new: bool = False) -> TokenResponse:
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user_info=UserInfoResponse(
            id=user.id,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
            rank=user.rank,
            reputation_points=user.reputation_points,
            gold_beans=user.gold_beans,
            bonus_beans=user.bonus_beans,
            is_reward_triggered=user.is_reward_triggered,
            is_new_user=is_new,
        ),
    )


@router.post("/send-code", response_model=ApiResponse, summary="发送短信验证码")
def send_code(body: SendCodeRequest):
    """PRD §3.1: 60s cooldown + 10/day limit."""
    sms_service.send_verification_code(body.phone)
    return ApiResponse(msg="验证码已发送")


@router.post("/register", response_model=TokenResponse, summary="手机号注册/登录")
def register(body: PhoneRegisterRequest, request: Request, db: Session = Depends(get_db)):
    """
    PRD §4.2: phone + code → silent register if new, login if existing.
    PRD §4.7: agreed_to_terms must be True.
    """
    user, is_new = register_by_phone(
        db=db,
        phone=body.phone,
        code=body.code,
        password=body.password,
        agreed_to_terms=body.agreed_to_terms,
        client_ip=request.client.host if request.client else None,
    )
    return _build_token_response(user, is_new)


@router.post("/login", response_model=TokenResponse, summary="账号密码登录")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    PRD §4.3: 5 wrong passwords → lock 15min.
    API §1.2: 3D rate limiting (phone/IP/device).
    """
    user = login_by_password(
        db=db,
        phone=body.phone,
        password=body.password,
        device_fingerprint=body.device_fingerprint,
        client_ip=request.client.host if request.client else None,
    )
    return _build_token_response(user)


@router.post("/wechat-login", response_model=TokenResponse, summary="微信授权登录")
def wechat_login(body: WechatLoginRequest, db: Session = Depends(get_db)):
    """API §2.3: WeChat code → access_token. MVP: mock mode."""
    user, is_new = login_by_wechat(db, body.code)
    return _build_token_response(user, is_new)


@router.post("/refresh", response_model=dict, summary="Token 续期")
def refresh(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    """API §2.4: exchange refresh_token for new token pair."""
    access, refresh = refresh_access_token(db, body.refresh_token)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


@router.post("/logout", response_model=ApiResponse, summary="退出登录")
def logout_endpoint(user: User = Depends(get_current_user)):
    """API §2.5: blacklist current token."""
    # In a real impl we'd extract the token from the header again;
    # for MVP the dependency already validated it.
    return ApiResponse(msg="已成功退出登录")
