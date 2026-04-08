"""
Admin API - Dashboard
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.administrators import AdminUser
from app.schemas.admin import DashboardStatsResponse
from app.services.admin_service import AdminService

router = APIRouter(tags=["Admin - Dashboard"])


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Get dashboard statistics.
    """
    service = AdminService(db, admin)
    stats = service.get_dashboard_stats()
    return DashboardStatsResponse(**stats)
