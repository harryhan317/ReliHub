"""
Service layer for Notification module.
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import uuid

from app.models.notification import Notification, NotificationType, NotificationPriority
from app.schemas.notification import (
    CreateNotificationRequest,
    BroadcastRequest,
    MarkAsReadRequest,
)


class NotificationService:
    """Service class for Notification management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        request: CreateNotificationRequest,
        sender_id: Optional[str] = None
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            id=str(uuid.uuid4()),
            receiver_id=request.receiver_id,
            sender_id=sender_id,
            type=request.type,
            priority=request.priority,
            is_broadcast_exemption=False,
            title=request.title,
            content=request.content,
            link_url=request.link_url,
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_notifications(
        self,
        user_id: str,
        notification_type: Optional[NotificationType] = None,
        unread_only: bool = False,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Notification], int]:
        """Get notifications for a user with pagination"""
        # Build filters
        filters = [Notification.receiver_id == user_id]
        
        if notification_type:
            filters.append(Notification.type == notification_type)
        
        if unread_only:
            filters.append(Notification.is_read == False)
        
        # Get total count
        count_query = select(func.count()).where(and_(*filters))
        total = (await self.db.execute(count_query)).scalar()
        
        # Get paginated results
        query = (
            select(Notification)
            .where(and_(*filters))
            .order_by(Notification.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        return list(notifications), total

    async def mark_as_read(
        self,
        user_id: str,
        notification_ids: List[str]
    ) -> int:
        """Mark notifications as read"""
        query = select(Notification).where(
            Notification.id.in_(notification_ids),
            Notification.receiver_id == user_id,
            Notification.is_read == False
        )
        
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            count += 1
        
        if count > 0:
            await self.db.commit()
        
        return count

    async def mark_all_as_read(
        self,
        user_id: str
    ) -> int:
        """Mark all notifications as read for a user"""
        query = select(Notification).where(
            Notification.receiver_id == user_id,
            Notification.is_read == False
        )
        
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            count += 1
        
        if count > 0:
            await self.db.commit()
        
        return count

    async def get_unread_count(
        self,
        user_id: str
    ) -> int:
        """Get unread notification count"""
        query = select(func.count()).where(
            Notification.receiver_id == user_id,
            Notification.is_read == False
        )
        
        result = await self.db.execute(query)
        return result.scalar()

    async def broadcast(
        self,
        request: BroadcastRequest,
        exclude_user_ids: Optional[List[str]] = None
    ) -> int:
        """Broadcast notification to all users"""
        # Get all user IDs (excluding specified ones)
        # Note: In production, you'd query the users table
        # For now, we'll create a placeholder implementation
        notification = Notification(
            id=str(uuid.uuid4()),
            receiver_id="BROADCAST",  # Special marker for broadcast
            sender_id=None,
            type=request.type,
            priority=request.priority,
            is_broadcast_exemption=True,
            title=request.title,
            content=request.content,
            link_url=request.link_url,
        )
        
        self.db.add(notification)
        await self.db.commit()
        
        # In production, this would fan out to all users
        # For now, return 1 to indicate the broadcast was created
        return 1

    async def get_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> Optional[Notification]:
        """Get a specific notification"""
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.receiver_id == user_id
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """Delete a notification"""
        notification = await self.get_notification(notification_id, user_id)
        
        if not notification:
            return False
        
        await self.db.delete(notification)
        await self.db.commit()
        return True

    async def get_stats(
        self,
        user_id: str
    ) -> dict:
        """Get notification statistics"""
        # Total count
        total_query = select(func.count()).where(
            Notification.receiver_id == user_id
        )
        total = (await self.db.execute(total_query)).scalar()
        
        # Unread count
        unread_query = select(func.count()).where(
            Notification.receiver_id == user_id,
            Notification.is_read == False
        )
        unread = (await self.db.execute(unread_query)).scalar()
        
        # By type
        type_query = select(
            Notification.type,
            func.count()
        ).where(
            Notification.receiver_id == user_id
        ).group_by(Notification.type)
        
        type_result = await self.db.execute(type_query)
        by_type = {row[0].value: row[1] for row in type_result.all()}
        
        return {
            "total_count": total,
            "unread_count": unread,
            "read_count": total - unread,
            "by_type": by_type,
        }
