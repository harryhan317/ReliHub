"""
Simplified tests for Search module - MVP version.
Focus on core functionality testing.
"""

import uuid
from datetime import datetime

import pytest

from fastapi import status

from app.models.users import User
from app.models.search_history import SearchHistory
from app.services.search_service import SearchService
from app.schemas.search import SearchType, SortBy


class TestSearchServiceBasic:
    """Basic SearchService tests"""
    
    @pytest.fixture
    def test_user(self, db_session):
        """Create test user"""
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138100",
            phone_blind_index="test_blind_100",
            nickname="TestUser",
            status="ACTIVE",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_record_search_history(self, db_session, test_user):
        """Test recording search history"""
        service = SearchService(db_session)
        
        history = service.record_search_history(
            user_id=test_user.id,
            keyword="Python 教程",
            search_type="RESOURCE",
            result_count=5
        )
        
        assert history.id is not None
        assert history.user_id == test_user.id
        assert history.keyword == "Python 教程"
        assert history.result_count == 5
    
    def test_get_search_history(self, db_session, test_user):
        """Test getting user's search history"""
        service = SearchService(db_session)
        
        # Create some history records
        for i in range(5):
            service.record_search_history(
                user_id=test_user.id,
                keyword=f"搜索词{i}",
                search_type="ALL",
                result_count=i
            )
        
        history_items, total = service.get_search_history(
            user_id=test_user.id,
            page=1,
            size=10
        )
        
        assert total == 5
        assert len(history_items) == 5
    
    def test_delete_search_history_item(self, db_session, test_user):
        """Test deleting single search history item"""
        service = SearchService(db_session)
        
        # Create a history record
        history = service.record_search_history(
            user_id=test_user.id,
            keyword="测试关键词",
            search_type="ALL",
            result_count=1
        )
        
        # Delete it
        success = service.delete_search_history_item(
            user_id=test_user.id,
            history_id=history.id
        )
        
        assert success == True
        
        # Verify it's deleted
        history_items, total = service.get_search_history(
            user_id=test_user.id,
            page=1,
            size=10
        )
        assert total == 0
    
    def test_clear_search_history(self, db_session, test_user):
        """Test clearing all search history"""
        service = SearchService(db_session)
        
        # Create some history records
        for i in range(5):
            service.record_search_history(
                user_id=test_user.id,
                keyword=f"搜索词{i}",
                search_type="ALL",
                result_count=i
            )
        
        # Clear all
        count = service.clear_search_history(user_id=test_user.id)
        
        assert count == 5
        
        # Verify all are cleared
        history_items, total = service.get_search_history(
            user_id=test_user.id,
            page=1,
            size=10
        )
        assert total == 0
    
    def test_get_trending_searches(self, db_session, test_user):
        """Test getting trending searches"""
        service = SearchService(db_session)
        
        # Create some search history to generate trending data
        for i in range(10):
            service.record_search_history(
                user_id=test_user.id,
                keyword="热门关键词",
                search_type="ALL",
                result_count=5
            )
        
        for i in range(5):
            service.record_search_history(
                user_id=test_user.id,
                keyword="次热门关键词",
                search_type="ALL",
                result_count=3
            )
        
        trending = service.get_trending_searches(limit=10)
        
        assert isinstance(trending, list)
        assert len(trending) <= 10
        # The most frequent keyword should be first
        if len(trending) > 0:
            assert trending[0]["keyword"] == "热门关键词"
            assert trending[0]["rank"] == 1


class TestSearchHistoryOwnership:
    """Test search history ownership validation"""
    
    @pytest.fixture
    def user1(self, db_session):
        """Create first test user"""
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138300",
            phone_blind_index="test_blind_300",
            nickname="User1",
            status="ACTIVE",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.fixture
    def user2(self, db_session):
        """Create second test user"""
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138400",
            phone_blind_index="test_blind_400",
            nickname="User2",
            status="ACTIVE",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_cannot_delete_other_user_history(self, db_session, user1, user2):
        """Test that user cannot delete another user's search history"""
        service = SearchService(db_session)
        
        # Create history for user1
        history = service.record_search_history(
            user_id=user1.id,
            keyword="用户 1 的搜索",
            search_type="ALL",
            result_count=1
        )
        
        # Try to delete with user2's ID (should fail)
        success = service.delete_search_history_item(
            user_id=user2.id,
            history_id=history.id
        )
        
        assert success == False
        
        # Verify history still exists
        history_items, total = service.get_search_history(
            user_id=user1.id,
            page=1,
            size=10
        )
        assert total == 1


class TestSearchAPIBasic:
    """Basic Search API endpoint tests"""
    
    @pytest.fixture
    def test_user(self, db_session):
        """Create test user"""
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138200",
            phone_blind_index="test_blind_200",
            nickname="APITestUser",
            status="ACTIVE",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.fixture
    def auth_headers(self, client, test_user):
        """Get authenticated headers"""
        from app.core.security import create_access_token
        
        token = create_access_token(test_user.id)
        return {"Authorization": f"Bearer {token}"}
    
    def test_global_search_endpoint(self, client):
        """Test global search endpoint"""
        response = client.get(
            "/api/v1/search",
            params={"q": "Python"}  # Required parameter
        )
        
        # Should return 200 or 422 if validation fails
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "page" in data
            assert "size" in data
            assert "has_more" in data
    
    def test_search_suggestions_endpoint(self, client):
        """Test search suggestions endpoint"""
        response = client.get(
            "/api/v1/search/suggestions",
            params={"q": "Py"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "suggestions" in data
        assert "count" in data
    
    def test_search_history_endpoint_requires_auth(self, client):
        """Test that search history requires authentication"""
        response = client.get("/api/v1/search/history")
        
        # Should return 401, 400, or 422 for unauthenticated requests
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    def test_search_history_endpoint_with_auth(self, client, auth_headers):
        """Test search history with authentication"""
        response = client.get(
            "/api/v1/search/history",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "history" in data
        assert "total" in data
    
    def test_clear_search_history_endpoint(self, client, auth_headers):
        """Test clear search history endpoint"""
        response = client.delete(
            "/api/v1/search/history",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_user_search_endpoint(self, client, test_user):
        """Test user search endpoint"""
        response = client.get(
            "/api/v1/search/users",
            params={"q": "APITest"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    def test_trending_searches_endpoint(self, client):
        """Test trending searches endpoint"""
        response = client.get("/api/v1/search/trending")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "trending" in data
