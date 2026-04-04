"""
AI Session ORM model – fully aligned with DB_ai 对话.md.
"""
from sqlalchemy import String, Integer, Boolean, DateTime, Text, Float, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
from . import Base


class AISession(Base):
    __tablename__ = "ai_sessions"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=True)  # NULL for guest users

    # ── Session Metadata ───────────────────────────────────────────────────────
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Auto-generated or user-defined
    model_type: Mapped[str] = mapped_column(String(50), default="general")  # general / multimodal
    system_prompt_version: Mapped[str] = mapped_column(String(50), default="v1.0")

    # ── Quota & Token Management ──────────────────────────────────────────────
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)  # Total tokens consumed in this session
    total_turns: Mapped[int] = mapped_column(Integer, default=0)  # Total QA turns in this session
    max_turns: Mapped[int] = mapped_column(Integer, default=50)  # Max turns per session (configurable)
    max_tokens: Mapped[int] = mapped_column(Integer, default=50000)  # Max tokens per session (configurable)

    # ── Status ────────────────────────────────────────────────────────────────
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)  # Soft delete

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ── Relationships ─────────────────────────────────────────────────────────
    messages: Mapped[List["AIMessage"]] = relationship("AIMessage", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
    )
