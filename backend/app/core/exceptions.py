"""
Global business exception system.
Aligned with: API_错误码对照表.md §2 (error code dictionary).
"""
from enum import Enum
from typing import Any, Optional

from fastapi import Request
from fastapi.responses import JSONResponse


class ErrorCode(str, Enum):
    """Business error codes per API_错误码对照表.md."""
    # Auth (§2.1)
    AUTH_4000 = "AUTH_4000"  # Token missing or invalid
    AUTH_4001 = "AUTH_4001"  # Access token expired
    AUTH_4002 = "AUTH_4002"  # Kicked by remote login
    AUTH_4003 = "AUTH_4003"  # Verification code / credential check failed
    AUTH_4004 = "AUTH_4004"  # SMS rate limit exceeded
    AUTH_4005 = "AUTH_4005"  # Refresh token expired / Agreement not accepted
    AUTH_4006 = "AUTH_4006"  # Admin IP whitelist fail

    # User (§2.1)
    USER_4010 = "USER_4010"  # Account banned / locked
    USER_4011 = "USER_4011"  # Account hibernated
    USER_4012 = "USER_4012"  # Reputation too low
    USER_4013 = "USER_4013"  # Rank insufficient
    USER_4014 = "USER_4014"  # Expert application rejected

    # Economy (§2.2)
    ECON_4001 = "ECON_4001"  # Insufficient cocoa beans
    ECON_4002 = "ECON_4002"  # Concurrent lock conflict

    # System (§2.6)
    SYS_4290 = "SYS_4290"   # Business-level rate limit
    SYS_5000 = "SYS_5000"   # Internal server error


# Map error codes to HTTP status codes
_HTTP_STATUS_MAP = {
    ErrorCode.AUTH_4000: 401,
    ErrorCode.AUTH_4001: 401,
    ErrorCode.AUTH_4002: 401,
    ErrorCode.AUTH_4003: 400,
    ErrorCode.AUTH_4004: 429,
    ErrorCode.AUTH_4005: 400,
    ErrorCode.AUTH_4006: 403,
    ErrorCode.USER_4010: 403,
    ErrorCode.USER_4011: 403,
    ErrorCode.USER_4012: 403,
    ErrorCode.USER_4013: 403,
    ErrorCode.USER_4014: 400,
    ErrorCode.ECON_4001: 400,
    ErrorCode.ECON_4002: 409,
    ErrorCode.SYS_4290: 429,
    ErrorCode.SYS_5000: 500,
}


class BusinessException(Exception):
    """Raise to return structured error response."""

    def __init__(
        self,
        code: ErrorCode,
        msg: str,
        data: Optional[dict[str, Any]] = None,
        http_status: Optional[int] = None,
    ):
        self.code = code
        self.msg = msg
        self.data = data or {}
        self.http_status = http_status or _HTTP_STATUS_MAP.get(code, 400)


async def business_exception_handler(_request: Request, exc: BusinessException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content={"code": exc.code.value, "msg": exc.msg, "data": exc.data},
    )


async def generic_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"code": "SYS_5000", "msg": "服务器处理异常，请稍后重试", "data": {}},
    )
