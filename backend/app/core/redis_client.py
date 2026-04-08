"""
Redis client configuration and connection management.

Features:
- Automatic reconnection with exponential backoff
- Health check mechanism
- Connection state monitoring
- Thread-safe operations
"""
import logging
import threading
import time
from datetime import datetime
from typing import Optional

import redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client wrapper with fallback support and high availability"""

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._is_available = False
        self._connection_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 1
        self._max_reconnect_delay = 30
        self._last_health_check: Optional[datetime] = None
        self._health_check_interval = 30
        self._lock = threading.Lock()
        self._metrics = {
            "total_operations": 0,
            "failed_operations": 0,
            "reconnect_count": 0,
            "last_error": None,
        }
        self._connect()

    def _connect(self) -> None:
        """Establish Redis connection with retry logic"""
        with self._lock:
            try:
                self._client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=self._health_check_interval,
                )
                self._client.ping()
                self._is_available = True
                self._connection_attempts = 0
                self._reconnect_delay = 1
                self._last_health_check = datetime.utcnow()
                logger.info("Redis connection established successfully")
            except (RedisError, Exception) as e:
                self._is_available = False
                self._client = None
                self._metrics["last_error"] = str(e)
                logger.warning(
                    f"Redis connection failed: {e}. Falling back to in-memory storage. "
                    f"Attempt {self._connection_attempts + 1}/{self._max_reconnect_attempts}"
                )

    def _reconnect(self) -> bool:
        """
        Attempt to reconnect to Redis with exponential backoff.
        
        Returns:
            bool: True if reconnection successful, False otherwise
        """
        with self._lock:
            if self._is_available:
                return True
            
            self._connection_attempts += 1
            
            if self._connection_attempts > self._max_reconnect_attempts:
                logger.error(
                    f"Max reconnection attempts ({self._max_reconnect_attempts}) reached. "
                    "Giving up reconnection."
                )
                return False
            
            delay = min(
                self._reconnect_delay * (2 ** (self._connection_attempts - 1)),
                self._max_reconnect_delay
            )
            
            logger.info(
                f"Attempting Redis reconnection in {delay}s "
                f"(attempt {self._connection_attempts}/{self._max_reconnect_attempts})"
            )
            
            time.sleep(delay)
            
            try:
                self._client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=self._health_check_interval,
                )
                self._client.ping()
                self._is_available = True
                self._connection_attempts = 0
                self._reconnect_delay = 1
                self._last_health_check = datetime.utcnow()
                self._metrics["reconnect_count"] += 1
                logger.info("Redis reconnection successful")
                return True
            except (RedisError, Exception) as e:
                self._is_available = False
                self._client = None
                self._metrics["last_error"] = str(e)
                logger.error(f"Redis reconnection failed: {e}")
                return False

    def _check_health(self) -> bool:
        """
        Perform health check on Redis connection.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        if not self._client:
            return False
        
        now = datetime.utcnow()
        
        if self._last_health_check:
            elapsed = (now - self._last_health_check).total_seconds()
            if elapsed < self._health_check_interval:
                return self._is_available
        
        try:
            self._client.ping()
            self._is_available = True
            self._last_health_check = now
            return True
        except (RedisError, Exception) as e:
            logger.warning(f"Redis health check failed: {e}")
            self._is_available = False
            self._metrics["last_error"] = str(e)
            return False

    def _execute_with_retry(self, operation, *args, **kwargs):
        """
        Execute Redis operation with automatic retry on failure.
        
        Args:
            operation: Redis operation to execute
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Operation result or None on failure
        """
        self._metrics["total_operations"] += 1
        
        if not self._check_health():
            if not self._reconnect():
                self._metrics["failed_operations"] += 1
                return None
        
        try:
            result = operation(*args, **kwargs)
            self._last_health_check = datetime.utcnow()
            return result
        except RedisError as e:
            logger.error(f"Redis operation failed: {e}")
            self._is_available = False
            self._metrics["failed_operations"] += 1
            self._metrics["last_error"] = str(e)
            
            if self._reconnect():
                try:
                    result = operation(*args, **kwargs)
                    self._last_health_check = datetime.utcnow()
                    return result
                except RedisError as retry_error:
                    logger.error(f"Redis operation failed after reconnection: {retry_error}")
                    self._metrics["failed_operations"] += 1
                    return None
            
            return None

    @property
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self._is_available

    def get_metrics(self) -> dict:
        """
        Get Redis client metrics.
        
        Returns:
            dict: Metrics including operation counts and connection status
        """
        return {
            **self._metrics,
            "is_available": self._is_available,
            "connection_attempts": self._connection_attempts,
            "last_health_check": self._last_health_check.isoformat() if self._last_health_check else None,
        }

    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if not self._client:
            return None
        return self._execute_with_retry(self._client.get, key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set key-value pair with optional expiration"""
        if not self._client:
            return False
        result = self._execute_with_retry(self._client.set, key, value, ex=ex)
        return result is not None and result

    def delete(self, key: str) -> bool:
        """Delete key"""
        if not self._client:
            return False
        result = self._execute_with_retry(self._client.delete, key)
        return result is not None and result > 0

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self._client:
            return False
        result = self._execute_with_retry(self._client.exists, key)
        return result is not None and result > 0

    def sadd(self, key: str, *values: str) -> bool:
        """Add members to a set"""
        if not self._client:
            return False
        result = self._execute_with_retry(self._client.sadd, key, *values)
        return result is not None and result > 0

    def sismember(self, key: str, value: str) -> bool:
        """Check if value is member of set"""
        if not self._client:
            return False
        result = self._execute_with_retry(self._client.sismember, key, value)
        return result is not None and result

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        if not self._client:
            return False
        result = self._execute_with_retry(self._client.expire, key, seconds)
        return result is not None and result

    def force_reconnect(self) -> bool:
        """
        Force a reconnection attempt.
        
        Returns:
            bool: True if reconnection successful
        """
        self._is_available = False
        self._client = None
        return self._reconnect()


redis_client = RedisClient()
