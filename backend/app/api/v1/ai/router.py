"""
API routes for AI Conversation module.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.deps import get_db, get_current_user
from app.services.ai_service import AISessionService, AIMessageService
from app.schemas.ai import (
    MessageRequest,
    CreateSessionRequest,
    SessionResponse,
    SessionListResponse,
    MessageResponse,
    MessageListResponse,
    FeedbackRequest,
)
from app.models.users import User

router = APIRouter(prefix="/ai", tags=["AI 对话"])


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Create a new AI session"""
    user_id = current_user.user_uuid if current_user else None
    service = AISessionService(db)
    session = await service.create_session(user_id, request)
    return session


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """List user's AI sessions"""
    user_id = current_user.user_uuid if current_user else None
    
    if not user_id:
        # For guest users, return empty list
        return SessionListResponse(sessions=[], total=0)
    
    service = AISessionService(db)
    sessions, total = await service.list_sessions(user_id, page, page_size)
    
    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=total
    )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get a specific session"""
    user_id = current_user.user_uuid if current_user else None
    service = AISessionService(db)
    session = await service.get_session(session_id, user_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Delete a session"""
    user_id = current_user.user_uuid if current_user else None
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    service = AISessionService(db)
    success = await service.delete_session(session_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}


@router.get("/sessions/{session_id}/messages", response_model=MessageListResponse)
async def list_messages(
    session_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get messages for a session"""
    user_id = current_user.user_uuid if current_user else None
    service = AISessionService(db)
    
    # Verify session ownership
    session = await service.get_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    message_service = AIMessageService(db)
    messages, total = await message_service.get_messages(session_id, page, page_size)
    
    return MessageListResponse(
        messages=[MessageResponse.model_validate(m) for m in messages],
        total=total
    )


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def create_message(
    session_id: str,
    request: MessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Send a message to AI.
    
    This endpoint:
    1. Saves user message
    2. Calls LLM API
    3. Saves AI response
    4. Updates token count
    """
    user_id = current_user.user_uuid if current_user else None
    session_service = AISessionService(db)
    
    # Verify session ownership
    session = await session_service.get_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    message_service = AIMessageService(db)
    
    # Save user message
    user_message = await message_service.create_message(
        session_id=session_id,
        role="user",
        content=request.content,
        attachment_ids=request.attachment_ids,
    )
    
    # TODO: Call LLM API to get response
    # For now, return a placeholder response
    ai_message = await message_service.create_message(
        session_id=session_id,
        role="assistant",
        content="This is a placeholder response. LLM integration pending.",
        token_count=10,
    )
    
    # Update session token count
    await session_service.update_token_count(session_id, ai_message.token_count)
    
    return ai_message


@router.post("/messages/{message_id}/feedback")
async def add_feedback(
    message_id: str,
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Add feedback to a message"""
    service = AIMessageService(db)
    success = await service.add_feedback(message_id, request.feedback_type)
    
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return {"message": "Feedback recorded successfully"}
