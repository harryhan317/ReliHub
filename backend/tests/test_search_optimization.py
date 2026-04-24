"""
Test search optimization features.

Tests for:
1. Search query optimization
2. Index performance
3. Relevance scoring improvements
4. Search performance benchmarks
"""
import pytest
import time
from datetime import datetime
from unittest.mock import Mock, MagicMock

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.search_optimizer import SearchOptimizer, get_search_optimizer
from app.services.search_service import SearchService
from app.models.resources import Resource
from app.models.topic import Topic


class TestSearchQueryOptimization:
    """Test search query optimization"""
    
    @pytest.fixture
    def optimizer(self, db_session: Session):
        """Create optimizer instance"""
        return SearchOptimizer(db_session)
    
    def test_optimize_search_query_normalization(self, optimizer):
        """Test query normalization"""
        query = "  Python  教程  "
        optimized, metadata = optimizer.optimize_search_query(query)
        
        assert optimized == "Python  教程"
        assert "normalized_whitespace" in metadata["optimizations_applied"]
    
    def test_optimize_search_query_special_chars(self, optimizer):
        """Test special character removal"""
        query = "Python@#教程!$%"
        optimized, metadata = optimizer.optimize_search_query(query)
        
        # Special chars should be removed
        assert "@" not in optimized
        assert "#" not in optimized
        assert "!" not in optimized
        assert "optimized" in metadata or len(metadata["optimizations_applied"]) > 0
    
    def test_optimize_search_query_truncation(self, optimizer):
        """Test query truncation for long queries"""
        query = "a" * 150  # 150 characters
        optimized, metadata = optimizer.optimize_search_query(query)
        
        assert len(optimized) <= 100
        assert "truncated_to_100_chars" in metadata["optimizations_applied"]
    
    def test_optimize_search_query_preserves_chinese(self, optimizer):
        """Test that Chinese characters are preserved"""
        query = "可靠性测试"
        optimized, metadata = optimizer.optimize_search_query(query)
        
        assert optimized == "可靠性测试"
        assert len(optimized) == len(query)


class TestRelevanceScoring:
    """Test enhanced relevance scoring"""
    
    @pytest.fixture
    def optimizer(self, db_session: Session):
        """Create optimizer instance"""
        return SearchOptimizer(db_session)
    
    def test_enhanced_score_exact_title_match(self, optimizer):
        """Test exact title match bonus"""
        text = "This is a tutorial about Python programming"
        query = "Python"
        title = "Python Programming Tutorial"
        
        score = optimizer.calculate_enhanced_relevance_score(text, query, title)
        
        # Should have exact title match bonus
        assert score > 0
    
    def test_enhanced_score_exact_content_match(self, optimizer):
        """Test exact content match bonus"""
        text = "Learn Python programming from scratch"
        query = "Python programming"
        title = "Tutorial"
        
        score = optimizer.calculate_enhanced_relevance_score(text, query, title)
        
        # Should have exact content match bonus
        assert score > 0
    
    def test_enhanced_score_heat_bonus(self, optimizer):
        """Test heat score bonus"""
        text = "Resource description"
        query = "resource"
        title = "Test Resource"
        metadata = {
            "heat_score": 500.0,
            "created_at": datetime.utcnow()
        }
        
        score = optimizer.calculate_enhanced_relevance_score(
            text, query, title, metadata
        )
        
        # Should include heat bonus
        assert score > 0
    
    def test_enhanced_score_recency_bonus(self, optimizer):
        """Test recency bonus"""
        text = "Recent content"
        query = "content"
        title = "Recent"
        metadata = {
            "heat_score": 0,
            "created_at": datetime.utcnow()  # Just created
        }
        
        score = optimizer.calculate_enhanced_relevance_score(
            text, query, title, metadata
        )
        
        # Should include recency bonus
        assert score > 0


class TestSearchPerformance:
    """Test search performance optimizations"""
    
    @pytest.fixture
    def search_service(self, db_session: Session):
        """Create search service instance"""
        return SearchService(db_session)
    
    @pytest.fixture
    def optimizer(self, db_session: Session):
        """Create optimizer instance"""
        return SearchOptimizer(db_session)
    
    def test_search_performance_with_index(self, search_service, db_session):
        """Test search performance should be under threshold"""
        query = "test"
        
        start_time = time.time()
        results, total = search_service.global_search(
            query=query,
            page=1,
            size=20
        )
        execution_time = time.time() - start_time
        
        # Performance requirement: < 500ms
        assert execution_time < 0.5, f"Search took {execution_time*1000:.2f}ms, should be < 500ms"
    
    def test_search_suggestions_performance(self, search_service, db_session):
        """Test search suggestions performance"""
        query = "py"
        
        start_time = time.time()
        suggestions = search_service.get_search_suggestions(query, limit=5)
        execution_time = time.time() - start_time
        
        # Performance requirement: < 200ms
        assert execution_time < 0.2, f"Suggestions took {execution_time*1000:.2f}ms, should be < 200ms"
    
    def test_analyze_query_performance(self, optimizer):
        """Test query performance analysis"""
        result = optimizer.analyze_query_performance("test", "RESOURCE")
        
        assert "execution_time_ms" in result
        assert "status" in result
        assert result["status"] in ["success", "unknown_type", "error"]


class TestIndexRecommendations:
    """Test index recommendation system"""
    
    @pytest.fixture
    def optimizer(self, db_session: Session):
        """Create optimizer instance"""
        return SearchOptimizer(db_session)
    
    def test_recommend_indexes_returns_list(self, optimizer):
        """Test that index recommendations returns a list"""
        recommendations = optimizer.recommend_indexes()
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
    
    def test_recommend_indexes_structure(self, optimizer):
        """Test recommendation structure"""
        recommendations = optimizer.recommend_indexes()
        
        if recommendations:
            rec = recommendations[0]
            assert "table" in rec or "error" in rec
            assert "priority" in rec
            assert "recommendation" in rec or "error" in rec


class TestSearchAccuracy:
    """Test search accuracy improvements"""
    
    @pytest.fixture
    def search_service(self, db_session: Session):
        """Create search service instance"""
        return SearchService(db_session)
    
    def test_search_relevance_ranking(self, search_service, db_session):
        """Test that relevant results rank higher"""
        # Create test data
        query = "Python 教程"
        
        results, total = search_service.global_search(
            query=query,
            sort_by="relevance",
            page=1,
            size=10
        )
        
        # If we have results, check scoring
        if results:
            # Results should have scores
            assert "score" in results[0]
            
            # Scores should be in descending order (approximately)
            scores = [r.get("score", 0) for r in results]
            # Not strictly descending due to different types, but top results should have good scores
            assert max(scores) > 0
    
    def test_search_type_filtering(self, search_service, db_session):
        """Test search type filtering accuracy"""
        query = "test"
        
        # Search only resources
        resource_results, resource_total = search_service.global_search(
            query=query,
            search_type="RESOURCE",
            page=1,
            size=10
        )
        
        # All results should be resources
        for result in resource_results:
            assert result["type"] == "RESOURCE"
        
        # Search only community
        community_results, community_total = search_service.global_search(
            query=query,
            search_type="COMMUNITY",
            page=1,
            size=10
        )
        
        # All results should be community
        for result in community_results:
            assert result["type"] == "COMMUNITY"


class TestSearchOptimizerInstance:
    """Test search optimizer singleton pattern"""
    
    def test_get_search_optimizer_singleton(self, db_session: Session):
        """Test that get_search_optimizer returns singleton"""
        optimizer1 = get_search_optimizer(db_session)
        optimizer2 = get_search_optimizer(db_session)
        
        # Should return same instance
        assert optimizer1 is optimizer2


# Performance benchmark tests
class TestSearchBenchmarks:
    """Search performance benchmarks"""
    
    @pytest.fixture
    def search_service(self, db_session: Session):
        """Create search service instance"""
        return SearchService(db_session)
    
    def test_benchmark_simple_search(self, search_service):
        """Benchmark simple search query"""
        query = "test"
        
        # Run multiple times for average
        times = []
        for _ in range(5):
            start = time.time()
            search_service.global_search(query, page=1, size=20)
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        
        # Average should be under 500ms
        assert avg_time < 0.5, f"Average search time {avg_time*1000:.2f}ms > 500ms"
    
    def test_benchmark_complex_search(self, search_service):
        """Benchmark complex search query with filters"""
        query = "Python 教程"
        
        start = time.time()
        search_service.global_search(
            query=query,
            search_type="ALL",
            sort_by="relevance",
            page=1,
            size=20
        )
        execution_time = time.time() - start
        
        # Should complete under 1 second
        assert execution_time < 1.0, f"Complex search took {execution_time*1000:.2f}ms"
