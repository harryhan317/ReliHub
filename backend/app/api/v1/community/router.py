"""
API routes for Community/Forum module.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.users import User
from app.schemas.community import (
    PostCreateRequest,
    PostListResponse,
    PostResponse,
    TopicCreateRequest,
    TopicListItem,
    TopicListResponse,
    TopicResponse,
    TopicUpdateRequest,
)
from app.services.community_service import PostService, TopicService

router = APIRouter(tags=["社区管理"])


@router.post("/topics", response_model=TopicResponse)
def create_topic(
    request: TopicCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new topic"""
    topic_service = TopicService(db)
    topic = topic_service.create_topic(current_user.id, request)
    return topic


@router.get("/topics", response_model=TopicListResponse)
def list_topics(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title/content"),
    sort_by: str = Query("heat_score", description="Sort field"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all topics with filters"""
    topic_service = TopicService(db)
    topics, total = topic_service.list_topics(
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
def get_topic(
    topic_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific topic"""
    topic_service = TopicService(db)
    topic = topic_service.get_topic(topic_id, include_posts=False)
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic_service.increment_view(topic_id)
    
    return topic


@router.put("/topics/{topic_id}", response_model=TopicResponse)
def update_topic(
    topic_id: str,
    request: TopicUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a topic"""
    topic_service = TopicService(db)
    topic = topic_service.update_topic(
        topic_id,
        current_user.id,
        request,
    )
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return topic


@router.delete("/topics/{topic_id}")
def delete_topic(
    topic_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a topic"""
    topic_service = TopicService(db)
    success = topic_service.delete_topic(topic_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return {"message": "Topic deleted successfully"}


@router.post("/topics/{topic_id}/posts", response_model=PostResponse)
def create_post(
    topic_id: str,
    request: PostCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new post/reply"""
    topic_service = TopicService(db)
    
    topic = topic_service.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    post_service = PostService(db)
    post = post_service.create_post(
        topic_id,
        current_user.id,
        request,
    )
    
    return post


@router.get("/topics/{topic_id}/posts", response_model=PostListResponse)
def list_posts(
    topic_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List posts for a topic"""
    post_service = PostService(db)
    posts, total = post_service.get_posts(topic_id, page, page_size)
    
    return PostListResponse(
        posts=[PostResponse.model_validate(p) for p in posts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/posts/{post_id}/accept")
def accept_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept a post as the answer (topic author only)"""
    post_service = PostService(db)
    post = post_service.get_post(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    success = post_service.accept_post(
        post.topic_id,
        post_id,
        current_user.id,
    )
    
    if not success:
        raise HTTPException(status_code=403, detail="Not authorized to accept this post")
    
    return {"message": "Post accepted as answer"}


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a post"""
    post_service = PostService(db)
    success = post_service.delete_post(post_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"message": "Post deleted successfully"}


@router.post("/posts/{post_id}/like")
def like_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Like a post"""
    return {"message": "Post liked"}
