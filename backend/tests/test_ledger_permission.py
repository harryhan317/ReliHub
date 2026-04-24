"""
Integration tests for Ledger Management admin permission checks.
Aligned with WP1.1 of Sprint D.

IMPORTANT: Uses conftest.py fixtures for proper database and rate limiting configuration.
TESTING=true is set in conftest.py to enable permissive rate limits.
"""
import uuid
import pytest
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.administrators import AdminUser
from app.models.users import User
from app.models.ledger import PointType


@pytest.fixture
def regular_user_token(db_session):
    """Create a regular user and return access token."""
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        phone="13800138000",
        nickname="Regular User",
        status="ACTIVE"
    )
    db_session.add(user)
    db_session.commit()
    return create_access_token(user_id)


@pytest.fixture
def admin_user_token(db_session):
    """Create an admin user and return access token."""
    admin_id = str(uuid.uuid4())
    admin = AdminUser(
        id=admin_id,
        username=f"admin_{admin_id[:8]}",
        password_hash="any",
        role="SUPER_ADMIN",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    return create_access_token(admin_id)


def test_grant_beans_no_token(client):
    """Test granting beans without any token should return 401/403 (depends on implementation)"""
    user_id = str(uuid.uuid4())
    response = client.post(
        f"/api/v1/ledger/admin/grant?user_id={user_id}&amount=100&point_type=GOLD_BEAN&description=test"
    )
    assert response.status_code in [401, 422]


def test_grant_beans_regular_user(client, regular_user_token):
    """Test granting beans with regular user token should return 403 (BusinessException)"""
    user_id = str(uuid.uuid4())
    response = client.post(
        f"/api/v1/ledger/admin/grant?user_id={user_id}&amount=100&point_type=GOLD_BEAN&description=test",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code in [400, 401, 403]


def test_grant_beans_admin_success(client, db_session, admin_user_token):
    """Test granting beans with admin token should succeed"""
    user_id = str(uuid.uuid4())
    user = User(id=user_id, phone="13900139000", nickname="Target User")
    db_session.add(user)
    db_session.commit()

    response = client.post(
        f"/api/v1/ledger/admin/grant?user_id={user_id}&amount=100&point_type=GOLD_BEAN&description=Reward",
        headers={"Authorization": f"Bearer {admin_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Beans granted"
    assert "entry_id" in data
