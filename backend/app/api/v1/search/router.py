"""
Search API - Global unified search across all modules.
Provides endpoints for searching resources, community topics, AI sessions, and users.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.exceptions import BusinessException, ErrorCode
from app.db.session import get_db
from app.models.users import User
from app.schemas.search import (
    SearchHistoryResponse,
    SearchRequest,
    SearchResponse,
    SearchSuggestionResponse,
    SearchType,
    TrendingSearchResponse,
)
from app.services.search_service import SearchService

# Import schemas for type hints
from app.schemas import search as search_schemas

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse, summary="全局统一搜索")
def global_search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=50, description="搜索关键词 (1-50 字符)"),
    type: SearchType = Query(default=SearchType.ALL, description="搜索范围"),
    sort_by: search_schemas.SortBy = Query(default=search_schemas.SortBy.RELEVANCE, description="排序方式"),
    page: int = Query(default=1, ge=1, description="页码"),
    size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    start_date: Optional[str] = Query(default=None, description="开始日期 (AI 类型专属，YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    全局统一搜索接口，支持搜索资源、社区话题、AI 会话和用户。

    - **q**: 搜索关键词 (1-50 字符)
    - **type**: 搜索范围 (RESOURCE/COMMUNITY/AI/USER/ALL)
    - **sort_by**: 排序方式 (relevance/heat/latest)
    - **page**: 页码 (default: 1)
    - **size**: 每页数量 (default: 20, max: 100)
    - **start_date**: 开始日期 (AI 类型专属，YYYY-MM-DD)
    - **end_date**: 结束日期 (YYYY-MM-DD)
    
    需要登录才能搜索 AI 会话（仅返回用户自己的会话）
    """
    service = SearchService(db)
    
    user_id = current_user.id if current_user else None
    
    items, total = service.global_search(
        query=q,
        search_type=type,
        sort_by=sort_by,
        page=page,
        size=size,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id
    )
    
    # Record search history if user is logged in
    if current_user:
        service.record_search_history(
            user_id=current_user.id,
            keyword=q,
            search_type=type.value,
            result_count=total
        )
    
    has_more = (page * size) < total
    
    return SearchResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        has_more=has_more
    )


@router.get("/suggestions", response_model=SearchSuggestionResponse, summary="搜索建议")
def search_suggestions(
    q: str = Query(..., min_length=1, max_length=50, description="搜索关键词 (1-50 字符)"),
    limit: int = Query(default=5, ge=1, le=20, description="建议数量 (default: 5, max: 20)"),
    db: Session = Depends(get_db),
):
    """
    获取搜索建议（自动补全）。
    
    - **q**: 搜索关键词
    - **limit**: 返回建议数量 (default: 5, max: 20)
    
    基于热门搜索和历史搜索生成建议列表
    """
    service = SearchService(db)
    
    suggestions = service.get_search_suggestions(query=q, limit=limit)
    
    return SearchSuggestionResponse(
        suggestions=suggestions,
        count=len(suggestions)
    )


@router.get("/history", response_model=SearchHistoryResponse, summary="获取搜索历史")
def get_search_history(
    page: int = Query(default=1, ge=1, description="页码"),
    size: int = Query(default=20, ge=1, le=50, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取当前用户的搜索历史。
    
    - **page**: 页码 (default: 1)
    - **size**: 每页数量 (default: 20, max: 50)
    
    需要登录才能访问
    """
    service = SearchService(db)
    
    history_items, total = service.get_search_history(
        user_id=current_user.id,
        page=page,
        size=size
    )
    
    history = [
        {
            "id": item.id,
            "keyword": item.keyword,
            "created_at": item.created_at
        }
        for item in history_items
    ]
    
    return SearchHistoryResponse(
        history=history,
        total=total
    )


@router.delete("/history/{history_id}", summary="删除单条搜索历史")
def delete_search_history_item(
    history_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除单条搜索历史记录。
    
    - **history_id**: 搜索历史记录 ID
    
    需要登录才能删除自己的搜索历史
    """
    service = SearchService(db)
    
    success = service.delete_search_history_item(
        user_id=current_user.id,
        history_id=history_id
    )
    
    if not success:
        raise BusinessException(
            ErrorCode.NOT_FOUND,
            "搜索历史记录不存在或不属于当前用户"
        )
    
    return {"msg": "删除成功"}


@router.delete("/history", summary="清空全部搜索历史")
def clear_search_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    清空当前用户的全部搜索历史记录。
    
    需要登录才能清空自己的搜索历史
    """
    service = SearchService(db)
    
    count = service.clear_search_history(user_id=current_user.id)
    
    return {"msg": f"清空成功，共删除 {count} 条记录"}


@router.get("/users", response_model=SearchResponse, summary="用户搜索")
def search_users(
    request: Request,
    q: str = Query(..., min_length=1, max_length=50, description="搜索关键词 (1-50 字符)"),
    sort_by: search_schemas.SortBy = Query(default=search_schemas.SortBy.RELEVANCE, description="排序方式"),
    page: int = Query(default=1, ge=1, description="页码"),
    size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
):
    """
    搜索用户（按昵称）。
    
    - **q**: 搜索关键词
    - **sort_by**: 排序方式 (relevance/heat/latest)
    - **page**: 页码 (default: 1)
    - **size**: 每页数量 (default: 20, max: 100)
    """
    service = SearchService(db)
    
    items, total = service._search_users(
        query=q,
        sort_by=sort_by,
        page=page,
        size=size
    )
    
    has_more = (page * size) < total
    
    return SearchResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        has_more=has_more
    )


@router.get("/ai-history", response_model=SearchResponse, summary="AI 历史搜索")
def search_ai_history(
    request: Request,
    q: str = Query(..., min_length=1, max_length=50, description="搜索关键词 (1-50 字符)"),
    sort_by: search_schemas.SortBy = Query(default=search_schemas.SortBy.RELEVANCE, description="排序方式"),
    page: int = Query(default=1, ge=1, description="页码"),
    size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    start_date: Optional[str] = Query(default=None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    搜索用户自己的 AI 会话历史。
    
    - **q**: 搜索关键词
    - **sort_by**: 排序方式 (relevance/heat/latest)
    - **page**: 页码 (default: 1)
    - **size**: 每页数量 (default: 20, max: 100)
    - **start_date**: 开始日期 (YYYY-MM-DD)
    - **end_date**: 结束日期 (YYYY-MM-DD)
    
    需要登录，仅返回用户自己的 AI 会话
    """
    service = SearchService(db)
    
    items, total = service._search_ai_sessions(
        query=q,
        sort_by=sort_by,
        page=page,
        size=size,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    has_more = (page * size) < total
    
    return SearchResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        has_more=has_more
    )


@router.get("/trending", response_model=TrendingSearchResponse, summary="热搜榜单")
def get_trending_searches(
    limit: int = Query(default=10, ge=1, le=50, description="榜单数量 (default: 10, max: 50)"),
    db: Session = Depends(get_db),
):
    """
    获取热搜榜单。
    
    - **limit**: 返回榜单数量 (default: 10, max: 50)
    
    基于用户搜索频率生成，定时更新
    """
    service = SearchService(db)
    
    trending = service.get_trending_searches(limit=limit)
    
    return TrendingSearchResponse(
        trending=trending
    )
