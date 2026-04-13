"""
SQLAlchemy Base and all model imports.
"""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps"""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


from .administrators import AdminAuditLog, AdminUser
from .ai_message import AIMessage
from .ai_session import AISession
from .feedback import Feedback, FeedbackStatus
from .file_meta import FileMeta, FileStatus, FileUsage, LifecycleStatus, TargetType
from .ledger import (
    AssetPackage,
    AttemptedTransaction,
    OrderType,
    PointLedger,
    PointType,
    UserPurchasedAsset,
)
from .llm_provider import LLMProvider
from .notification import Notification, NotificationPriority, NotificationType
from .payment import BalanceTransaction, PaymentOrder, UserBalance
from .resources import Resource, ResourcePreview, ResourceStatus
from .sensitive_word import SensitiveWord, SensitiveWordLog
from .system_config import SystemConfig
from .topic import BountyStatus, Post, Topic, TopicStatus
from .users import User
from .search_history import SearchHistory

__all__ = [
    "Base",
    "TimestampMixin",
    "AdminAuditLog",
    "AdminUser",
    "AIMessage",
    "AISession",
    "Feedback",
    "FeedbackStatus",
    "FileMeta",
    "FileStatus",
    "FileUsage",
    "LifecycleStatus",
    "TargetType",
    "AssetPackage",
    "AttemptedTransaction",
    "OrderType",
    "PointLedger",
    "PointType",
    "UserPurchasedAsset",
    "LLMProvider",
    "Notification",
    "NotificationPriority",
    "NotificationType",
    "BalanceTransaction",
    "PaymentOrder",
    "UserBalance",
    "Resource",
    "ResourcePreview",
    "ResourceStatus",
    "SensitiveWord",
    "SensitiveWordLog",
    "SystemConfig",
    "BountyStatus",
    "Post",
    "Topic",
    "TopicStatus",
    "User",
]
