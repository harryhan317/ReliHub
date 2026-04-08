"""
Unit tests for AI Session and Message Services.

Tests:
1. AISessionService CRUD operations
2. AIMessageService CRUD operations
3. Pagination
4. Soft delete
5. Feedback functionality

Database: PostgreSQL (uses shared fixtures from conftest.py)
"""

import pytest

from app.services.ai_service import AISessionService, AIMessageService
from app.models.ai_session import AISession
from app.models.ai_message import AIMessage


class TestAISessionService:
    """Test AISessionService CRUD operations"""
    
    @pytest.fixture
    def session_service(self, db_session):
        """Create AISessionService instance"""
        return AISessionService(db_session)
    
    def test_create_session(self, session_service):
        """Test creating a new session"""
        request = type('Request', (), {'title': 'Test Session', 'model_type': 'general'})()
        
        session = session_service.create_session(user_id='user-123', request=request)
        
        assert session.id is not None
        assert session.user_id == 'user-123'
        assert session.title == 'Test Session'
        assert session.model_type == 'general'
        assert session.total_tokens == 0
        assert session.total_cost == 0.0
        assert session.total_turns == 0
        assert session.is_deleted == False
    
    def test_create_session_with_default_title(self, session_service):
        """Test creating a session with default title"""
        request = type('Request', (), {})()
        
        session = session_service.create_session(user_id='user-123', request=request)
        
        assert session.title == 'New Session'
    
    def test_list_sessions(self, session_service):
        """Test listing sessions with pagination"""
        for i in range(5):
            request = type('Request', (), {'title': f'Session {i}'})()
            session_service.create_session(user_id='user-123', request=request)
        
        sessions, total = session_service.list_sessions(user_id='user-123', page=1, page_size=3)
        
        assert total == 5
        assert len(sessions) == 3
        
        sessions, total = session_service.list_sessions(user_id='user-123', page=2, page_size=3)
        assert len(sessions) == 2
    
    def test_list_sessions_only_user_sessions(self, session_service):
        """Test that list_sessions only returns user's own sessions"""
        request1 = type('Request', (), {'title': 'User 1 Session'})()
        request2 = type('Request', (), {'title': 'User 2 Session'})()
        
        session_service.create_session(user_id='user-1', request=request1)
        session_service.create_session(user_id='user-2', request=request2)
        
        sessions, total = session_service.list_sessions(user_id='user-1', page=1, page_size=10)
        
        assert total == 1
        assert sessions[0].title == 'User 1 Session'
    
    def test_get_session(self, session_service):
        """Test getting a specific session"""
        request = type('Request', (), {'title': 'Test Session'})()
        created = session_service.create_session(user_id='user-123', request=request)
        
        session = session_service.get_session(created.id, user_id='user-123')
        
        assert session is not None
        assert session.id == created.id
        assert session.title == 'Test Session'
    
    def test_get_session_wrong_user(self, session_service):
        """Test getting a session with wrong user"""
        request = type('Request', (), {'title': 'Test Session'})()
        created = session_service.create_session(user_id='user-123', request=request)
        
        session = session_service.get_session(created.id, user_id='user-456')
        
        assert session is None
    
    def test_get_session_without_user_check(self, session_service):
        """Test getting a session without user verification"""
        request = type('Request', (), {'title': 'Test Session'})()
        created = session_service.create_session(user_id='user-123', request=request)
        
        session = session_service.get_session(created.id, user_id=None)
        
        assert session is not None
        assert session.id == created.id
    
    def test_update_session(self, session_service):
        """Test updating a session"""
        request = type('Request', (), {'title': 'Original Title'})()
        created = session_service.create_session(user_id='user-123', request=request)
        
        updated = session_service.update_session(created.id, 'user-123', title='Updated Title')
        
        assert updated is not None
        assert updated.title == 'Updated Title'
    
    def test_update_session_wrong_user(self, session_service):
        """Test updating a session with wrong user"""
        request = type('Request', (), {'title': 'Original Title'})()
        created = session_service.create_session(user_id='user-123', request=request)
        
        updated = session_service.update_session(created.id, 'user-456', title='Updated Title')
        
        assert updated is None
    
    def test_delete_session(self, session_service):
        """Test soft deleting a session"""
        request = type('Request', (), {'title': 'Test Session'})()
        created = session_service.create_session(user_id='user-123', request=request)
        
        success = session_service.delete_session(created.id, 'user-123')
        
        assert success == True
        
        session = session_service.get_session(created.id, 'user-123')
        assert session is None
        
        db_session = session_service.db
        deleted = db_session.get(AISession, created.id)
        assert deleted.is_deleted == True
    
    def test_delete_session_wrong_user(self, session_service):
        """Test deleting a session with wrong user"""
        request = type('Request', (), {'title': 'Test Session'})()
        created = session_service.create_session(user_id='user-123', request=request)
        
        success = session_service.delete_session(created.id, 'user-456')
        
        assert success == False
    
    def test_increment_turns(self, session_service):
        """Test incrementing session turns"""
        request = type('Request', (), {'title': 'Test Session'})()
        created = session_service.create_session(user_id='user-123', request=request)
        
        session_service.increment_turns(created.id)
        session_service.increment_turns(created.id)
        
        db_session = session_service.db
        session = db_session.get(AISession, created.id)
        assert session.total_turns == 2


class TestAIMessageService:
    """Test AIMessageService CRUD operations"""
    
    @pytest.fixture
    def message_service(self, db_session):
        """Create AIMessageService instance"""
        return AIMessageService(db_session)
    
    @pytest.fixture
    def session_service(self, db_session):
        """Create AISessionService instance"""
        return AISessionService(db_session)
    
    @pytest.fixture
    def test_session(self, session_service):
        """Create a test session"""
        request = type('Request', (), {'title': 'Test Session'})()
        return session_service.create_session(user_id='user-123', request=request)
    
    def test_create_message(self, message_service, test_session):
        """Test creating a new message"""
        message = message_service.create_message(
            session_id=test_session.id,
            role='user',
            content='Hello, AI!',
            token_count=10
        )
        
        assert message.id is not None
        assert message.session_id == test_session.id
        assert message.role == 'user'
        assert message.content == 'Hello, AI!'
        assert message.token_count == 10
        assert message.is_deleted == False
    
    def test_create_message_with_attachment(self, message_service, test_session):
        """Test creating a message with attachment"""
        message = message_service.create_message(
            session_id=test_session.id,
            role='user',
            content='Check this file',
            has_attachment=True,
            attachment_ids='file-1,file-2'
        )
        
        assert message.has_attachment == True
        assert message.attachment_ids == 'file-1,file-2'
    
    def test_list_messages(self, message_service, test_session):
        """Test listing messages with pagination"""
        for i in range(5):
            message_service.create_message(
                session_id=test_session.id,
                role='user' if i % 2 == 0 else 'assistant',
                content=f'Message {i}'
            )
        
        messages, total = message_service.list_messages(test_session.id, page=1, page_size=3)
        
        assert total == 5
        assert len(messages) == 3
        
        messages, total = message_service.list_messages(test_session.id, page=2, page_size=3)
        assert len(messages) == 2
    
    def test_list_messages_order(self, message_service, test_session):
        """Test that messages are ordered by created_at ascending"""
        import time
        
        message_service.create_message(
            session_id=test_session.id,
            role='user',
            content='First'
        )
        time.sleep(0.01)
        message_service.create_message(
            session_id=test_session.id,
            role='assistant',
            content='Second'
        )
        
        messages, _ = message_service.list_messages(test_session.id, page=1, page_size=10)
        
        assert messages[0].content == 'First'
        assert messages[1].content == 'Second'
    
    def test_get_message(self, message_service, test_session):
        """Test getting a specific message"""
        created = message_service.create_message(
            session_id=test_session.id,
            role='user',
            content='Test message'
        )
        
        message = message_service.get_message(created.id)
        
        assert message is not None
        assert message.id == created.id
        assert message.content == 'Test message'
    
    def test_get_nonexistent_message(self, message_service):
        """Test getting a nonexistent message"""
        message = message_service.get_message('nonexistent-id')
        
        assert message is None
    
    def test_add_feedback(self, message_service, test_session):
        """Test adding feedback to a message"""
        message = message_service.create_message(
            session_id=test_session.id,
            role='assistant',
            content='AI response'
        )
        
        success = message_service.add_feedback(message.id, 'like')
        
        assert success == True
        
        updated = message_service.get_message(message.id)
        assert updated.feedback_type == 'like'
        assert updated.feedback_at is not None
    
    def test_add_feedback_to_user_message(self, message_service, test_session):
        """Test that feedback cannot be added to user messages"""
        message = message_service.create_message(
            session_id=test_session.id,
            role='user',
            content='User message'
        )
        
        success = message_service.add_feedback(message.id, 'like')
        
        assert success == False
    
    def test_add_feedback_nonexistent_message(self, message_service):
        """Test adding feedback to nonexistent message"""
        success = message_service.add_feedback('nonexistent-id', 'like')
        
        assert success == False
    
    def test_delete_message(self, message_service, test_session):
        """Test soft deleting a message"""
        message = message_service.create_message(
            session_id=test_session.id,
            role='user',
            content='To be deleted'
        )
        
        success = message_service.delete_message(message.id)
        
        assert success == True
        
        deleted = message_service.get_message(message.id)
        assert deleted is None
        
        db_session = message_service.db
        soft_deleted = db_session.get(AIMessage, message.id)
        assert soft_deleted.is_deleted == True
    
    def test_get_session_messages_for_chat(self, message_service, test_session):
        """Test getting messages for chat context"""
        import time
        
        for i in range(10):
            message_service.create_message(
                session_id=test_session.id,
                role='user' if i % 2 == 0 else 'assistant',
                content=f'Message {i}'
            )
            time.sleep(0.01)
        
        messages = message_service.get_session_messages_for_chat(test_session.id, limit=5)
        
        assert len(messages) == 5
        assert messages[0].content == 'Message 5'
        assert messages[4].content == 'Message 9'


class TestSessionMessageIntegration:
    """Test integration between Session and Message services"""
    
    def test_session_soft_delete_keeps_messages(self, db_session):
        """Test that soft deleting a session keeps messages in database"""
        session_service = AISessionService(db_session)
        message_service = AIMessageService(db_session)
        
        request = type('Request', (), {'title': 'Test Session'})()
        session = session_service.create_session(user_id='user-123', request=request)
        
        message_service.create_message(
            session_id=session.id,
            role='user',
            content='Message 1'
        )
        message_service.create_message(
            session_id=session.id,
            role='assistant',
            content='Message 2'
        )
        
        messages, total = message_service.list_messages(session.id, page=1, page_size=10)
        assert total == 2
        
        session_service.delete_session(session.id, 'user-123')
        
        messages, total = message_service.list_messages(session.id, page=1, page_size=10)
        assert total == 2
        
        deleted_session = db_session.get(AISession, session.id)
        assert deleted_session.is_deleted == True
    
    def test_full_conversation_flow(self, db_session):
        """Test a full conversation flow"""
        session_service = AISessionService(db_session)
        message_service = AIMessageService(db_session)
        
        request = type('Request', (), {'title': 'New Conversation'})()
        session = session_service.create_session(user_id='user-123', request=request)
        
        message_service.create_message(
            session_id=session.id,
            role='user',
            content='Hello!',
            token_count=5
        )
        
        message_service.create_message(
            session_id=session.id,
            role='assistant',
            content='Hi! How can I help you?',
            token_count=10
        )
        
        session_service.increment_turns(session.id)
        
        messages, total = message_service.list_messages(session.id, page=1, page_size=10)
        assert total == 2
        
        db_session.refresh(session)
        assert session.total_turns == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
