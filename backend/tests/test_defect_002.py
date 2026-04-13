"""
Test cases for DEFECT-002: Admin config validation
"""
import pytest
from sqlalchemy.orm import Session

from app.schemas.admin import SystemConfigUpdateRequest
from app.services.admin_service import AdminService
from app.models.administrators import AdminUser


class TestDefect002ConfigValidation:
    """Test cases for DEFECT-002: Admin config parameter validation"""
    
    @pytest.fixture
    def admin_user(self, db_session: Session):
        """Create a test admin user"""
        admin = AdminUser(
            id="test-admin-uuid",
            username="test_admin",
            password_hash="hashed_password",
            role="SUPER_ADMIN",
            is_active=True
        )
        db_session.add(admin)
        db_session.commit()
        return admin
    
    @pytest.fixture
    def admin_service(self, db_session: Session, admin_user: AdminUser):
        """Create admin service instance"""
        return AdminService(db_session, admin_user)
    
    def test_config_key_format_validation(self, admin_service, db_session):
        """Test config_key format validation"""
        from app.core.exceptions import BusinessException, ErrorCode
        
        # Test invalid config_key with special characters
        invalid_request = SystemConfigUpdateRequest(
            config_key="invalid@key",
            config_value="test_value"
        )
        
        with pytest.raises(BusinessException) as exc_info:
            admin_service.update_system_config(invalid_request)
        
        assert "配置键只能包含字母、数字和下划线" in exc_info.value.msg
        assert exc_info.value.code == ErrorCode.ADMIN_4002
    
    def test_config_key_whitelist_validation(self, admin_service, db_session):
        """Test config_key whitelist validation"""
        from app.core.exceptions import BusinessException, ErrorCode
        
        # Test config_key not in whitelist
        invalid_request = SystemConfigUpdateRequest(
            config_key="invalid_config_key",
            config_value="test_value"
        )
        
        with pytest.raises(BusinessException) as exc_info:
            admin_service.update_system_config(invalid_request)
        
        assert "不在允许列表中" in exc_info.value.msg
        assert "允许的配置项" in exc_info.value.msg
        assert exc_info.value.code == ErrorCode.ADMIN_4002
    
    def test_config_value_length_validation(self, admin_service, db_session):
        """Test config_value length validation"""
        from pydantic import ValidationError
        
        # Test config_value too long (> 5000 chars)
        with pytest.raises(ValidationError) as exc_info:
            SystemConfigUpdateRequest(
                config_key="site_name",
                config_value="a" * 5001
            )
        
        assert "config_value" in str(exc_info.value)
    
    def test_valid_config_update(self, admin_service, db_session):
        """Test valid config update"""
        # Test valid config update
        valid_request = SystemConfigUpdateRequest(
            config_key="site_name",
            config_value="ReliHub Test Site",
            description="Test site name"
        )
        
        config = admin_service.update_system_config(valid_request)
        
        assert config.config_key == "site_name"
        assert config.config_value == "ReliHub Test Site"
        assert config.description == "Test site name"
    
    def test_allowed_config_keys(self, admin_service, db_session):
        """Test all allowed config keys"""
        allowed_keys = [
            "site_name",
            "site_description",
            "max_upload_size",
            "feature_flags",
            "maintenance_mode",
            "registration_enabled",
            "email_verification_required",
            "search_cache_ttl",
            "trending_search_limit",
            "sensitive_words_enabled",
        ]
        
        for key in allowed_keys:
            request = SystemConfigUpdateRequest(
                config_key=key,
                config_value=f"test_value_for_{key}"
            )
            
            config = admin_service.update_system_config(request)
            assert config.config_key == key
    
    def test_config_key_format_edge_cases(self, admin_service, db_session):
        """Test config_key format edge cases"""
        from app.core.exceptions import BusinessException, ErrorCode
        
        # Test empty config_key
        with pytest.raises(Exception):
            SystemConfigUpdateRequest(
                config_key="",
                config_value="test"
            )
        
        # Test config_key with spaces
        with pytest.raises(BusinessException) as exc_info:
            request = SystemConfigUpdateRequest(
                config_key="invalid key",
                config_value="test"
            )
            admin_service.update_system_config(request)
        assert "配置键只能包含字母、数字和下划线" in exc_info.value.msg
        assert exc_info.value.code == ErrorCode.ADMIN_4002
        
        # Test config_key with Chinese characters
        with pytest.raises(BusinessException) as exc_info:
            request = SystemConfigUpdateRequest(
                config_key="配置键",
                config_value="test"
            )
            admin_service.update_system_config(request)
        assert "配置键只能包含字母、数字和下划线" in exc_info.value.msg
        assert exc_info.value.code == ErrorCode.ADMIN_4002
    
    def test_config_update_audit_log(self, admin_service, db_session, admin_user):
        """Test that config update creates audit log"""
        from app.models.administrators import AdminAuditLog
        from sqlalchemy import select
        
        request = SystemConfigUpdateRequest(
            config_key="site_name",
            config_value="New Site Name",
            description="Updated site name"
        )
        
        config = admin_service.update_system_config(request, ip_address="127.0.0.1")
        
        # Check audit log was created
        stmt = select(AdminAuditLog).where(
            AdminAuditLog.action == "UPDATE_CONFIG",
            AdminAuditLog.target_id == config.id
        )
        audit_logs = db_session.execute(stmt).scalars().all()
        
        assert len(audit_logs) > 0
        assert audit_logs[0].ip_address == "127.0.0.1"
