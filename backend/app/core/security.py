"""
JWT token management and Argon2id password hashing.
Aligned with: DB_users.md §9 (Argon2id), API_认证鉴权.md §2 (JWT).
"""
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from typing import Optional

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerificationError, VerifyMismatchError
from jose import jwt

from app.core.config import settings

# ── Argon2id Password Hasher ──────────────────────────────────────────────────

_hasher = PasswordHasher(
    time_cost=settings.ARGON2_TIME_COST,
    memory_cost=settings.ARGON2_MEMORY_COST,
    parallelism=settings.ARGON2_PARALLELISM,
    type=Type.ID,
)


def hash_password(plain: str) -> str:
    """Hash a plaintext password with Argon2id."""
    return _hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against the Argon2id hash."""
    try:
        return _hasher.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError):
        return False


def needs_rehash(hashed: str) -> bool:
    """Check if the hash should be upgraded (params changed)."""
    return _hasher.check_needs_rehash(hashed)


# ── JWT Token ─────────────────────────────────────────────────────────────────

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire, "type": "access", "jti": uuid.uuid4().hex}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": subject, "exp": expire, "type": "refresh", "jti": uuid.uuid4().hex}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    Raises:
        ExpiredSignatureError: If the token has expired.
        JWTError: If the token is invalid for other reasons.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


# ── Phone Blind Index (HMAC-SHA256) ──────────────────────────────────────────

def generate_phone_blind_index(phone: str) -> str:
    """
    Generate a blind index for encrypted phone lookup.
    Aligned with DB_users.md §9: HMAC-SHA256(phone, key)[:8] hex.
    """
    return hmac.new(
        settings.PHONE_BLIND_INDEX_KEY.encode(),
        phone.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]
