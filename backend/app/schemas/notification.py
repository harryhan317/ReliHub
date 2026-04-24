"""
Pydantic Schemas for Notification module.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificationType(str, Enum):
    """Notification type enum"""
    SYSTEM = "SYSTEM"
    INTERACTION = "INTERACTION"
    AUDIT = "AUDIT"
    REWARD = "REWARD"
    BROADCAST = "BROADCAST"


class NotificationPriority(str, Enum):
    """Notification priority enum"""
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class MarkAsReadRequest(BaseModel):
    """Request schema for marking notification as read"""
    notification_ids: List[str] = Field(..., min_length=1, description="List of notification IDs to mark as read")


class CreateNotificationRequest(BaseModel):
    """Request schema for creating a notification (admin use)"""
    receiver_id: str = Field(..., description="Receiver user ID")
    type: NotificationType = Field(..., description="Notification type")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL, description="Priority")
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=2000)
    link_url: Optional[str] = Field(None, max_length=500)


class BroadcastRequest(BaseModel):
    """Request schema for broadcasting notification"""
    type: NotificationType = Field(default=NotificationType.BROADCAST, description="Notification type")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL)
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=2000)
    link_url: Optional[str] = Field(None, max_length=500)
    exclude_user_ids: Optional[List[str]] = Field(None, description="User IDs to exclude from broadcast")


class NotificationResponse(BaseModel):
    """Response schema for a single notification"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    receiver_id: str
    sender_id: Optional[str] = None
    type: NotificationType
    priority: NotificationPriority
    is_broadcast_exemption: bool
    title: Optional[str] = None
    content: str
    link_url: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime


class NotificationListItem(BaseModel):
    """Response schema for notification list item"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    type: NotificationType
    priority: NotificationPriority
    title: Optional[str] = None
    content: str
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Response schema for notification list with pagination"""
    notifications: List[NotificationListItem]
    total: int
    unread_count: int
    page: int
    page_size: int


class NotificationStatsResponse(BaseModel):
    """Response schema for notification statistics"""
    total_count: int
    unread_count: int
    read_count: int
    by_type: dict
