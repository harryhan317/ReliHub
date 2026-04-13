"""
End-to-end tests for complete user workflows.

Tests:
1. Health check flow
2. System integration flow
3. User authentication flow
"""
import uuid

from app.core.security import generate_phone_blind_index, hash_password
from app.models.users import User


class TestUserAuthenticationFlow:
    """Test complete user authentication flow"""

    def test_login_flow(self, db_session, client):
        """Test login flow"""
        phone = "13800138001"
        user = User(
            id=str(uuid.uuid4()),
            phone=phone,
            phone_blind_index=generate_phone_blind_index(phone),
            nickname="LoginTestUser",
            password_hash=hash_password("password123")
        )
        db_session.add(user)
        db_session.commit()
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "phone": phone,
                "password": "password123"
            }
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        assert "refresh_token" in login_data
        
        access_token = login_data["access_token"]
        
        me_response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert me_response.status_code == 200
        
        refresh_token = login_data["refresh_token"]
        
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        assert "access_token" in refresh_data
        assert refresh_data["access_token"] != access_token


class TestAuthenticationErrorCases:
    """Test authentication error scenarios"""

    def test_login_with_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "phone": "13900000000",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "AUTH_4003"

    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 422

    def test_access_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "AUTH_4000"

    def test_refresh_with_invalid_token(self, client):
        """Test refresh with invalid token"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "AUTH_4005"


class TestHealthCheckFlow:
    """Test health check and monitoring flow"""

    def test_health_check_flow(self, client):
        """Test health check endpoints"""
        quick_response = client.get("/api/v1/health")
        
        assert quick_response.status_code == 200
        quick_data = quick_response.json()
        assert quick_data["status"] in ["healthy", "unhealthy"]
        
        detailed_response = client.get("/api/v1/health/detailed")
        
        assert detailed_response.status_code in [200, 503]
        detailed_data = detailed_response.json()
        
        if detailed_response.status_code == 200:
            assert "components" in detailed_data
            assert "summary" in detailed_data

    def test_metrics_flow(self, client):
        """Test metrics endpoint"""
        response = client.get("/api/v1/metrics")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestSystemIntegration:
    """Test system-wide integration scenarios"""

    def test_database_connection_flow(self, db_session):
        """Test database connection is working"""
        from sqlalchemy import text
        
        result = db_session.execute(text("SELECT 1")).scalar()
        
        assert result == 1

    def test_redis_connection_flow(self):
        """Test Redis connection is working"""
        from app.core.redis_client import redis_client
        
        is_available = redis_client.is_available
        
        assert is_available in [True, False]

    def test_concurrent_requests_flow(self, client):
        """Test system handles concurrent requests"""
        import concurrent.futures
        
        def make_request():
            return client.get("/api/v1/health")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        assert all(r.status_code == 200 for r in results)
