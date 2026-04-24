"""
Schemas for Payment module.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PaymentStatusEnum(str, Enum):
    """Payment status enum"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethodEnum(str, Enum):
    """Payment method enum"""
    WECHAT = "wechat"
    ALIPAY = "alipay"
    BANK_TRANSFER = "bank_transfer"


class PaymentOrderBase(BaseModel):
    """Base schema for PaymentOrder"""
    
    amount: float = Field(..., gt=0, description="Amount in CNY")
    subject: str = Field(..., min_length=1, max_length=255, description="Order title")
    body: Optional[str] = Field(None, max_length=1000, description="Order description")
    payment_method: PaymentMethodEnum = Field(default=PaymentMethodEnum.WECHAT)
    callback_url: Optional[str] = Field(None, max_length=500, description="Callback URL")


class PaymentOrderCreate(PaymentOrderBase):
    """Schema for creating a payment order"""
    pass


class PaymentOrderResponse(BaseModel):
    """Schema for payment order response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    order_no: str
    user_id: str
    amount: float
    currency: str
    payment_method: PaymentMethodEnum
    payment_status: PaymentStatusEnum
    subject: str
    body: Optional[str]
    transaction_id: Optional[str]
    paid_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class PaymentOrderListResponse(BaseModel):
    """Schema for payment order list response"""
    
    orders: List[PaymentOrderResponse]
    total: int


class UserBalanceResponse(BaseModel):
    """Schema for user balance response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    balance: float
    frozen_balance: float
    total_recharged: float
    total_consumed: float
    total_refunded: float
    created_at: datetime
    updated_at: datetime


class BalanceTransactionResponse(BaseModel):
    """Schema for balance transaction response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    transaction_type: str
    amount: float
    balance_after: float
    description: Optional[str]
    remark: Optional[str]
    created_at: datetime


class WechatPayRequest(BaseModel):
    """Schema for WeChat Pay request"""
    
    order_id: Optional[str] = Field(None, description="Existing order ID")
    amount: Optional[float] = Field(None, gt=0, description="Amount in CNY")
    subject: Optional[str] = Field(None, max_length=255, description="Order title")
    body: Optional[str] = Field(None, max_length=1000, description="Order description")


class WechatPayResponse(BaseModel):
    """Schema for WeChat Pay response"""
    
    order_id: str
    order_no: str
    prepay_id: Optional[str] = None
    code_url: Optional[str] = None
    
    appId: Optional[str] = None
    timeStamp: Optional[str] = None
    nonceStr: Optional[str] = None
    package: Optional[str] = None
    signType: Optional[str] = None
    paySign: Optional[str] = None
