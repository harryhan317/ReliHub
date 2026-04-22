"""
User interaction models: collections, likes, and reports.
"""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from . import Base


class TargetType(str, enum.Enum):
    RESOURCE = "RESOURCE"
    TOPIC = "TOPIC"
    POST = "POST"


class ReportReason(str, enum.Enum):
    SPAM = "SPAM"
    INAPPROPRIATE = "INAPPROPRIATE"
    COPYRIGHT = "COPYRIGHT"
    MISLEADING = "MISLEADING"
    OTHER = "OTHER"


class ReportStatus(str, enum.Enum):
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    DISMISSED = "DISMISSED"


class UserCollection(Base):
    __tablename__ = "user_collections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    target_type: Mapped[TargetType] = mapped_column(SQLEnum(TargetType), index=True)
    target_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserLike(Base):
    __tablename__ = "user_likes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    target_type: Mapped[TargetType] = mapped_column(SQLEnum(TargetType), index=True)
    target_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserReport(Base):
    __tablename__ = "user_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    target_type: Mapped[TargetType] = mapped_column(SQLEnum(TargetType), index=True)
    target_id: Mapped[str] = mapped_column(String(36), index=True)
    reason: Mapped[str] = mapped_column(String(50))
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        SQLEnum(ReportStatus),
        default=ReportStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserCheckin(Base):
    __tablename__ = "user_checkins"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    checkin_date: Mapped[str] = mapped_column(String(10), index=True)
    reward_beans: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
