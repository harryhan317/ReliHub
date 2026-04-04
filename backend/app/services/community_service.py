"""
Service layer for Community/Forum module.
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import uuid

from app.models.topic import Topic, Post, BountyStatus, TopicStatus
from app.schemas.community import (
    TopicCreateRequest,
    TopicUpdateRequest,
    PostCreateRequest,
    AcceptPostRequest,
)


class TopicService:
    """Service class for Topic management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_topic(
        self,
        author_id: str,
        request: TopicCreateRequest
    ) -> Topic:
        """Create a new topic"""
        bounty_status = BountyStatus.ACTIVE if request.bounty_amount > 0 else BountyStatus.NONE
        
        topic = Topic(
            id=str(uuid.uuid4()),
            author_id=author_id,
            title=request.title,
            content=request.content,
            category_id=request.category_id,
            bounty_amount=request.bounty_amount,
            bounty_status=bounty_status,
        )
        
        self.db.add(topic)
        await self.db.commit()
        await self.db.refresh(topic)
        return topic

    async def get_topic(
        self,
        topic_id: str,
        include_posts: bool = False
    ) -> Optional[Topic]:
        """Get a topic by ID"""
        query = select(Topic).where(
            Topic.id == topic_id,
            Topic.is_deleted == False,
            Topic.status == TopicStatus.NORMAL
        )
        
        if include_posts:
            query = query.options(selectinload(Topic.posts))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_topics(
        self,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "heat_score",
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Topic], int]:
        """List topics with filters and pagination"""
        # Build filters
        filters = [
            Topic.is_deleted == False,
            Topic.status == TopicStatus.NORMAL
        ]
        
        if category_id:
            filters.append(Topic.category_id == category_id)
        
        if search:
            filters.append(
                or_(
                    Topic.title.ilike(f"%{search}%"),
                    Topic.content.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        count_query = select(func.count()).where(and_(*filters))
        total = (await self.db.execute(count_query)).scalar()
        
        # Build sorting
        sort_columns = {
            "heat_score": Topic.heat_score.desc(),
            "created_at": Topic.created_at.desc(),
            "view_count": Topic.view_count.desc(),
            "post_count": Topic.post_count.desc(),
            "bounty_amount": Topic.bounty_amount.desc(),
        }
        order_by = sort_columns.get(sort_by, Topic.heat_score.desc())
        
        # Get paginated results
        query = (
            select(Topic)
            .where(and_(*filters))
            .order_by(order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await self.db.execute(query)
        topics = result.scalars().all()
        
        return list(topics), total

    async def update_topic(
        self,
        topic_id: str,
        author_id: str,
        request: TopicUpdateRequest
    ) -> Optional[Topic]:
        """Update a topic"""
        query = select(Topic).where(
            Topic.id == topic_id,
            Topic.author_id == author_id,
            Topic.is_deleted == False
        )
        result = await self.db.execute(query)
        topic = result.scalar_one_or_none()
        
        if not topic:
            return None
        
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(topic, field, value)
        
        await self.db.commit()
        await self.db.refresh(topic)
        return topic

    async def delete_topic(
        self,
        topic_id: str,
        author_id: str
    ) -> bool:
        """Soft delete a topic"""
        topic = await self.get_topic_for_user(topic_id, author_id)
        if not topic:
            return False
        
        topic.is_deleted = True
        await self.db.commit()
        return True

    async def get_topic_for_user(
        self,
        topic_id: str,
        user_id: str
    ) -> Optional[Topic]:
        """Get a topic for a specific user (for edit/delete)"""
        query = select(Topic).where(
            Topic.id == topic_id,
            Topic.author_id == user_id,
            Topic.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def increment_view(self, topic_id: str) -> bool:
        """Increment view count"""
        topic = await self.get_topic_admin(topic_id)
        if topic:
            topic.view_count += 1
            await self.db.commit()
            return True
        return False

    async def get_topic_admin(
        self,
        topic_id: str
    ) -> Optional[Topic]:
        """Get a topic for admin operations"""
        query = select(Topic).where(
            Topic.id == topic_id,
            Topic.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class PostService:
    """Service class for Post management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_post(
        self,
        topic_id: str,
        author_id: str,
        request: PostCreateRequest
    ) -> Post:
        """Create a new post"""
        post = Post(
            id=str(uuid.uuid4()),
            topic_id=topic_id,
            author_id=author_id,
            content=request.content,
            parent_id=request.parent_id,
        )
        
        self.db.add(post)
        
        # Increment post count
        topic_query = select(Topic).where(Topic.id == topic_id)
        result = await self.db.execute(topic_query)
        topic = result.scalar_one()
        topic.post_count += 1
        
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def get_posts(
        self,
        topic_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Post], int]:
        """Get posts for a topic with pagination"""
        # Get total count
        count_query = select(func.count()).where(
            Post.topic_id == topic_id
        )
        total = (await self.db.execute(count_query)).scalar()
        
        # Get paginated results
        query = (
            select(Post)
            .where(Post.topic_id == topic_id)
            .order_by(Post.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await self.db.execute(query)
        posts = result.scalars().all()
        
        return list(posts), total

    async def accept_post(
        self,
        topic_id: str,
        post_id: str,
        author_id: str
    ) -> bool:
        """Accept a post as the answer"""
        # Verify topic ownership
        topic_query = select(Topic).where(
            Topic.id == topic_id,
            Topic.author_id == author_id,
            Topic.is_deleted == False
        )
        result = await self.db.execute(topic_query)
        topic = result.scalar_one_or_none()
        
        if not topic:
            return False
        
        # Verify post exists and belongs to topic
        post_query = select(Post).where(
            Post.id == post_id,
            Post.topic_id == topic_id
        )
        result = await self.db.execute(post_query)
        post = result.scalar_one_or_none()
        
        if not post:
            return False
        
        # If there was a previous accepted post, unaccept it
        if topic.accepted_post_id:
            prev_accepted_query = select(Post).where(Post.id == topic.accepted_post_id)
            prev_result = await self.db.execute(prev_accepted_query)
            prev_post = prev_result.scalar_one_or_none()
            if prev_post:
                prev_post.is_accepted = False
        
        # Accept the new post
        post.is_accepted = True
        topic.accepted_post_id = post_id
        topic.bounty_status = BountyStatus.RESOLVED
        
        await self.db.commit()
        return True

    async def delete_post(
        self,
        post_id: str,
        author_id: str
    ) -> bool:
        """Delete a post (admin operation, requires manual cascade)"""
        post_query = select(Post).where(
            Post.id == post_id,
            Post.author_id == author_id
        )
        result = await self.db.execute(post_query)
        post = result.scalar_one_or_none()
        
        if not post:
            return False
        
        # Decrement post count
        topic_query = select(Topic).where(Topic.id == post.topic_id)
        result = await self.db.execute(topic_query)
        topic = result.scalar_one()
        if topic.post_count > 0:
            topic.post_count -= 1
        
        # Delete the post
        await self.db.delete(post)
        await self.db.commit()
        return True

    async def get_post(
        self,
        post_id: str
    ) -> Optional[Post]:
        """Get a post by ID"""
        query = select(Post).where(Post.id == post_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
