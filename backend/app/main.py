"""
ReliHub MVP Backend – FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import (
    BusinessException,
    business_exception_handler,
    generic_exception_handler,
)
from app.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="ReliHub MVP Backend API",
    version="1.0.0",
)

# ── Exception Handlers ────────────────────────────────────────────────────────
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/api/v1/health", tags=["系统"])
def health_check():
    return {"status": "ok", "message": "ReliHub backend is running"}
