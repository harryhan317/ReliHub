"""
Integration tests for Community/Forum module.

Tests:
1. Topic CRUD operations
2. Topic listing with filters and pagination
3. Post CRUD operations
4. Bounty system (create topic with bounty, accept post to resolve)
5. Soft delete

Database: PostgreSQL (uses shared fixtures from conftest.py)
"""

import pytest

from app.models.topic import BountyStatus, Post, Topic, TopicStatus
from app.models.users import User
from app.schemas.community import (
    PostCreateRequest,
    TopicCreateRequest,
    TopicUpdateRequest,
)
from app.services.community_service import PostService, TopicService


def create_test_user(db_session, user_id: str, username: str = "testuser") -> User:
    """Helper to create a test user"""
    user = User(
        id=user_id,
        phone=f"+8613800{user_id[-8:]}",
        nickname=username,
        password_hash="hashed_password",
        status="ACTIVE"
    )
    db_session.add(user)
    db_session.commit()
    return user


class TestTopicService:
    """Test TopicService CRUD operations"""
    
    @pytest.fixture
    def topic_service(self, db_session):
        """Create TopicService instance"""
        return TopicService(db_session)
    
    def test_create_topic(self, topic_service, db_session):
        """Test creating a new topic"""
        create_test_user(db_session, "user-123", "testuser1")
        
        request = TopicCreateRequest(
            title="Test Topic",
            content="This is test topic content with enough characters.",
            category_id=1,
            bounty_amount=0
        )
        
        topic = topic_service.create_topic(
            author_id="user-123",
            request=request
        )
        
        assert topic.id is not None
        assert topic.author_id == "user-123"
        assert topic.title == "Test Topic"
        assert topic.content == "This is test topic content with enough characters."
        assert topic.category_id == 1
        assert topic.bounty_amount == 0
        assert topic.bounty_status == BountyStatus.NONE
        assert topic.status == TopicStatus.NORMAL
        assert topic.view_count == 0
        assert topic.post_count == 0
        assert topic.is_deleted == False
    
    def test_create_topic_with_bounty(self, topic_service, db_session):
        """Test creating a topic with bounty"""
        create_test_user(db_session, "user-123", "testuser1")
        
        request = TopicCreateRequest(
            title="Bounty Topic",
            content="This is a bounty topic with enough characters.",
            category_id=1,
            bounty_amount=50
        )
        
        topic = topic_service.create_topic(
            author_id="user-123",
            request=request
        )
        
        assert topic.bounty_amount == 50
        assert topic.bounty_status == BountyStatus.ACTIVE
    
    def test_get_topic(self, topic_service, db_session):
        """Test getting a topic by ID"""
        create_test_user(db_session, "user-123", "testuser1")
        
        request = TopicCreateRequest(
            title="Test Topic",
            content="This is test topic content with enough characters.",
            category_id=1
        )
        created = topic_service.create_topic("user-123", request)
        
        topic = topic_service.get_topic(created.id)
        
        assert topic is not None
        assert topic.id == created.id
        assert topic.title == "Test Topic"
    
    def test_get_topic_not_found(self, topic_service):
        """Test getting nonexistent topic"""
        topic = topic_service.get_topic("nonexistent-id")
        assert topic is None
    
    def test_get_topic_blocked(self, topic_service, db_session):
        """Test that get_topic doesn't return blocked topics"""
        create_test_user(db_session, "user-123", "testuser1")
        
        request = TopicCreateRequest(
            title="Test Topic",
            content="This is test topic content with enough characters.",
            category_id=1
        )
        created = topic_service.create_topic("user-123", request)
        
        created.status = TopicStatus.BLOCKED
        topic_service.db.commit()
        
        topic = topic_service.get_topic(created.id)
        assert topic is None
    
    def test_get_topic_deleted(self, topic_service, db_session):
        """Test that get_topic doesn't return deleted topics"""
        create_test_user(db_session, "user-123", "testuser1")
        
        request = TopicCreateRequest(
            title="Test Topic",
            content="This is test topic content with enough characters.",
            category_id=1
        )
        created = topic_service.create_topic("user-123", request)
        
        created.is_deleted = True
        topic_service.db.commit()
        
        topic = topic_service.get_topic(created.id)
        assert topic is None
    
    def test_list_topics(self, topic_service, db_session):
        """Test listing topics with pagination"""
        create_test_user(db_session, "user-123", "testuser1")
        
        for i in range(5):
            request = TopicCreateRequest(
                title=f"Topic {i}",
                content=f"Content for topic {i} with enough characters.",
                category_id=1
            )
            topic_service.create_topic("user-123", request)
        
        topics, total = topic_service.list_topics(page=1, page_size=3)
        
        assert total == 5
        assert len(topics) == 3
        
        topics, total = topic_service.list_topics(page=2, page_size=3)
        assert len(topics) == 2
    
    def test_list_topics_with_category_filter(self, topic_service, db_session):
        """Test listing topics with category filter"""
        create_test_user(db_session, "user-123", "testuser1")
        
        for i in range(3):
            request = TopicCreateRequest(
                title=f"Topic Cat1-{i}",
                content=f"Content for topic {i} with enough characters.",
                category_id=1
            )
            topic_service.create_topic("user-123", request)
        
        for i in range(2):
            request = TopicCreateRequest(
                title=f"Topic Cat2-{i}",
                content=f"Content for topic {i} with enough characters.",
                category_id=2
            )
            topic_service.create_topic("user-123", request)
        
        topics, total = topic_service.list_topics(category_id=1)
        assert total == 3
        
        topics, total = topic_service.list_topics(category_id=2)
        assert total == 2
    
    def test_list_topics_with_search(self, topic_service, db_session):
        """Test listing topics with search"""
        create_test_user(db_session, "user-123", "testuser1")
        
        request1 = TopicCreateRequest(
            title="Python Tutorial",
            content="Learn Python programming from scratch.",
            category_id=1
        )
        request2 = TopicCreateRequest(
            title="Java Guide",
            content="Learn Java programming language.",
            category_id=1
        )
        
        topic_service.create_topic("user-123", request1)
        topic_service.create_topic("user-123", request2)
        
        topics, total = topic_service.list_topics(search="Python")
        
        assert total == 1
        assert topics[0].title == "Python Tutorial"
        
        topics, total = topic_service.list_topics(search="programming")
        assert total == 2
    
    def test_update_topic(self, topic_service, db_session):
        """Test updating a topic"""
        create_test_user(db_session, "user-123", "testuser1")
        
        request = TopicCreateRequest(
            title="Original Title",
            content="Original content with enough characters.",
            category_id=1
        )
        created = topic_service.create_topic("user-123", request)
        
        update_request = TopicUpdateRequest(
            title="Updated Title",
            content="Updated content with enough characters."
        )
        
        updated = topic_service.update_topic(
            topic_id=created.id,
            author_id="user-123",
            request=update_request
        )
        
        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.content == "Updated content with enough characters."
    
    def test_update_topic_wrong_user(self, topic_service, db_session):
        """Test that update fails for wrong user"""
        create_test_user(db_session, "user-123", "testuser1")
        create_test_user(db_session, "user-456", "testuser2")
        
        request = TopicCreateRequest(
            title="Original Title",
            content="Original content with enough characters.",
            category_id=1
        )
        created = topic_service.create_topic("user-123", request)
        
        update_request = TopicUpdateRequest(title="New Title")
        
        updated = topic_service.update_topic(
            topic_id=created.id,
            author_id="user-456",
            request=update_request
        )
        
        assert updated is None
    
    def test_delete_topic(self, topic_service, db_session):
        """Test soft deleting a topic"""
        create_test_user(db_session, "user-123", "testuser1")
        
        request = TopicCreateRequest(
            title="To Be Deleted",
            content="Content to be deleted with enough characters.",
            category_id=1
        )
        created = topic_service.create_topic("user-123", request)
        
        success = topic_service.delete_topic(created.id, "user-123")
        
        assert success == True
        
        deleted = db_session.get(Topic, created.id)
        assert deleted.is_deleted == True
    
    def test_delete_topic_wrong_user(self, topic_service, db_session):
        """Test that delete fails for wrong user"""
        create_test_user(db_session, "user-123", "testuser1")
        create_test_user(db_session, "user-456", "testuser2")
        
        request = TopicCreateRequest(
            title="To Be Deleted",
            content="Content to be deleted with enough characters.",
            category_id=1
        )
        created = topic_service.create_topic("user-123", request)
        
        success = topic_service.delete_topic(created.id, "user-456")
        
        assert success == False
    
    def test_increment_view(self, topic_service, db_session):
        """Test incrementing view count"""
        create_test_user(db_session, "user-123", "testuser1")
        
        request = TopicCreateRequest(
            title="Test Topic",
            content="Test content with enough characters.",
            category_id=1
        )
        created = topic_service.create_topic("user-123", request)
        
        initial_count = created.view_count
        
        topic_service.increment_view(created.id)
        topic_service.increment_view(created.id)
        
        topic = db_session.get(Topic, created.id)
        
        assert topic.view_count == initial_count + 2


class TestPostService:
    """Test PostService CRUD operations"""
    
    @pytest.fixture
    def topic_service(self, db_session):
        """Create TopicService instance"""
        return TopicService(db_session)
    
    @pytest.fixture
    def post_service(self, db_session):
        """Create PostService instance"""
        return PostService(db_session)
    
    @pytest.fixture
    def test_topic(self, topic_service, db_session):
        """Create a test topic"""
        create_test_user(db_session, "user-123", "testuser1")
        
        request = TopicCreateRequest(
            title="Test Topic",
            content="This is test topic content with enough characters.",
            category_id=1
        )
        return topic_service.create_topic("user-123", request)
    
    def test_create_post(self, post_service, test_topic, db_session):
        """Test creating a new post"""
        create_test_user(db_session, "user-456", "testuser2")
        
        request = PostCreateRequest(
            content="This is a test post."
        )
        
        post = post_service.create_post(
            topic_id=test_topic.id,
            author_id="user-456",
            request=request
        )
        
        assert post.id is not None
        assert post.topic_id == test_topic.id
        assert post.author_id == "user-456"
        assert post.content == "This is a test post."
        assert post.is_accepted == False
        
        topic = db_session.get(Topic, test_topic.id)
        assert topic.post_count == 1
    
    def test_create_reply_post(self, post_service, test_topic, db_session):
        """Test creating a reply post"""
        create_test_user(db_session, "user-456", "testuser2")
        create_test_user(db_session, "user-789", "testuser3")
        
        parent_request = PostCreateRequest(content="Parent post")
        parent = post_service.create_post(test_topic.id, "user-456", parent_request)
        
        reply_request = PostCreateRequest(
            content="Reply post",
            parent_id=parent.id
        )
        
        reply = post_service.create_post(
            topic_id=test_topic.id,
            author_id="user-789",
            request=reply_request
        )
        
        assert reply.parent_id == parent.id
    
    def test_get_posts(self, post_service, test_topic, db_session):
        """Test getting posts for a topic"""
        create_test_user(db_session, "user-456", "testuser2")
        
        for i in range(5):
            request = PostCreateRequest(content=f"Post {i}")
            post_service.create_post(test_topic.id, "user-456", request)
        
        posts, total = post_service.get_posts(test_topic.id, page=1, page_size=3)
        
        assert total == 5
        assert len(posts) == 3
        
        posts, total = post_service.get_posts(test_topic.id, page=2, page_size=3)
        assert len(posts) == 2
    
    def test_accept_post(self, post_service, test_topic, db_session):
        """Test accepting a post as answer"""
        create_test_user(db_session, "user-456", "testuser2")
        
        request = PostCreateRequest(content="Best answer")
        post = post_service.create_post(test_topic.id, "user-456", request)
        
        success = post_service.accept_post(
            topic_id=test_topic.id,
            post_id=post.id,
            author_id="user-123"
        )
        
        assert success == True
        
        topic = db_session.get(Topic, test_topic.id)
        assert topic.accepted_post_id == post.id
        assert topic.bounty_status == BountyStatus.RESOLVED
        
        updated_post = db_session.get(Post, post.id)
        assert updated_post.is_accepted == True
    
    def test_accept_post_wrong_author(self, post_service, test_topic, db_session):
        """Test that accept fails for wrong author"""
        create_test_user(db_session, "user-456", "testuser2")
        
        request = PostCreateRequest(content="Best answer")
        post = post_service.create_post(test_topic.id, "user-456", request)
        
        success = post_service.accept_post(
            topic_id=test_topic.id,
            post_id=post.id,
            author_id="user-456"
        )
        
        assert success == False
    
    def test_delete_post(self, post_service, test_topic, db_session):
        """Test deleting a post"""
        create_test_user(db_session, "user-456", "testuser2")
        
        request = PostCreateRequest(content="To be deleted")
        post = post_service.create_post(test_topic.id, "user-456", request)
        
        success = post_service.delete_post(post.id, "user-456")
        
        assert success == True
        
        deleted = db_session.get(Post, post.id)
        assert deleted is None
        
        topic = db_session.get(Topic, test_topic.id)
        assert topic.post_count == 0
    
    def test_delete_post_wrong_author(self, post_service, test_topic, db_session):
        """Test that delete fails for wrong author"""
        create_test_user(db_session, "user-456", "testuser2")
        create_test_user(db_session, "user-789", "testuser3")
        
        request = PostCreateRequest(content="Post")
        post = post_service.create_post(test_topic.id, "user-456", request)
        
        success = post_service.delete_post(post.id, "user-789")
        
        assert success == False


class TestBountyWorkflow:
    """Test bounty system workflow"""
    
    @pytest.fixture
    def topic_service(self, db_session):
        return TopicService(db_session)
    
    @pytest.fixture
    def post_service(self, db_session):
        return PostService(db_session)
    
    def test_bounty_workflow(self, topic_service, post_service, db_session):
        """Test full bounty workflow: create topic -> post answer -> accept"""
        create_test_user(db_session, "user-123", "testuser1")
        create_test_user(db_session, "user-456", "testuser2")
        
        topic_request = TopicCreateRequest(
            title="Bounty Question",
            content="I have a question about reliability engineering.",
            category_id=1,
            bounty_amount=100
        )
        topic = topic_service.create_topic("user-123", topic_request)
        
        assert topic.bounty_status == BountyStatus.ACTIVE
        
        post_request = PostCreateRequest(content="Here is the answer!")
        post = post_service.create_post(topic.id, "user-456", post_request)
        
        success = post_service.accept_post(topic.id, post.id, "user-123")
        
        assert success == True
        
        topic_updated = db_session.get(Topic, topic.id)
        
        assert topic_updated.accepted_post_id == post.id
        assert topic_updated.bounty_status == BountyStatus.RESOLVED


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
