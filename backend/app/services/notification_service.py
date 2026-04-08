"""
Service layer for Notification module.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType
from app.schemas.notification import (
    BroadcastRequest,
    CreateNotificationRequest,
)


class NotificationService:
    """Service class for Notification management"""

    def __init__(self, db: Session):
        self.db = db

    def create_notification(
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
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_notifications(
        self,
        user_id: str,
        notification_type: Optional[NotificationType] = None,
        unread_only: bool = False,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Notification], int]:
        """Get notifications for a user with pagination"""
        filters = [Notification.receiver_id == user_id]
        
        if notification_type:
            filters.append(Notification.type == notification_type)
        
        if unread_only:
            filters.append(Notification.is_read == False)
        
        count_query = select(func.count()).where(and_(*filters))
        total = self.db.execute(count_query).scalar()
        
        query = (
            select(Notification)
            .where(and_(*filters))
            .order_by(Notification.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = self.db.execute(query)
        notifications = result.scalars().all()
        
        return list(notifications), total

    def mark_as_read(
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
        
        result = self.db.execute(query)
        notifications = result.scalars().all()
        
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count

    def mark_all_as_read(
        self,
        user_id: str
    ) -> int:
        """Mark all notifications as read for a user"""
        query = select(Notification).where(
            Notification.receiver_id == user_id,
            Notification.is_read == False
        )
        
        result = self.db.execute(query)
        notifications = result.scalars().all()
        
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count

    def get_unread_count(
        self,
        user_id: str
    ) -> int:
        """Get unread notification count"""
        query = select(func.count()).where(
            Notification.receiver_id == user_id,
            Notification.is_read == False
        )
        
        result = self.db.execute(query)
        return result.scalar()

    def broadcast(
        self,
        request: BroadcastRequest,
        exclude_user_ids: Optional[List[str]] = None
    ) -> int:
        """Broadcast notification to all users"""
        notification = Notification(
            id=str(uuid.uuid4()),
            receiver_id="BROADCAST",
            sender_id=None,
            type=request.type,
            priority=request.priority,
            is_broadcast_exemption=True,
            title=request.title,
            content=request.content,
            link_url=request.link_url,
        )
        
        self.db.add(notification)
        self.db.commit()
        
        return 1

    def get_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> Optional[Notification]:
        """Get a specific notification"""
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.receiver_id == user_id
        )
        
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def delete_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """Delete a notification"""
        notification = self.get_notification(notification_id, user_id)
        
        if not notification:
            return False
        
        self.db.delete(notification)
        self.db.commit()
        return True

    def get_stats(
        self,
        user_id: str
    ) -> dict:
        """Get notification statistics"""
        total_query = select(func.count()).where(
            Notification.receiver_id == user_id
        )
        total = self.db.execute(total_query).scalar()
        
        unread_query = select(func.count()).where(
            Notification.receiver_id == user_id,
            Notification.is_read == False
        )
        unread = self.db.execute(unread_query).scalar()
        
        type_query = select(
            Notification.type,
            func.count()
        ).where(
            Notification.receiver_id == user_id
        ).group_by(Notification.type)
        
        type_result = self.db.execute(type_query)
        by_type = {row[0].value: row[1] for row in type_result.all()}
        
        return {
            "total_count": total,
            "unread_count": unread,
            "read_count": total - unread,
            "by_type": by_type,
        }
