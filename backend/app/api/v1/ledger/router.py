"""
API routes for Ledger/Economy module.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.services.ledger_service import PointLedgerService, AssetPackageService
from app.schemas.ledger import (
    RechargeRequest,
    AssetPackagePurchaseRequest,
    PointLedgerResponse,
    PointLedgerListResponse,
    UserBalanceResponse,
    AssetPackageResponse,
    UserPurchasedAssetResponse,
)
from app.models.users import User
from app.models.ledger import PointType

router = APIRouter(prefix="/ledger", tags=["可可豆经济"])


# ── Balance & History Routes ─────────────────────────────────────────────────

@router.get("/balance", response_model=UserBalanceResponse)
async def get_balance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's current balance"""
    service = PointLedgerService(db)
    gold_beans, bonus_beans = await service.get_user_balance(current_user.user_uuid)
    
    return UserBalanceResponse(
        user_id=current_user.user_uuid,
        gold_beans=gold_beans,
        bonus_beans=bonus_beans,
        total_beans=gold_beans + bonus_beans,
        last_updated=None,  # TODO: Get from latest ledger entry
    )


@router.get("/history", response_model=PointLedgerListResponse)
async def get_ledger_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's transaction history"""
    service = PointLedgerService(db)
    ledgers, total = await service.get_ledger_history(
        current_user.user_uuid,
        page,
        page_size,
    )
    
    return PointLedgerListResponse(
        ledgers=[PointLedgerResponse.model_validate(l) for l in ledgers],
        total=total,
        page=page,
        page_size=page_size,
    )


# ── Recharge Routes ───────────────────────────────────────────────────────────

@router.post("/recharge")
async def recharge(
    request: RechargeRequest,
    db: AsyncSession = Depends(get_db),
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
    # TODO: Implement payment integration
    # For now, return placeholder
    return {
        "message": "Payment order created",
        "amount": request.amount,
        "payment_method": request.payment_method,
        "order_id": "placeholder_order_id",
    }


# ── Asset Package Routes ──────────────────────────────────────────────────────

@router.get("/packages", response_model=list[AssetPackageResponse])
async def list_packages(
    db: AsyncSession = Depends(get_db),
):
    """List all available asset packages"""
    service = AssetPackageService(db)
    packages = await service.list_packages()
    return [AssetPackageResponse.model_validate(p) for p in packages]


@router.post("/packages/purchase")
async def purchase_package(
    request: AssetPackagePurchaseRequest,
    db: AsyncSession = Depends(get_db),
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
    package = await service.get_package(request.package_id)
    
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    # TODO: Check user balance
    # TODO: Deduct beans
    # TODO: Create purchased asset
    
    return {
        "message": "Package purchased",
        "package_id": package.id,
        "package_name": package.name,
    }


@router.get("/assets", response_model=list[UserPurchasedAssetResponse])
async def get_user_assets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's purchased assets"""
    service = AssetPackageService(db)
    assets = await service.get_user_assets(current_user.user_uuid)
    return [UserPurchasedAssetResponse.model_validate(a) for a in assets]


@router.get("/assets/quota")
async def get_total_quota(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's total remaining quota"""
    service = AssetPackageService(db)
    total_quota = await service.get_total_user_quota(current_user.user_uuid)
    
    return {
        "user_id": current_user.user_uuid,
        "total_remaining_mb": total_quota,
    }


# ── Admin Routes (TODO: Add admin permission check) ───────────────────────────

@router.post("/admin/grant")
async def grant_beans(
    user_id: str,
    amount: int,
    point_type: PointType,
    description: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Grant beans to a user (admin only).
    
    TODO: Add admin permission check
    """
    service = PointLedgerService(db)
    
    # Get current balance
    gold_beans, bonus_beans = await service.get_user_balance(user_id)
    current_balance = gold_beans if point_type == PointType.GOLD_BEAN else bonus_beans
    new_balance = current_balance + amount
    
    # Create ledger entry
    entry = await service.create_ledger_entry(
        user_id=user_id,
        amount=amount,
        point_type=point_type,
        order_type="SYSTEM_GIFT",  # type: ignore
        balance_after=new_balance,
        description=description,
    )
    
    return {
        "message": "Beans granted",
        "entry_id": entry.id,
        "new_balance": new_balance,
    }
