"""
API routes for Notification module.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.users import User
from app.schemas.notification import (
    BroadcastRequest,
    CreateNotificationRequest,
    MarkAsReadRequest,
    NotificationListItem,
    NotificationListResponse,
    NotificationResponse,
    NotificationStatsResponse,
    NotificationType,
)
from app.services.notification_service import NotificationService

router = APIRouter(tags=["通知管理"])


@router.get("", response_model=NotificationListResponse)
def get_notifications(
    notification_type: Optional[NotificationType] = Query(None),
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's notifications"""
    service = NotificationService(db)
    notifications, total = service.get_notifications(
        current_user.id,
        notification_type,
        unread_only,
        page,
        page_size,
    )
    
    unread_count = service.get_unread_count(current_user.id)
    
    return NotificationListResponse(
        notifications=[NotificationListItem.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size,
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific notification"""
    service = NotificationService(db)
    notification = service.get_notification(
        notification_id,
        current_user.id,
    )
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification


@router.post("/mark-as-read")
def mark_as_read(
    request: MarkAsReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark notifications as read"""
    service = NotificationService(db)
    count = service.mark_as_read(
        current_user.id,
        request.notification_ids,
    )
    
    return {
        "message": f"{count} notifications marked as read",
        "count": count,
    }


@router.post("/mark-all-as-read")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read"""
    service = NotificationService(db)
    count = service.mark_all_as_read(current_user.id)
    
    return {
        "message": f"All {count} notifications marked as read",
        "count": count,
    }


@router.get("/stats", response_model=NotificationStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get notification statistics"""
    service = NotificationService(db)
    stats = service.get_stats(current_user.id)
    return stats


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a notification"""
    service = NotificationService(db)
    success = service.delete_notification(
        notification_id,
        current_user.id,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification deleted"}


@router.post("/admin/create")
def create_notification(
    request: CreateNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a notification for a user (admin only).
    
    TODO: Add admin permission check
    """
    service = NotificationService(db)
    notification = service.create_notification(
        request,
        sender_id=current_user.id,
    )
    
    return NotificationResponse.model_validate(notification)


@router.post("/admin/broadcast")
def broadcast_notification(
    request: BroadcastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Broadcast notification to all users (admin only).
    
    TODO: Add admin permission check
    TODO: Implement fan-out to all users
    """
    service = NotificationService(db)
    count = service.broadcast(
        request,
        request.exclude_user_ids,
    )
    
    return {
        "message": "Broadcast created",
        "notification_count": count,
    }
