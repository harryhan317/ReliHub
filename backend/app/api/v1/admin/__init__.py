"""
Admin module initialization.
"""

from .auth import router as auth_router
from .audit import router as audit_router
from .config import router as config_router
from .content import router as content_router
from .dashboard import router as dashboard_router
from .feedback import router as feedback_router
from .llm_provider import router as llm_provider_router
from .packages import router as packages_router
from .users import router as users_router

__all__ = [
    "auth_router",
    "audit_router",
    "config_router",
    "content_router",
    "dashboard_router",
    "feedback_router",
    "llm_provider_router",
    "packages_router",
    "users_router",
]
