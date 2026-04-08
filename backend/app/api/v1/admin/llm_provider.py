"""
Admin API for LLM Provider management.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.llm_provider import LLMProvider
from app.schemas.llm_provider import (
    LLMProviderCreate,
    LLMProviderList,
    LLMProviderResponse,
    LLMProviderUpdate,
)

router = APIRouter(prefix="/admin/llm-providers", tags=["admin-llm-providers"])


@router.get("", response_model=LLMProviderList)
def list_llm_providers(
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """
    List all LLM providers (Admin only)
    
    - **enabled**: Filter by enabled status (optional)
    - Returns list of providers
    """
    query = select(LLMProvider)
    
    if enabled is not None:
        query = query.where(LLMProvider.enabled == enabled)
    
    query = query.order_by(LLMProvider.created_at.desc())
    
    result = db.execute(query)
    providers = result.scalars().all()
    
    return {
        "total": len(providers),
        "items": providers
    }


@router.get("/{provider_id}", response_model=LLMProviderResponse)
def get_llm_provider(
    provider_id: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """
    Get a specific LLM provider by ID (Admin only)
    """
    query = select(LLMProvider).where(LLMProvider.id == provider_id)
    result = db.execute(query)
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LLM Provider {provider_id} not found"
        )
    
    return provider


@router.post("", response_model=LLMProviderResponse, status_code=status.HTTP_201_CREATED)
def create_llm_provider(
    provider_data: LLMProviderCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """
    Create a new LLM provider (Admin only)
    
    - **name**: Unique identifier (e.g., 'deepseek', 'openai')
    - **display_name**: Display name (e.g., 'DeepSeek', 'OpenAI')
    - **api_base_url**: API base URL
    - **api_key_env**: Environment variable name for API key
    - **cost_per_1k_tokens**: Cost per 1k tokens
    - **rate_limit_per_minute**: Rate limit (default: 60)
    """
    query = select(LLMProvider).where(LLMProvider.name == provider_data.name)
    result = db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"LLM Provider '{provider_data.name}' already exists"
        )
    
    provider = LLMProvider(
        id=str(uuid.uuid4()),
        **provider_data.model_dump()
    )
    
    db.add(provider)
    db.commit()
    db.refresh(provider)
    
    return provider


@router.put("/{provider_id}", response_model=LLMProviderResponse)
def update_llm_provider(
    provider_id: str,
    provider_data: LLMProviderUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """
    Update an existing LLM provider (Admin only)
    """
    query = select(LLMProvider).where(LLMProvider.id == provider_id)
    result = db.execute(query)
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LLM Provider {provider_id} not found"
        )
    
    update_data = provider_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(provider, field, value)
    
    db.commit()
    db.refresh(provider)
    
    return provider


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_llm_provider(
    provider_id: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """
    Delete an LLM provider (Admin only)
    """
    query = select(LLMProvider).where(LLMProvider.id == provider_id)
    result = db.execute(query)
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LLM Provider {provider_id} not found"
        )
    
    db.delete(provider)
    db.commit()
    
    return None


@router.post("/{provider_id}/toggle", response_model=LLMProviderResponse)
def toggle_llm_provider(
    provider_id: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """
    Toggle LLM provider enabled status (Admin only)
    """
    query = select(LLMProvider).where(LLMProvider.id == provider_id)
    result = db.execute(query)
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LLM Provider {provider_id} not found"
        )
    
    provider.enabled = not provider.enabled
    db.commit()
    db.refresh(provider)
    
    return provider
