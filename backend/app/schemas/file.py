"""
Pydantic Schemas for File Management module.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FileStatus(str, Enum):
    """File status enum"""
    NORMAL = "NORMAL"
    SCANNING = "SCANNING"
    ISOLATED = "ISOLATED"
    SUSPICIOUS = "SUSPICIOUS"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"


class LifecycleStatus(str, Enum):
    """File lifecycle status enum"""
    ACTIVE = "ACTIVE"
    SOFT_DELETED = "SOFT_DELETED"
    PERMANENTLY_DELETED = "PERMANENTLY_DELETED"


class TargetType(str, Enum):
    """Target type enum for file usage"""
    CONVERSATION = "CONVERSATION"
    RESOURCE = "RESOURCE"
    TOPIC = "TOPIC"


# ── Request Schemas ───────────────────────────────────────────────────────────

class FileUploadRequest(BaseModel):
    """Request schema for file upload metadata"""
    file_name: str = Field(..., min_length=1, max_length=255, description="Original file name")
    file_size: int = Field(..., gt=0, le=52428800, description="File size in bytes (max 50MB)")
    mime_type: str = Field(..., description="File MIME type")


class FileUpdateStatusRequest(BaseModel):
    """Request schema for updating file status"""
    status: FileStatus = Field(..., description="New file status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")


# ── Response Schemas ──────────────────────────────────────────────────────────

class FileMetaResponse(BaseModel):
    """Response schema for file metadata"""
    file_uuid: str
    file_hash: str
    oss_path: str
    file_name: str
    file_size: int
    mime_type: str
    ref_counts: int
    status: FileStatus
    lifecycle_status: LifecycleStatus
    uploader_uid: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileUsageResponse(BaseModel):
    """Response schema for file usage record"""
    id: str
    file_uuid: str
    target_id: str
    target_type: TargetType
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Response schema for file upload result"""
    file_uuid: str
    file_hash: str
    oss_path: str
    file_name: str
    file_size: int
    mime_type: str
    upload_url: Optional[str] = None  # Pre-signed URL for direct upload
    download_url: Optional[str] = None  # Pre-signed URL for download


class FileListResponse(BaseModel):
    """Response schema for file list"""
    files: List[FileMetaResponse]
    total: int
    page: int
    page_size: int


class PresignedUrlResponse(BaseModel):
    """Response schema for presigned URL"""
    url: str
    expires_at: datetime
