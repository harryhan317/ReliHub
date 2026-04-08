"""
Admin API - Content Management
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.administrators import AdminUser
from app.schemas.admin import (
    ResourceListResponse,
    ResourceResponse,
    ResourceReviewRequest,
    TopicListResponse,
    TopicResponse,
)
from app.services.admin_service import AdminService

router = APIRouter(tags=["Admin - Content"])


@router.get("/resources/pending", response_model=ResourceListResponse)
def list_pending_resources(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    List all pending resources for review.
    """
    service = AdminService(db, admin)
    resources, total = service.list_pending_resources(page=page, page_size=page_size)
    
    return ResourceListResponse(
        resources=[ResourceResponse.model_validate(r) for r in resources],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/resources/{resource_id}/approve", response_model=ResourceResponse)
def approve_resource(
    resource_id: str,
    request: ResourceReviewRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Approve a pending resource.
    """
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    resource = service.approve_resource(resource_id, request, ip_address=ip_address)
    return ResourceResponse.model_validate(resource)


@router.post("/resources/{resource_id}/reject", response_model=ResourceResponse)
def reject_resource(
    resource_id: str,
    request: ResourceReviewRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Reject a pending resource.
    """
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    resource = service.reject_resource(resource_id, request, ip_address=ip_address)
    return ResourceResponse.model_validate(resource)


@router.post("/resources/{resource_id}/block", response_model=ResourceResponse)
def block_resource(
    resource_id: str,
    request: ResourceReviewRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Block an approved resource.
    """
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    resource = service.block_resource(resource_id, request, ip_address=ip_address)
    return ResourceResponse.model_validate(resource)


@router.get("/topics", response_model=TopicListResponse)
def list_topics(
    status: Optional[str] = Query(None, description="Filter by topic status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    List all topics with pagination and filtering.
    """
    service = AdminService(db, admin)
    topics, total = service.list_topics(status=status, page=page, page_size=page_size)
    
    return TopicListResponse(
        topics=[TopicResponse.model_validate(t) for t in topics],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/topics/{topic_id}/block", response_model=TopicResponse)
def block_topic(
    topic_id: str,
    request: ResourceReviewRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Block a topic.
    """
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    topic = service.block_topic(topic_id, request, ip_address=ip_address)
    return TopicResponse.model_validate(topic)
