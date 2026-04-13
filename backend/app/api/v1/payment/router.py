"""
Payment API Router

Handles payment-related HTTP requests.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.payment import PaymentMethod, PaymentStatus
from app.models.users import User
from app.schemas.payment import (
    BalanceTransactionResponse,
    PaymentOrderCreate,
    PaymentOrderListResponse,
    PaymentOrderResponse,
    UserBalanceResponse,
    WechatPayRequest,
    WechatPayResponse,
)
from app.services.payment_service import PaymentService
from app.services.wechat_pay import WeChatPayService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment", tags=["支付"])


@router.post("/orders", response_model=PaymentOrderResponse)
def create_payment_order(
    request: PaymentOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new payment order
    
    - **amount**: Amount in CNY
    - **subject**: Order title
    - **payment_method**: Payment method (wechat, alipay, etc.)
    """
    service = PaymentService(db)
    
    order = service.create_payment_order(
        user_id=current_user.id,
        amount=request.amount,
        subject=request.subject,
        payment_method=request.payment_method or PaymentMethod.WECHAT,
        body=request.body,
        callback_url=request.callback_url
    )
    
    return order


@router.get("/orders", response_model=PaymentOrderListResponse)
def list_payment_orders(
    status: Optional[PaymentStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List payment orders for current user
    
    - **status**: Filter by payment status
    - **page**: Page number
    - **page_size**: Page size
    """
    service = PaymentService(db)
    
    orders, total = service.list_payment_orders(
        user_id=current_user.id,
        status=status,
        page=page,
        page_size=page_size
    )
    
    return PaymentOrderListResponse(
        orders=[PaymentOrderResponse.model_validate(o) for o in orders],
        total=total
    )


@router.get("/orders/{order_id}", response_model=PaymentOrderResponse)
def get_payment_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get payment order by ID
    """
    service = PaymentService(db)
    
    order = service.get_payment_order(
        order_id=order_id,
        user_id=current_user.id
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    return order


@router.post("/wechat/jsapi", response_model=WechatPayResponse)
def create_wechat_jsapi_payment(
    request: WechatPayRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create WeChat JSAPI payment
    
    Returns parameters for WeChat JSAPI payment.
    """
    wechat_pay = _get_wechat_pay_service()
    
    payment_service = PaymentService(db, wechat_pay)
    
    if request.order_id:
        order = payment_service.get_payment_order(
            order_id=request.order_id,
            user_id=current_user.id
        )
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
    else:
        order = payment_service.create_payment_order(
            user_id=current_user.id,
            amount=request.amount,
            subject=request.subject,
            payment_method=PaymentMethod.WECHAT,
            body=request.body
        )
    
    try:
        result = wechat_pay.create_jsapi_order(
            out_trade_no=order.order_no,
            amount=order.amount,
            subject=order.subject,
            openid=current_user.wechat_openid,
            body=order.body,
            notify_url="https://your-domain.com/api/v1/payment/wechat/notify"
        )
        
        order.prepay_id = result["prepay_id"]
        db.commit()
        
        return WechatPayResponse(
            order_id=order.id,
            order_no=order.order_no,
            **result
        )
        
    except Exception as e:
        logger.error(f"WeChat JSAPI payment failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/wechat/native", response_model=WechatPayResponse)
def create_wechat_native_payment(
    request: WechatPayRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create WeChat Native payment (QR code)
    
    Returns code_url for QR code generation.
    """
    wechat_pay = _get_wechat_pay_service()
    
    payment_service = PaymentService(db, wechat_pay)
    
    if request.order_id:
        order = payment_service.get_payment_order(
            order_id=request.order_id,
            user_id=current_user.id
        )
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
    else:
        order = payment_service.create_payment_order(
            user_id=current_user.id,
            amount=request.amount,
            subject=request.subject,
            payment_method=PaymentMethod.WECHAT,
            body=request.body
        )
    
    try:
        result = wechat_pay.create_native_order(
            out_trade_no=order.order_no,
            amount=order.amount,
            subject=order.subject,
            body=order.body,
            notify_url="https://your-domain.com/api/v1/payment/wechat/notify"
        )
        
        order.prepay_id = result["prepay_id"]
        db.commit()
        
        return WechatPayResponse(
            order_id=order.id,
            order_no=order.order_no,
            code_url=result["code_url"],
            **result
        )
        
    except Exception as e:
        logger.error(f"WeChat Native payment failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/wechat/notify")
def wechat_payment_notify(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    WeChat Pay notification callback
    
    WeChat will POST payment results to this endpoint.
    """
    notify_data = request.json()
    
    wechat_pay = _get_wechat_pay_service()
    payment_service = PaymentService(db, wechat_pay)
    
    try:
        success, message = payment_service.handle_wechat_notify(notify_data)
        
        if success:
            return {"code": "SUCCESS", "message": message}
        else:
            logger.error(f"WeChat notify failed: {message}")
            return {"code": "FAIL", "message": message}
            
    except Exception as e:
        logger.error(f"WeChat notify error: {e}")
        return {"code": "FAIL", "message": str(e)}


@router.get("/balance", response_model=UserBalanceResponse)
def get_user_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's balance
    """
    service = PaymentService(db)
    balance = service.get_or_create_user_balance(current_user.id)
    
    return balance


@router.get("/balance/transactions", response_model=List[BalanceTransactionResponse])
def list_balance_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List balance transactions for current user
    """
    from sqlalchemy import select

    from app.models.payment import BalanceTransaction
    
    query = (
        select(BalanceTransaction)
        .where(BalanceTransaction.user_id == current_user.id)
        .order_by(BalanceTransaction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    
    result = db.execute(query)
    transactions = list(result.scalars().all())
    
    return [BalanceTransactionResponse.model_validate(t) for t in transactions]


@router.post("/balance/recharge")
def recharge_balance(
    amount: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Recharge balance (for testing)
    
    This is a test endpoint. In production, use WeChat Pay.
    """
    if amount <= 0:
        raise HTTPException(status_code=400, detail="充值金额必须大于 0")
    
    service = PaymentService(db)
    
    order = service.create_payment_order(
        user_id=current_user.id,
        amount=amount,
        subject="测试充值",
        payment_method=PaymentMethod.WECHAT
    )
    
    service.update_payment_status(order, PaymentStatus.SUCCESS)
    service.add_balance(
        user_id=current_user.id,
        amount=amount,
        transaction_type="recharge",
        description="测试充值",
        payment_order_id=order.id
    )
    
    return {
        "message": "充值成功",
        "order_no": order.order_no,
        "amount": amount
    }


def _get_wechat_pay_service() -> WeChatPayService:
    """
    Get WeChat Pay service instance
    
    In production, load config from environment or database.
    """
    import os
    
    return WeChatPayService(
        appid=os.getenv("WECHAT_APPID", "wx_test_appid"),
        mchid=os.getenv("WECHAT_MCHID", "1234567890"),
        api_key=os.getenv("WECHAT_API_KEY", "test_api_key"),
        private_key=os.getenv("WECHAT_PRIVATE_KEY", ""),
        serial_no=os.getenv("WECHAT_SERIAL_NO", "test_serial_no"),
        sandbox=True
    )
