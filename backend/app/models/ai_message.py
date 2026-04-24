"""
AI Message ORM model – fully aligned with DB_ai 对话.md.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from . import Base

if TYPE_CHECKING:
    from .ai_session import AISession


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_sessions.id", ondelete="CASCADE"),
        index=True
    )

    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)

    has_attachment: Mapped[bool] = mapped_column(Boolean, default=False)
    attachment_ids: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    feedback_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    feedback_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["AISession"] = relationship("AISession", back_populates="messages")

    __table_args__ = (
        Index('idx_session_created', 'session_id', 'created_at'),
    )
