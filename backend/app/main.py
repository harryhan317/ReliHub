"""
ReliHub MVP Backend – FastAPI application entry point.
"""
import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api import api_router
from app.core.config import settings
from app.core.exceptions import (
    BusinessException,
    business_exception_handler,
    generic_exception_handler,
)
from app.core.health_check import health_checker
from app.core.logging_config import setup_logging
from app.core.monitoring import metrics_collector

# 初始化日志配置
environment = os.getenv("ENVIRONMENT", "development")
setup_logging(environment)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="ReliHub MVP Backend API",
    version="1.0.0",
)

app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/api/v1/health", tags=["系统"])
def health_check():
    """Quick health check endpoint"""
    return health_checker.perform_quick_check()


@app.get("/api/v1/health/detailed", tags=["系统"])
def detailed_health_check():
    """Detailed health check with all components"""
    result = health_checker.perform_full_check()
    
    if result["status"] != "healthy":
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=result)
    
    return result


@app.get("/api/v1/metrics", tags=["系统"])
def metrics():
    """Prometheus metrics endpoint"""
    metrics_collector.set_application_info(
        version="1.0.0",
        environment=getattr(settings, 'ENVIRONMENT', 'development')
    )
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    metrics_collector.set_application_info(
        version="1.0.0",
        environment=getattr(settings, 'ENVIRONMENT', 'development')
    )
