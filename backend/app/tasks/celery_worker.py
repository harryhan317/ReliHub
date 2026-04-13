"""
Celery tasks for background processing.
"""
from app.celery_app import celery_app


@celery_app.task
def dummy_task():
    return "Task works"


@celery_app.task(bind=True, priority=5)
def broadcast_notification_task(
    self,
    notification_type: str,
    title: str,
    content: str,
    priority: str = "NORMAL",
    link_url: str = None,
    exclude_user_ids: list = None,
    batch_size: int = 1000
):
    """
    Celery task to broadcast notifications to all users with optimized performance.
    
    Performance optimizations:
    - Paginated user queries to avoid memory overload
    - Bulk insert using bulk_insert_mappings for faster database writes
    - Progress tracking for large broadcasts
    - Memory-efficient processing
    
    Args:
        self: Celery task instance
        notification_type: Type of notification
        title: Notification title
        content: Notification content
        priority: Notification priority (default: NORMAL)
        link_url: Optional link URL
        exclude_user_ids: List of user IDs to exclude
        batch_size: Number of users to process per batch (default: 1000)
    
    Returns:
        dict: Task result with total count and performance metrics
    """
    import time
    import uuid
    from datetime import datetime

    from sqlalchemy import func, select

    from app.core.database import SessionLocal
    from app.models.notification import (
        Notification,
        NotificationPriority,
        NotificationType,
    )
    from app.models.users import User
    
    start_time = time.time()
    db = SessionLocal()
    
    try:
        exclude_user_ids = exclude_user_ids or []
        
        count_query = select(func.count()).select_from(User)
        if exclude_user_ids:
            count_query = count_query.where(User.id.notin_(exclude_user_ids))
        
        total_users = db.execute(count_query).scalar()
        
        if total_users == 0:
            return {
                'status': 'SUCCESS',
                'total_created': 0,
                'total_users': 0,
                'duration_seconds': 0
            }
        
        total_created = 0
        offset = 0
        
        while offset < total_users:
            query = select(User.id).offset(offset).limit(batch_size)
            if exclude_user_ids:
                query = query.where(User.id.notin_(exclude_user_ids))
            
            result = db.execute(query)
            batch_user_ids = [row[0] for row in result.all()]
            
            if not batch_user_ids:
                break
            
            notification_mappings = []
            now = datetime.utcnow()
            
            for user_id in batch_user_ids:
                notification_mappings.append({
                    'id': str(uuid.uuid4()),
                    'receiver_id': user_id,
                    'sender_id': None,
                    'type': NotificationType(notification_type),
                    'priority': NotificationPriority(priority),
                    'is_broadcast_exemption': False,
                    'title': title,
                    'content': content,
                    'link_url': link_url,
                    'is_read': False,
                    'created_at': now,
                    'updated_at': now,
                })
            
            if notification_mappings:
                db.bulk_insert_mappings(Notification, notification_mappings)
                db.commit()
                total_created += len(notification_mappings)
            
            offset += batch_size
            
            progress = min(offset, total_users)
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': progress,
                    'total': total_users,
                    'status': f'Created {total_created} notifications',
                    'percentage': round((progress / total_users) * 100, 2)
                }
            )
        
        duration = time.time() - start_time
        notifications_per_second = total_created / duration if duration > 0 else 0
        
        return {
            'status': 'SUCCESS',
            'total_created': total_created,
            'total_users': total_users,
            'duration_seconds': round(duration, 2),
            'notifications_per_second': round(notifications_per_second, 2)
        }
    
    except Exception as e:
        db.rollback()
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(e),
                'total_created': total_created if 'total_created' in locals() else 0
            }
        )
        raise
    
    finally:
        db.close()


@celery_app.task(bind=True, priority=3)
def send_notification_to_user(
    self,
    user_id: str,
    notification_type: str,
    title: str,
    content: str,
    priority: str = "NORMAL",
    link_url: str = None
):
    """
    Send notification to a specific user (high priority task).
    
    Args:
        self: Celery task instance
        user_id: Target user ID
        notification_type: Type of notification
        title: Notification title
        content: Notification content
        priority: Notification priority
        link_url: Optional link URL
    
    Returns:
        dict: Task result
    """
    import uuid

    from app.core.database import SessionLocal
    from app.models.notification import (
        Notification,
        NotificationPriority,
        NotificationType,
    )
    
    db = SessionLocal()
    
    try:
        notification = Notification(
            id=str(uuid.uuid4()),
            receiver_id=user_id,
            sender_id=None,
            type=NotificationType(notification_type),
            priority=NotificationPriority(priority),
            is_broadcast_exemption=False,
            title=title,
            content=content,
            link_url=link_url,
        )
        
        db.add(notification)
        db.commit()
        
        return {
            'status': 'SUCCESS',
            'notification_id': notification.id,
            'user_id': user_id
        }
    
    except Exception:
        db.rollback()
        raise
    
    finally:
        db.close()
