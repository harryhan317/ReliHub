"""
File Meta ORM model – fully aligned with DB_文件元数据.md.
"""
from sqlalchemy import String, Integer, Boolean, DateTime, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
import enum
from . import Base


class FileStatus(str, enum.Enum):
    """File status enum aligned with DB_文件元数据.md"""
    NORMAL = "NORMAL"
    SCANNING = "SCANNING"
    ISOLATED = "ISOLATED"
    SUSPICIOUS = "SUSPICIOUS"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"


class LifecycleStatus(str, enum.Enum):
    """File lifecycle status enum"""
    ACTIVE = "ACTIVE"
    SOFT_DELETED = "SOFT_DELETED"
    PERMANENTLY_DELETED = "PERMANENTLY_DELETED"


class TargetType(str, enum.Enum):
    """Target type enum for file usage"""
    CONVERSATION = "CONVERSATION"
    RESOURCE = "RESOURCE"
    TOPIC = "TOPIC"


class FileMeta(Base):
    __tablename__ = "file_meta"

    # ── Identity ──────────────────────────────────────────────────────────────
    file_uuid: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ── File Metadata ─────────────────────────────────────────────────────────
    file_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # Full MD5 hash for instant upload
    oss_path: Mapped[str] = mapped_column(String(1024))  # Physical storage path in OSS
    file_name: Mapped[str] = mapped_column(String(255))  # Original filename
    file_size: Mapped[int] = mapped_column(Integer)  # File size in bytes
    mime_type: Mapped[str] = mapped_column(String(100))  # MIME type

    # ── Reference Counting ────────────────────────────────────────────────────
    ref_counts: Mapped[int] = mapped_column(Integer, default=1)  # Global reference count

    # ── Status ────────────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(String(50), default=FileStatus.SCANNING.value, index=True)
    lifecycle_status: Mapped[str] = mapped_column(String(50), default=LifecycleStatus.ACTIVE.value, index=True)

    # ── Uploader ──────────────────────────────────────────────────────────────
    uploader_uid: Mapped[str] = mapped_column(String(36), index=True)  # FK -> users.id (first uploader)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ── Relationships ─────────────────────────────────────────────────────────
    usages: Mapped[List["FileUsage"]] = relationship("FileUsage", back_populates="file", cascade="all, delete-orphan")


class FileUsage(Base):
    __tablename__ = "file_usage"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    # ── File Reference ────────────────────────────────────────────────────────
    file_uuid: Mapped[str] = mapped_column(String(36), index=True)  # FK -> file_meta.file_uuid
    target_id: Mapped[str] = mapped_column(String(36), index=True)  # Reference target (Conversation/Resource/Topic ID)
    target_type: Mapped[str] = mapped_column(String(50))  # Target type: CONVERSATION/RESOURCE/TOPIC
    user_id: Mapped[str] = mapped_column(String(36))  # Current referencing user ID

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # ── Relationships ─────────────────────────────────────────────────────────
    file: Mapped["FileMeta"] = relationship("FileMeta", back_populates="usages")
