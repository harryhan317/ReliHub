"""
API routes for Notification module.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationType,
    NotificationPriority,
    MarkAsReadRequest,
    CreateNotificationRequest,
    BroadcastRequest,
    NotificationResponse,
    NotificationListResponse,
    NotificationListItem,
    NotificationStatsResponse,
)
from app.models.users import User

router = APIRouter(prefix="/notifications", tags=["通知管理"])


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    notification_type: Optional[NotificationType] = Query(None),
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's notifications"""
    service = NotificationService(db)
    notifications, total = await service.get_notifications(
        current_user.user_uuid,
        notification_type,
        unread_only,
        page,
        page_size,
    )
    
    # Get unread count
    unread_count = await service.get_unread_count(current_user.user_uuid)
    
    return NotificationListResponse(
        notifications=[NotificationListItem.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size,
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific notification"""
    service = NotificationService(db)
    notification = await service.get_notification(
        notification_id,
        current_user.user_uuid,
    )
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification


@router.post("/mark-as-read")
async def mark_as_read(
    request: MarkAsReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark notifications as read"""
    service = NotificationService(db)
    count = await service.mark_as_read(
        current_user.user_uuid,
        request.notification_ids,
    )
    
    return {
        "message": f"{count} notifications marked as read",
        "count": count,
    }


@router.post("/mark-all-as-read")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read"""
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user.user_uuid)
    
    return {
        "message": f"All {count} notifications marked as read",
        "count": count,
    }


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get notification statistics"""
    service = NotificationService(db)
    stats = await service.get_stats(current_user.user_uuid)
    return stats


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a notification"""
    service = NotificationService(db)
    success = await service.delete_notification(
        notification_id,
        current_user.user_uuid,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification deleted"}


# ── Admin Routes ──────────────────────────────────────────────────────────────

@router.post("/admin/create")
async def create_notification(
    request: CreateNotificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a notification for a user (admin only).
    
    TODO: Add admin permission check
    """
    service = NotificationService(db)
    notification = await service.create_notification(
        request,
        sender_id=current_user.user_uuid,
    )
    
    return NotificationResponse.model_validate(notification)


@router.post("/admin/broadcast")
async def broadcast_notification(
    request: BroadcastRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Broadcast notification to all users (admin only).
    
    TODO: Add admin permission check
    TODO: Implement fan-out to all users
    """
    service = NotificationService(db)
    count = await service.broadcast(
        request,
        request.exclude_user_ids,
    )
    
    return {
        "message": "Broadcast created",
        "notification_count": count,
    }
