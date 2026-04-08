"""
API Endpoint Tests for AI Module.

Uses PostgreSQL test database via conftest.py fixtures.

Tests:
1. Session endpoints (create, list, get, delete)
2. Message endpoints (create, list)
3. Provider endpoints (list)
4. Feedback endpoints
5. Authentication and authorization
"""

import pytest
import uuid
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.users import User
from app.models.ai_session import AISession
from app.models.ai_message import AIMessage
from app.models.llm_provider import LLMProvider
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


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"phone": "13800138000", "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_provider(db_session):
    provider = LLMProvider(
        id=str(uuid.uuid4()),
        name="deepseek",
        display_name="DeepSeek",
        api_base_url="https://api.deepseek.com/v1",
        api_key_env="DEEPSEEK_API_KEY",
        cost_per_1k_tokens=0.001,
        enabled=True
    )
    db_session.add(provider)
    db_session.commit()
    db_session.refresh(provider)
    return provider


@pytest.fixture
def test_session(db_session, test_user):
    session = AISession(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        title="Test Session",
        model_type="general",
        total_tokens=0,
        total_cost=0.0,
        total_turns=0
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


class TestAISessionEndpoints:
    """Test AI Session API Endpoints"""
    
    def test_list_sessions_authenticated(self, client, auth_headers, test_session):
        response = client.get(
            "/api/v1/ai/sessions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
    
    def test_list_sessions_pagination(self, client, auth_headers, test_session):
        response = client.get(
            "/api/v1/ai/sessions?page=1&page_size=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
    
    def test_get_session_not_found(self, client, auth_headers):
        response = client.get(
            f"/api/v1/ai/sessions/{str(uuid.uuid4())}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestAIMessageEndpoints:
    """Test AI Message API Endpoints"""
    
    def test_list_messages_session_not_found(self, client, auth_headers):
        response = client.get(
            f"/api/v1/ai/sessions/{str(uuid.uuid4())}/messages",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestAIProviderEndpoints:
    """Test AI Provider API Endpoints"""
    
    def test_list_providers_with_data(self, client, test_provider, auth_headers):
        response = client.get("/api/v1/ai/providers", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_list_providers_only_enabled(self, client, db_session, auth_headers):
        enabled_provider = LLMProvider(
            id=str(uuid.uuid4()),
            name="enabled_test",
            display_name="Enabled Test",
            api_base_url="https://api.enabled.com/v1",
            api_key_env="ENABLED_API_KEY",
            cost_per_1k_tokens=0.001,
            enabled=True
        )
        disabled_provider = LLMProvider(
            id=str(uuid.uuid4()),
            name="disabled_test",
            display_name="Disabled Test",
            api_base_url="https://api.disabled.com/v1",
            api_key_env="DISABLED_API_KEY",
            cost_per_1k_tokens=0.002,
            enabled=False
        )
        db_session.add(enabled_provider)
        db_session.add(disabled_provider)
        db_session.commit()
        
        response = client.get("/api/v1/ai/providers", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        provider_names = [p["name"] for p in data]
        assert "enabled_test" in provider_names
        assert "disabled_test" not in provider_names


class TestAIFeedbackEndpoints:
    """Test AI Feedback API Endpoints"""
    
    def test_feedback_endpoint_requires_auth(self, client, test_session):
        response = client.post(
            f"/api/v1/ai/sessions/{test_session.id}/feedback",
            params={"message_id": str(uuid.uuid4())},
            json={"feedback_type": "like"}
        )
        
        assert response.status_code in [401, 422]


class TestAIEndpointsValidation:
    """Test API Input Validation"""
    
    def test_list_sessions_invalid_page(self, client, auth_headers):
        response = client.get(
            "/api/v1/ai/sessions?page=0",
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_list_sessions_invalid_page_size(self, client, auth_headers):
        response = client.get(
            "/api/v1/ai/sessions?page_size=200",
            headers=auth_headers
        )
        
        assert response.status_code == 422


class TestHealthEndpoint:
    """Test Health Check Endpoint"""
    
    def test_health_check(self, client):
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ok", "healthy"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
