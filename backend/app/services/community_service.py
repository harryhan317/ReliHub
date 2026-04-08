"""
Service layer for Community/Forum module.
"""
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.topic import BountyStatus, Post, Topic, TopicStatus
from app.schemas.community import (
    PostCreateRequest,
    TopicCreateRequest,
    TopicUpdateRequest,
)


class TopicService:
    """Service class for Topic management"""

    def __init__(self, db: Session):
        self.db = db

    def create_topic(
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
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def get_topic(
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
        
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def list_topics(
        self,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "heat_score",
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Topic], int]:
        """List topics with filters and pagination"""
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
        
        count_query = select(func.count()).where(and_(*filters))
        total = self.db.execute(count_query).scalar()
        
        sort_columns = {
            "heat_score": Topic.heat_score.desc(),
            "created_at": Topic.created_at.desc(),
            "view_count": Topic.view_count.desc(),
            "post_count": Topic.post_count.desc(),
            "bounty_amount": Topic.bounty_amount.desc(),
        }
        order_by = sort_columns.get(sort_by, Topic.heat_score.desc())
        
        query = (
            select(Topic)
            .where(and_(*filters))
            .order_by(order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = self.db.execute(query)
        topics = result.scalars().all()
        
        return list(topics), total

    def update_topic(
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
        result = self.db.execute(query)
        topic = result.scalar_one_or_none()
        
        if not topic:
            return None
        
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(topic, field, value)
        
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def delete_topic(
        self,
        topic_id: str,
        author_id: str
    ) -> bool:
        """Soft delete a topic"""
        topic = self.get_topic_for_user(topic_id, author_id)
        if not topic:
            return False
        
        topic.is_deleted = True
        self.db.commit()
        return True

    def get_topic_for_user(
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
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def increment_view(self, topic_id: str) -> bool:
        """Increment view count"""
        topic = self.get_topic_admin(topic_id)
        if topic:
            topic.view_count += 1
            self.db.commit()
            return True
        return False

    def get_topic_admin(
        self,
        topic_id: str
    ) -> Optional[Topic]:
        """Get a topic for admin operations"""
        query = select(Topic).where(
            Topic.id == topic_id,
            Topic.is_deleted == False
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()


class PostService:
    """Service class for Post management"""

    def __init__(self, db: Session):
        self.db = db

    def create_post(
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
        
        topic_query = select(Topic).where(Topic.id == topic_id)
        result = self.db.execute(topic_query)
        topic = result.scalar_one()
        topic.post_count += 1
        
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_posts(
        self,
        topic_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Post], int]:
        """Get posts for a topic with pagination"""
        count_query = select(func.count()).where(
            Post.topic_id == topic_id
        )
        total = self.db.execute(count_query).scalar()
        
        query = (
            select(Post)
            .where(Post.topic_id == topic_id)
            .order_by(Post.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = self.db.execute(query)
        posts = result.scalars().all()
        
        return list(posts), total

    def accept_post(
        self,
        topic_id: str,
        post_id: str,
        author_id: str
    ) -> bool:
        """Accept a post as the answer"""
        topic_query = select(Topic).where(
            Topic.id == topic_id,
            Topic.author_id == author_id,
            Topic.is_deleted == False
        )
        result = self.db.execute(topic_query)
        topic = result.scalar_one_or_none()
        
        if not topic:
            return False
        
        post_query = select(Post).where(
            Post.id == post_id,
            Post.topic_id == topic_id
        )
        result = self.db.execute(post_query)
        post = result.scalar_one_or_none()
        
        if not post:
            return False
        
        if topic.accepted_post_id:
            prev_accepted_query = select(Post).where(Post.id == topic.accepted_post_id)
            prev_result = self.db.execute(prev_accepted_query)
            prev_post = prev_result.scalar_one_or_none()
            if prev_post:
                prev_post.is_accepted = False
        
        post.is_accepted = True
        topic.accepted_post_id = post_id
        topic.bounty_status = BountyStatus.RESOLVED
        
        self.db.commit()
        return True

    def delete_post(
        self,
        post_id: str,
        author_id: str
    ) -> bool:
        """Delete a post (admin operation, requires manual cascade)"""
        post_query = select(Post).where(
            Post.id == post_id,
            Post.author_id == author_id
        )
        result = self.db.execute(post_query)
        post = result.scalar_one_or_none()
        
        if not post:
            return False
        
        topic_query = select(Topic).where(Topic.id == post.topic_id)
        result = self.db.execute(topic_query)
        topic = result.scalar_one()
        if topic.post_count > 0:
            topic.post_count -= 1
        
        self.db.delete(post)
        self.db.commit()
        return True

    def get_post(
        self,
        post_id: str
    ) -> Optional[Post]:
        """Get a post by ID"""
        query = select(Post).where(Post.id == post_id)
        result = self.db.execute(query)
        return result.scalar_one_or_none()
