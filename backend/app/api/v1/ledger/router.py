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
    AssetPackageListResponse,
    AssetPackageResponse,
    PointLedgerListResponse,
    PointLedgerResponse,
    RechargeRequest,
    UserBalanceResponse,
    UserPurchasedAssetResponse,
)
from app.services.interaction_service import CheckinService
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


@router.get("/ledger", response_model=PointLedgerListResponse)
def get_ledger(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Get user's point ledger"""
    service = PointLedgerService(db)
    ledgers, total = service.get_user_ledger(current_user.id, page, page_size)
    
    return PointLedgerListResponse(
        items=ledgers,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/ledger/{ledger_id}", response_model=PointLedgerResponse)
def get_ledger_detail(
    ledger_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ledger detail"""
    service = PointLedgerService(db)
    ledger = service.get_ledger_detail(ledger_id, current_user.id)
    if not ledger:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return PointLedgerResponse(**ledger.__dict__)


@router.get("/packages", response_model=AssetPackageListResponse)
def get_packages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get available asset packages"""
    service = AssetPackageService(db)
    packages = service.get_available_packages()
    
    return AssetPackageListResponse(
        items=packages,
        total=len(packages),
    )


@router.post("/recharge")
def recharge(
    request: RechargeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recharge beans"""
    service = PointLedgerService(db)
    result = service.recharge(current_user.id, request.package_id)
    
    return result


@router.post("/checkin")
def checkin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Daily check-in.
    
    This endpoint:
    1. Checks if user already checked in today
    2. If not, awards bonus beans (5 per day)
    3. Records ledger entry with SIGN_IN order type
    """
    service = CheckinService(db)
    return service.checkin(current_user.id)


@router.get("/checkin/status")
def get_checkin_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's check-in status"""
    service = CheckinService(db)
    return service.get_checkin_status(current_user.id)


@router.get("/admin/ledger")
def admin_get_ledger(
    db: Session = Depends(get_db),
    admin_user: AdminUser = Depends(require_admin),
    user_id: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Admin get ledger (all users)"""
    service = PointLedgerService(db)
    ledgers, total = service.get_ledger_admin(user_id, page, page_size)
    
    return PointLedgerListResponse(
        items=ledgers,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/admin/purchased")
def admin_get_purchased_assets(
    db: Session = Depends(get_db),
    admin_user: AdminUser = Depends(require_admin),
    user_id: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Admin get purchased assets"""
    service = AssetPackageService(db)
    assets, total = service.get_purchased_assets_admin(user_id, page, page_size)
    
    return UserPurchasedAssetResponse(
        items=assets,
        total=total,
        page=page,
        page_size=page_size,
    )