"""
SQLAlchemy Base and all model imports.
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import all models here for Alembic auto-detection
from .users import User
from .ai_session import AISession
from .ai_message import AIMessage
from .file_meta import FileMeta, FileUsage, FileStatus, LifecycleStatus, TargetType
from .resources import Resource, ResourcePreview, ResourceStatus
from .topic import Topic, Post, BountyStatus, TopicStatus
from .ledger import PointLedger, AttemptedTransaction, AssetPackage, UserPurchasedAsset, PointType, OrderType
from .notification import Notification, NotificationType, NotificationPriority
from .administrators import AdminUser, AdminAuditLog
