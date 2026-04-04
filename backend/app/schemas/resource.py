"""
Pydantic Schemas for Resource Management module.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ResourceStatus(str, Enum):
    """Resource status enum"""
    SCANNING = "SCANNING"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPEALING = "APPEALING"
    BLOCKED = "BLOCKED"


# ── Request Schemas ───────────────────────────────────────────────────────────

class ResourceCreateRequest(BaseModel):
    """Request schema for creating a resource"""
    title: str = Field(..., min_length=1, max_length=255, description="Resource title")
    description: Optional[str] = Field(None, max_length=2000, description="Resource description")
    category_id: int = Field(..., ge=1, description="Category ID")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    price: int = Field(default=5, ge=0, le=100, description="Price in cocoa beans")
    file_uuid: str = Field(..., description="File UUID")


class ResourceUpdateRequest(BaseModel):
    """Request schema for updating a resource"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category_id: Optional[int] = Field(None, ge=1)
    tags: Optional[List[str]] = None
    price: Optional[int] = Field(None, ge=0, le=100)


class ResourceReviewRequest(BaseModel):
    """Request schema for resource review"""
    status: ResourceStatus = Field(..., description="Review result: APPROVED or REJECTED")
    reason: Optional[str] = Field(None, max_length=500, description="Rejection reason")


class ResourceAppealRequest(BaseModel):
    """Request schema for resource appeal"""
    reason: str = Field(..., min_length=10, max_length=1000, description="Appeal reason")


# ── Response Schemas ──────────────────────────────────────────────────────────

class ResourcePreviewResponse(BaseModel):
    """Response schema for resource preview"""
    id: str
    resource_id: str
    preview_url: str
    page_number: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResourceResponse(BaseModel):
    """Response schema for a single resource"""
    id: str
    uploader_id: str
    title: str
    description: Optional[str] = None
    category_id: int
    tags: Optional[str] = None
    price: int
    file_uuid: str
    view_count: int
    download_count: int
    like_count: int
    dislike_count: int
    heat_score: float
    is_seed: bool
    status: ResourceStatus
    anonymized_user_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    previews: Optional[List[ResourcePreviewResponse]] = None

    class Config:
        from_attributes = True


class ResourceListItem(BaseModel):
    """Response schema for resource list item"""
    id: str
    title: str
    description: Optional[str] = None
    category_id: int
    price: int
    view_count: int
    download_count: int
    like_count: int
    heat_score: float
    is_seed: bool
    status: ResourceStatus
    created_at: datetime

    class Config:
        from_attributes = True


class ResourceListResponse(BaseModel):
    """Response schema for resource list with pagination"""
    resources: List[ResourceListItem]
    total: int
    page: int
    page_size: int


class CategoryResponse(BaseModel):
    """Response schema for resource category"""
    id: int
    name: str
    parent_id: Optional[int] = None
    level: int
    sort_order: int

    class Config:
        from_attributes = True
