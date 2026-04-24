"""
Monitoring module for application metrics and health checks.

Features:
- Prometheus metrics collection
- Health check endpoints
- Performance monitoring
- Alert configuration
"""
import time
from functools import wraps
from typing import Any, Callable

from prometheus_client import Counter, Gauge, Histogram, Info

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Active HTTP requests',
    ['method', 'endpoint']
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Active database connections'
)

REDIS_OPERATIONS = Counter(
    'redis_operations_total',
    'Total Redis operations',
    ['operation', 'status']
)

NOTIFICATION_SENT = Counter(
    'notifications_sent_total',
    'Total notifications sent',
    ['type', 'priority']
)

BROADCAST_OPERATIONS = Counter(
    'broadcast_operations_total',
    'Total broadcast operations',
    ['status']
)

BROADCAST_DURATION = Histogram(
    'broadcast_duration_seconds',
    'Broadcast operation duration',
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
)

USER_REGISTRATIONS = Counter(
    'user_registrations_total',
    'Total user registrations',
    ['method']
)

USER_LOGINS = Counter(
    'user_logins_total',
    'Total user logins',
    ['status']
)

APPLICATION_INFO = Info(
    'application',
    'Application information'
)

ERROR_COUNT = Counter(
    'application_errors_total',
    'Total application errors',
    ['type', 'endpoint']
)


class MetricsCollector:
    """Collect and manage application metrics"""
    
    def __init__(self):
        self._start_time = time.time()
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
    
    def increment_active_requests(self, method: str, endpoint: str):
        """Increment active requests counter"""
        ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()
    
    def decrement_active_requests(self, method: str, endpoint: str):
        """Decrement active requests counter"""
        ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()
    
    def record_redis_operation(self, operation: str, success: bool):
        """Record Redis operation metrics"""
        status = 'success' if success else 'failure'
        REDIS_OPERATIONS.labels(operation=operation, status=status).inc()
    
    def record_notification(self, notification_type: str, priority: str):
        """Record notification sent metrics"""
        NOTIFICATION_SENT.labels(type=notification_type, priority=priority).inc()
    
    def record_broadcast(self, status: str, duration: float = None):
        """Record broadcast operation metrics"""
        BROADCAST_OPERATIONS.labels(status=status).inc()
        if duration is not None:
            BROADCAST_DURATION.observe(duration)
    
    def record_user_registration(self, method: str):
        """Record user registration metrics"""
        USER_REGISTRATIONS.labels(method=method).inc()
    
    def record_user_login(self, success: bool):
        """Record user login metrics"""
        status = 'success' if success else 'failure'
        USER_LOGINS.labels(status=status).inc()
    
    def record_error(self, error_type: str, endpoint: str):
        """Record application error metrics"""
        ERROR_COUNT.labels(type=error_type, endpoint=endpoint).inc()
    
    def set_database_connections(self, count: int):
        """Set active database connections count"""
        DATABASE_CONNECTIONS.set(count)
    
    def set_application_info(self, version: str, environment: str):
        """Set application information"""
        APPLICATION_INFO.info({
            'version': version,
            'environment': environment,
            'uptime': str(time.time() - self._start_time)
        })
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return time.time() - self._start_time


metrics_collector = MetricsCollector()


def monitor_performance(endpoint_name: str = None):
    """
    Decorator to monitor function performance.
    
    Args:
        endpoint_name: Name of the endpoint (optional)
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            endpoint = endpoint_name or func.__name__
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                metrics_collector.record_request(
                    method='ASYNC',
                    endpoint=endpoint,
                    status=200,
                    duration=duration
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics_collector.record_request(
                    method='ASYNC',
                    endpoint=endpoint,
                    status=500,
                    duration=duration
                )
                metrics_collector.record_error(
                    error_type=type(e).__name__,
                    endpoint=endpoint
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            endpoint = endpoint_name or func.__name__
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                metrics_collector.record_request(
                    method='SYNC',
                    endpoint=endpoint,
                    status=200,
                    duration=duration
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics_collector.record_request(
                    method='SYNC',
                    endpoint=endpoint,
                    status=500,
                    duration=duration
                )
                metrics_collector.record_error(
                    error_type=type(e).__name__,
                    endpoint=endpoint
                )
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
