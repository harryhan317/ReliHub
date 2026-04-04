"""
User ORM model – fully aligned with DB_users.md.
"""
from sqlalchemy import String, Integer, Boolean, DateTime, Text, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from . import Base


class User(Base):
    __tablename__ = "users"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    wechat_openid: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)  # AES-256-CBC encrypted
    phone_blind_index: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Argon2id

    # ── Profile ───────────────────────────────────────────────────────────────
    nickname: Mapped[str] = mapped_column(String(50), default="新用户")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # ── Reputation & Rank ─────────────────────────────────────────────────────
    rank: Mapped[str] = mapped_column(String(20), default="新兵")
    reputation_points: Mapped[int] = mapped_column(Integer, default=50)
    reputation_status: Mapped[str] = mapped_column(String(20), default="NORMAL")
    is_expert: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Economy ───────────────────────────────────────────────────────────────
    gold_beans: Mapped[int] = mapped_column(Integer, default=0)
    bonus_beans: Mapped[int] = mapped_column(Integer, default=0)

    # ── Invitation ────────────────────────────────────────────────────────────
    invite_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    referrer_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    is_reward_triggered: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Security & Audit ──────────────────────────────────────────────────────
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    last_login_device: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    lock_until_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    agreement_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Status & Config ───────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    admin_subnet: Mapped[Optional[str]] = mapped_column(Text, default='["0.0.0.0/0"]', nullable=True)
    daily_token_usage: Mapped[int] = mapped_column(Integer, default=0)
    total_ai_storage_mb: Mapped[float] = mapped_column(Float, default=0.0)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
