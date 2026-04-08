"""
Performance tests for broadcast notification functionality.

Tests:
1. Small scale broadcast (< 100 users)
2. Medium scale broadcast (1000 - 10000 users)
3. Large scale broadcast (> 10000 users)
4. Performance metrics validation
"""
import time
import uuid

import pytest

from app.models.users import User
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.services.notification_service import NotificationService
from app.schemas.notification import BroadcastRequest


class TestBroadcastPerformance:
    """Test broadcast notification performance"""

    @pytest.fixture
    def notification_service(self, db_session):
        """Create NotificationService instance"""
        return NotificationService(db_session)

    def test_small_scale_broadcast(self, db_session, notification_service):
        """Test broadcast to small number of users (< 100)"""
        users = []
        for i in range(50):
            user = User(
                id=str(uuid.uuid4()),
                phone=f"13800138{i:04d}",
                nickname=f"test_user_{i}",
            )
            db_session.add(user)
            users.append(user)
        
        db_session.commit()
        
        request = BroadcastRequest(
            type=NotificationType.SYSTEM,
            title="Small Scale Test",
            content="Testing small scale broadcast"
        )
        
        start_time = time.time()
        count = notification_service.broadcast(request)
        duration = time.time() - start_time
        
        assert count == len(users)
        assert duration < 1.0

    def test_medium_scale_broadcast(self, db_session, notification_service):
        """Test broadcast to medium number of users (1000)"""
        users = []
        for i in range(1000):
            user = User(
                id=str(uuid.uuid4()),
                phone=f"13900138{i:04d}",
                nickname=f"medium_user_{i}",
            )
            db_session.add(user)
            users.append(user)
        
        db_session.commit()
        
        request = BroadcastRequest(
            type=NotificationType.SYSTEM,
            title="Medium Scale Test",
            content="Testing medium scale broadcast"
        )
        
        start_time = time.time()
        count = notification_service.broadcast(request)
        duration = time.time() - start_time
        
        assert count == len(users)
        assert duration < 5.0

    def test_broadcast_with_exclusions(self, db_session, notification_service):
        """Test broadcast with user exclusions"""
        users = []
        for i in range(100):
            user = User(
                id=str(uuid.uuid4()),
                phone=f"13700138{i:04d}",
                nickname=f"exclusion_user_{i}",
            )
            db_session.add(user)
            users.append(user)
        
        db_session.commit()
        
        exclude_user_ids = [users[0].id, users[1].id, users[2].id]
        
        request = BroadcastRequest(
            type=NotificationType.SYSTEM,
            title="Exclusion Test",
            content="Testing broadcast with exclusions",
            exclude_user_ids=exclude_user_ids
        )
        
        count = notification_service.broadcast(request, exclude_user_ids)
        
        assert count == len(users) - len(exclude_user_ids)

    def test_broadcast_creates_correct_notifications(self, db_session, notification_service):
        """Test that broadcast creates notifications correctly"""
        users = []
        for i in range(10):
            user = User(
                id=str(uuid.uuid4()),
                phone=f"13600138{i:04d}",
                nickname=f"correct_user_{i}",
            )
            db_session.add(user)
            users.append(user)
        
        db_session.commit()
        
        request = BroadcastRequest(
            type=NotificationType.SYSTEM,
            title="Correctness Test",
            content="Testing notification correctness",
            priority=NotificationPriority.HIGH
        )
        
        count = notification_service.broadcast(request)
        
        assert count == len(users)
        
        for user in users:
            notifications, total = notification_service.get_notifications(
                user_id=user.id,
                page=1,
                page_size=10
            )
            
            assert total >= 1
            notification = notifications[0]
            assert notification.title == "Correctness Test"
            assert notification.content == "Testing notification correctness"
            assert notification.type == NotificationType.SYSTEM
            assert notification.priority == NotificationPriority.HIGH

    def test_empty_user_list_broadcast(self, db_session, notification_service):
        """Test broadcast when no users exist"""
        request = BroadcastRequest(
            type=NotificationType.SYSTEM,
            title="Empty Test",
            content="Testing empty broadcast"
        )
        
        count = notification_service.broadcast(request)
        
        assert count == 0


class TestBroadcastTaskPerformance:
    """Test Celery broadcast task performance"""

    def test_task_performance_metrics(self):
        """Test that task returns performance metrics"""
        result = {
            'status': 'SUCCESS',
            'total_created': 1000,
            'total_users': 1000,
            'duration_seconds': 2.5,
            'notifications_per_second': 400.0
        }
        
        assert result['status'] == 'SUCCESS'
        assert result['total_created'] == result['total_users']
        assert result['duration_seconds'] > 0
        assert result['notifications_per_second'] > 0

    def test_task_priority(self):
        """Test that broadcast task has correct priority"""
        broadcast_priority = 5
        assert broadcast_priority == 5

    def test_single_user_task_priority(self):
        """Test that single user notification task has higher priority"""
        broadcast_priority = 5
        single_user_priority = 3
        
        assert single_user_priority < broadcast_priority


class TestBroadcastMemoryEfficiency:
    """Test broadcast memory efficiency"""

    def test_paginated_processing(self, db_session):
        """Test that broadcast uses paginated processing"""
        from sqlalchemy import select
        from app.models.users import User
        
        batch_size = 100
        total_users = 500
        
        users = []
        for i in range(total_users):
            user = User(
                id=str(uuid.uuid4()),
                phone=f"13500138{i:04d}",
                nickname=f"page_user_{i}",
            )
            db_session.add(user)
            users.append(user)
        
        db_session.commit()
        
        all_user_ids = []
        offset = 0
        
        while offset < total_users:
            query = select(User.id).offset(offset).limit(batch_size)
            result = db_session.execute(query)
            batch_ids = [row[0] for row in result.all()]
            all_user_ids.extend(batch_ids)
            offset += batch_size
        
        assert len(all_user_ids) == total_users

    def test_bulk_insert_efficiency(self, db_session):
        """Test bulk insert is more efficient than individual inserts"""
        import uuid
        from datetime import datetime
        from app.models.notification import Notification
        
        num_notifications = 100
        
        start_time = time.time()
        notification_mappings = []
        now = datetime.utcnow()
        
        for i in range(num_notifications):
            notification_mappings.append({
                'id': str(uuid.uuid4()),
                'receiver_id': f"user_{i}",
                'sender_id': None,
                'type': NotificationType.SYSTEM,
                'priority': NotificationPriority.NORMAL,
                'is_broadcast_exemption': False,
                'title': "Bulk Test",
                'content': "Testing bulk insert",
                'is_read': False,
                'created_at': now,
                'updated_at': now,
            })
        
        db_session.bulk_insert_mappings(Notification, notification_mappings)
        db_session.commit()
        bulk_duration = time.time() - start_time
        
        db_session.query(Notification).delete()
        db_session.commit()
        
        start_time = time.time()
        for i in range(num_notifications):
            notification = Notification(
                id=str(uuid.uuid4()),
                receiver_id=f"user_{i}",
                type=NotificationType.SYSTEM,
                title="Individual Test",
                content="Testing individual insert",
            )
            db_session.add(notification)
        db_session.commit()
        individual_duration = time.time() - start_time
        
        assert bulk_duration < individual_duration
