"""
Service layer for File Management module.
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import uuid

from app.models.file_meta import (
    FileMeta,
    FileUsage,
    FileStatus,
    LifecycleStatus,
    TargetType,
)
from app.schemas.file import FileUploadRequest


class FileService:
    """Service class for File Management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_file_meta(
        self,
        file_uuid: str,
        file_hash: str,
        oss_path: str,
        file_name: str,
        file_size: int,
        mime_type: str,
        uploader_uid: str
    ) -> FileMeta:
        """Create file metadata"""
        file_meta = FileMeta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=oss_path,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            ref_counts=1,
            status=FileStatus.SCANNING,
            lifecycle_status=LifecycleStatus.ACTIVE,
            uploader_uid=uploader_uid,
        )
        
        self.db.add(file_meta)
        await self.db.commit()
        await self.db.refresh(file_meta)
        return file_meta

    async def get_file_by_uuid(
        self,
        file_uuid: str
    ) -> Optional[FileMeta]:
        """Get file metadata by UUID"""
        query = select(FileMeta).where(
            FileMeta.file_uuid == file_uuid,
            FileMeta.lifecycle_status == LifecycleStatus.ACTIVE
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_file_by_hash(
        self,
        file_hash: str
    ) -> Optional[FileMeta]:
        """Get file metadata by hash"""
        query = select(FileMeta).where(
            FileMeta.file_hash == file_hash,
            FileMeta.lifecycle_status == LifecycleStatus.ACTIVE
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_file_usage(
        self,
        file_uuid: str,
        target_id: str,
        target_type: TargetType,
        user_id: str
    ) -> FileUsage:
        """Create a file usage record"""
        # Check if usage already exists
        existing_query = select(FileUsage).where(
            FileUsage.file_uuid == file_uuid,
            FileUsage.target_id == target_id,
            FileUsage.target_type == target_type
        )
        result = await self.db.execute(existing_query)
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing
        
        # Create new usage record
        usage = FileUsage(
            id=str(uuid.uuid4()),
            file_uuid=file_uuid,
            target_id=target_id,
            target_type=target_type,
            user_id=user_id,
        )
        
        self.db.add(usage)
        
        # Increment ref count
        file_meta = await self.get_file_by_uuid(file_uuid)
        if file_meta:
            file_meta.ref_counts += 1
        
        await self.db.commit()
        await self.db.refresh(usage)
        return usage

    async def update_file_status(
        self,
        file_uuid: str,
        status: FileStatus
    ) -> bool:
        """Update file status"""
        file_meta = await self.get_file_by_uuid(file_uuid)
        
        if not file_meta:
            return False
        
        file_meta.status = status
        await self.db.commit()
        return True

    async def get_user_files(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[FileMeta], int]:
        """Get files uploaded by a user"""
        # Get total count
        count_query = select(func.count()).where(
            FileMeta.uploader_uid == user_id,
            FileMeta.lifecycle_status == LifecycleStatus.ACTIVE
        )
        total = (await self.db.execute(count_query)).scalar()
        
        # Get paginated results
        query = (
            select(FileMeta)
            .where(
                FileMeta.uploader_uid == user_id,
                FileMeta.lifecycle_status == LifecycleStatus.ACTIVE
            )
            .order_by(FileMeta.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await self.db.execute(query)
        files = result.scalars().all()
        
        return list(files), total

    async def delete_file(
        self,
        file_uuid: str,
        user_id: str
    ) -> bool:
        """Soft delete a file"""
        file_meta = await self.get_file_by_uuid(file_uuid)
        
        if not file_meta or file_meta.uploader_uid != user_id:
            return False
        
        file_meta.lifecycle_status = LifecycleStatus.SOFT_DELETED
        await self.db.commit()
        return True

    async def get_file_usages(
        self,
        file_uuid: str
    ) -> List[FileUsage]:
        """Get all usage records for a file"""
        query = select(FileUsage).where(
            FileUsage.file_uuid == file_uuid
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def check_file_access(
        self,
        file_uuid: str,
        user_id: str
    ) -> bool:
        """Check if user has access to a file"""
        file_meta = await self.get_file_by_uuid(file_uuid)
        
        if not file_meta:
            return False
        
        # Owner has access
        if file_meta.uploader_uid == user_id:
            return True
        
        # Check if user has usage record
        usage_query = select(FileUsage).where(
            FileUsage.file_uuid == file_uuid,
            FileUsage.user_id == user_id
        )
        result = await self.db.execute(usage_query)
        usage = result.scalar_one_or_none()
        
        return usage is not None
