"""
Pydantic schemas for auth endpoints.
Aligned with: API_认证鉴权.md §2 & PRD_MVP_登录注册模块.md.
"""
import re
from typing import Optional
from pydantic import BaseModel, field_validator


# ── Requests ──────────────────────────────────────────────────────────────────

class SendCodeRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("当前仅支持中国大陆手机号")
        return v


class PhoneRegisterRequest(BaseModel):
    phone: str
    code: str
    password: Optional[str] = None
    agreed_to_terms: bool

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("当前仅支持中国大陆手机号")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) < 8 or len(v) > 20:
            raise ValueError("密码长度须为 8~20 位")
        categories = 0
        if re.search(r"[a-z]", v):
            categories += 1
        if re.search(r"[A-Z]", v):
            categories += 1
        if re.search(r"\d", v):
            categories += 1
        if re.search(r"[^a-zA-Z0-9]", v):
            categories += 1
        if categories < 2:
            raise ValueError("密码须包含大小写字母、数字、特殊符号中至少 2 项")
        return v


class LoginRequest(BaseModel):
    phone: str
    password: str
    device_fingerprint: Optional[str] = None


class WechatLoginRequest(BaseModel):
    code: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ── Responses ─────────────────────────────────────────────────────────────────

class UserInfoResponse(BaseModel):
    id: str
    nickname: str
    avatar_url: Optional[str] = None
    rank: str
    reputation_points: int
    gold_beans: int
    bonus_beans: int
    is_reward_triggered: bool
    is_new_user: bool = False

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_info: UserInfoResponse
