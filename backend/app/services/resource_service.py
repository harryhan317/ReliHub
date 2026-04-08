"""
Service layer for Resource Management module.
"""
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models.resources import Resource, ResourcePreview, ResourceStatus
from app.schemas.resource import (
    ResourceCreateRequest,
    ResourceReviewRequest,
    ResourceUpdateRequest,
)


class ResourceService:
    """Service class for Resource management"""

    def __init__(self, db: Session):
        self.db = db

    def create_resource(
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
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def get_resource(
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
        
        result = self.db.execute(query)
        resource = result.scalar_one_or_none()
        
        if resource and include_previews:
            previews = self.get_previews(resource_id)
            resource.previews = previews
        
        return resource
    
    def get_previews(self, resource_id: str) -> List[ResourcePreview]:
        """Get previews for a resource"""
        query = select(ResourcePreview).where(
            ResourcePreview.resource_id == resource_id
        ).order_by(ResourcePreview.page_number)
        
        result = self.db.execute(query)
        return list(result.scalars().all())

    def list_resources(
        self,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "heat_score",
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Resource], int]:
        """List resources with filters and pagination"""
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
        
        count_query = select(func.count()).where(and_(*filters))
        total = self.db.execute(count_query).scalar()
        
        sort_columns = {
            "heat_score": Resource.heat_score.desc(),
            "created_at": Resource.created_at.desc(),
            "view_count": Resource.view_count.desc(),
            "download_count": Resource.download_count.desc(),
            "price": Resource.price.asc(),
        }
        order_by = sort_columns.get(sort_by, Resource.heat_score.desc())
        
        query = (
            select(Resource)
            .where(and_(*filters))
            .order_by(order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = self.db.execute(query)
        resources = result.scalars().all()
        
        return list(resources), total

    def update_resource(
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
        result = self.db.execute(query)
        resource = result.scalar_one_or_none()
        
        if not resource:
            return None
        
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "tags" and value is not None:
                value = ",".join(value) if isinstance(value, list) else value
            setattr(resource, field, value)
        
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def delete_resource(
        self,
        resource_id: str,
        uploader_id: str
    ) -> bool:
        """Soft delete a resource"""
        resource = self.get_resource_admin(resource_id, uploader_id)
        if not resource:
            return False
        
        resource.is_deleted = True
        self.db.commit()
        return True

    def get_resource_admin(
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
        
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def review_resource(
        self,
        resource_id: str,
        request: ResourceReviewRequest
    ) -> Optional[Resource]:
        """Review a resource (admin operation)"""
        resource = self.get_resource_admin(resource_id)
        if not resource:
            return None
        
        resource.status = request.status
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def add_preview(
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
        self.db.commit()
        self.db.refresh(preview)
        return preview

    def increment_view(self, resource_id: str) -> bool:
        """Increment view count"""
        resource = self.get_resource_admin(resource_id)
        if resource:
            resource.view_count += 1
            self.db.commit()
            return True
        return False

    def increment_download(self, resource_id: str) -> bool:
        """Increment download count"""
        resource = self.get_resource_admin(resource_id)
        if resource:
            resource.download_count += 1
            self.db.commit()
            return True
        return False

    def update_heat_score(
        self,
        resource_id: str,
        heat_score: float
    ) -> bool:
        """Update heat score"""
        resource = self.get_resource_admin(resource_id)
        if resource:
            resource.heat_score = heat_score
            self.db.commit()
            return True
        return False
