"""
Health check module for monitoring system components.

Features:
- Database health check
- Redis health check
- System resource monitoring
- Detailed health status reporting
"""
import time
from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.redis_client import redis_client
from app.core.config import settings


class HealthCheckResult:
    """Health check result for a single component"""
    
    def __init__(self, name: str, healthy: bool, details: Dict[str, Any] = None):
        self.name = name
        self.healthy = healthy
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "healthy": self.healthy,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


class HealthChecker:
    """System health checker"""
    
    def __init__(self):
        self._start_time = time.time()
    
    def check_database(self) -> HealthCheckResult:
        """Check database connectivity and performance"""
        db = SessionLocal()
        
        try:
            start = time.time()
            result = db.execute(text("SELECT 1")).scalar()
            latency = (time.time() - start) * 1000
            
            if result == 1:
                return HealthCheckResult(
                    name="database",
                    healthy=True,
                    details={
                        "type": "postgresql",
                        "latency_ms": round(latency, 2),
                        "status": "connected"
                    }
                )
            else:
                return HealthCheckResult(
                    name="database",
                    healthy=False,
                    details={
                        "error": "Unexpected query result",
                        "status": "error"
                    }
                )
        
        except Exception as e:
            return HealthCheckResult(
                name="database",
                healthy=False,
                details={
                    "error": str(e),
                    "status": "disconnected"
                }
            )
        
        finally:
            db.close()
    
    def check_redis(self) -> HealthCheckResult:
        """Check Redis connectivity and performance"""
        try:
            start = time.time()
            is_available = redis_client.is_available
            latency = (time.time() - start) * 1000
            
            if is_available:
                metrics = redis_client.get_metrics()
                return HealthCheckResult(
                    name="redis",
                    healthy=True,
                    details={
                        "latency_ms": round(latency, 2),
                        "status": "connected",
                        "metrics": {
                            "total_operations": metrics.get("total_operations", 0),
                            "failed_operations": metrics.get("failed_operations", 0),
                            "reconnect_count": metrics.get("reconnect_count", 0)
                        }
                    }
                )
            else:
                return HealthCheckResult(
                    name="redis",
                    healthy=False,
                    details={
                        "status": "disconnected",
                        "fallback": "in_memory_storage"
                    }
                )
        
        except Exception as e:
            return HealthCheckResult(
                name="redis",
                healthy=False,
                details={
                    "error": str(e),
                    "status": "error"
                }
            )
    
    def check_system_resources(self) -> HealthCheckResult:
        """Check system resource usage"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            healthy = (
                cpu_percent < 90 and
                memory.percent < 90 and
                disk.percent < 90
            )
            
            return HealthCheckResult(
                name="system_resources",
                healthy=healthy,
                details={
                    "cpu_percent": round(cpu_percent, 2),
                    "memory_percent": round(memory.percent, 2),
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_percent": round(disk.percent, 2),
                    "disk_free_gb": round(disk.free / (1024**3), 2)
                }
            )
        
        except ImportError:
            return HealthCheckResult(
                name="system_resources",
                healthy=True,
                details={
                    "status": "monitoring_unavailable",
                    "message": "psutil not installed"
                }
            )
        
        except Exception as e:
            return HealthCheckResult(
                name="system_resources",
                healthy=False,
                details={
                    "error": str(e)
                }
            )
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return time.time() - self._start_time
    
    def perform_full_check(self) -> Dict[str, Any]:
        """Perform full health check on all components"""
        checks = [
            self.check_database(),
            self.check_redis(),
            self.check_system_resources()
        ]
        
        all_healthy = all(check.healthy for check in checks)
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": round(self.get_uptime(), 2),
            "version": settings.VERSION if hasattr(settings, 'VERSION') else "1.0.0",
            "environment": settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else "development",
            "components": [check.to_dict() for check in checks],
            "summary": {
                "total_components": len(checks),
                "healthy_components": sum(1 for c in checks if c.healthy),
                "unhealthy_components": sum(1 for c in checks if not c.healthy)
            }
        }
    
    def perform_quick_check(self) -> Dict[str, Any]:
        """Perform quick health check (no system resources)"""
        checks = [
            self.check_database(),
            self.check_redis()
        ]
        
        all_healthy = all(check.healthy for check in checks)
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": round(self.get_uptime(), 2),
            "components": [check.to_dict() for check in checks]
        }


health_checker = HealthChecker()
