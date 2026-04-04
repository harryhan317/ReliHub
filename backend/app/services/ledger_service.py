"""
Service layer for Ledger/Economy module.
"""
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
import uuid

from app.models.ledger import (
    PointLedger,
    AttemptedTransaction,
    AssetPackage,
    UserPurchasedAsset,
    PointType,
    OrderType,
)
from app.schemas.ledger import RechargeRequest, AssetPackagePurchaseRequest


class PointLedgerService:
    """Service class for Point Ledger management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_ledger_entry(
        self,
        user_id: str,
        amount: int,
        point_type: PointType,
        order_type: OrderType,
        balance_after: int,
        related_id: Optional[str] = None,
        description: Optional[str] = None,
        dist_ratio: Optional[float] = None,
        transaction_uuid: Optional[str] = None
    ) -> PointLedger:
        """Create a new ledger entry"""
        if transaction_uuid is None:
            transaction_uuid = str(uuid.uuid4())
        
        entry = PointLedger(
            id=str(uuid.uuid4()),
            transaction_uuid=transaction_uuid,
            user_id=user_id,
            amount=amount,
            point_type=point_type,
            dist_ratio=dist_ratio,
            order_type=order_type,
            balance_after=balance_after,
            related_id=related_id,
            description=description,
        )
        
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def get_user_balance(
        self,
        user_id: str
    ) -> Tuple[int, int]:
        """Get user's current balance (gold beans, bonus beans)"""
        query = select(PointLedger).where(
            PointLedger.user_id == user_id
        ).order_by(PointLedger.created_at.desc())
        
        result = await self.db.execute(query)
        ledgers = result.scalars().all()
        
        gold_beans = 0
        bonus_beans = 0
        
        # Calculate balance from ledger (last entry for each type)
        for ledger in ledgers:
            if ledger.point_type == PointType.GOLD_BEAN:
                if gold_beans == 0:
                    gold_beans = ledger.balance_after
            elif ledger.point_type == PointType.BONUS_BEAN:
                if bonus_beans == 0:
                    bonus_beans = ledger.balance_after
            
            if gold_beans > 0 and bonus_beans > 0:
                break
        
        return gold_beans, bonus_beans

    async def get_ledger_history(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[PointLedger], int]:
        """Get user's ledger history with pagination"""
        # Get total count
        count_query = select(func.count()).where(
            PointLedger.user_id == user_id
        )
        total = (await self.db.execute(count_query)).scalar()
        
        # Get paginated results
        query = (
            select(PointLedger)
            .where(PointLedger.user_id == user_id)
            .order_by(PointLedger.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await self.db.execute(query)
        ledgers = result.scalars().all()
        
        return list(ledgers), total

    async def record_attempted_transaction(
        self,
        user_id: str,
        order_type: OrderType,
        amount: int,
        reason: str
    ) -> AttemptedTransaction:
        """Record an attempted transaction (for anti-fraud)"""
        attempt = AttemptedTransaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            order_type=order_type,
            amount=amount,
            reason=reason,
        )
        
        self.db.add(attempt)
        await self.db.commit()
        await self.db.refresh(attempt)
        return attempt

    async def get_recent_attempts(
        self,
        user_id: str,
        minutes: int = 5
    ) -> List[AttemptedTransaction]:
        """Get recent attempted transactions"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        query = select(AttemptedTransaction).where(
            AttemptedTransaction.user_id == user_id,
            AttemptedTransaction.created_at >= cutoff_time
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


class AssetPackageService:
    """Service class for Asset Package management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_package(
        self,
        name: str,
        price_beans: int,
        quota_mb: int,
        discount_rate: float
    ) -> AssetPackage:
        """Create a new asset package"""
        package = AssetPackage(
            id=str(uuid.uuid4()),
            name=name,
            price_beans=price_beans,
            quota_mb=quota_mb,
            discount_rate=discount_rate,
        )
        
        self.db.add(package)
        await self.db.commit()
        await self.db.refresh(package)
        return package

    async def get_package(
        self,
        package_id: str
    ) -> Optional[AssetPackage]:
        """Get a package by ID"""
        query = select(AssetPackage).where(
            AssetPackage.id == package_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_packages(self) -> List[AssetPackage]:
        """List all available packages"""
        query = select(AssetPackage).order_by(AssetPackage.price_beans)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def purchase_package(
        self,
        user_id: str,
        package_id: str,
        expires_at: datetime
    ) -> UserPurchasedAsset:
        """Purchase an asset package"""
        purchased = UserPurchasedAsset(
            id=str(uuid.uuid4()),
            user_id=user_id,
            package_id=package_id,
            remaining_mb=0,  # Will be set when package is retrieved
            used_mb=0,
            expires_at=expires_at,
            is_active=True,
        )
        
        self.db.add(purchased)
        await self.db.commit()
        await self.db.refresh(purchased)
        return purchased

    async def get_user_assets(
        self,
        user_id: str
    ) -> List[UserPurchasedAsset]:
        """Get user's purchased assets"""
        query = select(UserPurchasedAsset).where(
            UserPurchasedAsset.user_id == user_id,
            UserPurchasedAsset.is_active == True,
            UserPurchasedAsset.expires_at > datetime.utcnow()
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def use_asset_quota(
        self,
        user_id: str,
        mb_amount: int
    ) -> bool:
        """Use asset quota from user's purchased packages"""
        assets = await self.get_user_assets(user_id)
        
        if not assets:
            return False
        
        remaining = mb_amount
        for asset in sorted(assets, key=lambda x: x.expires_at):
            if asset.remaining_mb >= remaining:
                asset.remaining_mb -= remaining
                asset.used_mb += remaining
                remaining = 0
                break
            else:
                remaining -= asset.remaining_mb
                asset.used_mb += asset.remaining_mb
                asset.remaining_mb = 0
        
        if remaining > 0:
            return False  # Not enough quota
        
        await self.db.commit()
        return True

    async def get_total_user_quota(
        self,
        user_id: str
    ) -> int:
        """Get user's total remaining quota"""
        assets = await self.get_user_assets(user_id)
        return sum(asset.remaining_mb for asset in assets)
