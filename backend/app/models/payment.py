"""
Database models for Payment module.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin

if TYPE_CHECKING:
    from .users import User


class PaymentStatus(enum.Enum):
    """Payment status"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(enum.Enum):
    """Payment method"""
    WECHAT = "wechat"
    ALIPAY = "alipay"
    BANK_TRANSFER = "bank_transfer"


class PaymentOrder(Base, TimestampMixin):
    """
    Payment Order
    
    Stores payment order information.
    """
    __tablename__ = "payment_orders"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="payment_orders")
    
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="CNY")
    
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), default=PaymentMethod.WECHAT)
    payment_status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    transaction_id: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)
    prepay_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    callback_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notify_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    additional_data: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    transactions: Mapped[list["BalanceTransaction"]] = relationship(
        "BalanceTransaction",
        back_populates="payment_order",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_payment_orders_user_status', 'user_id', 'payment_status'),
        Index('idx_payment_orders_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<PaymentOrder(id={self.id}, order_no={self.order_no}, amount={self.amount})>"


class UserBalance(Base, TimestampMixin):
    """
    User Balance
    
    Stores user account balance.
    """
    __tablename__ = "user_balances"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="balance")
    
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    frozen_balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    total_recharged: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_consumed: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_refunded: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    __table_args__ = (
        Index('idx_user_balances_balance', 'balance'),
    )
    
    def __repr__(self) -> str:
        return f"<UserBalance(user_id={self.user_id}, balance={self.balance})>"


class BalanceTransaction(Base, TimestampMixin):
    """
    Balance Transaction
    
    Records all balance changes.
    """
    __tablename__ = "balance_transactions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="balance_transactions")
    
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)
    
    payment_order_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("payment_orders.id"), nullable=True, index=True)
    payment_order: Mapped[Optional["PaymentOrder"]] = relationship("PaymentOrder", back_populates="transactions")
    
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    remark: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    additional_data: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    
    __table_args__ = (
        Index('idx_balance_transactions_user_type', 'user_id', 'transaction_type'),
        Index('idx_balance_transactions_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<BalanceTransaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"
