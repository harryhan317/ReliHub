"""
Resource ORM model – fully aligned with DB_资源.md.
"""
from sqlalchemy import String, Integer, Boolean, DateTime, Text, Float, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
import enum
from . import Base


class ResourceStatus(str, enum.Enum):
    """Resource status enum aligned with DB_资源.md"""
    SCANNING = "SCANNING"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPEALING = "APPEALING"
    BLOCKED = "BLOCKED"


class Resource(Base):
    __tablename__ = "resources"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ── Uploader ──────────────────────────────────────────────────────────────
    uploader_id: Mapped[str] = mapped_column(String(36), index=True)  # FK -> users.id

    # ── Metadata ──────────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(255), index=True)  # Resource title (≤100 chars)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Resource description
    category_id: Mapped[int] = mapped_column(Integer)  # FK -> categories.id
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # JSON string of tags (e.g., ["可靠性", "HALT"])

    # ── Pricing ───────────────────────────────────────────────────────────────
    price: Mapped[int] = mapped_column(Integer, default=5)  # Price in cocoa beans (range: 5-100,000)

    # ── File Reference ────────────────────────────────────────────────────────
    file_uuid: Mapped[str] = mapped_column(String(36))  # FK -> file_meta.file_uuid

    # ── Statistics ────────────────────────────────────────────────────────────
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    dislike_count: Mapped[int] = mapped_column(Integer, default=0)
    heat_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)  # Heat index (calculated asynchronously)

    # ── Special Flags ─────────────────────────────────────────────────────────
    is_seed: Mapped[bool] = mapped_column(Boolean, default=False)  # Basic resource (free within quota)

    # ── Status ────────────────────────────────────────────────────────────────
    status: Mapped[ResourceStatus] = mapped_column(SQLEnum(ResourceStatus), default=ResourceStatus.SCANNING)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)  # Soft delete

    # ── Anonymization (for deleted users) ─────────────────────────────────────
    anonymized_user_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ── Relationships ─────────────────────────────────────────────────────────
    # previews: Mapped[List["ResourcePreview"]] = relationship("ResourcePreview", back_populates="resource", cascade="all, delete-orphan")


class ResourcePreview(Base):
    __tablename__ = "resource_previews"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    resource_id: Mapped[str] = mapped_column(String(36), index=True)  # FK -> resources.id

    # ── Preview Data ──────────────────────────────────────────────────────────
    preview_url: Mapped[str] = mapped_column(String(1024))  # Preview image URL or PDF page path
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # For PDF multi-page previews

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # ── Relationships ─────────────────────────────────────────────────────────
    # resource: Mapped["Resource"] = relationship("Resource", back_populates="previews")
