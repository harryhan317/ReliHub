"""
Pydantic Schemas for Ledger/Economy module.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PointType(str, Enum):
    """Point type enum"""
    GOLD_BEAN = "GOLD_BEAN"
    BONUS_BEAN = "BONUS_BEAN"


class OrderType(str, Enum):
    """Order type enum"""
    DOWNLOAD = "DOWNLOAD"
    DOWNLOAD_REVENUE = "DOWNLOAD_REVENUE"
    DESTRUCTION = "DESTRUCTION"
    RECHARGE = "RECHARGE"
    SYSTEM_GIFT = "SYSTEM_GIFT"
    SHARE_REWARD = "SHARE_REWARD"
    EARLYBIRD_REWARD = "EARLYBIRD_REWARD"
    SIGN_IN = "SIGN_IN"
    INVITE_REWARD = "INVITE_REWARD"
    CONTENT_TOPIC = "CONTENT_TOPIC"
    CONTENT_POST = "CONTENT_POST"
    CATEGORY_FIRST_POST_REWARD = "CATEGORY_FIRST_POST_REWARD"
    CONTENT_ADOPTED = "CONTENT_ADOPTED"
    BOUNTY_LOCK = "BOUNTY_LOCK"
    BOUNTY_RELEASE = "BOUNTY_RELEASE"
    BOUNTY_REFUND = "BOUNTY_REFUND"
    FEEDBACK_AWARD = "FEEDBACK_AWARD"


# ── Request Schemas ───────────────────────────────────────────────────────────

class RechargeRequest(BaseModel):
    """Request schema for recharging cocoa beans"""
    amount: int = Field(..., ge=10, le=10000, description="Recharge amount in CNY")
    payment_method: str = Field(..., pattern="^(wechat|alipay)$", description="Payment method")


class DownloadRequest(BaseModel):
    """Request schema for downloading a resource"""
    resource_id: str = Field(..., description="Resource ID to download")


class AssetPackagePurchaseRequest(BaseModel):
    """Request schema for purchasing an asset package"""
    package_id: str = Field(..., description="Asset package ID")


# ── Response Schemas ──────────────────────────────────────────────────────────

class PointLedgerResponse(BaseModel):
    """Response schema for a point ledger entry"""
    id: str
    transaction_uuid: str
    user_id: str
    amount: int
    point_type: PointType
    dist_ratio: Optional[float] = None
    order_type: OrderType
    balance_after: int
    related_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PointLedgerListResponse(BaseModel):
    """Response schema for point ledger list"""
    ledgers: List[PointLedgerResponse]
    total: int
    page: int
    page_size: int


class UserBalanceResponse(BaseModel):
    """Response schema for user balance"""
    user_id: str
    gold_beans: int
    bonus_beans: int
    total_beans: int
    last_updated: datetime


class AssetPackageResponse(BaseModel):
    """Response schema for asset package"""
    id: str
    name: str
    price_beans: int
    quota_mb: int
    discount_rate: float
    created_at: datetime

    class Config:
        from_attributes = True


class UserPurchasedAssetResponse(BaseModel):
    """Response schema for user purchased asset"""
    id: str
    user_id: str
    package_id: str
    remaining_mb: int
    used_mb: int
    expires_at: datetime
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AttemptedTransactionResponse(BaseModel):
    """Response schema for attempted transaction (dead letter)"""
    id: str
    user_id: str
    order_type: OrderType
    amount: int
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionHistoryResponse(BaseModel):
    """Response schema for transaction history"""
    transactions: List[PointLedgerResponse]
    total_income: int
    total_expense: int
    current_balance: int
