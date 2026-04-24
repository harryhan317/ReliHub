"""
Notification ORM model – fully aligned with DB_通知.md.
"""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from . import Base


class NotificationType(str, enum.Enum):
    """Notification type enum aligned with DB_通知.md"""
    SYSTEM = "SYSTEM"  # System notifications
    INTERACTION = "INTERACTION"  # Interaction notifications (likes, replies, etc.)
    AUDIT = "AUDIT"  # Audit notifications (resource/topic review results)
    REWARD = "REWARD"  # Reward notifications (cocoa beans, reputation points)
    BROADCAST = "BROADCAST"  # Broadcast notifications (announcements)


class NotificationPriority(str, enum.Enum):
    """Notification priority enum"""
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class Notification(Base):
    __tablename__ = "notifications"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ── Receiver ──────────────────────────────────────────────────────────────
    receiver_id: Mapped[str] = mapped_column(String(36), index=True)  # FK -> users.id

    # ── Sender ────────────────────────────────────────────────────────────────
    sender_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # FK -> users.id (NULL for system notifications)

    # ── Type & Priority ───────────────────────────────────────────────────────
    type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), index=True)
    priority: Mapped[NotificationPriority] = mapped_column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)

    # ── DND Exemption ─────────────────────────────────────────────────────────
    is_broadcast_exemption: Mapped[bool] = mapped_column(Boolean, default=False)  # Exempt from DND mode (for broadcasts)

    # ── Content ───────────────────────────────────────────────────────────────
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Short title
    content: Mapped[str] = mapped_column(Text)  # Detailed content (supports template variables)

    # ── Link ──────────────────────────────────────────────────────────────────
    link_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Click-to-jump URL (e.g., /resources/xxx)

    # ── Read Status ───────────────────────────────────────────────────────────
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
