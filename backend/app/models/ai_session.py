"""
AI Session ORM model – fully aligned with DB_ai 对话.md.
"""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from . import Base

if TYPE_CHECKING:
    from .ai_message import AIMessage


class AISession(Base):
    __tablename__ = "ai_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=True)

    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model_type: Mapped[str] = mapped_column(String(50), default="general")
    system_prompt_version: Mapped[str] = mapped_column(String(50), default="v1.0")
    provider_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    total_turns: Mapped[int] = mapped_column(Integer, default=0)
    max_turns: Mapped[int] = mapped_column(Integer, default=50)
    max_tokens: Mapped[int] = mapped_column(Integer, default=50000)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    messages: Mapped[List["AIMessage"]] = relationship("AIMessage", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
    )
