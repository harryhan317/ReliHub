"""
Comprehensive tests for Ledger Service module.

Tests:
1. Point Ledger operations
   - Create ledger entries
   - Get user balance
   - Ledger history with pagination
   - Attempted transaction tracking

2. Asset Package operations
   - Create packages
   - Purchase packages
   - Use quota
   - Expiration handling
"""

import uuid
from datetime import datetime, timedelta

import pytest

from app.models.ledger import (
    AssetPackage,
    AttemptedTransaction,
    OrderType,
    PointLedger,
    PointType,
    UserPurchasedAsset,
)
from app.models.users import User
from app.services.ledger_service import AssetPackageService, PointLedgerService


class TestPointLedgerService:
    """Test PointLedgerService functionality"""
    
    @pytest.fixture
    def ledger_service(self, db_session):
        """Create PointLedgerService instance"""
        return PointLedgerService(db_session)
    
    @pytest.fixture
    def test_user(self, db_session):
        """Create test user"""
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138000",
            nickname="test_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_create_ledger_entry_gold_bean(self, ledger_service, test_user):
        """Test creating a gold bean ledger entry"""
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=100,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.SYSTEM_GIFT,
            balance_after=100,
            description="Initial reward",
        )
        
        assert entry.id is not None
        assert entry.user_id == test_user.id
        assert entry.amount == 100
        assert entry.point_type == PointType.GOLD_BEAN
        assert entry.order_type == OrderType.SYSTEM_GIFT
        assert entry.balance_after == 100
        assert entry.description == "Initial reward"
    
    def test_create_ledger_entry_bonus_bean(self, ledger_service, test_user):
        """Test creating a bonus bean ledger entry"""
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=50,
            point_type=PointType.BONUS_BEAN,
            order_type=OrderType.SYSTEM_GIFT,
            balance_after=50,
            description="Bonus reward",
        )
        
        assert entry.point_type == PointType.BONUS_BEAN
        assert entry.amount == 50
    
    def test_create_ledger_entry_with_related_id(self, ledger_service, test_user):
        """Test creating ledger entry with related ID"""
        related_id = str(uuid.uuid4())
        
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=30,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.BOUNTY_LOCK,
            balance_after=70,
            related_id=related_id,
            description="Bounty lock",
        )
        
        assert entry.related_id == related_id
    
    def test_create_ledger_entry_with_dist_ratio(self, ledger_service, test_user):
        """Test creating ledger entry with distribution ratio"""
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=100,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.RECHARGE,
            balance_after=200,
            dist_ratio=0.7,
        )
        
        assert entry.dist_ratio == 0.7
    
    def test_create_ledger_entry_with_transaction_uuid(self, ledger_service, test_user):
        """Test creating ledger entry with custom transaction UUID"""
        tx_uuid = str(uuid.uuid4())
        
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=50,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.SYSTEM_GIFT,
            balance_after=50,
            transaction_uuid=tx_uuid,
        )
        
        assert entry.transaction_uuid == tx_uuid
    
    def test_get_user_balance_empty(self, ledger_service, test_user):
        """Test getting balance for user with no transactions"""
        gold, bonus = ledger_service.get_user_balance(test_user.id)
        
        assert gold == 0
        assert bonus == 0
    
    def test_get_user_balance_gold_only(self, ledger_service, test_user):
        """Test getting balance with only gold beans"""
        ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=100,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.SYSTEM_GIFT,
            balance_after=100,
        )
        
        gold, bonus = ledger_service.get_user_balance(test_user.id)
        
        assert gold == 100
        assert bonus == 0
    
    def test_get_user_balance_bonus_only(self, ledger_service, test_user):
        """Test getting balance with only bonus beans"""
        ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=50,
            point_type=PointType.BONUS_BEAN,
            order_type=OrderType.SYSTEM_GIFT,
            balance_after=50,
        )
        
        gold, bonus = ledger_service.get_user_balance(test_user.id)
        
        assert gold == 0
        assert bonus == 50
    
    def test_get_user_balance_both_types(self, ledger_service, test_user):
        """Test getting balance with both bean types"""
        ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=100,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.SYSTEM_GIFT,
            balance_after=100,
        )
        
        ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=50,
            point_type=PointType.BONUS_BEAN,
            order_type=OrderType.SYSTEM_GIFT,
            balance_after=50,
        )
        
        gold, bonus = ledger_service.get_user_balance(test_user.id)
        
        assert gold == 100
        assert bonus == 50
    
    def test_get_user_balance_multiple_entries(self, ledger_service, test_user):
        """Test that balance returns most recent entry by point type"""
        ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=100,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.SYSTEM_GIFT,
            balance_after=100,
        )
        
        ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=50,
            point_type=PointType.BONUS_BEAN,
            order_type=OrderType.SYSTEM_GIFT,
            balance_after=50,
        )
        
        gold, bonus = ledger_service.get_user_balance(test_user.id)
        
        assert gold == 100
        assert bonus == 50
    
    def test_get_ledger_history_empty(self, ledger_service, test_user):
        """Test getting history for user with no transactions"""
        ledgers, total = ledger_service.get_ledger_history(test_user.id)
        
        assert total == 0
        assert ledgers == []
    
    def test_get_ledger_history_pagination(self, ledger_service, test_user):
        """Test ledger history pagination"""
        for i in range(25):
            ledger_service.create_ledger_entry(
                user_id=test_user.id,
                amount=10,
                point_type=PointType.GOLD_BEAN,
                order_type=OrderType.SYSTEM_GIFT,
                balance_after=10 * (i + 1),
            )
        
        ledgers_page1, total1 = ledger_service.get_ledger_history(test_user.id, page=1, page_size=10)
        ledgers_page2, total2 = ledger_service.get_ledger_history(test_user.id, page=2, page_size=10)
        
        assert total1 == 25
        assert len(ledgers_page1) == 10
        assert total2 == 25
        assert len(ledgers_page2) == 10
    
    def test_record_attempted_transaction(self, ledger_service, test_user):
        """Test recording attempted transaction"""
        attempt = ledger_service.record_attempted_transaction(
            user_id=test_user.id,
            order_type=OrderType.DOWNLOAD,
            amount=1000,
            reason="Insufficient balance",
        )
        
        assert attempt.id is not None
        assert attempt.user_id == test_user.id
        assert attempt.order_type == OrderType.DOWNLOAD
        assert attempt.amount == 1000
        assert attempt.reason == "Insufficient balance"
    
    def test_get_recent_attempts(self, ledger_service, test_user):
        """Test getting recent attempted transactions"""
        ledger_service.record_attempted_transaction(
            user_id=test_user.id,
            order_type=OrderType.DOWNLOAD,
            amount=100,
            reason="Test 1",
        )
        
        ledger_service.record_attempted_transaction(
            user_id=test_user.id,
            order_type=OrderType.BOUNTY_LOCK,
            amount=200,
            reason="Test 2",
        )
        
        attempts = ledger_service.get_recent_attempts(test_user.id, minutes=5)
        
        assert len(attempts) == 2
    
    def test_get_recent_attempts_time_filter(self, ledger_service, test_user):
        """Test that old attempts are filtered out"""
        old_attempt = AttemptedTransaction(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            order_type=OrderType.DOWNLOAD,
            amount=100,
            reason="Old attempt",
        )
        old_attempt.created_at = datetime.utcnow() - timedelta(minutes=10)
        ledger_service.db.add(old_attempt)
        ledger_service.db.commit()
        
        ledger_service.record_attempted_transaction(
            user_id=test_user.id,
            order_type=OrderType.BOUNTY_LOCK,
            amount=200,
            reason="New attempt",
        )
        
        attempts = ledger_service.get_recent_attempts(test_user.id, minutes=5)
        
        assert len(attempts) == 1
        assert attempts[0].reason == "New attempt"


class TestAssetPackageService:
    """Test AssetPackageService functionality"""
    
    @pytest.fixture
    def package_service(self, db_session):
        """Create AssetPackageService instance"""
        return AssetPackageService(db_session)
    
    @pytest.fixture
    def test_user(self, db_session):
        """Create test user"""
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138001",
            nickname="package_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_create_package(self, package_service):
        """Test creating an asset package"""
        package = package_service.create_package(
            name="Basic Package",
            price_beans=100,
            quota_mb=1024,
            discount_rate=0.9,
        )
        
        assert package.id is not None
        assert package.name == "Basic Package"
        assert package.price_beans == 100
        assert package.quota_mb == 1024
        assert package.discount_rate == 0.9
    
    def test_get_package(self, package_service):
        """Test getting a package by ID"""
        created = package_service.create_package(
            name="Test Package",
            price_beans=50,
            quota_mb=512,
            discount_rate=1.0,
        )
        
        retrieved = package_service.get_package(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Package"
    
    def test_get_package_not_found(self, package_service):
        """Test getting non-existent package"""
        result = package_service.get_package("non-existent-id")
        
        assert result is None
    
    def test_list_packages(self, package_service):
        """Test listing all packages"""
        package_service.create_package("Package A", 100, 1024, 0.9)
        package_service.create_package("Package B", 50, 512, 1.0)
        package_service.create_package("Package C", 200, 2048, 0.8)
        
        packages = package_service.list_packages()
        
        assert len(packages) == 3
        assert packages[0].price_beans <= packages[1].price_beans
    
    def test_purchase_package(self, package_service, test_user):
        """Test purchasing a package"""
        package = package_service.create_package(
            name="Test Package",
            price_beans=100,
            quota_mb=1024,
            discount_rate=0.9,
        )
        
        expires_at = datetime.utcnow() + timedelta(days=30)
        purchased = package_service.purchase_package(
            user_id=test_user.id,
            package_id=package.id,
            expires_at=expires_at,
        )
        
        assert purchased.id is not None
        assert purchased.user_id == test_user.id
        assert purchased.package_id == package.id
        assert purchased.is_active == True
    
    def test_get_user_assets_empty(self, package_service, test_user):
        """Test getting assets for user with no purchases"""
        assets = package_service.get_user_assets(test_user.id)
        
        assert assets == []
    
    def test_get_user_assets(self, package_service, test_user):
        """Test getting user's purchased assets"""
        package = package_service.create_package(
            name="Test Package",
            price_beans=100,
            quota_mb=1024,
            discount_rate=0.9,
        )
        
        expires_at = datetime.utcnow() + timedelta(days=30)
        purchased = package_service.purchase_package(
            user_id=test_user.id,
            package_id=package.id,
            expires_at=expires_at,
        )
        purchased.remaining_mb = 1024
        package_service.db.commit()
        
        assets = package_service.get_user_assets(test_user.id)
        
        assert len(assets) == 1
        assert assets[0].remaining_mb == 1024
    
    def test_get_user_assets_excludes_expired(self, package_service, test_user):
        """Test that expired assets are excluded"""
        package = package_service.create_package(
            name="Test Package",
            price_beans=100,
            quota_mb=1024,
            discount_rate=0.9,
        )
        
        expired_at = datetime.utcnow() - timedelta(days=1)
        purchased = package_service.purchase_package(
            user_id=test_user.id,
            package_id=package.id,
            expires_at=expired_at,
        )
        purchased.remaining_mb = 1024
        package_service.db.commit()
        
        assets = package_service.get_user_assets(test_user.id)
        
        assert len(assets) == 0
    
    def test_get_user_assets_excludes_inactive(self, package_service, test_user):
        """Test that inactive assets are excluded"""
        package = package_service.create_package(
            name="Test Package",
            price_beans=100,
            quota_mb=1024,
            discount_rate=0.9,
        )
        
        expires_at = datetime.utcnow() + timedelta(days=30)
        purchased = package_service.purchase_package(
            user_id=test_user.id,
            package_id=package.id,
            expires_at=expires_at,
        )
        purchased.remaining_mb = 1024
        purchased.is_active = False
        package_service.db.commit()
        
        assets = package_service.get_user_assets(test_user.id)
        
        assert len(assets) == 0
    
    def test_use_asset_quota_success(self, package_service, test_user):
        """Test using asset quota successfully"""
        package = package_service.create_package(
            name="Test Package",
            price_beans=100,
            quota_mb=1024,
            discount_rate=0.9,
        )
        
        expires_at = datetime.utcnow() + timedelta(days=30)
        purchased = package_service.purchase_package(
            user_id=test_user.id,
            package_id=package.id,
            expires_at=expires_at,
        )
        purchased.remaining_mb = 1024
        package_service.db.commit()
        
        result = package_service.use_asset_quota(test_user.id, 512)
        
        assert result == True
        package_service.db.refresh(purchased)
        assert purchased.remaining_mb == 512
        assert purchased.used_mb == 512
    
    def test_use_asset_quota_insufficient(self, package_service, test_user):
        """Test using more quota than available"""
        package = package_service.create_package(
            name="Test Package",
            price_beans=100,
            quota_mb=1024,
            discount_rate=0.9,
        )
        
        expires_at = datetime.utcnow() + timedelta(days=30)
        purchased = package_service.purchase_package(
            user_id=test_user.id,
            package_id=package.id,
            expires_at=expires_at,
        )
        purchased.remaining_mb = 100
        package_service.db.commit()
        
        result = package_service.use_asset_quota(test_user.id, 200)
        
        assert result == False
    
    def test_use_asset_quota_no_assets(self, package_service, test_user):
        """Test using quota when user has no assets"""
        result = package_service.use_asset_quota(test_user.id, 100)
        
        assert result == False
    
    def test_use_asset_quota_multiple_packages(self, package_service, test_user):
        """Test using quota across multiple packages"""
        package1 = package_service.create_package("Package 1", 100, 500, 1.0)
        package2 = package_service.create_package("Package 2", 200, 1000, 0.9)
        
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        purchased1 = package_service.purchase_package(
            user_id=test_user.id,
            package_id=package1.id,
            expires_at=expires_at - timedelta(days=10),
        )
        purchased1.remaining_mb = 500
        
        purchased2 = package_service.purchase_package(
            user_id=test_user.id,
            package_id=package2.id,
            expires_at=expires_at,
        )
        purchased2.remaining_mb = 1000
        
        package_service.db.commit()
        
        result = package_service.use_asset_quota(test_user.id, 700)
        
        assert result == True
        package_service.db.refresh(purchased1)
        package_service.db.refresh(purchased2)
        assert purchased1.remaining_mb == 0
        assert purchased1.used_mb == 500
        assert purchased2.remaining_mb == 800
        assert purchased2.used_mb == 200
    
    def test_get_total_user_quota(self, package_service, test_user):
        """Test getting total user quota"""
        package1 = package_service.create_package("Package 1", 100, 500, 1.0)
        package2 = package_service.create_package("Package 2", 200, 1000, 0.9)
        
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        purchased1 = package_service.purchase_package(
            user_id=test_user.id,
            package_id=package1.id,
            expires_at=expires_at,
        )
        purchased1.remaining_mb = 500
        
        purchased2 = package_service.purchase_package(
            user_id=test_user.id,
            package_id=package2.id,
            expires_at=expires_at,
        )
        purchased2.remaining_mb = 1000
        
        package_service.db.commit()
        
        total = package_service.get_total_user_quota(test_user.id)
        
        assert total == 1500


class TestLedgerOrderTypes:
    """Test different order types in ledger"""
    
    @pytest.fixture
    def ledger_service(self, db_session):
        return PointLedgerService(db_session)
    
    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138002",
            nickname="order_type_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_download_order_type(self, ledger_service, test_user):
        """Test DOWNLOAD order type"""
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=-10,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.DOWNLOAD,
            balance_after=90,
        )
        assert entry.order_type == OrderType.DOWNLOAD
    
    def test_recharge_order_type(self, ledger_service, test_user):
        """Test RECHARGE order type"""
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=100,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.RECHARGE,
            balance_after=100,
        )
        assert entry.order_type == OrderType.RECHARGE
    
    def test_bounty_lock_order_type(self, ledger_service, test_user):
        """Test BOUNTY_LOCK order type"""
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=-50,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.BOUNTY_LOCK,
            balance_after=50,
        )
        assert entry.order_type == OrderType.BOUNTY_LOCK
    
    def test_content_topic_order_type(self, ledger_service, test_user):
        """Test CONTENT_TOPIC order type"""
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=10,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.CONTENT_TOPIC,
            balance_after=60,
        )
        assert entry.order_type == OrderType.CONTENT_TOPIC
    
    def test_content_post_order_type(self, ledger_service, test_user):
        """Test CONTENT_POST order type"""
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=5,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.CONTENT_POST,
            balance_after=65,
        )
        assert entry.order_type == OrderType.CONTENT_POST
    
    def test_sign_in_order_type(self, ledger_service, test_user):
        """Test SIGN_IN order type"""
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=5,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.SIGN_IN,
            balance_after=70,
        )
        assert entry.order_type == OrderType.SIGN_IN
    
    def test_invite_reward_order_type(self, ledger_service, test_user):
        """Test INVITE_REWARD order type"""
        entry = ledger_service.create_ledger_entry(
            user_id=test_user.id,
            amount=20,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.INVITE_REWARD,
            balance_after=90,
        )
        assert entry.order_type == OrderType.INVITE_REWARD
