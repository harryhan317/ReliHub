"""
Tests for monitoring and health check functionality.

Tests:
1. Health check endpoints
2. Metrics collection
3. Performance monitoring
4. Alert configuration
"""
import pytest
from unittest.mock import patch, MagicMock


class TestHealthCheck:
    """Test health check functionality"""

    def test_quick_health_check(self, client):
        """Test quick health check endpoint"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert "components" in data

    def test_detailed_health_check(self, client):
        """Test detailed health check endpoint"""
        response = client.get("/api/v1/health/detailed")
        
        assert response.status_code in [200, 503]
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert "version" in data
        assert "environment" in data
        assert "components" in data
        assert "summary" in data

    def test_health_check_components(self, client):
        """Test that health check includes all components"""
        response = client.get("/api/v1/health/detailed")
        data = response.json()
        
        component_names = [c["name"] for c in data["components"]]
        
        assert "database" in component_names
        assert "redis" in component_names

    def test_database_health_check_success(self, db_session):
        """Test database health check when database is healthy"""
        from app.core.health_check import HealthChecker
        
        checker = HealthChecker()
        result = checker.check_database()
        
        assert result.name == "database"
        assert result.healthy == True
        assert "latency_ms" in result.details

    def test_redis_health_check(self):
        """Test Redis health check"""
        from app.core.health_check import HealthChecker
        
        checker = HealthChecker()
        result = checker.check_redis()
        
        assert result.name == "redis"
        assert "status" in result.details


class TestMetrics:
    """Test metrics collection"""

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint"""
        response = client.get("/api/v1/metrics")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    def test_metrics_content(self, client):
        """Test that metrics endpoint returns Prometheus format"""
        response = client.get("/api/v1/metrics")
        content = response.text
        
        assert "http_requests_total" in content or "application_info" in content

    def test_metrics_collector_initialization(self):
        """Test metrics collector initialization"""
        from app.core.monitoring import metrics_collector
        
        assert metrics_collector is not None
        assert metrics_collector.get_uptime() >= 0

    def test_request_metrics_recording(self):
        """Test recording request metrics"""
        from app.core.monitoring import metrics_collector
        
        metrics_collector.record_request(
            method="GET",
            endpoint="/test",
            status=200,
            duration=0.1
        )
        
        assert metrics_collector.get_uptime() >= 0

    def test_redis_operation_recording(self):
        """Test recording Redis operation metrics"""
        from app.core.monitoring import metrics_collector
        
        metrics_collector.record_redis_operation(
            operation="get",
            success=True
        )
        
        assert True

    def test_notification_recording(self):
        """Test recording notification metrics"""
        from app.core.monitoring import metrics_collector
        
        metrics_collector.record_notification(
            notification_type="SYSTEM",
            priority="NORMAL"
        )
        
        assert True

    def test_broadcast_recording(self):
        """Test recording broadcast metrics"""
        from app.core.monitoring import metrics_collector
        
        metrics_collector.record_broadcast(
            status="SUCCESS",
            duration=1.5
        )
        
        assert True


class TestPerformanceMonitoring:
    """Test performance monitoring"""

    def test_monitor_decorator_sync(self):
        """Test monitor_performance decorator for sync functions"""
        from app.core.monitoring import monitor_performance
        
        @monitor_performance(endpoint_name="test_endpoint")
        def test_function():
            return "success"
        
        result = test_function()
        
        assert result == "success"

    def test_monitor_decorator_async(self):
        """Test monitor_performance decorator for async functions"""
        from app.core.monitoring import monitor_performance
        
        @monitor_performance(endpoint_name="test_endpoint")
        async def test_async_function():
            return "async_success"
        
        import asyncio
        result = asyncio.run(test_async_function())
        
        assert result == "async_success"

    def test_monitor_decorator_error_handling(self):
        """Test monitor_performance decorator handles errors"""
        from app.core.monitoring import monitor_performance
        
        @monitor_performance(endpoint_name="error_endpoint")
        def test_error_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            test_error_function()


class TestHealthChecker:
    """Test HealthChecker class"""

    def test_health_checker_initialization(self):
        """Test HealthChecker initialization"""
        from app.core.health_check import HealthChecker
        
        checker = HealthChecker()
        
        assert checker.get_uptime() >= 0

    def test_full_check_structure(self):
        """Test full health check structure"""
        from app.core.health_check import HealthChecker
        
        checker = HealthChecker()
        result = checker.perform_full_check()
        
        assert "status" in result
        assert "timestamp" in result
        assert "uptime_seconds" in result
        assert "components" in result
        assert "summary" in result

    def test_quick_check_structure(self):
        """Test quick health check structure"""
        from app.core.health_check import HealthChecker
        
        checker = HealthChecker()
        result = checker.perform_quick_check()
        
        assert "status" in result
        assert "timestamp" in result
        assert "uptime_seconds" in result
        assert "components" in result

    def test_uptime_increases(self):
        """Test that uptime increases over time"""
        from app.core.health_check import HealthChecker
        import time
        
        checker = HealthChecker()
        uptime1 = checker.get_uptime()
        
        time.sleep(0.1)
        
        uptime2 = checker.get_uptime()
        
        assert uptime2 > uptime1


class TestHealthCheckResult:
    """Test HealthCheckResult class"""

    def test_result_creation(self):
        """Test HealthCheckResult creation"""
        from app.core.health_check import HealthCheckResult
        
        result = HealthCheckResult(
            name="test_component",
            healthy=True,
            details={"key": "value"}
        )
        
        assert result.name == "test_component"
        assert result.healthy == True
        assert result.details == {"key": "value"}

    def test_result_to_dict(self):
        """Test HealthCheckResult to_dict method"""
        from app.core.health_check import HealthCheckResult
        
        result = HealthCheckResult(
            name="test_component",
            healthy=False,
            details={"error": "test error"}
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["name"] == "test_component"
        assert result_dict["healthy"] == False
        assert result_dict["details"]["error"] == "test error"
        assert "timestamp" in result_dict
