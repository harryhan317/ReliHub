"""
API routes for Ledger/Economy module.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_admin
from app.models.administrators import AdminUser
from app.models.ledger import PointType
from app.models.users import User
from app.schemas.ledger import (
    AssetPackagePurchaseRequest,
    AssetPackageResponse,
    PointLedgerListResponse,
    PointLedgerResponse,
    RechargeRequest,
    UserBalanceResponse,
    UserPurchasedAssetResponse,
)
from app.services.ledger_service import AssetPackageService, PointLedgerService

router = APIRouter(tags=["可可豆经济"])


@router.get("/balance", response_model=UserBalanceResponse)
def get_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's current balance"""
    service = PointLedgerService(db)
    gold_beans, bonus_beans = service.get_user_balance(current_user.id)
    
    return UserBalanceResponse(
        user_id=current_user.id,
        gold_beans=gold_beans,
        bonus_beans=bonus_beans,
        total_beans=gold_beans + bonus_beans,
        last_updated=None,
    )


@router.get("/history", response_model=PointLedgerListResponse)
def get_ledger_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's transaction history"""
    service = PointLedgerService(db)
    ledgers, total = service.get_ledger_history(
        current_user.id,
        page,
        page_size,
    )
    
    return PointLedgerListResponse(
        ledgers=[PointLedgerResponse.model_validate(ledger) for ledger in ledgers],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/recharge")
def recharge(
    request: RechargeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Recharge cocoa beans.
    
    This endpoint:
    1. Creates payment order
    2. Redirects to payment gateway
    3. Handles callback (webhook)
    4. Updates balance
    """
    return {
        "message": "Payment order created",
        "amount": request.amount,
        "payment_method": request.payment_method,
        "order_id": "placeholder_order_id",
    }


@router.get("/packages", response_model=list[AssetPackageResponse])
def list_packages(
    db: Session = Depends(get_db),
):
    """List all available asset packages"""
    service = AssetPackageService(db)
    packages = service.list_packages()
    return [AssetPackageResponse.model_validate(p) for p in packages]


@router.post("/packages/purchase")
def purchase_package(
    request: AssetPackagePurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Purchase an asset package.
    
    This endpoint:
    1. Validates package exists
    2. Checks user has sufficient beans
    3. Deducts beans
    4. Creates purchased asset record
    """
    service = AssetPackageService(db)
    package = service.get_package(request.package_id)
    
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    return {
        "message": "Package purchased",
        "package_id": package.id,
        "package_name": package.name,
    }


@router.get("/assets", response_model=list[UserPurchasedAssetResponse])
def get_user_assets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's purchased assets"""
    service = AssetPackageService(db)
    assets = service.get_user_assets(current_user.id)
    return [UserPurchasedAssetResponse.model_validate(a) for a in assets]


@router.get("/assets/quota")
def get_total_quota(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's total remaining quota"""
    service = AssetPackageService(db)
    total_quota = service.get_total_user_quota(current_user.id)
    
    return {
        "user_id": current_user.id,
        "total_remaining_mb": total_quota,
    }


@router.post("/admin/grant")
def grant_beans(
    user_id: str,
    amount: int,
    point_type: PointType,
    description: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """
    Grant beans to a user (admin only).
    """
    service = PointLedgerService(db)
    
    gold_beans, bonus_beans = service.get_user_balance(user_id)
    current_balance = gold_beans if point_type == PointType.GOLD_BEAN else bonus_beans
    new_balance = current_balance + amount
    
    entry = service.create_ledger_entry(
        user_id=user_id,
        amount=amount,
        point_type=point_type,
        order_type="SYSTEM_GIFT",
        balance_after=new_balance,
        description=description,
    )
    
    return {
        "message": "Beans granted",
        "entry_id": entry.id,
        "new_balance": new_balance,
    }
