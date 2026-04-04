"""
Service layer for AI Conversation module.
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
import uuid

from app.models.ai_session import AISession
from app.models.ai_message import AIMessage
from app.schemas.ai import MessageRequest, CreateSessionRequest, FeedbackRequest


class AISessionService:
    """Service class for AI Session management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        user_id: Optional[str],
        request: CreateSessionRequest
    ) -> AISession:
        """Create a new AI session"""
        session = AISession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=request.title,
            model_type=request.model_type,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> Optional[AISession]:
        """Get a session by ID"""
        query = select(AISession).where(
            AISession.id == session_id,
            AISession.is_deleted == False
        )
        
        if user_id:
            query = query.where(AISession.user_id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_sessions(
        self,
        user_id: Optional[str],
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[AISession], int]:
        """List sessions for a user with pagination"""
        # Get total count
        count_query = select(func.count()).where(
            AISession.user_id == user_id,
            AISession.is_deleted == False
        )
        total = (await self.db.execute(count_query)).scalar()
        
        # Get paginated results
        query = (
            select(AISession)
            .where(
                AISession.user_id == user_id,
                AISession.is_deleted == False
            )
            .order_by(AISession.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        
        return list(sessions), total

    async def delete_session(
        self,
        session_id: str,
        user_id: Optional[str]
    ) -> bool:
        """Soft delete a session"""
        session = await self.get_session(session_id, user_id)
        if not session:
            return False
        
        session.is_deleted = True
        await self.db.commit()
        return True

    async def update_token_count(
        self,
        session_id: str,
        token_count: int
    ) -> AISession:
        """Update session token count"""
        session = await self.get_session(session_id)
        if session:
            session.total_tokens += token_count
            session.total_turns += 1
            await self.db.commit()
            await self.db.refresh(session)
        return session


class AIMessageService:
    """Service class for AI Message management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(
        self,
        session_id: str,
        role: str,
        content: str,
        token_count: int = 0,
        attachment_ids: Optional[List[str]] = None
    ) -> AIMessage:
        """Create a new message"""
        has_attachment = bool(attachment_ids)
        
        message = AIMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            token_count=token_count,
            has_attachment=has_attachment,
            attachment_ids=",".join(attachment_ids) if attachment_ids else None,
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_messages(
        self,
        session_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[AIMessage], int]:
        """Get messages for a session with pagination"""
        # Get total count
        count_query = select(func.count()).where(
            AIMessage.session_id == session_id,
            AIMessage.is_deleted == False
        )
        total = (await self.db.execute(count_query)).scalar()
        
        # Get paginated results
        query = (
            select(AIMessage)
            .where(
                AIMessage.session_id == session_id,
                AIMessage.is_deleted == False
            )
            .order_by(AIMessage.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        return list(messages), total

    async def add_feedback(
        self,
        message_id: str,
        feedback_type: str
    ) -> bool:
        """Add feedback to a message"""
        query = select(AIMessage).where(AIMessage.id == message_id)
        result = await self.db.execute(query)
        message = result.scalar_one_or_none()
        
        if message:
            message.feedback_type = feedback_type
            message.feedback_at = datetime.utcnow()
            await self.db.commit()
            return True
        return False

    async def get_conversation_history(
        self,
        session_id: str,
        max_turns: int = 50
    ) -> List[Tuple[str, str]]:
        """Get conversation history for LLM context"""
        query = (
            select(AIMessage)
            .where(
                AIMessage.session_id == session_id,
                AIMessage.is_deleted == False
            )
            .order_by(AIMessage.created_at.asc())
            .limit(max_turns)
        )
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        return [(msg.role, msg.content) for msg in messages]
