"""
Pydantic Schemas for AI Conversation module.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(str, Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageRequest(BaseModel):
    """Request schema for sending a message"""
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")
    attachment_ids: Optional[List[str]] = Field(None, description="List of attachment file UUIDs")
    stream: bool = Field(default=True, description="Whether to stream the response")
    provider_name: Optional[str] = Field(None, description="LLM provider name")
    model: Optional[str] = Field(None, description="Model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: int = Field(default=2000, ge=1, le=32000, description="Maximum tokens")


class CreateSessionRequest(BaseModel):
    """Request schema for creating a new AI session"""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Session title")
    model_type: str = Field(default="general", description="Model type: general or multimodal")


class MessageResponse(BaseModel):
    """Response schema for a single message"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    session_id: str
    role: str
    content: str
    token_count: int
    has_attachment: bool
    attachment_ids: Optional[str] = None
    feedback_type: Optional[str] = None
    created_at: datetime


class SessionResponse(BaseModel):
    """Response schema for a session"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: Optional[str] = None
    title: Optional[str] = None
    model_type: str
    total_tokens: int
    total_turns: int
    created_at: datetime
    updated_at: datetime


class SessionListResponse(BaseModel):
    """Response schema for session list"""
    sessions: List[SessionResponse]
    total: int


class MessageListResponse(BaseModel):
    """Response schema for message list"""
    messages: List[MessageResponse]
    total: int


class FeedbackRequest(BaseModel):
    """Request schema for message feedback"""
    feedback_type: str = Field(..., pattern="^(like|dislike)$", description="Feedback type: like or dislike")
