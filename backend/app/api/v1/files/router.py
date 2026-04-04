"""
API routes for File Management module.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid
import hashlib

from app.core.deps import get_db, get_current_user
from app.services.file_service import FileService
from app.schemas.file import (
    FileStatus,
    FileUploadResponse,
    FileMetaResponse,
    FileListResponse,
    PresignedUrlResponse,
)
from app.models.users import User

router = APIRouter(prefix="/files", tags=["文件管理"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a file.
    
    This endpoint:
    1. Generates file UUID and hash
    2. Uploads to OSS
    3. Creates file metadata
    4. Returns file info
    """
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Generate file hash (SHA-256)
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Generate file UUID
    file_uuid = str(uuid.uuid4())
    
    # TODO: Upload to OSS and get OSS path
    # For now, use placeholder
    oss_path = f"/uploads/{file_uuid}/{file.filename}"
    
    service = FileService(db)
    
    # Check if file already exists (deduplication)
    existing = await service.get_file_by_hash(file_hash)
    if existing:
        # File exists, increment ref count
        return FileUploadResponse(
            file_uuid=existing.file_uuid,
            file_hash=existing.file_hash,
            oss_path=existing.oss_path,
            file_name=existing.file_name,
            file_size=existing.file_size,
            mime_type=existing.mime_type,
        )
    
    # Create new file metadata
    file_meta = await service.create_file_meta(
        file_uuid=file_uuid,
        file_hash=file_hash,
        oss_path=oss_path,
        file_name=file.filename or "unnamed",
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        uploader_uid=current_user.user_uuid,
    )
    
    return FileUploadResponse(
        file_uuid=file_meta.file_uuid,
        file_hash=file_meta.file_hash,
        oss_path=file_meta.oss_path,
        file_name=file_meta.file_name,
        file_size=file_meta.file_size,
        mime_type=file_meta.mime_type,
    )


@router.get("/{file_uuid}", response_model=FileMetaResponse)
async def get_file(
    file_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get file metadata"""
    service = FileService(db)
    file_meta = await service.get_file_by_uuid(file_uuid)
    
    if not file_meta:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check access
    has_access = await service.check_file_access(file_uuid, current_user.user_uuid)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return file_meta


@router.get("/{file_uuid}/download")
async def get_download_url(
    file_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get file download URL.
    
    This endpoint:
    1. Checks user has access
    2. Generates pre-signed URL
    3. Returns download URL
    """
    service = FileService(db)
    file_meta = await service.get_file_by_uuid(file_uuid)
    
    if not file_meta:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check access
    has_access = await service.check_file_access(file_uuid, current_user.user_uuid)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Generate pre-signed URL from OSS
    download_url = f"{file_meta.oss_path}?download=true"
    
    return {"download_url": download_url, "file_name": file_meta.file_name}


@router.get("/user/my-files", response_model=FileListResponse)
async def get_user_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get files uploaded by current user"""
    service = FileService(db)
    files, total = await service.get_user_files(
        current_user.user_uuid,
        page,
        page_size,
    )
    
    return FileListResponse(
        files=[FileMetaResponse.model_validate(f) for f in files],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete("/{file_uuid}")
async def delete_file(
    file_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a file"""
    service = FileService(db)
    success = await service.delete_file(file_uuid, current_user.user_uuid)
    
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"message": "File deleted"}


@router.post("/{file_uuid}/usage")
async def create_file_usage(
    file_uuid: str,
    target_id: str,
    target_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Record file usage.
    
    This endpoint:
    1. Validates target exists
    2. Creates usage record
    3. Increments ref count
    """
    from app.models.file_meta import TargetType
    
    try:
        target_type_enum = TargetType(target_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid target type")
    
    service = FileService(db)
    
    # Check file exists
    file_meta = await service.get_file_by_uuid(file_uuid)
    if not file_meta:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Create usage record
    usage = await service.create_file_usage(
        file_uuid=file_uuid,
        target_id=target_id,
        target_type=target_type_enum,
        user_id=current_user.user_uuid,
    )
    
    return {
        "message": "Usage recorded",
        "usage_id": usage.id,
    }


@router.get("/{file_uuid}/usages")
async def get_file_usages(
    file_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all usage records for a file"""
    service = FileService(db)
    file_meta = await service.get_file_by_uuid(file_uuid)
    
    if not file_meta:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check access
    has_access = await service.check_file_access(file_uuid, current_user.user_uuid)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    usages = await service.get_file_usages(file_uuid)
    
    return {
        "file_uuid": file_uuid,
        "usages": [
            {
                "id": u.id,
                "target_id": u.target_id,
                "target_type": u.target_type.value,
                "user_id": u.user_id,
                "created_at": u.created_at,
            }
            for u in usages
        ],
    }
