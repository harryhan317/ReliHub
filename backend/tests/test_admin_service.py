"""
Unit tests for AdminService.

Uses PostgreSQL test database via conftest.py fixtures.
"""
import hashlib
import json
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ErrorCode
from app.models.administrators import AdminAuditLog, AdminUser
from app.models.feedback import Feedback, FeedbackStatus
from app.models.ledger import AssetPackage
from app.models.resources import Resource, ResourceStatus
from app.models.system_config import SystemConfig
from app.models.topic import Post, Topic, TopicStatus
from app.models.users import User
from app.schemas.admin import (
    AssetPackageUpdateRequest,
    BanUserRequest,
    FeedbackReplyRequest,
    LockUserRequest,
    ResourceReviewRequest,
    SystemConfigUpdateRequest,
)
from app.services.admin_service import AdminService


@pytest.fixture
def admin_user(db_session: Session):
    """Create a test admin user."""
    admin = AdminUser(
        id=str(uuid.uuid4()),
        username="testadmin",
        password_hash="hashed_password",
        role="SUPER_ADMIN",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def operator_admin(db_session: Session):
    """Create a test operator admin."""
    admin = AdminUser(
        id=str(uuid.uuid4()),
        username="operator",
        password_hash="hashed_password",
        role="OPERATOR",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def auditor_admin(db_session: Session):
    """Create a test auditor admin."""
    admin = AdminUser(
        id=str(uuid.uuid4()),
        username="auditor",
        password_hash="hashed_password",
        role="AUDITOR",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        phone="+8613800138000",
        nickname="testuser",
        password_hash="hashed_password",
        status="ACTIVE",
        rank="M1",
        reputation_points=100,
        gold_beans=50,
        bonus_beans=30,
        is_expert=False
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_resource(db_session: Session, test_user: User):
    """Create a test resource."""
    resource = Resource(
        id=str(uuid.uuid4()),
        uploader_id=test_user.id,
        title="Test Resource",
        description="Test description",
        category_id=1,
        price=10,
        status=ResourceStatus.PENDING_REVIEW,
        view_count=0,
        download_count=0,
        is_deleted=False,
        file_uuid=str(uuid.uuid4())
    )
    db_session.add(resource)
    db_session.commit()
    return resource


@pytest.fixture
def test_topic(db_session: Session, test_user: User):
    """Create a test topic."""
    topic = Topic(
        id=str(uuid.uuid4()),
        author_id=test_user.id,
        title="Test Topic",
        content="Test content for topic",
        category_id=1,
        status=TopicStatus.NORMAL,
        view_count=0,
        post_count=0,
        is_deleted=False
    )
    db_session.add(topic)
    db_session.commit()
    return topic


@pytest.fixture
def test_feedback(db_session: Session, test_user: User):
    """Create a test feedback."""
    feedback = Feedback(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        content="Test feedback content",
        status=FeedbackStatus.PENDING
    )
    db_session.add(feedback)
    db_session.commit()
    return feedback


@pytest.fixture
def test_asset_package(db_session: Session):
    """Create a test asset package."""
    package = AssetPackage(
        id=str(uuid.uuid4()),
        name="Test Package",
        price_beans=80,
        quota_mb=100,
        discount_rate=0.85
    )
    db_session.add(package)
    db_session.commit()
    return package


class TestAdminServicePermission:
    """Tests for permission checking."""

    def test_super_admin_has_all_permissions(self, db_session: Session, admin_user: AdminUser):
        service = AdminService(db_session, admin_user)
        assert service.check_permission(["SUPER_ADMIN"]) == True
        assert service.check_permission(["SUPER_ADMIN", "OPERATOR"]) == True

    def test_operator_has_limited_permissions(self, db_session: Session, operator_admin: AdminUser):
        service = AdminService(db_session, operator_admin)
        assert service.check_permission(["SUPER_ADMIN", "OPERATOR"]) == True
        with pytest.raises(BusinessException) as exc:
            service.check_permission(["SUPER_ADMIN"])
        assert exc.value.code == ErrorCode.ADMIN_4002

    def test_auditor_has_readonly_permissions(self, db_session: Session, auditor_admin: AdminUser):
        service = AdminService(db_session, auditor_admin)
        with pytest.raises(BusinessException) as exc:
            service.check_permission(["SUPER_ADMIN", "OPERATOR"])
        assert exc.value.code == ErrorCode.ADMIN_4002


class TestAdminServiceUserManagement:
    """Tests for user management."""

    def test_list_users(self, db_session: Session, admin_user: AdminUser, test_user: User):
        service = AdminService(db_session, admin_user)
        users, total = service.list_users()
        assert total >= 1
        assert len(users) >= 1

    def test_list_users_with_status_filter(self, db_session: Session, admin_user: AdminUser, test_user: User):
        service = AdminService(db_session, admin_user)
        users, total = service.list_users(status="ACTIVE")
        assert total >= 1
        for user in users:
            assert user.status == "ACTIVE"

    def test_list_users_with_search(self, db_session: Session, admin_user: AdminUser, test_user: User):
        service = AdminService(db_session, admin_user)
        users, total = service.list_users(search="testuser")
        assert total >= 1
        for user in users:
            assert "testuser" in user.nickname

    def test_get_user(self, db_session: Session, admin_user: AdminUser, test_user: User):
        service = AdminService(db_session, admin_user)
        user = service.get_user(test_user.id)
        assert user is not None
        assert user.id == test_user.id

    def test_get_nonexistent_user(self, db_session: Session, admin_user: AdminUser):
        service = AdminService(db_session, admin_user)
        user = service.get_user("nonexistent-id")
        assert user is None

    def test_ban_user(self, db_session: Session, admin_user: AdminUser, test_user: User):
        service = AdminService(db_session, admin_user)
        request = BanUserRequest(reason="Violation of terms")
        user = service.ban_user(test_user.id, request)
        assert user.status == "DISABLED"

    def test_unban_user(self, db_session: Session, admin_user: AdminUser, test_user: User):
        service = AdminService(db_session, admin_user)
        test_user.status = "DISABLED"
        db_session.commit()
        user = service.unban_user(test_user.id)
        assert user.status == "ACTIVE"

    def test_lock_user(self, db_session: Session, admin_user: AdminUser, test_user: User):
        service = AdminService(db_session, admin_user)
        request = LockUserRequest(reason="Suspicious activity")
        user = service.lock_user(test_user.id, request)
        assert user.status == "LOCKED"

    def test_unlock_user(self, db_session: Session, admin_user: AdminUser, test_user: User):
        service = AdminService(db_session, admin_user)
        test_user.status = "LOCKED"
        db_session.commit()
        user = service.unlock_user(test_user.id)
        assert user.status == "ACTIVE"

    def test_ban_nonexistent_user(self, db_session: Session, admin_user: AdminUser):
        service = AdminService(db_session, admin_user)
        request = BanUserRequest(reason="Test")
        with pytest.raises(BusinessException) as exc:
            service.ban_user("nonexistent-id", request)
        assert exc.value.code == ErrorCode.ADMIN_4004


class TestAdminServiceContentReview:
    """Tests for content review."""

    def test_list_pending_resources(self, db_session: Session, admin_user: AdminUser, test_resource: Resource):
        service = AdminService(db_session, admin_user)
        resources, total = service.list_pending_resources()
        assert total >= 1
        assert len(resources) >= 1

    def test_approve_resource(self, db_session: Session, admin_user: AdminUser, test_resource: Resource):
        service = AdminService(db_session, admin_user)
        request = ResourceReviewRequest(reason="Good quality")
        resource = service.approve_resource(test_resource.id, request)
        assert resource.status == ResourceStatus.APPROVED

    def test_reject_resource(self, db_session: Session, admin_user: AdminUser, test_resource: Resource):
        service = AdminService(db_session, admin_user)
        request = ResourceReviewRequest(reason="Low quality")
        resource = service.reject_resource(test_resource.id, request)
        assert resource.status == ResourceStatus.REJECTED

    def test_block_resource(self, db_session: Session, admin_user: AdminUser, test_resource: Resource):
        test_resource.status = ResourceStatus.APPROVED
        db_session.commit()
        service = AdminService(db_session, admin_user)
        request = ResourceReviewRequest(reason="Inappropriate content")
        resource = service.block_resource(test_resource.id, request)
        assert resource.status == ResourceStatus.BLOCKED

    def test_list_topics(self, db_session: Session, admin_user: AdminUser, test_topic: Topic):
        service = AdminService(db_session, admin_user)
        topics, total = service.list_topics()
        assert total >= 1
        assert len(topics) >= 1

    def test_block_topic(self, db_session: Session, admin_user: AdminUser, test_topic: Topic):
        service = AdminService(db_session, admin_user)
        request = ResourceReviewRequest(reason="Spam")
        topic = service.block_topic(test_topic.id, request)
        assert topic.status == TopicStatus.BLOCKED


class TestAdminServiceAuditLog:
    """Tests for audit logs."""

    def test_list_audit_logs(self, db_session: Session, admin_user: AdminUser):
        service = AdminService(db_session, admin_user)
        logs, total = service.list_audit_logs()
        assert total >= 0

    def test_audit_log_created_on_ban_user(self, db_session: Session, admin_user: AdminUser, test_user: User):
        service = AdminService(db_session, admin_user)
        request = BanUserRequest(reason="Test")
        service.ban_user(test_user.id, request)
        
        logs, total = service.list_audit_logs(action="BAN_USER")
        assert total >= 1
        assert logs[0].action == "BAN_USER"
        assert logs[0].target_id == test_user.id

    def test_audit_log_hash_chaining(self, db_session: Session, admin_user: AdminUser, test_user: User):
        service = AdminService(db_session, admin_user)
        
        request1 = BanUserRequest(reason="Test 1")
        service.ban_user(test_user.id, request1)
        
        logs_after_first, _ = service.list_audit_logs()
        first_log = logs_after_first[0]
        
        request2 = LockUserRequest(reason="Test 2")
        test_user.status = "ACTIVE"
        db_session.commit()
        service.lock_user(test_user.id, request2)
        
        logs_after_second, _ = service.list_audit_logs()
        second_log = logs_after_second[0]
        
        assert second_log.prev_log_hash == first_log.log_hash
        assert len(first_log.log_hash) == 64


class TestAdminServiceSystemConfig:
    """Tests for system configuration."""

    def test_list_system_configs(self, db_session: Session, admin_user: AdminUser):
        service = AdminService(db_session, admin_user)
        configs = service.list_system_configs()
        assert isinstance(configs, list)

    def test_create_system_config(self, db_session: Session, admin_user: AdminUser):
        service = AdminService(db_session, admin_user)
        request = SystemConfigUpdateRequest(
            config_key="test_config",
            config_value="test_value",
            description="Test configuration"
        )
        config = service.update_system_config(request)
        assert config.config_key == "test_config"
        assert config.config_value == "test_value"

    def test_update_system_config(self, db_session: Session, admin_user: AdminUser):
        service = AdminService(db_session, admin_user)
        
        create_request = SystemConfigUpdateRequest(
            config_key="test_config",
            config_value="initial_value"
        )
        service.update_system_config(create_request)
        
        update_request = SystemConfigUpdateRequest(
            config_key="test_config",
            config_value="updated_value"
        )
        config = service.update_system_config(update_request)
        assert config.config_value == "updated_value"

    def test_operator_cannot_update_config(self, db_session: Session, operator_admin: AdminUser):
        service = AdminService(db_session, operator_admin)
        request = SystemConfigUpdateRequest(
            config_key="test_config",
            config_value="test_value"
        )
        with pytest.raises(BusinessException) as exc:
            service.update_system_config(request)
        assert exc.value.code == ErrorCode.ADMIN_4002


class TestAdminServiceFeedback:
    """Tests for feedback management."""

    def test_list_feedbacks(self, db_session: Session, admin_user: AdminUser, test_feedback: Feedback):
        service = AdminService(db_session, admin_user)
        feedbacks, total = service.list_feedbacks()
        assert total >= 1
        assert len(feedbacks) >= 1

    def test_list_feedbacks_with_status_filter(self, db_session: Session, admin_user: AdminUser, test_feedback: Feedback):
        service = AdminService(db_session, admin_user)
        feedbacks, total = service.list_feedbacks(status="PENDING")
        assert total >= 1
        for feedback in feedbacks:
            assert feedback.status == FeedbackStatus.PENDING

    def test_get_feedback(self, db_session: Session, admin_user: AdminUser, test_feedback: Feedback):
        service = AdminService(db_session, admin_user)
        feedback = service.get_feedback(test_feedback.id)
        assert feedback is not None
        assert feedback.id == test_feedback.id

    def test_reply_feedback(self, db_session: Session, admin_user: AdminUser, test_feedback: Feedback):
        service = AdminService(db_session, admin_user)
        request = FeedbackReplyRequest(reply="Thank you for your feedback!")
        feedback = service.reply_feedback(test_feedback.id, request)
        assert feedback.reply == "Thank you for your feedback!"
        assert feedback.status == FeedbackStatus.RESOLVED
        assert feedback.replied_by == admin_user.id


class TestAdminServiceAssetPackage:
    """Tests for asset package management."""

    def test_list_asset_packages(self, db_session: Session, admin_user: AdminUser, test_asset_package: AssetPackage):
        service = AdminService(db_session, admin_user)
        packages = service.list_asset_packages()
        assert len(packages) >= 1

    def test_update_asset_package(self, db_session: Session, admin_user: AdminUser, test_asset_package: AssetPackage):
        service = AdminService(db_session, admin_user)
        request = AssetPackageUpdateRequest(price_beans=100, discount_rate=0.80)
        package = service.update_asset_package(test_asset_package.id, request)
        assert package.price_beans == 100
        assert package.discount_rate == 0.80

    def test_update_asset_package_partial(self, db_session: Session, admin_user: AdminUser, test_asset_package: AssetPackage):
        service = AdminService(db_session, admin_user)
        original_rate = test_asset_package.discount_rate
        request = AssetPackageUpdateRequest(price_beans=120)
        package = service.update_asset_package(test_asset_package.id, request)
        assert package.price_beans == 120
        assert package.discount_rate == original_rate

    def test_operator_cannot_update_package(self, db_session: Session, operator_admin: AdminUser, test_asset_package: AssetPackage):
        service = AdminService(db_session, operator_admin)
        request = AssetPackageUpdateRequest(price_beans=100)
        with pytest.raises(BusinessException) as exc:
            service.update_asset_package(test_asset_package.id, request)
        assert exc.value.code == ErrorCode.ADMIN_4002


class TestAdminServiceDashboard:
    """Tests for dashboard statistics."""

    def test_get_dashboard_stats(
        self,
        db_session: Session,
        admin_user: AdminUser,
        test_user: User,
        test_resource: Resource,
        test_topic: Topic,
        test_feedback: Feedback
    ):
        service = AdminService(db_session, admin_user)
        stats = service.get_dashboard_stats()
        
        assert "total_users" in stats
        assert "active_users" in stats
        assert "total_resources" in stats
        assert "pending_resources" in stats
        assert "total_topics" in stats
        assert "total_posts" in stats
        assert "total_feedbacks" in stats
        assert "pending_feedbacks" in stats
        
        assert stats["total_users"] >= 1
        assert stats["total_resources"] >= 1
        assert stats["total_topics"] >= 1
        assert stats["total_feedbacks"] >= 1
