"""
Tests for Payment module

Uses PostgreSQL test database via conftest.py fixtures.
"""

import uuid
from unittest.mock import MagicMock

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.security import generate_phone_blind_index, hash_password
from app.models.payment import PaymentMethod, PaymentStatus
from app.models.users import User
from app.services.payment_service import PaymentService
from app.services.wechat_pay import WeChatPayService


def generate_test_rsa_key():
    """Generate a test RSA private key in PEM format"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    return private_key_pem


@pytest.fixture
def test_user(db_session):
    """Create a test user for payment tests"""
    phone = "13900139000"
    user = User(
        id=str(uuid.uuid4()),
        phone=phone,
        phone_blind_index=generate_phone_blind_index(phone),
        nickname="payment_user",
        password_hash=hash_password("TestPassword123!"),
        status="ACTIVE",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestWeChatPayService:
    """Test WeChat Pay Service"""
    
    def test_init(self):
        """Test WeChatPayService initialization"""
        private_key_pem = generate_test_rsa_key()
        
        service = WeChatPayService(
            appid="wx_test",
            mchid="1234567890",
            api_key="test_key",
            private_key=private_key_pem,
            serial_no="test_serial",
            sandbox=True
        )
        
        assert service.appid == "wx_test"
        assert service.mchid == "1234567890"
        assert service.sandbox is True
    
    def test_create_jsapi_order_mock(self):
        """Test creating JSAPI order (mocked)"""
        private_key_pem = generate_test_rsa_key()
        
        service = WeChatPayService(
            appid="wx_test",
            mchid="1234567890",
            api_key="test_key",
            private_key=private_key_pem,
            serial_no="test_serial",
            sandbox=True
        )
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "prepay_id": "wx_test_prepay_id"
        }
        
        service.client.post = MagicMock(return_value=mock_response)
        
        result = service.create_jsapi_order(
            out_trade_no="test_order_001",
            amount=100.0,
            subject="Test Product",
            openid="user_openid"
        )
        
        assert "prepay_id" in result
        assert result["prepay_id"] == "wx_test_prepay_id"


class TestPaymentService:
    """Test Payment Service"""
    
    def test_create_payment_order(self, db_session, test_user):
        """Test creating payment order"""
        service = PaymentService(db_session)
        
        order = service.create_payment_order(
            user_id=test_user.id,
            amount=100.0,
            subject="Test Order",
            payment_method=PaymentMethod.WECHAT
        )
        
        assert order is not None
        assert order.amount == 100.0
        assert order.payment_status == PaymentStatus.PENDING
        assert order.order_no is not None
        assert len(order.order_no) > 10
    
    def test_get_payment_order(self, db_session, test_user):
        """Test getting payment order"""
        service = PaymentService(db_session)
        
        order = service.create_payment_order(
            user_id=test_user.id,
            amount=100.0,
            subject="Test Order"
        )
        
        retrieved = service.get_payment_order(order_id=order.id)
        
        assert retrieved is not None
        assert retrieved.id == order.id
        assert retrieved.order_no == order.order_no
    
    def test_update_payment_status(self, db_session, test_user):
        """Test updating payment status"""
        service = PaymentService(db_session)
        
        order = service.create_payment_order(
            user_id=test_user.id,
            amount=100.0,
            subject="Test Order"
        )
        
        updated = service.update_payment_status(
            order,
            PaymentStatus.SUCCESS,
            "wechat_transaction_001"
        )
        
        assert updated.payment_status == PaymentStatus.SUCCESS
        assert updated.transaction_id == "wechat_transaction_001"
        assert updated.paid_at is not None
    
    def test_get_or_create_user_balance(self, db_session, test_user):
        """Test getting or creating user balance"""
        service = PaymentService(db_session)
        
        balance = service.get_or_create_user_balance(test_user.id)
        
        assert balance is not None
        assert balance.user_id == test_user.id
        assert balance.balance == 0.0
    
    def test_add_balance(self, db_session, test_user):
        """Test adding balance"""
        service = PaymentService(db_session)
        
        balance = service.add_balance(
            user_id=test_user.id,
            amount=100.0,
            transaction_type="recharge",
            description="Test recharge"
        )
        
        assert balance.balance == 100.0
        assert balance.total_recharged == 100.0
    
    def test_deduct_balance(self, db_session, test_user):
        """Test deducting balance"""
        service = PaymentService(db_session)
        
        service.add_balance(
            user_id=test_user.id,
            amount=100.0,
            transaction_type="recharge"
        )
        
        balance = service.deduct_balance(
            user_id=test_user.id,
            amount=50.0,
            transaction_type="consume",
            description="Test consume"
        )
        
        assert balance.balance == 50.0
        assert balance.total_consumed == 50.0
    
    def test_deduct_insufficient_balance(self, db_session, test_user):
        """Test deducting with insufficient balance"""
        service = PaymentService(db_session)
        
        with pytest.raises(ValueError) as exc_info:
            service.deduct_balance(
                user_id=test_user.id,
                amount=100.0,
                transaction_type="consume"
            )
        
        assert "Insufficient balance" in str(exc_info.value)
    
    def test_list_payment_orders(self, db_session, test_user):
        """Test listing payment orders"""
        service = PaymentService(db_session)
        
        for i in range(5):
            service.create_payment_order(
                user_id=test_user.id,
                amount=100.0 + i,
                subject=f"Test Order {i}"
            )
        
        orders, total = service.list_payment_orders(
            user_id=test_user.id,
            page=1,
            page_size=10
        )
        
        assert len(orders) == 5
        assert total == 5


class TestOrderNumberGeneration:
    """Test order number generation"""
    
    def test_order_no_format(self, db_session, test_user):
        """Test order number format"""
        service = PaymentService(db_session)
        order = service.create_payment_order(
            user_id=test_user.id,
            amount=100.0,
            subject="Test"
        )
        
        assert len(order.order_no) >= 22
        assert order.order_no[:14].isdigit()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
