"""
Pydantic Schemas for Admin module.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AdminRole(str, Enum):
    """Admin role enum"""
    SUPER_ADMIN = "SUPER_ADMIN"
    OPERATOR = "OPERATOR"
    AUDITOR = "AUDITOR"


class UserStatus(str, Enum):
    """User status enum"""
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    LOCKED = "LOCKED"
    HIBERNATED = "HIBERNATED"


class FeedbackStatus(str, Enum):
    """Feedback status enum"""
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class BanUserRequest(BaseModel):
    """Request schema for banning a user"""
    reason: str = Field(..., min_length=1, max_length=500, description="Ban reason")
    duration_days: Optional[int] = Field(None, ge=1, description="Ban duration in days (None for permanent)")


class LockUserRequest(BaseModel):
    """Request schema for locking a user"""
    reason: str = Field(..., min_length=1, max_length=500, description="Lock reason")


class ResourceReviewRequest(BaseModel):
    """Request schema for resource review"""
    reason: Optional[str] = Field(None, max_length=500, description="Review reason/notes")


class FeedbackReplyRequest(BaseModel):
    """Request schema for replying to feedback"""
    reply: str = Field(..., min_length=1, max_length=2000, description="Reply content")


import re


class SystemConfigUpdateRequest(BaseModel):
    """Request schema for updating system config"""
    config_key: str = Field(..., min_length=1, max_length=100)
    config_value: str = Field(..., max_length=5000)
    description: Optional[str] = Field(None, max_length=500)
    
    def validate_config_key(self) -> str:
        """Validate config_key format"""
        if not re.match(r'^[a-zA-Z0-9_]+$', self.config_key):
            raise ValueError('配置键只能包含字母、数字和下划线')
        return self.config_key


class AssetPackageUpdateRequest(BaseModel):
    """Request schema for updating asset package"""
    price_beans: Optional[int] = Field(None, ge=1, le=100000)
    discount_rate: Optional[float] = Field(None, ge=0.0, le=1.0)


class UserResponse(BaseModel):
    """Response schema for user"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    nickname: str
    phone: Optional[str] = None
    status: str
    rank: str
    reputation_points: int
    gold_beans: int
    bonus_beans: int
    is_expert: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class UserListResponse(BaseModel):
    """Response schema for user list"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int


class ResourceResponse(BaseModel):
    """Response schema for resource"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    uploader_id: str
    title: str
    description: Optional[str] = None
    category_id: int
    price: int
    status: str
    view_count: int
    download_count: int
    created_at: datetime


class ResourceListResponse(BaseModel):
    """Response schema for resource list"""
    resources: List[ResourceResponse]
    total: int
    page: int
    page_size: int


class TopicResponse(BaseModel):
    """Response schema for topic"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    author_id: str
    title: str
    content: str
    category_id: int
    status: str
    view_count: int
    post_count: int
    created_at: datetime


class TopicListResponse(BaseModel):
    """Response schema for topic list"""
    topics: List[TopicResponse]
    total: int
    page: int
    page_size: int


class AuditLogResponse(BaseModel):
    """Response schema for audit log"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    admin_id: str
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    before_data: Optional[str] = None
    after_data: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Response schema for audit log list"""
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


class SystemConfigResponse(BaseModel):
    """Response schema for system config"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    config_key: str
    config_value: str
    description: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SystemConfigListResponse(BaseModel):
    """Response schema for system config list"""
    configs: List[SystemConfigResponse]
    total: int


class FeedbackResponse(BaseModel):
    """Response schema for feedback"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    type: str
    content: str
    status: str
    images: Optional[List[str]] = None
    contact: Optional[str] = None
    reply: Optional[str] = None
    replied_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FeedbackListResponse(BaseModel):
    """Response schema for feedback list"""
    feedbacks: List[FeedbackResponse]
    total: int
    page: int
    page_size: int


class AssetPackageResponse(BaseModel):
    """Response schema for asset package"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    price_beans: int
    quota_mb: int
    discount_rate: float
    created_at: datetime


class AssetPackageListResponse(BaseModel):
    """Response schema for asset package list"""
    packages: List[AssetPackageResponse]
    total: int


class DashboardStatsResponse(BaseModel):
    """Response schema for dashboard statistics"""
    total_users: int
    active_users: int
    total_resources: int
    pending_resources: int
    total_topics: int
    total_posts: int
    total_revenue: int
    total_feedbacks: int
    pending_feedbacks: int
