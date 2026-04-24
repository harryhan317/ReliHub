"""
Database models for Sensitive Words module.
"""

import enum
from typing import Optional

from sqlalchemy import Boolean, Index, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base, TimestampMixin


class SensitiveWordCategory(enum.Enum):
    """Sensitive word category"""
    POLITICAL = "political"
    VIOLENCE = "violence"
    PORNOGRAPHY = "pornography"
    GAMBLING = "gambling"
    DRUGS = "drugs"
    FRAUD = "fraud"
    RUMOR = "rumor"
    INSULT = "insult"
    ADVERTISEMENT = "advertisement"
    OTHER = "other"


class SensitiveWordLevel(enum.Enum):
    """Sensitive word level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SensitiveWord(Base, TimestampMixin):
    """
    Sensitive Word
    
    Stores sensitive words for filtering.
    """
    __tablename__ = "sensitive_words"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    category: Mapped[SensitiveWordCategory] = mapped_column(
        SAEnum(SensitiveWordCategory, name='sensitive_word_category'),
        default=SensitiveWordCategory.OTHER,
        nullable=False
    )
    level: Mapped[SensitiveWordLevel] = mapped_column(
        SAEnum(SensitiveWordLevel, name='sensitive_word_level'),
        default=SensitiveWordLevel.LOW,
        nullable=False
    )
    
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    hit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        Index('idx_sensitive_words_category', 'category'),
        Index('idx_sensitive_words_level', 'level'),
        Index('idx_sensitive_words_enabled_hit', 'enabled', 'hit_count'),
    )
    
    def __repr__(self) -> str:
        return f"<SensitiveWord(id={self.id}, word='{self.word}', level={self.level.value})>"


class SensitiveWordLog(Base, TimestampMixin):
    """
    Sensitive Word Hit Log
    
    Logs when sensitive words are detected.
    """
    __tablename__ = "sensitive_word_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    matched_words: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    additional_data: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    
    __table_args__ = (
        Index('idx_sensitive_word_logs_created', 'created_at'),
        Index('idx_sensitive_word_logs_user_action', 'user_id', 'action'),
    )
    
    def __repr__(self) -> str:
        return f"<SensitiveWordLog(id={self.id}, user_id={self.user_id}, action={self.action})>"
