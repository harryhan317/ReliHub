"""
Topic and Post ORM models – fully aligned with DB_社区.md.
"""
import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from . import Base


class BountyStatus(str, enum.Enum):
    """Bounty status enum aligned with DB_社区.md"""
    NONE = "NONE"
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    REFUNDED = "REFUNDED"


class TopicStatus(str, enum.Enum):
    """Topic status enum"""
    NORMAL = "NORMAL"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"


class Topic(Base):
    __tablename__ = "topics"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ── Author ────────────────────────────────────────────────────────────────
    author_id: Mapped[str] = mapped_column(String(36), index=True)  # FK -> users.id

    # ── Content ───────────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(255))  # Topic title (5-50 chars)
    content: Mapped[str] = mapped_column(Text)  # Topic content (Markdown support)
    category_id: Mapped[int] = mapped_column(Integer)  # Category ID

    # ── Bounty System ─────────────────────────────────────────────────────────
    bounty_amount: Mapped[int] = mapped_column(Integer, default=0)  # Bounty in cocoa beans
    bounty_status: Mapped[BountyStatus] = mapped_column(SQLEnum(BountyStatus), default=BountyStatus.NONE)
    accepted_post_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # FK -> posts.id (accepted answer)

    # ── Status ────────────────────────────────────────────────────────────────
    status: Mapped[TopicStatus] = mapped_column(SQLEnum(TopicStatus), default=TopicStatus.NORMAL)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)  # Soft delete

    # ── Statistics ────────────────────────────────────────────────────────────
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    post_count: Mapped[int] = mapped_column(Integer, default=0)
    heat_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)  # Heat index

    # ── Anonymization (for deleted users) ─────────────────────────────────────
    anonymized_user_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="topic", cascade="all, delete-orphan", foreign_keys="Post.topic_id")


class Post(Base):
    __tablename__ = "posts"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ── Topic Reference ───────────────────────────────────────────────────────
    topic_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("topics.id", ondelete="CASCADE"),
        index=True
    )  # FK -> topics.id

    # ── Author ────────────────────────────────────────────────────────────────
    author_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL")
    )  # FK -> users.id

    # ── Content ───────────────────────────────────────────────────────────────
    content: Mapped[str] = mapped_column(Text)  # Post content

    # ── Parent Post (for nested comments) ─────────────────────────────────────
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("posts.id", ondelete="SET NULL"),
        nullable=True
    )  # FK -> posts.id (self-reference)

    # ── Acceptance Status ─────────────────────────────────────────────────────
    is_accepted: Mapped[bool] = mapped_column(Boolean, default=False)  # Accepted as best answer

    # ── Statistics ────────────────────────────────────────────────────────────
    like_count: Mapped[int] = mapped_column(Integer, default=0)

    # ── Anonymization (for deleted users) ─────────────────────────────────────
    anonymized_user_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # ── Relationships ─────────────────────────────────────────────────────────
    topic: Mapped["Topic"] = relationship("Topic", back_populates="posts")
    parent: Mapped[Optional["Post"]] = relationship("Post", remote_side="Post.id", foreign_keys="Post.parent_id")
