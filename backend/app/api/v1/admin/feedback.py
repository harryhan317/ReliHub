"""
Admin API - Feedback Management
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.administrators import AdminUser
from app.schemas.admin import (
    FeedbackListResponse,
    FeedbackReplyRequest,
    FeedbackResponse,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/feedbacks", tags=["Admin - Feedback"])


@router.get("", response_model=FeedbackListResponse)
def list_feedbacks(
    status: Optional[str] = Query(None, description="Filter by feedback status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    List all feedbacks with pagination and filtering.
    
    - **status**: Filter by status (PENDING, RESOLVED, CLOSED)
    """
    service = AdminService(db, admin)
    feedbacks, total = service.list_feedbacks(status=status, page=page, page_size=page_size)
    
    return FeedbackListResponse(
        feedbacks=[FeedbackResponse.model_validate(f) for f in feedbacks],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(
    feedback_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Get feedback details by ID.
    """
    service = AdminService(db, admin)
    feedback = service.get_feedback(feedback_id)
    
    if not feedback:
        from app.core.exceptions import BusinessException, ErrorCode
        raise BusinessException(ErrorCode.ADMIN_4007, "反馈不存在")
    
    return FeedbackResponse.model_validate(feedback)


@router.post("/{feedback_id}/reply", response_model=FeedbackResponse)
def reply_feedback(
    feedback_id: str,
    request: FeedbackReplyRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Reply to a user feedback.
    
    - **reply**: Reply content
    """
    service = AdminService(db, admin)
    ip_address = http_request.client.host if http_request.client else None
    feedback = service.reply_feedback(feedback_id, request, ip_address=ip_address)
    return FeedbackResponse.model_validate(feedback)
