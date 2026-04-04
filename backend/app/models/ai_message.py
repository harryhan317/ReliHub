"""
AI Message ORM model – fully aligned with DB_ai 对话.md.
"""
from sqlalchemy import String, Integer, Boolean, DateTime, Text, Float, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from . import Base


class AIMessage(Base):
    __tablename__ = "ai_messages"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)  # FK -> ai_sessions.id

    # ── Message Content ───────────────────────────────────────────────────────
    role: Mapped[str] = mapped_column(String(20))  # user / assistant / system
    content: Mapped[str] = mapped_column(Text)  # Markdown content
    token_count: Mapped[int] = mapped_column(Integer, default=0)  # Tokens consumed by this message

    # ── Attachment References (Optional) ──────────────────────────────────────
    has_attachment: Mapped[bool] = mapped_column(Boolean, default=False)
    attachment_ids: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Comma-separated file UUIDs

    # ── Feedback (Optional) ───────────────────────────────────────────────────
    feedback_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # like / dislike / NULL
    feedback_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Status ────────────────────────────────────────────────────────────────
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)  # Soft delete

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # ── Relationships ─────────────────────────────────────────────────────────
    # session relationship is defined in AISession model

    __table_args__ = (
        Index('idx_session_created', 'session_id', 'created_at'),
    )
