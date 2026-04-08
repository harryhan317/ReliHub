"""
Integration tests for Sprint B modules.
Tests endpoints that work with synchronous database sessions.

Uses PostgreSQL test database via conftest.py fixtures.
"""
import pytest
import uuid

from fastapi.testclient import TestClient
from app.main import app
from app.models.users import User
from app.core.security import hash_password, generate_phone_blind_index
from app.db.session import get_db as original_get_db


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[original_get_db] = override_get_db
    
    with TestClient(app=app) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    user = User(
        id=str(uuid.uuid4()),
        nickname="testuser",
        phone="13800138000",
        phone_blind_index=generate_phone_blind_index("13800138000"),
        password_hash=hash_password("password123"),
        rank="新兵",
        reputation_points=50,
        gold_beans=30,
        bonus_beans=0,
        status="ACTIVE",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "healthy"]


def test_auth_login_success(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"phone": "13800138000", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user_info" in data


def test_auth_login_wrong_password(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"phone": "13800138000", "password": "wrongpassword"}
    )
    assert response.status_code == 400


def test_auth_login_user_not_found(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"phone": "19999999999", "password": "password123"}
    )
    assert response.status_code == 400


def test_get_current_user(client, test_user):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"phone": "13800138000", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == "testuser"


def test_refresh_token(client, test_user):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"phone": "13800138000", "password": "password123"}
    )
    refresh_token = login_response.json()["refresh_token"]
    
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
