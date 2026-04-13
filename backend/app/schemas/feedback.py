"""
Pydantic Schemas for User Feedback module.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FeedbackType(str, Enum):
    """Feedback type enum"""
    BUG = "BUG"
    SUGGESTION = "SUGGESTION"
    CONTENT = "CONTENT"
    OTHER = "OTHER"


class FeedbackStatus(str, Enum):
    """Feedback status enum"""
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class FeedbackCreateRequest(BaseModel):
    """Request schema for creating a feedback"""
    type: FeedbackType = Field(..., description="Feedback type: BUG/SUGGESTION/CONTENT/OTHER")
    content: str = Field(..., min_length=10, max_length=500, description="Feedback content (10-500 chars)")
    images: Optional[List[str]] = Field(default=None, max_length=3, description="Image URLs (max 3)")
    contact: Optional[str] = Field(default=None, max_length=100, description="Contact info (optional)")


class FeedbackResponse(BaseModel):
    """Response schema for feedback"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    content: str
    status: str
    images: Optional[List[str]] = None
    contact: Optional[str] = None
    reply: Optional[str] = None
    replied_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FeedbackDetailResponse(BaseModel):
    """Response schema for feedback detail with reply info"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    content: str
    images: Optional[List[str]] = None
    contact: Optional[str] = None
    status: str
    reply: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class FeedbackListResponse(BaseModel):
    """Response schema for feedback list"""
    feedbacks: List[FeedbackResponse]
    total: int
    page: int
    page_size: int


class FeedbackListItem(BaseModel):
    """Simplified feedback list item for user's feedback list"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    content: str
    status: str
    created_at: datetime
