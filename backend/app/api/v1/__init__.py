"""
API v1 package.
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .resources import router as resources_router

# Import new routers for Sprint B
from .ai import router as ai_router
from .community import router as community_router
from .ledger import router as ledger_router
from .notification import router as notification_router
from .files import router as files_router

# Create main v1 router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(users_router, prefix="/users")
api_router.include_router(resources_router, prefix="/resources")

# Sprint B routers
api_router.include_router(ai_router, prefix="/ai")
api_router.include_router(community_router, prefix="/community")
api_router.include_router(ledger_router, prefix="/ledger")
api_router.include_router(notification_router, prefix="/notifications")
api_router.include_router(files_router, prefix="/files")

router = api_router
