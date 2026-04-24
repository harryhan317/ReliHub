"""
Service layer for all modules.
"""

# Auth functions (not a class)
from .ai_service import AIService
from .auth_service import (
    blacklist_token,
    is_token_blacklisted,
    login_by_password,
    login_by_wechat,
    logout,
    refresh_access_token,
    register_by_phone,
)
from .community_service import PostService, TopicService
from .file_service import FileService
from .ledger_service import AssetPackageService, PointLedgerService
from .notification_service import NotificationService
from .resource_service import ResourceService
from .sms_service import send_verification_code, verify_code

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
    "AIService",
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
