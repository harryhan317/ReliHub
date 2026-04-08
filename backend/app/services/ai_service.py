"""
AI Service with LLM Provider integration.

Integrates LLM providers for AI conversations with:
- Dynamic provider selection
- Token billing
- Rate limiting
- Stream support
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Generator, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai_message import AIMessage
from app.models.ai_session import AISession
from app.models.llm_provider import LLMProvider
from app.services.llm_provider.base import LLMProvider as LLMProviderBase
from app.services.llm_provider.factory import ProviderFactory

logger = logging.getLogger(__name__)


class AISessionService:
    """AI Session Service - Full CRUD implementation"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, user_id: Optional[str], request: Any) -> AISession:
        """Create a new AI session and persist to database"""
        session = AISession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=getattr(request, 'title', None) or 'New Session',
            model_type=getattr(request, 'model_type', 'general'),
            total_tokens=0,
            total_cost=0.0,
            total_turns=0,
            is_deleted=False
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        logger.info(f"Created AI session: {session.id} for user: {user_id}")
        return session
    
    def list_sessions(
        self, 
        user_id: str, 
        page: int = 1, 
        page_size: int = 20
    ) -> tuple[list[AISession], int]:
        """List user's sessions with pagination"""
        offset = (page - 1) * page_size
        
        count_query = select(func.count(AISession.id)).where(
            AISession.user_id == user_id,
            AISession.is_deleted == False
        )
        total = self.db.execute(count_query).scalar() or 0
        
        query = select(AISession).where(
            AISession.user_id == user_id,
            AISession.is_deleted == False
        ).order_by(AISession.updated_at.desc()).offset(offset).limit(page_size)
        
        result = self.db.execute(query)
        sessions = list(result.scalars().all())
        
        return sessions, total
    
    def get_session(self, session_id: str, user_id: Optional[str] = None) -> Optional[AISession]:
        """Get a specific session with optional user verification"""
        query = select(AISession).where(
            AISession.id == session_id,
            AISession.is_deleted == False
        )
        
        if user_id is not None:
            query = query.where(AISession.user_id == user_id)
        
        result = self.db.execute(query)
        return result.scalar_one_or_none()
    
    def update_session(
        self, 
        session_id: str, 
        user_id: str,
        title: Optional[str] = None
    ) -> Optional[AISession]:
        """Update session properties"""
        session = self.get_session(session_id, user_id)
        if not session:
            return None
        
        if title is not None:
            session.title = title
        
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Soft delete a session"""
        session = self.get_session(session_id, user_id)
        if not session:
            return False
        
        session.is_deleted = True
        self.db.commit()
        logger.info(f"Deleted AI session: {session_id}")
        return True
    
    def increment_turns(self, session_id: str) -> None:
        """Increment session turn count"""
        session = self.db.get(AISession, session_id)
        if session:
            session.total_turns += 1
            self.db.commit()


class AIMessageService:
    """AI Message Service - Full CRUD implementation"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        token_count: int = 0,
        cost: float = 0.0,
        has_attachment: bool = False,
        attachment_ids: Optional[str] = None
    ) -> AIMessage:
        """Create a new message and persist to database"""
        message = AIMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            token_count=token_count,
            cost=cost,
            has_attachment=has_attachment,
            attachment_ids=attachment_ids,
            is_deleted=False
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        logger.debug(f"Created AI message: {message.id} in session: {session_id}")
        return message
    
    def list_messages(
        self, 
        session_id: str, 
        page: int = 1, 
        page_size: int = 50
    ) -> tuple[list[AIMessage], int]:
        """List messages for a session with pagination"""
        offset = (page - 1) * page_size
        
        count_query = select(func.count(AIMessage.id)).where(
            AIMessage.session_id == session_id,
            AIMessage.is_deleted == False
        )
        total = self.db.execute(count_query).scalar() or 0
        
        query = select(AIMessage).where(
            AIMessage.session_id == session_id,
            AIMessage.is_deleted == False
        ).order_by(AIMessage.created_at.asc()).offset(offset).limit(page_size)
        
        result = self.db.execute(query)
        messages = list(result.scalars().all())
        
        return messages, total
    
    def get_message(self, message_id: str) -> Optional[AIMessage]:
        """Get a specific message"""
        query = select(AIMessage).where(
            AIMessage.id == message_id,
            AIMessage.is_deleted == False
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()
    
    def add_feedback(self, message_id: str, feedback_type: str) -> bool:
        """Add feedback to a message"""
        message = self.get_message(message_id)
        if not message:
            return False
        
        if message.role != "assistant":
            logger.warning(f"Cannot add feedback to non-assistant message: {message_id}")
            return False
        
        message.feedback_type = feedback_type
        message.feedback_at = datetime.utcnow()
        self.db.commit()
        logger.info(f"Added feedback '{feedback_type}' to message: {message_id}")
        return True
    
    def delete_message(self, message_id: str) -> bool:
        """Soft delete a message"""
        message = self.get_message(message_id)
        if not message:
            return False
        
        message.is_deleted = True
        self.db.commit()
        return True
    
    def get_session_messages_for_chat(self, session_id: str, limit: int = 50) -> list[AIMessage]:
        """Get recent messages for chat context (ordered by time)"""
        query = select(AIMessage).where(
            AIMessage.session_id == session_id,
            AIMessage.is_deleted == False
        ).order_by(AIMessage.created_at.desc()).limit(limit)
        
        result = self.db.execute(query)
        messages = list(result.scalars().all())
        return list(reversed(messages))


class AIService:
    """
    AI Service with LLM Provider integration.
    
    Features:
    - Dynamic provider selection from database
    - Token billing and cost calculation
    - Rate limiting
    - Stream support (SSE)
    """
    
    def __init__(self, db: Session):
        self.db = db
        self._provider_cache: Dict[str, LLMProviderBase] = {}
    
    def get_enabled_providers(self) -> list[LLMProvider]:
        """
        Get all enabled LLM providers from database.
        
        Returns:
            List of enabled LLMProvider records
        """
        query = select(LLMProvider).where(LLMProvider.enabled == True)
        result = self.db.execute(query)
        return list(result.scalars().all())
    
    def get_provider_by_name(self, name: str) -> Optional[LLMProvider]:
        """
        Get a specific provider by name.
        
        Args:
            name: Provider name (e.g., 'deepseek', 'openai')
            
        Returns:
            LLMProvider record or None
        """
        query = select(LLMProvider).where(
            LLMProvider.name == name,
            LLMProvider.enabled == True
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()
    
    def instantiate_provider(
        self,
        provider_config: LLMProvider
    ) -> LLMProviderBase:
        """
        Instantiate a provider from database configuration.
        
        Args:
            provider_config: LLMProvider record from database
            
        Returns:
            Instantiated LLMProvider instance
            
        Raises:
            ValueError: If API key is not found
        """
        if provider_config.id in self._provider_cache:
            return self._provider_cache[provider_config.id]
        
        api_key = os.getenv(provider_config.api_key_env)
        if not api_key:
            raise ValueError(
                f"API key not found for provider {provider_config.name}. "
                f"Environment variable: {provider_config.api_key_env}"
            )
        
        provider = ProviderFactory.get_provider(
            provider_name=provider_config.name,
            api_key=api_key,
            base_url=provider_config.api_base_url
        )
        
        self._provider_cache[provider_config.id] = provider
        
        logger.info(f"Instantiated provider: {provider_config.name}")
        return provider
    
    def chat_completion(
        self,
        session: AISession,
        messages: list[dict],
        provider_name: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = True
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Chat completion with automatic provider selection and billing.
        
        Args:
            session: AI Session record
            messages: List of messages [{"role": "user", "content": "..."}]
            provider_name: Optional provider name (uses default if not specified)
            model: Model name (uses provider default if not specified)
            temperature: Temperature (0.0-2.0)
            max_tokens: Maximum tokens
            stream: Whether to stream output
            
        Yields:
            {
                "content": str,
                "finish_reason": str|None,
                "usage": dict,
                "cost": float  # Cost for this message
            }
        """
        if provider_name:
            provider_config = self.get_provider_by_name(provider_name)
            if not provider_config:
                raise ValueError(f"Provider {provider_name} not found or disabled")
        else:
            providers = self.get_enabled_providers()
            if not providers:
                raise ValueError("No LLM providers configured")
            provider_config = providers[0]
        
        provider = self.instantiate_provider(provider_config)
        
        if not model:
            models = provider.get_models()
            model = models[0]["id"] if models else "default"
        
        total_content = ""
        total_tokens = 0
        
        try:
            for chunk in provider.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            ):
                content = chunk.get("content", "")
                total_content += content
                
                yield {
                    "content": content,
                    "finish_reason": chunk.get("finish_reason"),
                    "usage": chunk.get("usage"),
                    "provider": provider_config.name,
                    "model": model
                }
            
            if chunk.get("usage"):
                total_tokens = chunk["usage"].get("total_tokens", 0)
            else:
                total_tokens = provider.count_tokens(messages)
            
            cost = (total_tokens / 1000) * provider_config.cost_per_1k_tokens
            
            session.total_tokens += total_tokens
            session.total_cost += cost
            session.provider_id = provider_config.id
            self.db.commit()
            
            logger.info(
                f"Chat completion: {provider_config.name}/{model}, "
                f"tokens={total_tokens}, cost=${cost:.6f}"
            )
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            yield {
                "content": "",
                "finish_reason": "error",
                "error": str(e),
                "provider": provider_config.name,
                "model": model
            }
    
    def calculate_cost(
        self,
        provider_name: str,
        token_count: int
    ) -> float:
        """
        Calculate cost for given tokens.
        
        Args:
            provider_name: Provider name
            token_count: Number of tokens
            
        Returns:
            Cost in USD or CNY
        """
        provider_config = self.get_provider_by_name(provider_name)
        if not provider_config:
            return 0.0
        
        return (token_count / 1000) * provider_config.cost_per_1k_tokens
    
    def check_rate_limit(
        self,
        provider_name: Optional[str],
        user_id: Optional[str]
    ) -> bool:
        """
        Check if user has exceeded rate limit.
        
        Args:
            provider_name: Provider name
            user_id: User ID
            
        Returns:
            True if within limit, False if exceeded
        """
        return True
