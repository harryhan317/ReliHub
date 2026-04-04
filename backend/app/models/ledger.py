"""
Point Ledger ORM model – fully aligned with DB_可可豆.md.
"""
from sqlalchemy import String, Integer, Boolean, DateTime, Index, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
import enum
from . import Base


class PointType(str, enum.Enum):
    """Point type enum aligned with DB_可可豆.md"""
    GOLD_BEAN = "GOLD_BEAN"  # Asset beans (withdrawable)
    BONUS_BEAN = "BONUS_BEAN"  # Bonus beans (non-withdrawable)


class OrderType(str, enum.Enum):
    """Order type enum aligned with DB_可可豆.md §1"""
    # Resource related
    DOWNLOAD = "DOWNLOAD"  # Resource download payment
    DOWNLOAD_REVENUE = "DOWNLOAD_REVENUE"  # Resource download revenue (70% to uploader)
    DESTRUCTION = "DESTRUCTION"  # System burn (30% deflation)
    
    # Recharge and gifts
    RECHARGE = "RECHARGE"  # User recharge
    SYSTEM_GIFT = "SYSTEM_GIFT"  # System gift (e.g., registration 30 beans)
    SHARE_REWARD = "SHARE_REWARD"  # Share reward (Phase 2)
    EARLYBIRD_REWARD = "EARLYBIRD_REWARD"  # First 200 users bonus (20 beans)
    SIGN_IN = "SIGN_IN"  # Daily sign-in reward
    INVITE_REWARD = "INVITE_REWARD"  # Invitation reward
    
    # Content related
    CONTENT_TOPIC = "CONTENT_TOPIC"  # Topic creation reward (10 beans)
    CONTENT_POST = "CONTENT_POST"  # Post reply reward (5 beans)
    CATEGORY_FIRST_POST_REWARD = "CATEGORY_FIRST_POST_REWARD"  # Category first post bonus (30 beans)
    CONTENT_ADOPTED = "CONTENT_ADOPTED"  # Content adopted (reputation only, no beans)
    
    # Bounty related
    BOUNTY_LOCK = "BOUNTY_LOCK"  # Bounty lock (freeze)
    BOUNTY_RELEASE = "BOUNTY_RELEASE"  # Bounty release (70/30 split)
    BOUNTY_REFUND = "BOUNTY_REFUND"  # Bounty refund (timeout)
    
    # Feedback
    FEEDBACK_AWARD = "FEEDBACK_AWARD"  # Feedback award (Phase 2)


class PointLedger(Base):
    __tablename__ = "point_ledger"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ── Transaction Grouping ──────────────────────────────────────────────────
    transaction_uuid: Mapped[str] = mapped_column(String(36), index=True)  # Groups multiple ledger entries for one transaction

    # ── User ──────────────────────────────────────────────────────────────────
    user_id: Mapped[str] = mapped_column(String(36), index=True)  # FK -> users.id (transaction subject)

    # ── Amount ────────────────────────────────────────────────────────────────
    amount: Mapped[int] = mapped_column(Integer)  # Amount change (negative for spending, positive for earning)

    # ── Point Type ────────────────────────────────────────────────────────────
    point_type: Mapped[PointType] = mapped_column(SQLEnum(PointType))  # GOLD_BEAN / BONUS_BEAN

    # ── Distribution Ratio ────────────────────────────────────────────────────
    dist_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Distribution ratio (0.7 / 0.3 / 0.15, etc.)

    # ── Order Type ────────────────────────────────────────────────────────────
    order_type: Mapped[OrderType] = mapped_column(SQLEnum(OrderType), index=True)

    # ── Balance Snapshot ──────────────────────────────────────────────────────
    balance_after: Mapped[int] = mapped_column(Integer)  # Balance after transaction (for audit)

    # ── Related Business ID ───────────────────────────────────────────────────
    related_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)  # Related business ID (resource/topic/order ID)

    # ── Description ───────────────────────────────────────────────────────────
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Transaction description

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class AttemptedTransaction(Base):
    __tablename__ = "attempted_transaction"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ── User ──────────────────────────────────────────────────────────────────
    user_id: Mapped[str] = mapped_column(String(36), index=True)  # FK -> users.id

    # ── Order Type ────────────────────────────────────────────────────────────
    order_type: Mapped[OrderType] = mapped_column(SQLEnum(OrderType))  # Attempted order type

    # ── Amount ────────────────────────────────────────────────────────────────
    amount: Mapped[int] = mapped_column(Integer)  # Attempted amount (for audit)

    # ── Reason ────────────────────────────────────────────────────────────────
    reason: Mapped[str] = mapped_column(String(500))  # Block reason string snapshot

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AssetPackage(Base):
    __tablename__ = "asset_packages"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ── Package Info ──────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(50))  # Package name (e.g., 特惠包 / 畅享包)
    price_beans: Mapped[int] = mapped_column(Integer)  # Price in beans (default: 特惠包 80 / 畅享包 350)
    quota_mb: Mapped[int] = mapped_column(Integer)  # Quota capacity in MB
    discount_rate: Mapped[float] = mapped_column(Float)  # Discount rate (e.g., 0.85 / 0.70)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserPurchasedAsset(Base):
    __tablename__ = "user_purchased_assets"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ── User & Package ────────────────────────────────────────────────────────
    user_id: Mapped[str] = mapped_column(String(36), index=True)  # FK -> users.id
    package_id: Mapped[str] = mapped_column(String(36))  # FK -> asset_packages.id

    # ── Quota Management ──────────────────────────────────────────────────────
    remaining_mb: Mapped[int] = mapped_column(Integer)  # Remaining quota in MB
    used_mb: Mapped[int] = mapped_column(Integer, default=0)  # Used quota in MB

    # ── Expiry ────────────────────────────────────────────────────────────────
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # ── Status ────────────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
