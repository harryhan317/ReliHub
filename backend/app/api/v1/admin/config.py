"""
Admin API - System Configuration
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.administrators import AdminUser
from app.schemas.admin import (
    SystemConfigListResponse,
    SystemConfigResponse,
    SystemConfigUpdateRequest,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/system-configs", tags=["Admin - Config"])


@router.get("", response_model=SystemConfigListResponse)
def list_system_configs(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    List all system configurations.
    """
    service = AdminService(db, admin)
    configs = service.list_system_configs()
    
    return SystemConfigListResponse(
        configs=[SystemConfigResponse.model_validate(c) for c in configs],
        total=len(configs)
    )


@router.patch("", response_model=SystemConfigResponse)
def update_system_config(
    request: SystemConfigUpdateRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Update or create a system configuration.
    
    - **config_key**: Configuration key
    - **config_value**: Configuration value
    - **description**: Optional description
    """
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    config = service.update_system_config(request, ip_address=ip_address)
    return SystemConfigResponse.model_validate(config)
