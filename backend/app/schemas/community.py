"""
Pydantic Schemas for Community/Forum module.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BountyStatus(str, Enum):
    """Bounty status enum"""
    NONE = "NONE"
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    REFUNDED = "REFUNDED"


class TopicStatus(str, Enum):
    """Topic status enum"""
    NORMAL = "NORMAL"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"


# ── Request Schemas ───────────────────────────────────────────────────────────

class TopicCreateRequest(BaseModel):
    """Request schema for creating a topic"""
    title: str = Field(..., min_length=1, max_length=255, description="Topic title")
    content: str = Field(..., min_length=10, max_length=50000, description="Topic content")
    category_id: int = Field(..., ge=1, description="Category ID")
    bounty_amount: int = Field(default=0, ge=0, description="Bounty amount in cocoa beans")


class TopicUpdateRequest(BaseModel):
    """Request schema for updating a topic"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=10, max_length=50000)
    category_id: Optional[int] = Field(None, ge=1)


class PostCreateRequest(BaseModel):
    """Request schema for creating a post"""
    content: str = Field(..., min_length=1, max_length=10000, description="Post content")
    parent_id: Optional[str] = Field(None, description="Parent post ID for replies")


class PostUpdateRequest(BaseModel):
    """Request schema for updating a post"""
    content: Optional[str] = Field(None, min_length=1, max_length=10000)


class AcceptPostRequest(BaseModel):
    """Request schema for accepting a post as answer"""
    post_id: str = Field(..., description="Post ID to accept as answer")


# ── Response Schemas ──────────────────────────────────────────────────────────

class PostResponse(BaseModel):
    """Response schema for a single post"""
    id: str
    topic_id: str
    author_id: str
    content: str
    parent_id: Optional[str] = None
    is_accepted: bool
    like_count: int
    anonymized_user_hash: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TopicResponse(BaseModel):
    """Response schema for a single topic"""
    id: str
    author_id: str
    title: str
    content: str
    category_id: int
    bounty_amount: int
    bounty_status: BountyStatus
    accepted_post_id: Optional[str] = None
    status: TopicStatus
    view_count: int
    post_count: int
    heat_score: float
    anonymized_user_hash: Optional[str] = None
    created_at: datetime
    posts: Optional[List[PostResponse]] = None

    class Config:
        from_attributes = True


class TopicListItem(BaseModel):
    """Response schema for topic list item"""
    id: str
    title: str
    author_id: str
    category_id: int
    bounty_amount: int
    bounty_status: BountyStatus
    post_count: int
    view_count: int
    heat_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class TopicListResponse(BaseModel):
    """Response schema for topic list with pagination"""
    topics: List[TopicListItem]
    total: int
    page: int
    page_size: int


class PostListResponse(BaseModel):
    """Response schema for post list"""
    posts: List[PostResponse]
    total: int
    page: int
    page_size: int


class CategoryResponse(BaseModel):
    """Response schema for community category"""
    id: int
    name: str
    parent_id: Optional[int] = None
    level: int
    sort_order: int

    class Config:
        from_attributes = True
