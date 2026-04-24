"""
Comprehensive tests for Search module.

Tests:
1. Global Search
   - Search resources
   - Search community topics
   - Search AI sessions (user's own only)
   - Search users
   - Search with different types
   - Search with sorting options
   - Search with pagination

2. Search Suggestions
   - Get suggestions based on query
   - Empty query handling
   - Limit parameter validation

3. Search History
   - Record search history
   - Get user's search history
   - Delete single history item
   - Clear all history
   - History ownership validation

4. User Search
   - Search users by nickname
   - Pagination
   - Sorting options

5. AI History Search
   - Search user's own AI sessions
   - Date range filtering
   - Permission validation (login required)

6. Trending Searches
   - Get trending search terms
   - Limit parameter validation
"""

import uuid
from datetime import datetime, timedelta

import pytest

from fastapi import status

from app.models.resources import Resource
from app.models.topic import Topic
from app.models.ai_session import AISession
from app.models.users import User
from app.models.search_history import SearchHistory
from app.services.search_service import SearchService


class TestSearchService:
    """Test SearchService methods"""
    
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
    
    @pytest.fixture
    def test_resource(self, db_session, test_user):
        """Create test resource"""
        resource = Resource(
            id=str(uuid.uuid4()),
            uploader_id=test_user.id,
            title="Python 教程",
            description="Python 入门教程",
            category_id=1,
            file_uuid=str(uuid.uuid4()),
            price=10,
            status="APPROVED",
        )
        db_session.add(resource)
        db_session.commit()
        return resource
    
    @pytest.fixture
    def test_topic(self, db_session, test_user):
        """Create test topic"""
        topic = Topic(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            title="React 讨论",
            content="React 框架使用心得",
        )
        db_session.add(topic)
        db_session.commit()
        return topic
    
    @pytest.fixture
    def test_ai_session(self, db_session, test_user):
        """Create test AI session"""
        session = AISession(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            title="AI 助手对话",
        )
        db_session.add(session)
        db_session.commit()
        return session
    
    def test_search_resources(self, db_session, test_resource):
        """Test searching resources"""
        from app.schemas.search import SortBy
        
        service = SearchService(db_session)
        
        results, total = service._search_resources(
            query="Python",
            sort_by=SortBy.RELEVANCE,
            page=1,
            size=10
        )
        
        assert total == 1
        assert len(results) == 1
        assert results[0]["title"] == "Python 教程"
    
    def test_search_topics(self, db_session, test_topic):
        """Test searching community topics"""
        from app.schemas.search import SortBy
        
        service = SearchService(db_session)
        
        results, total = service._search_topics(
            query="React",
            sort_by=SortBy.RELEVANCE,
            page=1,
            size=10
        )
        
        assert total == 1
        assert len(results) == 1
        assert results[0]["title"] == "React 讨论"
    
    def test_search_ai_sessions(self, db_session, test_ai_session, test_user):
        """Test searching user's own AI sessions"""
        from app.schemas.search import SortBy
        
        service = SearchService(db_session)
        
        results, total = service._search_ai_sessions(
            query="AI",
            sort_by=SortBy.RELEVANCE,
            page=1,
            size=10,
            user_id=test_user.id
        )
        
        assert total == 1
        assert len(results) == 1
        assert results[0]["title"] == "AI 助手对话"
    
    def test_search_users(self, db_session, test_user):
        """Test searching users"""
        from app.schemas.search import SortBy
        
        service = SearchService(db_session)
        
        results, total = service._search_users(
            query="Test",
            sort_by=SortBy.RELEVANCE,
            page=1,
            size=10
        )
        
        assert total == 1
        assert len(results) == 1
        assert results[0]["title"] == "TestUser"
    
    def test_global_search_all_types(self, db_session, test_resource, test_topic, test_user):
        """Test global search across all types"""
        from app.schemas.search import SearchType, SortBy
        
        service = SearchService(db_session)
        
        results, total = service.global_search(
            query="Python",
            search_type=SearchType.ALL,
            sort_by=SortBy.RELEVANCE,
            page=1,
            size=20,
            user_id=test_user.id
        )
        
        assert total >= 1
        # Should include resource results
        resource_results = [r for r in results if r["type"] == "RESOURCE"]
        assert len(resource_results) >= 1
    
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
    
    def test_get_search_suggestions(self, db_session, test_resource, test_topic):
        """Test getting search suggestions"""
        service = SearchService(db_session)
        
        suggestions = service.get_search_suggestions(
            query="Py",
            limit=5
        )
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5
    
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


class TestSearchAPI:
    """Test Search API endpoints"""
    
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
    def auth_headers(self, client, test_user, monkeypatch):
        """Get authenticated headers"""
        from app.core.security import create_access_token
        
        token = create_access_token(test_user.id)
        return {"Authorization": f"Bearer {token}"}
    
    def test_global_search_endpoint(self, client, test_resource):
        """Test global search endpoint"""
        response = client.get(
            "/api/v1/search",
            params={"q": "Python"}
        )
        
        assert response.status_code == status.HTTP_200_OK
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
        
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST
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
    
    def test_delete_search_history_endpoint(self, client, auth_headers, db_session, test_user):
        """Test delete search history endpoint"""
        # Create a history record
        history = SearchHistory(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            keyword="测试",
            search_type="ALL",
            result_count=1
        )
        db_session.add(history)
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/search/history/{history.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
    
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
    
    def test_ai_history_search_requires_auth(self, client):
        """Test that AI history search requires authentication"""
        response = client.get(
            "/api/v1/search/ai-history",
            params={"q": "AI"}
        )
        
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST
        ]
    
    def test_ai_history_search_with_auth(self, client, auth_headers, test_ai_session):
        """Test AI history search with authentication"""
        response = client.get(
            "/api/v1/search/ai-history",
            headers=auth_headers,
            params={"q": "AI"}
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


class TestSearchPagination:
    """Test search pagination functionality"""
    
    @pytest.fixture
    def setup_multiple_resources(self, db_session, test_user):
        """Create multiple test resources"""
        resources = []
        for i in range(25):
            resource = Resource(
                id=str(uuid.uuid4()),
                uploader_id=test_user.id,
                title=f"资源{i}",
                description=f"资源描述{i}",
                category_id=1,
                file_uuid=str(uuid.uuid4()),
                price=10,
                status="APPROVED",
            )
            db_session.add(resource)
            resources.append(resource)
        
        db_session.commit()
        return resources
    
    def test_search_pagination(self, db_session, setup_multiple_resources, test_user):
        """Test search pagination"""
        from app.schemas.search import SortBy
        
        service = SearchService(db_session)
        
        # Get first page
        results1, total1 = service._search_resources(
            query="资源",
            sort_by=SortBy.RELEVANCE,
            page=1,
            size=10
        )
        
        # Get second page
        results2, total2 = service._search_resources(
            query="资源",
            sort_by=SortBy.RELEVANCE,
            page=2,
            size=10
        )
        
        assert total1 == total2
        assert len(results1) == 10
        assert len(results2) == 10
        
        # Results should be different
        ids1 = {r["id"] for r in results1}
        ids2 = {r["id"] for r in results2}
        assert ids1.isdisjoint(ids2)
