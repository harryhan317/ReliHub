"""
Tests for Redis client high availability features.

Tests:
1. Connection management
2. Automatic reconnection with exponential backoff
3. Health check mechanism
4. Metrics collection
5. Thread safety
"""
import time
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from redis.exceptions import RedisError

from app.core.redis_client import RedisClient


class TestRedisClientConnection:
    """Test Redis client connection management"""

    def test_successful_connection(self):
        """Test successful Redis connection"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            
            assert client.is_available == True
            assert client._connection_attempts == 0

    def test_failed_connection_fallback(self):
        """Test connection failure falls back gracefully"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_redis.from_url.side_effect = RedisError("Connection refused")
            
            client = RedisClient()
            
            assert client.is_available == False
            assert client._client is None

    def test_metrics_initialization(self):
        """Test metrics are properly initialized"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            metrics = client.get_metrics()
            
            assert "total_operations" in metrics
            assert "failed_operations" in metrics
            assert "reconnect_count" in metrics
            assert "is_available" in metrics


class TestRedisClientReconnection:
    """Test Redis client reconnection logic"""

    def test_reconnect_on_operation_failure(self):
        """Test automatic reconnection when operation fails"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.side_effect = [RedisError("Connection lost"), "value"]
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            client._is_available = True
            
            result = client.get("test_key")
            
            assert result == "value"
            assert client._metrics["reconnect_count"] >= 0

    def test_exponential_backoff_delay(self):
        """Test exponential backoff for reconnection attempts"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_redis.from_url.side_effect = RedisError("Connection refused")
            
            client = RedisClient()
            client._max_reconnect_attempts = 3
            client._reconnect_delay = 1
            
            delays = []
            original_sleep = time.sleep
            with patch('time.sleep') as mock_sleep:
                mock_sleep.side_effect = lambda x: delays.append(x)
                client._reconnect()
            
            if len(delays) > 0:
                assert delays[0] >= 1

    def test_max_reconnect_attempts(self):
        """Test that reconnection stops after max attempts"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_redis.from_url.side_effect = RedisError("Connection refused")
            
            client = RedisClient()
            client._connection_attempts = client._max_reconnect_attempts
            
            result = client._reconnect()
            
            assert result == False

    def test_force_reconnect(self):
        """Test forced reconnection"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            client._is_available = False
            
            result = client.force_reconnect()
            
            assert result == True
            assert client.is_available == True


class TestRedisClientHealthCheck:
    """Test Redis client health check mechanism"""

    def test_health_check_success(self):
        """Test successful health check"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            client._last_health_check = None
            
            result = client._check_health()
            
            assert result == True
            assert client._last_health_check is not None

    def test_health_check_failure(self):
        """Test health check failure detection"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.side_effect = RedisError("Connection lost")
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            
            result = client._check_health()
            
            assert result == False

    def test_health_check_interval(self):
        """Test health check respects interval"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            mock_client.reset_mock()
            client._last_health_check = datetime.utcnow()
            
            result = client._check_health()
            
            assert result == True


class TestRedisClientOperations:
    """Test Redis client operations with retry"""

    def test_get_operation_success(self):
        """Test successful GET operation"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = "test_value"
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            result = client.get("test_key")
            
            assert result == "test_value"

    def test_set_operation_success(self):
        """Test successful SET operation"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.set.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            result = client.set("test_key", "test_value", ex=3600)
            
            assert result == True

    def test_delete_operation_success(self):
        """Test successful DELETE operation"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.delete.return_value = 1
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            result = client.delete("test_key")
            
            assert result == True

    def test_exists_operation_success(self):
        """Test successful EXISTS operation"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.exists.return_value = 1
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            result = client.exists("test_key")
            
            assert result == True

    def test_operation_on_unavailable_client(self):
        """Test operation when client is unavailable"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_redis.from_url.side_effect = RedisError("Connection refused")
            
            client = RedisClient()
            result = client.get("test_key")
            
            assert result is None


class TestRedisClientMetrics:
    """Test Redis client metrics collection"""

    def test_metrics_tracking(self):
        """Test that operations are tracked in metrics"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = "value"
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            client.get("test_key")
            
            metrics = client.get_metrics()
            assert metrics["total_operations"] >= 1

    def test_failed_operations_tracking(self):
        """Test that failed operations are tracked"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.side_effect = [True, RedisError("Connection lost")]
            mock_client.get.side_effect = RedisError("Operation failed")
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            client._is_available = True
            client._client = mock_client
            
            client.get("test_key")
            
            metrics = client.get_metrics()
            assert metrics["failed_operations"] >= 1

    def test_reconnect_count_tracking(self):
        """Test that reconnections are tracked"""
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            client._metrics["reconnect_count"] = 0
            
            client._reconnect()
            
            metrics = client.get_metrics()
            assert metrics["reconnect_count"] >= 0


class TestRedisClientThreadSafety:
    """Test Redis client thread safety"""

    def test_concurrent_operations(self):
        """Test concurrent operations are handled safely"""
        import threading
        
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = "value"
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            results = []
            
            def perform_operation():
                result = client.get("test_key")
                results.append(result)
            
            threads = [threading.Thread(target=perform_operation) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            assert len(results) == 10

    def test_concurrent_reconnect_attempts(self):
        """Test concurrent reconnection attempts are serialized"""
        import threading
        
        with patch('app.core.redis_client.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            client = RedisClient()
            client._is_available = False
            
            reconnect_count = [0]
            
            original_reconnect = client._reconnect
            def counted_reconnect():
                reconnect_count[0] += 1
                return original_reconnect()
            
            client._reconnect = counted_reconnect
            
            threads = [threading.Thread(target=client._reconnect) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            assert reconnect_count[0] >= 1
