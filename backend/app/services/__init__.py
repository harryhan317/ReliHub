"""
Service layer for all modules.
"""

# Auth functions (not a class)
from .auth_service import (
    register_by_phone,
    login_by_password,
    login_by_wechat,
    refresh_access_token,
    logout,
    is_token_blacklisted,
    blacklist_token,
)
from .sms_service import send_verification_code, verify_code
from .ai_service import AISessionService, AIMessageService
from .resource_service import ResourceService
from .community_service import TopicService, PostService
from .ledger_service import PointLedgerService, AssetPackageService
from .notification_service import NotificationService
from .file_service import FileService

__all__ = [
    # Auth
    "register_by_phone",
    "login_by_password",
    "login_by_wechat",
    "refresh_access_token",
    "logout",
    "is_token_blacklisted",
    "blacklist_token",
    "send_verification_code",
    "verify_code",
    # AI
    "AISessionService",
    "AIMessageService",
    # Resource
    "ResourceService",
    # Community
    "TopicService",
    "PostService",
    # Ledger
    "PointLedgerService",
    "AssetPackageService",
    # Notification
    "NotificationService",
    # File
    "FileService",
]
