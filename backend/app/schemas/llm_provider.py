"""
Schemas for LLM Provider.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LLMProviderBase(BaseModel):
    """Base schema for LLM Provider"""
    
    name: str = Field(..., min_length=1, max_length=50, description="Unique identifier (e.g., 'deepseek', 'openai')")
    display_name: str = Field(..., min_length=1, max_length=100, description="Display name (e.g., 'DeepSeek', 'OpenAI')")
    api_base_url: str = Field(..., description="API base URL")
    api_key_env: str = Field(..., description="Environment variable name for API key")
    cost_per_1k_tokens: float = Field(..., gt=0, description="Cost per 1k tokens")
    rate_limit_per_minute: int = Field(default=60, ge=1, description="Rate limit per minute")


class LLMProviderCreate(LLMProviderBase):
    """Schema for creating an LLM Provider"""
    pass


class LLMProviderUpdate(BaseModel):
    """Schema for updating an LLM Provider"""
    
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_base_url: Optional[str] = Field(None)
    api_key_env: Optional[str] = Field(None)
    cost_per_1k_tokens: Optional[float] = Field(None, gt=0)
    rate_limit_per_minute: Optional[int] = Field(None, ge=1)
    enabled: Optional[bool] = Field(None)


class LLMProviderResponse(LLMProviderBase):
    """Schema for LLM Provider response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    enabled: bool
    created_at: datetime
    updated_at: datetime


class LLMProviderList(BaseModel):
    """Schema for LLM Provider list response"""
    
    total: int
    items: list[LLMProviderResponse]
