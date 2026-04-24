"""
Payment Service

Handles payment orders, balance management, and payment processing.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.payment import (
    BalanceTransaction,
    PaymentMethod,
    PaymentOrder,
    PaymentStatus,
    UserBalance,
)
from app.services.wechat_pay import WeChatPayService

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for payment operations"""
    
    def __init__(self, db: Session, wechat_pay: Optional[WeChatPayService] = None):
        self.db = db
        self.wechat_pay = wechat_pay
    
    def create_payment_order(
        self,
        user_id: str,
        amount: float,
        subject: str,
        payment_method: PaymentMethod = PaymentMethod.WECHAT,
        body: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> PaymentOrder:
        """
        Create a new payment order
        
        Args:
            user_id: User ID
            amount: Amount in CNY
            subject: Order title
            payment_method: Payment method
            body: Order description
            callback_url: Callback URL after payment
            
        Returns:
            PaymentOrder instance
        """
        order_no = self._generate_order_no()
        
        order = PaymentOrder(
            id=str(uuid.uuid4()),
            order_no=order_no,
            user_id=user_id,
            amount=amount,
            currency="CNY",
            payment_method=payment_method,
            payment_status=PaymentStatus.PENDING,
            subject=subject,
            body=body,
            callback_url=callback_url,
            notify_url="/api/v1/payment/wechat/notify",
            additional_data=json.dumps({
                "created_at": datetime.now().isoformat()
            })
        )
        
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        logger.info(f"Created payment order: {order_no}, amount: {amount}")
        return order
    
    def get_payment_order(
        self,
        order_id: Optional[str] = None,
        order_no: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Optional[PaymentOrder]:
        """
        Get payment order by ID or order number
        
        Args:
            order_id: Order ID
            order_no: Order number
            user_id: User ID (for ownership check)
            
        Returns:
            PaymentOrder or None
        """
        query = select(PaymentOrder)
        
        if order_id:
            query = query.where(PaymentOrder.id == order_id)
        
        if order_no:
            query = query.where(PaymentOrder.order_no == order_no)
        
        if user_id:
            query = query.where(PaymentOrder.user_id == user_id)
        
        result = self.db.execute(query)
        return result.scalar_one_or_none()
    
    def list_payment_orders(
        self,
        user_id: str,
        status: Optional[PaymentStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[PaymentOrder], int]:
        """
        List payment orders for a user
        
        Args:
            user_id: User ID
            status: Filter by status
            page: Page number
            page_size: Page size
            
        Returns:
            List of PaymentOrder and total count
        """
        count_query = select(func.count()).select_from(PaymentOrder).where(PaymentOrder.user_id == user_id)
        if status:
            count_query = count_query.where(PaymentOrder.payment_status == status)
        
        total = self.db.execute(count_query).scalar()
        
        query = (
            select(PaymentOrder)
            .where(PaymentOrder.user_id == user_id)
            .order_by(PaymentOrder.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        if status:
            query = query.where(PaymentOrder.payment_status == status)
        
        result = self.db.execute(query)
        orders = list(result.scalars().all())
        
        return orders, total
    
    def update_payment_status(
        self,
        order: PaymentOrder,
        status: PaymentStatus,
        transaction_id: Optional[str] = None
    ) -> PaymentOrder:
        """
        Update payment order status
        
        Args:
            order: PaymentOrder instance
            status: New status
            transaction_id: Third-party transaction ID
            
        Returns:
            Updated PaymentOrder
        """
        old_status = order.payment_status
        order.payment_status = status
        
        if transaction_id:
            order.transaction_id = transaction_id
        
        if status == PaymentStatus.SUCCESS:
            order.paid_at = datetime.now()
        elif status == PaymentStatus.CANCELLED:
            order.cancelled_at = datetime.now()
        elif status == PaymentStatus.REFUNDED:
            order.refunded_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(order)
        
        logger.info(
            f"Payment order {order.order_no} status changed: "
            f"{old_status.value} -> {status.value}"
        )
        
        return order
    
    def get_user_balance(self, user_id: str) -> Optional[UserBalance]:
        """
        Get user balance
        
        Args:
            user_id: User ID
            
        Returns:
            UserBalance or None
        """
        query = select(UserBalance).where(UserBalance.user_id == user_id)
        result = self.db.execute(query)
        return result.scalar_one_or_none()
    
    def get_or_create_user_balance(self, user_id: str) -> UserBalance:
        """
        Get or create user balance
        
        Args:
            user_id: User ID
            
        Returns:
            UserBalance instance
        """
        balance = self.get_user_balance(user_id)
        
        if not balance:
            balance = UserBalance(
                id=str(uuid.uuid4()),
                user_id=user_id,
                balance=0.0,
                frozen_balance=0.0
            )
            self.db.add(balance)
            self.db.commit()
            self.db.refresh(balance)
        
        return balance
    
    def add_balance(
        self,
        user_id: str,
        amount: float,
        transaction_type: str,
        description: Optional[str] = None,
        payment_order_id: Optional[str] = None,
        remark: Optional[str] = None
    ) -> UserBalance:
        """
        Add balance to user account
        
        Args:
            user_id: User ID
            amount: Amount to add
            transaction_type: Transaction type (recharge, refund, etc.)
            description: Transaction description
            payment_order_id: Related payment order ID
            remark: Remark
            
        Returns:
            Updated UserBalance
        """
        balance = self.get_or_create_user_balance(user_id)
        
        balance.balance += amount
        balance.total_recharged += amount
        
        transaction = BalanceTransaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=balance.balance,
            payment_order_id=payment_order_id,
            description=description or f"充值 {amount} 元",
            remark=remark,
            additional_data=json.dumps({
                "timestamp": datetime.now().isoformat()
            })
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(balance)
        
        logger.info(
            f"Added balance to user {user_id}: +{amount}, "
            f"new balance: {balance.balance}"
        )
        
        return balance
    
    def deduct_balance(
        self,
        user_id: str,
        amount: float,
        transaction_type: str,
        description: Optional[str] = None,
        payment_order_id: Optional[str] = None,
        remark: Optional[str] = None
    ) -> UserBalance:
        """
        Deduct balance from user account
        
        Args:
            user_id: User ID
            amount: Amount to deduct
            transaction_type: Transaction type (consume, etc.)
            description: Transaction description
            payment_order_id: Related payment order ID
            remark: Remark
            
        Returns:
            Updated UserBalance
            
        Raises:
            ValueError: If insufficient balance
        """
        balance = self.get_or_create_user_balance(user_id)
        
        if balance.balance < amount:
            raise ValueError(
                f"Insufficient balance: {balance.balance} < {amount}"
            )
        
        balance.balance -= amount
        balance.total_consumed += amount
        
        transaction = BalanceTransaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            transaction_type=transaction_type,
            amount=-amount,
            balance_after=balance.balance,
            payment_order_id=payment_order_id,
            description=description or f"消费 {amount} 元",
            remark=remark,
            additional_data=json.dumps({
                "timestamp": datetime.now().isoformat()
            })
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(balance)
        
        logger.info(
            f"Deducted balance from user {user_id}: -{amount}, "
            f"new balance: {balance.balance}"
        )
        
        return balance
    
    def handle_wechat_notify(
        self,
        notify_data: dict
    ) -> Tuple[bool, str]:
        """
        Handle WeChat Pay notification
        
        Args:
            notify_data: Notification data from WeChat
            
        Returns:
            Tuple of (success, message)
        """
        out_trade_no = notify_data.get("out_trade_no")
        transaction_id = notify_data.get("transaction_id")
        trade_state = notify_data.get("trade_state")
        
        order = self.get_payment_order(order_no=out_trade_no)
        if not order:
            return False, "Order not found"
        
        if order.payment_status == PaymentStatus.SUCCESS:
            return True, "Already processed"
        
        if trade_state == "SUCCESS":
            self.update_payment_status(
                order,
                PaymentStatus.SUCCESS,
                transaction_id
            )
            
            self.add_balance(
                user_id=order.user_id,
                amount=order.amount,
                transaction_type="recharge",
                description=f"充值 - {order.subject}",
                payment_order_id=order.id,
                remark=f"订单号：{order.order_no}"
            )
            
            return True, "Success"
        
        return False, f"Unknown trade state: {trade_state}"
    
    def _generate_order_no(self) -> str:
        """
        Generate unique order number
        
        Format: YYYYMMDDHHMMSS + 8 random digits
        """
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        random_part = str(uuid.uuid4())[:8].replace("-", "")
        return f"{timestamp}{random_part}"
