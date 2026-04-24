"""
Feedback ORM model.
"""
import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy import Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from . import Base


class FeedbackType(str, enum.Enum):
    """Feedback type enum"""
    BUG = "BUG"
    SUGGESTION = "SUGGESTION"
    CONTENT = "CONTENT"
    OTHER = "OTHER"


class FeedbackStatus(str, enum.Enum):
    """Feedback status enum"""
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    type: Mapped[FeedbackType] = mapped_column(
        SQLEnum(FeedbackType),
        default=FeedbackType.OTHER
    )
    content: Mapped[str] = mapped_column(Text)
    images: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[FeedbackStatus] = mapped_column(
        SQLEnum(FeedbackStatus),
        default=FeedbackStatus.PENDING
    )
    reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    replied_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
