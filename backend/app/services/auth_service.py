"""
Core authentication business logic.
Aligned with:
  - PRD_MVP_登录注册模块.md §4 (register, login, lock, WeChat)
  - API_认证鉴权.md §2 (endpoints)
  - DB_users.md §1 (users table fields)
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BusinessException, ErrorCode
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_phone_blind_index,
    hash_password,
    needs_rehash,
    verify_password,
)
from app.models.users import User
from app.services.sms_service import verify_code

logger = logging.getLogger(__name__)

# ── Token blacklist with Redis fallback ───────────────────────────────────────
# Production: Redis SET + TTL matching token expiry.
# Fallback: In-memory set when Redis is unavailable.
from app.core.redis_client import redis_client

_memory_blacklist: set[str] = set()


def is_token_blacklisted(jti: str) -> bool:
    """
    Check if token is blacklisted.
    Uses Redis if available, falls back to in-memory storage.
    """
    if redis_client.is_available:
        redis_key = f"token_blacklist:{jti}"
        return redis_client.exists(redis_key)
    else:
        return jti in _memory_blacklist


def blacklist_token(jti: str) -> None:
    """
    Add token to blacklist.
    Uses Redis if available, falls back to in-memory storage.
    """
    if redis_client.is_available:
        redis_key = f"token_blacklist:{jti}"
        ttl_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        redis_client.set(redis_key, "1", ex=ttl_seconds)
    else:
        _memory_blacklist.add(jti)


# ── Register ─────────────────────────────────────────────────────────────────

def register_by_phone(
    db: Session,
    phone: str,
    code: str,
    password: Optional[str],
    agreed_to_terms: bool,
    client_ip: Optional[str] = None,
) -> tuple[User, bool]:
    """
    Register or login by phone + SMS code.
    Returns (user, is_new_user).
    PRD §4.7: agreed_to_terms MUST be True → AUTH_4005.
    PRD §4.2: if phone not in DB → silent register; else → login.
    """
    if not agreed_to_terms:
        raise BusinessException(
            ErrorCode.AUTH_4005,
            "为了您的权益，请阅读并勾选许可协议",
        )

    # Verify SMS code
    verify_code(phone, code)

    # Lookup by blind index
    blind = generate_phone_blind_index(phone)
    user = db.query(User).filter(User.phone_blind_index == blind).first()

    is_new = user is None

    if is_new:
        user = User(
            id=uuid.uuid4().hex,
            phone=phone,  # MVP: plaintext; production: AES-256-CBC
            phone_blind_index=blind,
            nickname="新用户",
            rank="新兵",
            reputation_points=50,  # PRD requirement: initial 50 points
            gold_beans=30,   # Registration reward: 30 cocoa beans (Audit requirement)
            bonus_beans=0,
            status="ACTIVE",
            invite_code=uuid.uuid4().hex[:8].upper(),
            agreement_timestamp=datetime.now(timezone.utc),
            last_login_ip=client_ip,
        )
        if password:
            user.password_hash = hash_password(password)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New user registered: {user.id}")
    else:
        # Existing user: update login info
        user.last_login_ip = client_ip
        user.last_login_at = datetime.now(timezone.utc)
        user.failed_login_attempts = 0
        user.lock_until_time = None
        db.commit()

    return user, is_new


# ── Password Login ───────────────────────────────────────────────────────────

def login_by_password(
    db: Session,
    phone: str,
    password: str,
    device_fingerprint: Optional[str] = None,
    client_ip: Optional[str] = None,
) -> User:
    """
    Login by phone + password.
    PRD §4.3: 5 consecutive failures → lock 15 min (AUTH_4004).
    PRD §4.3: wrong password → AUTH_4003 with remaining attempts.
    """
    blind = generate_phone_blind_index(phone)
    user = db.query(User).filter(User.phone_blind_index == blind).first()

    if user is None:
        raise BusinessException(ErrorCode.AUTH_4003, "账号或密码错误")

    # Check lock
    now = datetime.now(timezone.utc)
    if user.lock_until_time and user.lock_until_time > now:
        raise BusinessException(
            ErrorCode.USER_4010,
            "账户出于安全防护已锁定15分钟",
            {"ban_until": user.lock_until_time.isoformat()},
        )

    if not user.password_hash:
        raise BusinessException(ErrorCode.AUTH_4003, "该账号未设置密码，请使用验证码登录")

    if not verify_password(password, user.password_hash):
        user.failed_login_attempts += 1
        remaining = 5 - user.failed_login_attempts

        if user.failed_login_attempts >= 5:
            from datetime import timedelta
            user.lock_until_time = now + timedelta(minutes=15)
            db.commit()
            raise BusinessException(
                ErrorCode.USER_4010,
                "账户出于安全防护已锁定15分钟",
                {"ban_until": user.lock_until_time.isoformat()},
            )

        db.commit()
        raise BusinessException(
            ErrorCode.AUTH_4003,
            f"密码错误，您还有 {max(remaining, 0)} 次机会",
        )

    # Success → reset counters
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)
    user.failed_login_attempts = 0
    user.lock_until_time = None
    user.last_login_ip = client_ip
    user.last_login_device = device_fingerprint
    user.last_login_at = now
    db.commit()

    return user


# ── WeChat Login (Mock) ──────────────────────────────────────────────────────

def login_by_wechat(db: Session, code: str) -> tuple[User, bool]:
    """
    WeChat login via authorization code.
    MVP mock: code starting with 'test_' returns a mock openid.
    """
    if settings.WECHAT_MOCK_MODE:
        openid = f"mock_openid_{code}"
    else:
        # Production: exchange code for openid via WeChat API
        raise NotImplementedError("WeChat production login not yet implemented")

    user = db.query(User).filter(User.wechat_openid == openid).first()
    is_new = user is None

    if is_new:
        user = User(
            id=uuid.uuid4().hex,
            wechat_openid=openid,
            nickname="微信用户",
            rank="新兵",
            reputation_points=50,
            bonus_beans=30,
            status="ACTIVE",
            invite_code=uuid.uuid4().hex[:8].upper(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user, is_new


# ── Token Refresh ────────────────────────────────────────────────────────────

def refresh_access_token(db: Session, refresh_token: str) -> tuple[str, str]:
    """
    Issue a new access+refresh token pair from a valid refresh token.
    API_认证鉴权.md §2.4.
    """
    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise BusinessException(ErrorCode.AUTH_4005, "Refresh Token 已失效，请重新登录")
    
    if payload is None or payload.get("type") != "refresh":
        raise BusinessException(ErrorCode.AUTH_4005, "Refresh Token 已失效，请重新登录")

    jti = payload.get("jti", "")
    if is_token_blacklisted(jti):
        raise BusinessException(ErrorCode.AUTH_4005, "Refresh Token 已失效，请重新登录")

    user_id = payload.get("sub", "")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise BusinessException(ErrorCode.AUTH_4005, "Refresh Token 已失效，请重新登录")

    # Blacklist old refresh token
    blacklist_token(jti)

    return create_access_token(user_id), create_refresh_token(user_id)


# ── Logout ───────────────────────────────────────────────────────────────────

def logout(token: str) -> None:
    """Blacklist the current access token. API_认证鉴权.md §2.5."""
    payload = decode_token(token)
    if payload and "jti" in payload:
        blacklist_token(payload["jti"])
