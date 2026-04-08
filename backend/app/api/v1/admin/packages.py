"""
Admin API - Asset Package Management
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.administrators import AdminUser
from app.schemas.admin import (
    AssetPackageListResponse,
    AssetPackageResponse,
    AssetPackageUpdateRequest,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/asset-packages", tags=["Admin - Packages"])


@router.get("", response_model=AssetPackageListResponse)
def list_asset_packages(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    List all asset packages.
    """
    service = AdminService(db, admin)
    packages = service.list_asset_packages()
    
    return AssetPackageListResponse(
        packages=[AssetPackageResponse.model_validate(p) for p in packages],
        total=len(packages)
    )


@router.patch("/{package_id}", response_model=AssetPackageResponse)
def update_asset_package(
    package_id: str,
    request: AssetPackageUpdateRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Update an asset package.
    
    - **price_beans**: Price in beans (1-100000)
    - **discount_rate**: Discount rate (0.0-1.0)
    """
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    package = service.update_asset_package(package_id, request, ip_address=ip_address)
    return AssetPackageResponse.model_validate(package)
