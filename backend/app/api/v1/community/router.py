"""
API routes for Community/Forum module.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.services.community_service import TopicService, PostService
from app.schemas.community import (
    TopicCreateRequest,
    TopicUpdateRequest,
    PostCreateRequest,
    AcceptPostRequest,
    TopicResponse,
    TopicListResponse,
    TopicListItem,
    PostResponse,
    PostListResponse,
)
from app.models.users import User

router = APIRouter(prefix="/community", tags=["社区管理"])


# ── Topic Routes ──────────────────────────────────────────────────────────────

@router.post("/topics", response_model=TopicResponse)
async def create_topic(
    request: TopicCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new topic"""
    topic_service = TopicService(db)
    topic = await topic_service.create_topic(current_user.user_uuid, request)
    return topic


@router.get("/topics", response_model=TopicListResponse)
async def list_topics(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title/content"),
    sort_by: str = Query("heat_score", description="Sort field"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List all topics with filters"""
    topic_service = TopicService(db)
    topics, total = await topic_service.list_topics(
        category_id=category_id,
        search=search,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    
    return TopicListResponse(
        topics=[TopicListItem.model_validate(t) for t in topics],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific topic"""
    topic_service = TopicService(db)
    topic = await topic_service.get_topic(topic_id, include_posts=False)
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Increment view count
    await topic_service.increment_view(topic_id)
    
    return topic


@router.put("/topics/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: str,
    request: TopicUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a topic"""
    topic_service = TopicService(db)
    topic = await topic_service.update_topic(
        topic_id,
        current_user.user_uuid,
        request,
    )
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return topic


@router.delete("/topics/{topic_id}")
async def delete_topic(
    topic_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a topic"""
    topic_service = TopicService(db)
    success = await topic_service.delete_topic(topic_id, current_user.user_uuid)
    
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return {"message": "Topic deleted successfully"}


# ── Post Routes ───────────────────────────────────────────────────────────────

@router.post("/topics/{topic_id}/posts", response_model=PostResponse)
async def create_post(
    topic_id: str,
    request: PostCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new post/reply"""
    topic_service = TopicService(db)
    
    # Verify topic exists
    topic = await topic_service.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    post_service = PostService(db)
    post = await post_service.create_post(
        topic_id,
        current_user.user_uuid,
        request,
    )
    
    return post


@router.get("/topics/{topic_id}/posts", response_model=PostListResponse)
async def list_posts(
    topic_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List posts for a topic"""
    post_service = PostService(db)
    posts, total = await post_service.get_posts(topic_id, page, page_size)
    
    return PostListResponse(
        posts=[PostResponse.model_validate(p) for p in posts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/posts/{post_id}/accept")
async def accept_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept a post as the answer (topic author only)"""
    post_service = PostService(db)
    post = await post_service.get_post(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    topic_service = TopicService(db)
    success = await post_service.accept_post(
        post.topic_id,
        post_id,
        current_user.user_uuid,
    )
    
    if not success:
        raise HTTPException(status_code=403, detail="Not authorized to accept this post")
    
    return {"message": "Post accepted as answer"}


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a post"""
    post_service = PostService(db)
    success = await post_service.delete_post(post_id, current_user.user_uuid)
    
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"message": "Post deleted successfully"}


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Like a post"""
    # TODO: Implement like logic
    return {"message": "Post liked"}
