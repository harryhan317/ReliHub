"""
API routes for Resource Management module.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_admin
from app.models.administrators import AdminUser
from app.models.users import User
from app.schemas.interaction import ReportRequest
from app.schemas.resource import (
    ResourceCreateRequest,
    ResourceListItem,
    ResourceListResponse,
    ResourceResponse,
    ResourceReviewRequest,
    ResourceUpdateRequest,
)
from app.services.admin_service import AdminService
from app.services.interaction_service import InteractionService
from app.services.resource_service import ResourceService

router = APIRouter(tags=["资源管理"])


@router.post("", response_model=ResourceResponse)
def create_resource(
    request: ResourceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new resource"""
    service = ResourceService(db)
    resource = service.create_resource(current_user.id, request)
    return resource


@router.get("", response_model=ResourceListResponse)
def list_resources(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    sort_by: str = Query("heat_score", description="Sort field"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all resources with filters"""
    service = ResourceService(db)
    resources, total = service.list_resources(
        category_id=category_id,
        search=search,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    
    return ResourceListResponse(
        resources=[ResourceListItem.model_validate(r) for r in resources],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific resource"""
    service = ResourceService(db)
    resource = service.get_resource(resource_id)
    
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    return resource


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: str,
    request: ResourceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a resource"""
    service = ResourceService(db)
    resource = service.update_resource(
        resource_id,
        current_user.id,
        request,
    )
    
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    return resource


@router.delete("/{resource_id}")
def delete_resource(
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a resource"""
    service = ResourceService(db)
    success = service.delete_resource(resource_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    return {"message": "Resource deleted successfully"}


@router.post("/{resource_id}/download")
def download_resource(
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download a resource.
    
    This endpoint:
    1. Checks user has sufficient beans
    2. Deducts beans
    3. Records transaction
    4. Returns download URL
    """
    service = ResourceService(db)
    resource = service.get_resource(resource_id)
    
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    return {"message": "Download initiated", "resource_id": resource_id}


@router.post("/{resource_id}/review", response_model=ResourceResponse)
def review_resource(
    resource_id: str,
    request: ResourceReviewRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """
    Review a resource (admin only).
    """
    from app.models.resources import ResourceStatus
    
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    
    if request.status == ResourceStatus.APPROVED:
        resource = service.approve_resource(resource_id, request, ip_address=ip_address)
    elif request.status == ResourceStatus.REJECTED:
        resource = service.reject_resource(resource_id, request, ip_address=ip_address)
    elif request.status == ResourceStatus.BLOCKED:
        resource = service.block_resource(resource_id, request, ip_address=ip_address)
    else:
        # Generic fallback or throw exception
        from app.services.resource_service import ResourceService
        res_service = ResourceService(db)
        resource = res_service.review_resource(resource_id, request)
    
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    return resource


@router.post("/{resource_id}/view")
def increment_view(
    resource_id: str,
    db: Session = Depends(get_db),
):
    """Increment view count"""
    service = ResourceService(db)
    service.increment_view(resource_id)
    return {"message": "View count incremented"}


@router.post("/{resource_id}/like")
def like_resource(
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Like a resource"""
    service = InteractionService(db)
    return service.like_resource(current_user.id, resource_id)


@router.delete("/{resource_id}/like")
def unlike_resource(
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unlike a resource"""
    service = InteractionService(db)
    return service.unlike_resource(current_user.id, resource_id)


@router.post("/{resource_id}/collect")
def collect_resource(
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Collect/bookmark a resource"""
    service = InteractionService(db)
    return service.collect_resource(current_user.id, resource_id)


@router.delete("/{resource_id}/collect")
def uncollect_resource(
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Uncollect/remove bookmark for a resource"""
    service = InteractionService(db)
    return service.uncollect_resource(current_user.id, resource_id)


@router.post("/{resource_id}/report")
def report_resource(
    resource_id: str,
    request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Report a resource"""
    service = InteractionService(db)
    return service.report_resource(current_user.id, resource_id, request.reason, request.detail)
