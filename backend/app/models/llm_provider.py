"""
LLM Provider ORM model.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from . import Base


class LLMProvider(Base):
    __tablename__ = "llm_providers"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # 'deepseek', 'openai', 'claude'
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)  # 'DeepSeek', 'OpenAI', 'Claude'

    # ── API Configuration ─────────────────────────────────────────────────────
    api_base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key_env: Mapped[str] = mapped_column(String(100), nullable=False)  # Environment variable name

    # ── Provider Settings ─────────────────────────────────────────────────────
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=60)
    cost_per_1k_tokens: Mapped[float] = mapped_column(Float, nullable=False)  # Cost per 1k tokens (in USD or CNY)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_llm_providers_enabled', 'enabled'),
        Index('idx_llm_providers_name', 'name'),
    )
