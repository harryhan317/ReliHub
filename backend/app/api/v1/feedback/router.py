"""
User API - Feedback Management
Provides endpoints for users to submit and view their feedbacks.
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.users import User
from app.models.feedback import Feedback, FeedbackStatus, FeedbackType
from app.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackDetailResponse,
    FeedbackListItem,
    FeedbackListResponse,
    FeedbackResponse,
)
from app.core.exceptions import BusinessException, ErrorCode

router = APIRouter(prefix="/feedback", tags=["User - Feedback"])


def create_feedback_record(
    db: Session,
    user_id: str,
    feedback_type: FeedbackType,
    content: str,
    images: Optional[list] = None,
    contact: Optional[str] = None
) -> Feedback:
    """Create a new feedback record."""
    feedback = Feedback(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=feedback_type,
        content=content,
        images=images,
        contact=contact,
        status=FeedbackStatus.PENDING
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.post("", response_model=FeedbackResponse, status_code=201)
def create_feedback(
    request: FeedbackCreateRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a new feedback.

    - **type**: Feedback type (BUG/SUGGESTION/CONTENT/OTHER)
    - **content**: Feedback content (10-500 characters)
    - **images**: Optional image URLs (max 3)
    - **contact**: Optional contact information
    """
    feedback = create_feedback_record(
        db=db,
        user_id=current_user.id,
        feedback_type=request.type,
        content=request.content,
        images=request.images,
        contact=request.contact
    )

    return FeedbackResponse(
        id=feedback.id,
        type=feedback.type.value,
        content=feedback.content,
        status=feedback.status.value,
        images=feedback.images,
        contact=feedback.contact,
        reply=feedback.reply,
        replied_by=feedback.replied_by,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at
    )


@router.get("/my", response_model=FeedbackListResponse)
def list_my_feedbacks(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=50, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's feedback list.

    - **page**: Page number (default: 1)
    - **size**: Page size (default: 20, max: 50)
    - **status**: Optional status filter (PENDING/RESOLVED/CLOSED)
    """
    query = db.query(Feedback).filter(Feedback.user_id == current_user.id)

    if status:
        try:
            status_enum = FeedbackStatus(status)
            query = query.filter(Feedback.status == status_enum)
        except ValueError:
            raise BusinessException(
                ErrorCode.FEEDBACK_4003,
                f"无效的状态值: {status}"
            )

    total = query.count()
    feedbacks = query.order_by(Feedback.created_at.desc())\
                     .offset((page - 1) * size)\
                     .limit(size)\
                     .all()

    items = [
        FeedbackListItem(
            id=f.id,
            type=f.type.value,
            content=f.content,
            status=f.status.value,
            created_at=f.created_at
        )
        for f in feedbacks
    ]

    return FeedbackListResponse(
        feedbacks=items,
        total=total,
        page=page,
        page_size=size
    )


@router.get("/{feedback_id}", response_model=FeedbackDetailResponse)
def get_feedback_detail(
    feedback_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get feedback detail by ID.

    Users can only view their own feedbacks.
    """
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.user_id == current_user.id
    ).first()

    if not feedback:
        raise BusinessException(
            ErrorCode.FEEDBACK_4041,
            "反馈不存在或无权访问"
        )

    reply_info = None
    if feedback.reply:
        reply_info = {
            "content": feedback.reply,
            "operator": feedback.replied_by,
            "replied_at": feedback.updated_at.isoformat() if feedback.updated_at else None
        }

    return FeedbackDetailResponse(
        id=feedback.id,
        type=feedback.type.value,
        content=feedback.content,
        images=feedback.images,
        contact=feedback.contact,
        status=feedback.status.value,
        reply=reply_info,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at
    )
