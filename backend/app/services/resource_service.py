"""
Service layer for Resource Management module.
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import uuid

from app.models.resources import Resource, ResourcePreview, ResourceStatus
from app.schemas.resource import (
    ResourceCreateRequest,
    ResourceUpdateRequest,
    ResourceReviewRequest,
)


class ResourceService:
    """Service class for Resource management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_resource(
        self,
        uploader_id: str,
        request: ResourceCreateRequest
    ) -> Resource:
        """Create a new resource"""
        resource = Resource(
            id=str(uuid.uuid4()),
            uploader_id=uploader_id,
            title=request.title,
            description=request.description,
            category_id=request.category_id,
            tags=",".join(request.tags) if request.tags else None,
            price=request.price,
            file_uuid=request.file_uuid,
            status=ResourceStatus.SCANNING,
        )
        
        self.db.add(resource)
        await self.db.commit()
        await self.db.refresh(resource)
        return resource

    async def get_resource(
        self,
        resource_id: str,
        include_previews: bool = True
    ) -> Optional[Resource]:
        """Get a resource by ID"""
        query = select(Resource).where(
            Resource.id == resource_id,
            Resource.is_deleted == False,
            Resource.status == ResourceStatus.APPROVED
        )
        
        if include_previews:
            query = query.options(selectinload(Resource.previews))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_resources(
        self,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "heat_score",
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Resource], int]:
        """List resources with filters and pagination"""
        # Build filters
        filters = [
            Resource.is_deleted == False,
            Resource.status == ResourceStatus.APPROVED
        ]
        
        if category_id:
            filters.append(Resource.category_id == category_id)
        
        if search:
            filters.append(
                or_(
                    Resource.title.ilike(f"%{search}%"),
                    Resource.description.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        count_query = select(func.count()).where(and_(*filters))
        total = (await self.db.execute(count_query)).scalar()
        
        # Build sorting
        sort_columns = {
            "heat_score": Resource.heat_score.desc(),
            "created_at": Resource.created_at.desc(),
            "view_count": Resource.view_count.desc(),
            "download_count": Resource.download_count.desc(),
            "price": Resource.price.asc(),
        }
        order_by = sort_columns.get(sort_by, Resource.heat_score.desc())
        
        # Get paginated results
        query = (
            select(Resource)
            .where(and_(*filters))
            .order_by(order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await self.db.execute(query)
        resources = result.scalars().all()
        
        return list(resources), total

    async def update_resource(
        self,
        resource_id: str,
        uploader_id: str,
        request: ResourceUpdateRequest
    ) -> Optional[Resource]:
        """Update a resource"""
        query = select(Resource).where(
            Resource.id == resource_id,
            Resource.uploader_id == uploader_id,
            Resource.is_deleted == False
        )
        result = await self.db.execute(query)
        resource = result.scalar_one_or_none()
        
        if not resource:
            return None
        
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "tags" and value is not None:
                value = ",".join(value) if isinstance(value, list) else value
            setattr(resource, field, value)
        
        await self.db.commit()
        await self.db.refresh(resource)
        return resource

    async def delete_resource(
        self,
        resource_id: str,
        uploader_id: str
    ) -> bool:
        """Soft delete a resource"""
        resource = await self.get_resource_admin(resource_id, uploader_id)
        if not resource:
            return False
        
        resource.is_deleted = True
        await self.db.commit()
        return True

    async def get_resource_admin(
        self,
        resource_id: str,
        uploader_id: Optional[str] = None
    ) -> Optional[Resource]:
        """Get a resource for admin operations"""
        query = select(Resource).where(
            Resource.id == resource_id,
            Resource.is_deleted == False
        )
        
        if uploader_id:
            query = query.where(Resource.uploader_id == uploader_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def review_resource(
        self,
        resource_id: str,
        request: ResourceReviewRequest
    ) -> Optional[Resource]:
        """Review a resource (admin operation)"""
        resource = await self.get_resource_admin(resource_id)
        if not resource:
            return None
        
        resource.status = request.status
        await self.db.commit()
        await self.db.refresh(resource)
        return resource

    async def add_preview(
        self,
        resource_id: str,
        preview_url: str,
        page_number: Optional[int] = None
    ) -> ResourcePreview:
        """Add a preview for a resource"""
        preview = ResourcePreview(
            id=str(uuid.uuid4()),
            resource_id=resource_id,
            preview_url=preview_url,
            page_number=page_number,
        )
        
        self.db.add(preview)
        await self.db.commit()
        await self.db.refresh(preview)
        return preview

    async def increment_view(self, resource_id: str) -> bool:
        """Increment view count"""
        resource = await self.get_resource_admin(resource_id)
        if resource:
            resource.view_count += 1
            await self.db.commit()
            return True
        return False

    async def increment_download(self, resource_id: str) -> bool:
        """Increment download count"""
        resource = await self.get_resource_admin(resource_id)
        if resource:
            resource.download_count += 1
            await self.db.commit()
            return True
        return False

    async def update_heat_score(
        self,
        resource_id: str,
        heat_score: float
    ) -> bool:
        """Update heat score"""
        resource = await self.get_resource_admin(resource_id)
        if resource:
            resource.heat_score = heat_score
            await self.db.commit()
            return True
        return False
