"""
Pydantic Schemas for Search module.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SearchType(str, Enum):
    """Search type enum"""
    RESOURCE = "RESOURCE"
    COMMUNITY = "COMMUNITY"
    AI = "AI"
    USER = "USER"
    ALL = "ALL"


class SortBy(str, Enum):
    """Sort by enum"""
    RELEVANCE = "relevance"
    HEAT = "heat"
    LATEST = "latest"


class SearchRequest(BaseModel):
    """Request schema for global search"""
    q: str = Field(..., min_length=1, max_length=50, description="搜索关键词 (1-50 字符)")
    type: SearchType = Field(default=SearchType.ALL, description="搜索范围")
    sort_by: SortBy = Field(default=SortBy.RELEVANCE, description="排序方式")
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    start_date: Optional[str] = Field(default=None, description="开始日期 (AI 类型专属，YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="结束日期 (YYYY-MM-DD)")


class SearchItem(BaseModel):
    """Base schema for search result item"""
    type: str
    id: str
    title: str
    description: str
    score: float
    created_at: datetime


class ResourceSearchItem(SearchItem):
    """Resource search result item"""
    type: str = "RESOURCE"
    file_type: Optional[str] = None
    download_count: int = 0


class TopicSearchItem(SearchItem):
    """Community topic search result item"""
    type: str = "COMMUNITY"
    reply_count: int = 0
    view_count: int = 0


class AISessionSearchItem(SearchItem):
    """AI session search result item"""
    type: str = "AI"
    message_count: int = 0


class UserSearchItem(SearchItem):
    """User search result item"""
    type: str = "USER"
    avatar_url: Optional[str] = None
    level: int = 1


class SearchResponse(BaseModel):
    """Response schema for global search"""
    items: List[dict] = []  # Can be ResourceSearchItem, TopicSearchItem, etc.
    total: int
    page: int
    size: int
    has_more: bool


class SearchSuggestionResponse(BaseModel):
    """Response schema for search suggestions"""
    suggestions: List[str] = []
    count: int


class TrendingSearchResponse(BaseModel):
    """Response schema for trending searches"""
    trending: List[dict] = []


class SearchHistoryItem(BaseModel):
    """Search history item"""
    id: str
    keyword: str
    created_at: datetime


class SearchHistoryResponse(BaseModel):
    """Response schema for search history"""
    history: List[SearchHistoryItem]
    total: int
