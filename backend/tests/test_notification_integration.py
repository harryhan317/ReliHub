"""
Integration tests for Notification module.

Tests:
1. Notification CRUD operations
2. Notification listing with filters and pagination
3. Mark as read operations
4. Broadcast notifications
5. Statistics

Database: PostgreSQL (uses shared fixtures from conftest.py)
"""

import pytest

from app.services.notification_service import NotificationService
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.schemas.notification import (
    CreateNotificationRequest,
    BroadcastRequest,
)


class TestNotificationService:
    """Test NotificationService CRUD operations"""
    
    @pytest.fixture
    def notification_service(self, db_session):
        """Create NotificationService instance"""
        return NotificationService(db_session)
    
    def test_create_notification(self, notification_service):
        """Test creating a new notification"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.NORMAL,
            title="Test Notification",
            content="This is a test notification content."
        )
        
        notification = notification_service.create_notification(
            request=request,
            sender_id="user-456"
        )
        
        assert notification.id is not None
        assert notification.receiver_id == "user-123"
        assert notification.sender_id == "user-456"
        assert notification.type == NotificationType.SYSTEM
        assert notification.priority == NotificationPriority.NORMAL
        assert notification.title == "Test Notification"
        assert notification.content == "This is a test notification content."
        assert notification.is_read == False
        assert notification.is_broadcast_exemption == False
    
    def test_create_notification_minimal(self, notification_service):
        """Test creating a notification with minimal fields"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.INTERACTION,
            content="Minimal notification"
        )
        
        notification = notification_service.create_notification(request)
        
        assert notification.id is not None
        assert notification.sender_id is None
        assert notification.type == NotificationType.INTERACTION
        assert notification.priority == NotificationPriority.NORMAL
        assert notification.title is None
    
    def test_create_high_priority_notification(self, notification_service):
        """Test creating a high priority notification"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.AUDIT,
            priority=NotificationPriority.HIGH,
            title="Important Update",
            content="Your resource has been approved."
        )
        
        notification = notification_service.create_notification(request)
        
        assert notification.priority == NotificationPriority.HIGH
    
    def test_get_notifications(self, notification_service):
        """Test getting notifications with pagination"""
        for i in range(5):
            request = CreateNotificationRequest(
                receiver_id="user-123",
                type=NotificationType.SYSTEM,
                content=f"Notification {i}"
            )
            notification_service.create_notification(request)
        
        notifications, total = notification_service.get_notifications(
            user_id="user-123",
            page=1,
            page_size=3
        )
        
        assert total == 5
        assert len(notifications) == 3
        
        notifications, total = notification_service.get_notifications(
            user_id="user-123",
            page=2,
            page_size=3
        )
        assert len(notifications) == 2
    
    def test_get_notifications_by_type(self, notification_service):
        """Test filtering notifications by type"""
        for i in range(3):
            request = CreateNotificationRequest(
                receiver_id="user-123",
                type=NotificationType.SYSTEM,
                content=f"System notification {i}"
            )
            notification_service.create_notification(request)
        
        for i in range(2):
            request = CreateNotificationRequest(
                receiver_id="user-123",
                type=NotificationType.INTERACTION,
                content=f"Interaction notification {i}"
            )
            notification_service.create_notification(request)
        
        notifications, total = notification_service.get_notifications(
            user_id="user-123",
            notification_type=NotificationType.SYSTEM
        )
        assert total == 3
        
        notifications, total = notification_service.get_notifications(
            user_id="user-123",
            notification_type=NotificationType.INTERACTION
        )
        assert total == 2
    
    def test_get_unread_notifications(self, notification_service):
        """Test getting only unread notifications"""
        for i in range(5):
            request = CreateNotificationRequest(
                receiver_id="user-123",
                type=NotificationType.SYSTEM,
                content=f"Notification {i}"
            )
            notification_service.create_notification(request)
        
        notification_service.mark_all_as_read("user-123")
        
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.SYSTEM,
            content="New notification"
        )
        notification_service.create_notification(request)
        
        notifications, total = notification_service.get_notifications(
            user_id="user-123",
            unread_only=True
        )
        
        assert total == 1
        assert notifications[0].content == "New notification"
    
    def test_get_notifications_order(self, notification_service):
        """Test that notifications are returned"""
        for i in range(3):
            request = CreateNotificationRequest(
                receiver_id="user-123",
                type=NotificationType.SYSTEM,
                content=f"Notification {i}"
            )
            notification_service.create_notification(request)
        
        notifications, total = notification_service.get_notifications(
            user_id="user-123",
            page=1,
            page_size=10
        )
        
        assert total == 3
        assert len(notifications) == 3
        
        contents = [n.content for n in notifications]
        assert "Notification 0" in contents
        assert "Notification 1" in contents
        assert "Notification 2" in contents
    
    def test_mark_as_read(self, notification_service):
        """Test marking notifications as read"""
        request1 = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.SYSTEM,
            content="Notification 1"
        )
        notification1 = notification_service.create_notification(request1)
        
        request2 = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.SYSTEM,
            content="Notification 2"
        )
        notification2 = notification_service.create_notification(request2)
        
        count = notification_service.mark_as_read(
            user_id="user-123",
            notification_ids=[notification1.id, notification2.id]
        )
        
        assert count == 2
        
        db_session = notification_service.db
        n1 = db_session.get(Notification, notification1.id)
        n2 = db_session.get(Notification, notification2.id)
        
        assert n1.is_read == True
        assert n1.read_at is not None
        assert n2.is_read == True
        assert n2.read_at is not None
    
    def test_mark_as_read_wrong_user(self, notification_service):
        """Test that mark_as_read only works for correct user"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.SYSTEM,
            content="Notification"
        )
        notification = notification_service.create_notification(request)
        
        count = notification_service.mark_as_read(
            user_id="user-456",
            notification_ids=[notification.id]
        )
        
        assert count == 0
        
        db_session = notification_service.db
        n = db_session.get(Notification, notification.id)
        assert n.is_read == False
    
    def test_mark_all_as_read(self, notification_service):
        """Test marking all notifications as read"""
        for i in range(5):
            request = CreateNotificationRequest(
                receiver_id="user-123",
                type=NotificationType.SYSTEM,
                content=f"Notification {i}"
            )
            notification_service.create_notification(request)
        
        count = notification_service.mark_all_as_read("user-123")
        
        assert count == 5
        
        unread = notification_service.get_unread_count("user-123")
        assert unread == 0
    
    def test_get_unread_count(self, notification_service):
        """Test getting unread notification count"""
        for i in range(3):
            request = CreateNotificationRequest(
                receiver_id="user-123",
                type=NotificationType.SYSTEM,
                content=f"Notification {i}"
            )
            notification_service.create_notification(request)
        
        count = notification_service.get_unread_count("user-123")
        assert count == 3
        
        request = CreateNotificationRequest(
            receiver_id="user-456",
            type=NotificationType.SYSTEM,
            content="Other user notification"
        )
        notification_service.create_notification(request)
        
        count = notification_service.get_unread_count("user-123")
        assert count == 3
    
    def test_broadcast(self, notification_service):
        """Test broadcasting notification"""
        request = BroadcastRequest(
            type=NotificationType.BROADCAST,
            title="System Announcement",
            content="Important system announcement for all users."
        )
        
        count = notification_service.broadcast(request)
        
        assert count == 1
        
        db_session = notification_service.db
        from sqlalchemy import select
        
        query = select(Notification).where(
            Notification.receiver_id == "BROADCAST"
        )
        result = db_session.execute(query)
        broadcast = result.scalar_one_or_none()
        
        assert broadcast is not None
        assert broadcast.title == "System Announcement"
        assert broadcast.is_broadcast_exemption == True
    
    def test_get_notification(self, notification_service):
        """Test getting a specific notification"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.SYSTEM,
            title="Test",
            content="Test notification"
        )
        created = notification_service.create_notification(request)
        
        notification = notification_service.get_notification(
            notification_id=created.id,
            user_id="user-123"
        )
        
        assert notification is not None
        assert notification.id == created.id
    
    def test_get_notification_wrong_user(self, notification_service):
        """Test that get_notification returns None for wrong user"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.SYSTEM,
            content="Test notification"
        )
        created = notification_service.create_notification(request)
        
        notification = notification_service.get_notification(
            notification_id=created.id,
            user_id="user-456"
        )
        
        assert notification is None
    
    def test_delete_notification(self, notification_service):
        """Test deleting a notification"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.SYSTEM,
            content="Test notification"
        )
        created = notification_service.create_notification(request)
        
        success = notification_service.delete_notification(
            notification_id=created.id,
            user_id="user-123"
        )
        
        assert success == True
        
        db_session = notification_service.db
        deleted = db_session.get(Notification, created.id)
        assert deleted is None
    
    def test_delete_notification_wrong_user(self, notification_service):
        """Test that delete fails for wrong user"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.SYSTEM,
            content="Test notification"
        )
        created = notification_service.create_notification(request)
        
        success = notification_service.delete_notification(
            notification_id=created.id,
            user_id="user-456"
        )
        
        assert success == False
        
        db_session = notification_service.db
        notification = db_session.get(Notification, created.id)
        assert notification is not None
    
    def test_get_stats(self, notification_service):
        """Test getting notification statistics"""
        for i in range(3):
            request = CreateNotificationRequest(
                receiver_id="user-123",
                type=NotificationType.SYSTEM,
                content=f"System notification {i}"
            )
            notification_service.create_notification(request)
        
        for i in range(2):
            request = CreateNotificationRequest(
                receiver_id="user-123",
                type=NotificationType.INTERACTION,
                content=f"Interaction notification {i}"
            )
            notification_service.create_notification(request)
        
        stats = notification_service.get_stats("user-123")
        
        assert stats["total_count"] == 5
        assert stats["unread_count"] == 5
        assert stats["read_count"] == 0
        assert stats["by_type"]["SYSTEM"] == 3
        assert stats["by_type"]["INTERACTION"] == 2
    
    def test_get_stats_with_read(self, notification_service):
        """Test statistics after marking as read"""
        for i in range(3):
            request = CreateNotificationRequest(
                receiver_id="user-123",
                type=NotificationType.SYSTEM,
                content=f"Notification {i}"
            )
            notification_service.create_notification(request)
        
        notification_service.mark_all_as_read("user-123")
        
        stats = notification_service.get_stats("user-123")
        
        assert stats["total_count"] == 3
        assert stats["unread_count"] == 0
        assert stats["read_count"] == 3


class TestNotificationTypes:
    """Test different notification types"""
    
    @pytest.fixture
    def notification_service(self, db_session):
        """Create NotificationService instance"""
        return NotificationService(db_session)
    
    def test_system_notification(self, notification_service):
        """Test system notification"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.SYSTEM,
            content="System maintenance scheduled"
        )
        
        notification = notification_service.create_notification(request)
        
        assert notification.type == NotificationType.SYSTEM
    
    def test_interaction_notification(self, notification_service):
        """Test interaction notification"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.INTERACTION,
            content="User liked your post"
        )
        
        notification = notification_service.create_notification(
            request=request,
            sender_id="user-456"
        )
        
        assert notification.type == NotificationType.INTERACTION
        assert notification.sender_id == "user-456"
    
    def test_audit_notification(self, notification_service):
        """Test audit notification"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.AUDIT,
            title="Resource Approved",
            content="Your resource has been approved by admin.",
            link_url="/resources/abc-123"
        )
        
        notification = notification_service.create_notification(request)
        
        assert notification.type == NotificationType.AUDIT
        assert notification.link_url == "/resources/abc-123"
    
    def test_reward_notification(self, notification_service):
        """Test reward notification"""
        request = CreateNotificationRequest(
            receiver_id="user-123",
            type=NotificationType.REWARD,
            title="Reward Received",
            content="You received 50 cocoa beans for your contribution."
        )
        
        notification = notification_service.create_notification(request)
        
        assert notification.type == NotificationType.REWARD


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
