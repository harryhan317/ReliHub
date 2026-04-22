"""
Pydantic Schemas for user interaction endpoints (collect, like, report).
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TargetType(str, Enum):
    RESOURCE = "RESOURCE"
    TOPIC = "TOPIC"
    POST = "POST"


class ReportReason(str, Enum):
    SPAM = "SPAM"
    INAPPROPRIATE = "INAPPROPRIATE"
    COPYRIGHT = "COPYRIGHT"
    MISLEADING = "MISLEADING"
    OTHER = "OTHER"


class ReportRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=50, description="Report reason")
    detail: Optional[str] = Field(None, max_length=1000, description="Additional details")


class LikeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    target_type: TargetType
    target_id: str
    created_at: datetime


class CollectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    target_type: TargetType
    target_id: str
    created_at: datetime


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    target_type: TargetType
    target_id: str
    reason: str
    detail: Optional[str] = None
    status: str
    created_at: datetime


class CheckinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    checkin_date: str
    reward_beans: int
    created_at: datetime


class UserProfileUpdateRequest(BaseModel):
    nickname: Optional[str] = Field(None, min_length=1, max_length=50, description="Nickname")
    avatar_url: Optional[str] = Field(None, max_length=1024, description="Avatar URL")
