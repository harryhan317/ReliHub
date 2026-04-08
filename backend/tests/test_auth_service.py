"""
Comprehensive tests for Auth Service module.

Tests:
1. Registration
   - Phone + SMS code registration
   - New user vs existing user
   - Terms agreement validation
   - Password setting

2. Password Login
   - Successful login
   - Wrong password handling
   - Account lockout after 5 failures
   - Lock duration

3. Token Management
   - Access token creation
   - Refresh token flow
   - Token blacklisting
   - Logout

4. WeChat Login (Mock)
   - Mock mode login
   - New user creation
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.core.exceptions import BusinessException, ErrorCode
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_phone_blind_index,
    hash_password,
    verify_password,
)
from app.models.users import User
from app.services import auth_service


class TestPhoneRegistration:
    """Test phone registration functionality"""
    
    def test_register_new_user(self, db_session, monkeypatch):
        """Test registering a new user"""
        def mock_verify_code(phone, code):
            return True
        
        monkeypatch.setattr("app.services.auth_service.verify_code", mock_verify_code)
        
        user, is_new = auth_service.register_by_phone(
            db=db_session,
            phone="13800138000",
            code="123456",
            password=None,
            agreed_to_terms=True,
            client_ip="127.0.0.1",
        )
        
        assert is_new == True
        assert user.phone == "13800138000"
        assert user.nickname == "新用户"
        assert user.rank == "新兵"
        assert user.reputation_points == 50
        assert user.gold_beans == 30
        assert user.status == "ACTIVE"
    
    def test_register_existing_user_login(self, db_session, monkeypatch):
        """Test that existing user is logged in"""
        def mock_verify_code(phone, code):
            return True
        
        monkeypatch.setattr("app.services.auth_service.verify_code", mock_verify_code)
        
        phone = "13800138001"
        existing_user = User(
            id=str(uuid.uuid4()),
            phone=phone,
            phone_blind_index=generate_phone_blind_index(phone),
            nickname="existing_user",
            status="ACTIVE",
        )
        db_session.add(existing_user)
        db_session.commit()
        
        user, is_new = auth_service.register_by_phone(
            db=db_session,
            phone="13800138001",
            code="123456",
            password=None,
            agreed_to_terms=True,
            client_ip="127.0.0.1",
        )
        
        assert is_new == False
        assert user.id == existing_user.id
        assert user.last_login_ip == "127.0.0.1"
    
    def test_register_without_terms_agreement(self, db_session, monkeypatch):
        """Test that registration fails without terms agreement"""
        def mock_verify_code(phone, code):
            return True
        
        monkeypatch.setattr("app.services.auth_service.verify_code", mock_verify_code)
        
        with pytest.raises(BusinessException) as exc_info:
            auth_service.register_by_phone(
                db=db_session,
                phone="13800138002",
                code="123456",
                password=None,
                agreed_to_terms=False,
            )
        
        assert exc_info.value.code == ErrorCode.AUTH_4005
    
    def test_register_with_password(self, db_session, monkeypatch):
        """Test registering with password"""
        def mock_verify_code(phone, code):
            return True
        
        monkeypatch.setattr("app.services.auth_service.verify_code", mock_verify_code)
        
        user, is_new = auth_service.register_by_phone(
            db=db_session,
            phone="13800138003",
            code="123456",
            password="SecurePassword123!",
            agreed_to_terms=True,
        )
        
        assert is_new == True
        assert user.password_hash is not None
        assert verify_password("SecurePassword123!", user.password_hash)


class TestPasswordLogin:
    """Test password login functionality"""
    
    @pytest.fixture
    def test_user(self, db_session):
        """Create test user with password"""
        phone = "13800138010"
        user = User(
            id=str(uuid.uuid4()),
            phone=phone,
            phone_blind_index=generate_phone_blind_index(phone),
            nickname="password_user",
            password_hash=hash_password("CorrectPassword123!"),
            status="ACTIVE",
            failed_login_attempts=0,
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_login_success(self, db_session, test_user):
        """Test successful password login"""
        user = auth_service.login_by_password(
            db=db_session,
            phone="13800138010",
            password="CorrectPassword123!",
            client_ip="127.0.0.1",
        )
        
        assert user.id == test_user.id
        assert user.last_login_ip == "127.0.0.1"
        assert user.failed_login_attempts == 0
    
    def test_login_wrong_password(self, db_session, test_user):
        """Test login with wrong password"""
        with pytest.raises(BusinessException) as exc_info:
            auth_service.login_by_password(
                db=db_session,
                phone="13800138010",
                password="WrongPassword123!",
            )
        
        assert exc_info.value.code == ErrorCode.AUTH_4003
        db_session.refresh(test_user)
        assert test_user.failed_login_attempts == 1
    
    def test_login_user_not_found(self, db_session):
        """Test login with non-existent user"""
        with pytest.raises(BusinessException) as exc_info:
            auth_service.login_by_password(
                db=db_session,
                phone="13999999999",
                password="AnyPassword123!",
            )
        
        assert exc_info.value.code == ErrorCode.AUTH_4003
    
    def test_login_locked_account(self, db_session):
        """Test login with locked account"""
        phone = "13800138011"
        lock_time = datetime.now(timezone.utc) + timedelta(minutes=15)
        user = User(
            id=str(uuid.uuid4()),
            phone=phone,
            phone_blind_index=generate_phone_blind_index(phone),
            nickname="locked_user",
            password_hash=hash_password("Password123!"),
            status="ACTIVE",
            lock_until_time=lock_time,
        )
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(BusinessException) as exc_info:
            auth_service.login_by_password(
                db=db_session,
                phone="13800138011",
                password="Password123!",
            )
        
        assert exc_info.value.code == ErrorCode.USER_4010
    
    def test_login_five_failures_lockout(self, db_session):
        """Test account lockout after 5 failed attempts"""
        phone = "13800138012"
        user = User(
            id=str(uuid.uuid4()),
            phone=phone,
            phone_blind_index=generate_phone_blind_index(phone),
            nickname="lockout_user",
            password_hash=hash_password("CorrectPassword123!"),
            status="ACTIVE",
            failed_login_attempts=4,
        )
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(BusinessException) as exc_info:
            auth_service.login_by_password(
                db=db_session,
                phone="13800138012",
                password="WrongPassword123!",
            )
        
        assert exc_info.value.code == ErrorCode.USER_4010
        db_session.refresh(user)
        assert user.lock_until_time is not None
    
    def test_login_no_password_set(self, db_session):
        """Test login when user has no password set"""
        phone = "13800138013"
        user = User(
            id=str(uuid.uuid4()),
            phone=phone,
            phone_blind_index=generate_phone_blind_index(phone),
            nickname="no_password_user",
            status="ACTIVE",
        )
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(BusinessException) as exc_info:
            auth_service.login_by_password(
                db=db_session,
                phone="13800138013",
                password="AnyPassword123!",
            )
        
        assert exc_info.value.code == ErrorCode.AUTH_4003


class TestTokenManagement:
    """Test token management functionality"""
    
    def test_create_access_token(self):
        """Test creating access token"""
        user_id = str(uuid.uuid4())
        token = create_access_token(user_id)
        
        assert token is not None
        
        payload = decode_token(token)
        assert payload is not None
        assert payload.get("sub") == user_id
        assert payload.get("type") == "access"
    
    def test_create_refresh_token(self):
        """Test creating refresh token"""
        user_id = str(uuid.uuid4())
        token = create_refresh_token(user_id)
        
        assert token is not None
        
        payload = decode_token(token)
        assert payload is not None
        assert payload.get("sub") == user_id
        assert payload.get("type") == "refresh"
    
    def test_token_blacklist(self):
        """Test token blacklisting"""
        jti = str(uuid.uuid4())
        
        assert auth_service.is_token_blacklisted(jti) == False
        
        auth_service.blacklist_token(jti)
        
        assert auth_service.is_token_blacklisted(jti) == True
    
    def test_logout(self):
        """Test logout blacklists token"""
        user_id = str(uuid.uuid4())
        token = create_access_token(user_id)
        
        payload = decode_token(token)
        jti = payload.get("jti")
        
        assert auth_service.is_token_blacklisted(jti) == False
        
        auth_service.logout(token)
        
        assert auth_service.is_token_blacklisted(jti) == True


class TestRefreshToken:
    """Test refresh token functionality"""
    
    @pytest.fixture
    def test_user(self, db_session):
        """Create test user"""
        phone = "13800138020"
        user = User(
            id=str(uuid.uuid4()),
            phone=phone,
            phone_blind_index=generate_phone_blind_index(phone),
            nickname="refresh_user",
            status="ACTIVE",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_refresh_access_token_success(self, db_session, test_user):
        """Test successful token refresh"""
        refresh_token = create_refresh_token(test_user.id)
        
        new_access, new_refresh = auth_service.refresh_access_token(
            db=db_session,
            refresh_token=refresh_token,
        )
        
        assert new_access is not None
        assert new_refresh is not None
        
        access_payload = decode_token(new_access)
        assert access_payload.get("sub") == test_user.id
        assert access_payload.get("type") == "access"
    
    def test_refresh_access_token_invalid_type(self, db_session):
        """Test refresh with access token instead of refresh token"""
        access_token = create_access_token(str(uuid.uuid4()))
        
        with pytest.raises(BusinessException) as exc_info:
            auth_service.refresh_access_token(
                db=db_session,
                refresh_token=access_token,
            )
        
        assert exc_info.value.code == ErrorCode.AUTH_4005
    
    def test_refresh_access_token_blacklisted(self, db_session, test_user):
        """Test refresh with blacklisted token"""
        refresh_token = create_refresh_token(test_user.id)
        payload = decode_token(refresh_token)
        auth_service.blacklist_token(payload.get("jti"))
        
        with pytest.raises(BusinessException) as exc_info:
            auth_service.refresh_access_token(
                db=db_session,
                refresh_token=refresh_token,
            )
        
        assert exc_info.value.code == ErrorCode.AUTH_4005
    
    def test_refresh_access_token_user_not_found(self, db_session):
        """Test refresh with non-existent user"""
        refresh_token = create_refresh_token(str(uuid.uuid4()))
        
        with pytest.raises(BusinessException) as exc_info:
            auth_service.refresh_access_token(
                db=db_session,
                refresh_token=refresh_token,
            )
        
        assert exc_info.value.code == ErrorCode.AUTH_4005


class TestWeChatLogin:
    """Test WeChat login functionality"""
    
    def test_wechat_login_new_user(self, db_session, monkeypatch):
        """Test WeChat login creates new user"""
        monkeypatch.setattr("app.services.auth_service.settings.WECHAT_MOCK_MODE", True)
        
        user, is_new = auth_service.login_by_wechat(
            db=db_session,
            code="test_code_123",
        )
        
        assert is_new == True
        assert user.wechat_openid == "mock_openid_test_code_123"
        assert user.nickname == "微信用户"
    
    def test_wechat_login_existing_user(self, db_session, monkeypatch):
        """Test WeChat login for existing user"""
        monkeypatch.setattr("app.services.auth_service.settings.WECHAT_MOCK_MODE", True)
        
        existing_user = User(
            id=str(uuid.uuid4()),
            wechat_openid="mock_openid_test_code_456",
            nickname="existing_wechat_user",
            status="ACTIVE",
        )
        db_session.add(existing_user)
        db_session.commit()
        
        user, is_new = auth_service.login_by_wechat(
            db=db_session,
            code="test_code_456",
        )
        
        assert is_new == False
        assert user.id == existing_user.id


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert verify_password(password, hashed) == True
    
    def test_verify_password_correct(self):
        """Test verifying correct password"""
        password = "CorrectPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True
    
    def test_verify_password_incorrect(self):
        """Test verifying incorrect password"""
        password = "CorrectPassword123!"
        hashed = hash_password(password)
        
        assert verify_password("WrongPassword123!", hashed) == False
    
    def test_different_passwords_different_hashes(self):
        """Test that same password produces different hashes"""
        password = "SamePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) == True
        assert verify_password(password, hash2) == True


class TestTokenBlacklistRedisMigration:
    """Test token blacklist Redis migration"""
    
    def test_blacklist_token_with_redis(self, monkeypatch):
        """Test blacklisting token with Redis available"""
        from app.core.redis_client import redis_client
        from app.services import auth_service
        
        jti = str(uuid.uuid4())
        
        auth_service.blacklist_token(jti)
        
        assert auth_service.is_token_blacklisted(jti) == True
    
    def test_blacklist_token_fallback_to_memory(self, monkeypatch):
        """Test blacklisting token falls back to memory when Redis unavailable"""
        from app.core.redis_client import redis_client
        from app.services import auth_service
        
        original_available = redis_client._is_available
        redis_client._is_available = False
        
        try:
            jti = str(uuid.uuid4())
            
            auth_service.blacklist_token(jti)
            
            assert auth_service.is_token_blacklisted(jti) == True
        finally:
            redis_client._is_available = original_available
    
    def test_is_token_blacklisted_false_initially(self):
        """Test that token is not blacklisted initially"""
        from app.services import auth_service
        
        jti = str(uuid.uuid4())
        
        assert auth_service.is_token_blacklisted(jti) == False
    
    def test_multiple_tokens_blacklist(self):
        """Test blacklisting multiple tokens"""
        from app.services import auth_service
        
        jti1 = str(uuid.uuid4())
        jti2 = str(uuid.uuid4())
        jti3 = str(uuid.uuid4())
        
        auth_service.blacklist_token(jti1)
        auth_service.blacklist_token(jti2)
        
        assert auth_service.is_token_blacklisted(jti1) == True
        assert auth_service.is_token_blacklisted(jti2) == True
        assert auth_service.is_token_blacklisted(jti3) == False
    
    def test_logout_blacklists_token(self, db_session, monkeypatch):
        """Test that logout blacklists the token"""
        from app.services import auth_service
        
        def mock_verify_code(phone, code):
            return True
        
        monkeypatch.setattr("app.services.auth_service.verify_code", mock_verify_code)
        
        user, _ = auth_service.register_by_phone(
            db=db_session,
            phone="13800138000",
            code="123456",
            password=None,
            agreed_to_terms=True,
        )
        
        access_token = create_access_token(user.id)
        payload = decode_token(access_token)
        jti = payload.get("jti")
        
        assert auth_service.is_token_blacklisted(jti) == False
        
        auth_service.logout(access_token)
        
        assert auth_service.is_token_blacklisted(jti) == True
    
    def test_refresh_token_blacklist_old_token(self, db_session, monkeypatch):
        """Test that refresh token blacklists old token"""
        from app.services import auth_service
        
        def mock_verify_code(phone, code):
            return True
        
        monkeypatch.setattr("app.services.auth_service.verify_code", mock_verify_code)
        
        user, _ = auth_service.register_by_phone(
            db=db_session,
            phone="13800138001",
            code="123456",
            password=None,
            agreed_to_terms=True,
        )
        
        refresh_token = create_refresh_token(user.id)
        payload = decode_token(refresh_token)
        old_jti = payload.get("jti")
        
        assert auth_service.is_token_blacklisted(old_jti) == False
        
        new_access, new_refresh = auth_service.refresh_access_token(db_session, refresh_token)
        
        assert auth_service.is_token_blacklisted(old_jti) == True
        assert new_access is not None
        assert new_refresh is not None
