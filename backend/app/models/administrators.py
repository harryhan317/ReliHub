"""
Administrator ORM models – aligned with DB_管理员.md.
"""
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from . import Base


class AdminUser(Base):
    """admin_users table – DB_管理员.md §1."""
    __tablename__ = "admin_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="OPERATOR")  # SUPER_ADMIN / OPERATOR / AUDITOR
    allowed_subnet: Mapped[Optional[str]] = mapped_column(Text, default='["0.0.0.0/0"]', nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AdminAuditLog(Base):
    """admin_audit_logs table – DB_管理员.md §2. Hash-chained audit trail."""
    __tablename__ = "admin_audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    admin_id: Mapped[str] = mapped_column(String(36), index=True)
    action: Mapped[str] = mapped_column(String(50), index=True)  # DELETE_RESOURCE, BAN_USER, etc.
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # users / resources / topics
    target_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    before_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON snapshot
    after_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # JSON snapshot
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    prev_log_hash: Mapped[str] = mapped_column(String(64))
    log_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
