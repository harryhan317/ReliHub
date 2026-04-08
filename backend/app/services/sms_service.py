"""
SMS verification code service (MVP: mock mode).
Aligned with: PRD_MVP_登录注册模块.md §3.1 (rate limiting), §3.2 (lifecycle).
"""
import logging
import random

from app.core.config import settings
from app.core.exceptions import BusinessException, ErrorCode

logger = logging.getLogger(__name__)

# ── In-memory store (MVP; production uses Redis) ─────────────────────────────
_code_store: dict[str, dict] = {}
_send_count: dict[str, int] = {}


def send_verification_code(phone: str) -> str:
    """
    Generate and 'send' a 6-digit verification code.
    MVP: logs the code and returns it; does not actually send SMS.
    Rate limits: 60s cooldown per phone, 10 sends/day per phone.
    """
    import time

    now = time.time()
    key = f"sms:{phone}"

    # 60s cooldown check
    if key in _code_store:
        elapsed = now - _code_store[key].get("sent_at", 0)
        if elapsed < 60:
            raise BusinessException(
                ErrorCode.AUTH_4004,
                "验证码获取过于频繁，请稍后再试",
            )

    # Daily limit check (10 per day)
    daily_key = f"sms_daily:{phone}"
    count = _send_count.get(daily_key, 0)
    if count >= 10:
        raise BusinessException(
            ErrorCode.AUTH_4004,
            "当前号码今日请求达上限",
        )

    # Generate code
    if settings.SMS_TEST_CODE:
        code = settings.SMS_TEST_CODE  # MVP fixed test code: 888888
    else:
        code = f"{random.randint(100000, 999999)}"

    # Store with 5-min TTL
    _code_store[key] = {"code": code, "sent_at": now, "expires_at": now + 300}
    _send_count[daily_key] = count + 1

    logger.info(f"[SMS Mock] Verification code for {phone[:3]}****{phone[-4:]}: {code}")
    return code


def verify_code(phone: str, code: str) -> bool:
    """
    Verify and consume a one-time code.
    Returns True if valid, raises BusinessException otherwise.
    """
    import time

    key = f"sms:{phone}"
    record = _code_store.get(key)

    if record is None:
        raise BusinessException(ErrorCode.AUTH_4003, "验证码错误，请重新输入")

    if time.time() > record["expires_at"]:
        _code_store.pop(key, None)
        raise BusinessException(ErrorCode.AUTH_4003, "验证码已过期，请重新获取")

    if record["code"] != code:
        raise BusinessException(ErrorCode.AUTH_4003, "验证码错误，请重新输入")

    # One-time consumption
    _code_store.pop(key, None)
    return True
