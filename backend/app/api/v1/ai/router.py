"""
API routes for AI Conversation module.

Supports:
- Stream responses (SSE)
- Multiple LLM providers
- Token billing
"""

import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.ai_message import AIMessage
from app.models.ai_session import AISession
from app.models.users import User
from app.schemas.ai import (
    CreateSessionRequest,
    FeedbackRequest,
    MessageListResponse,
    MessageRequest,
    MessageResponse,
    SessionListResponse,
    SessionResponse,
)
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI 对话"])


@router.post("/sessions", response_model=SessionResponse)
def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Create a new AI session"""
    from app.services.ai_service import AISessionService
    
    user_id = current_user.id if current_user else None
    service = AISessionService(db)
    session = service.create_session(user_id, request)
    return session


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """List user's AI sessions"""
    from app.services.ai_service import AISessionService
    
    user_id = current_user.id if current_user else None
    
    if not user_id:
        return SessionListResponse(sessions=[], total=0)
    
    service = AISessionService(db)
    sessions, total = service.list_sessions(user_id, page, page_size)
    
    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=total
    )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get a specific session"""
    from app.services.ai_service import AISessionService
    
    user_id = current_user.id if current_user else None
    service = AISessionService(db)
    session = service.get_session(session_id, user_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Delete a session"""
    from app.services.ai_service import AISessionService
    
    user_id = current_user.id if current_user else None
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    service = AISessionService(db)
    success = service.delete_session(session_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}


@router.get("/sessions/{session_id}/messages", response_model=MessageListResponse)
def list_messages(
    session_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get messages for a session"""
    from app.services.ai_service import AIMessageService, AISessionService
    
    user_id = current_user.id if current_user else None
    session_service = AISessionService(db)
    
    session = session_service.get_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    message_service = AIMessageService(db)
    messages, total = message_service.list_messages(session_id, page, page_size)
    
    return MessageListResponse(
        messages=[MessageResponse.model_validate(m) for m in messages],
        total=total
    )


@router.post("/sessions/{session_id}/messages")
def create_message(
    session_id: str,
    request: MessageRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Send a message to AI with stream support.
    
    Supports both streaming (SSE) and non-streaming responses.
    Use stream=true for real-time typing effect.
    """
    from app.services.ai_service import AIMessageService, AISessionService
    
    user_id = current_user.id if current_user else None
    session_service = AISessionService(db)
    
    session = session_service.get_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    message_service = AIMessageService(db)
    ai_service = AIService(db)

    message_service.create_message(
        session_id=session_id,
        role="user",
        content=request.content,
        token_count=0
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        *[_message_to_dict(m) for m in message_service.list_messages(session_id, 1, 50)[0]]
    ]
    
    provider_name = request.provider_name if hasattr(request, 'provider_name') else None
    if not ai_service.check_rate_limit(provider_name, user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    if request.stream:
        return StreamingResponse(
            _stream_response(
                ai_service=ai_service,
                session=session,
                messages=messages,
                provider_name=provider_name,
                model=request.model if hasattr(request, 'model') else None,
                temperature=request.temperature if hasattr(request, 'temperature') else 0.7,
                max_tokens=request.max_tokens if hasattr(request, 'max_tokens') else 2000
            ),
            media_type="text/event-stream"
        )
    else:
        full_content = ""
        for chunk in ai_service.chat_completion(
            session=session,
            messages=messages,
            provider_name=provider_name,
            model=request.model if hasattr(request, 'model') else None,
            temperature=request.temperature if hasattr(request, 'temperature') else 0.7,
            max_tokens=request.max_tokens if hasattr(request, 'max_tokens') else 2000,
            stream=False
        ):
            full_content += chunk.get("content", "")
        
        ai_message = message_service.create_message(
            session_id=session_id,
            role="assistant",
            content=full_content,
            token_count=0
        )
        
        return MessageResponse.model_validate(ai_message)


def _stream_response(
    ai_service: AIService,
    session: AISession,
    messages: list,
    provider_name: Optional[str],
    model: Optional[str],
    temperature: float,
    max_tokens: int
):
    """
    Stream AI response using SSE.
    
    Format:
    data: {"content": "Hello", "finish_reason": null}
    data: {"content": "!", "finish_reason": "stop"}
    """
    try:
        from app.services.ai_service import AIMessageService
        
        db = ai_service.db
        message_service = AIMessageService(db)
        
        full_content = ""
        
        for chunk in ai_service.chat_completion(
            session=session,
            messages=messages,
            provider_name=provider_name,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        ):
            content = chunk.get("content", "")
            full_content += content

            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        message_service.create_message(
            session_id=session.id,
            role="assistant",
            content=full_content,
            token_count=0
        )

        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"Stream error: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


def _message_to_dict(message: AIMessage) -> dict:
    """Convert AIMessage to dict"""
    return {
        "role": message.role,
        "content": message.content
    }


@router.post("/sessions/{session_id}/feedback")
def add_feedback(
    session_id: str,
    message_id: str,
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Add feedback to an AI message"""
    from app.services.ai_service import AIMessageService

    message_service = AIMessageService(db)

    message = message_service.get_message(message_id)
    if not message or message.session_id != session_id:
        raise HTTPException(status_code=404, detail="Message not found")

    message_service.add_feedback(
        message_id=message_id,
        feedback_type=request.feedback_type
    )
    
    return {"message": "Feedback recorded"}


@router.get("/providers", response_model=List[dict])
def list_providers(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    List available LLM providers.
    
    Returns enabled providers that users can select.
    """
    ai_service = AIService(db)
    providers = ai_service.get_enabled_providers()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "display_name": p.display_name,
            "cost_per_1k_tokens": p.cost_per_1k_tokens
        }
        for p in providers
    ]
