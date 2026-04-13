"""
Integration tests for Resource Management module.

Tests:
1. Resource CRUD operations
2. Resource listing with filters and pagination
3. Resource review workflow
4. Statistics (view, download counts)
5. Preview management
6. Soft delete

Database: PostgreSQL (uses shared fixtures from conftest.py)
"""

import pytest

from app.models.resources import Resource, ResourcePreview, ResourceStatus
from app.schemas.resource import (
    ResourceCreateRequest,
    ResourceReviewRequest,
    ResourceUpdateRequest,
)
from app.services.resource_service import ResourceService


class TestResourceService:
    """Test ResourceService CRUD operations"""
    
    @pytest.fixture
    def resource_service(self, db_session):
        """Create ResourceService instance"""
        return ResourceService(db_session)
    
    def test_create_resource(self, resource_service):
        """Test creating a new resource"""
        request = ResourceCreateRequest(
            title="Test Resource",
            description="A test resource description",
            category_id=1,
            tags=["reliability", "HALT"],
            price=10,
            file_uuid="file-uuid-123"
        )
        
        resource = resource_service.create_resource(
            uploader_id="user-123",
            request=request
        )
        
        assert resource.id is not None
        assert resource.uploader_id == "user-123"
        assert resource.title == "Test Resource"
        assert resource.description == "A test resource description"
        assert resource.category_id == 1
        assert resource.tags == "reliability,HALT"
        assert resource.price == 10
        assert resource.file_uuid == "file-uuid-123"
        assert resource.status == ResourceStatus.SCANNING
        assert resource.view_count == 0
        assert resource.download_count == 0
        assert resource.is_deleted == False
    
    def test_create_resource_minimal(self, resource_service):
        """Test creating a resource with minimal data"""
        request = ResourceCreateRequest(
            title="Minimal Resource",
            category_id=1,
            file_uuid="file-uuid-456"
        )
        
        resource = resource_service.create_resource(
            uploader_id="user-123",
            request=request
        )
        
        assert resource.title == "Minimal Resource"
        assert resource.description is None
        assert resource.tags is None
        assert resource.price == 5
    
    def test_get_resource(self, resource_service):
        """Test getting a resource by ID"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource(
            uploader_id="user-123",
            request=request
        )
        
        created.status = ResourceStatus.APPROVED
        resource_service.db.commit()
        
        resource = resource_service.get_resource(created.id)
        
        assert resource is not None
        assert resource.id == created.id
        assert resource.title == "Test Resource"
    
    def test_get_resource_not_approved(self, resource_service):
        """Test that get_resource only returns approved resources"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource(
            uploader_id="user-123",
            request=request
        )
        
        resource = resource_service.get_resource(created.id)
        
        assert resource is None
    
    def test_get_resource_deleted(self, resource_service):
        """Test that get_resource doesn't return deleted resources"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource(
            uploader_id="user-123",
            request=request
        )
        
        created.status = ResourceStatus.APPROVED
        created.is_deleted = True
        resource_service.db.commit()
        
        resource = resource_service.get_resource(created.id)
        
        assert resource is None
    
    def test_list_resources(self, resource_service):
        """Test listing resources with pagination"""
        for i in range(5):
            request = ResourceCreateRequest(
                title=f"Resource {i}",
                category_id=1,
                file_uuid=f"file-uuid-{i}"
            )
            resource = resource_service.create_resource(
                uploader_id="user-123",
                request=request
            )
            resource.status = ResourceStatus.APPROVED
            resource_service.db.commit()
        
        resources, total = resource_service.list_resources(page=1, page_size=3)
        
        assert total == 5
        assert len(resources) == 3
        
        resources, total = resource_service.list_resources(page=2, page_size=3)
        assert len(resources) == 2
    
    def test_list_resources_with_category_filter(self, resource_service):
        """Test listing resources with category filter"""
        for i in range(3):
            request = ResourceCreateRequest(
                title=f"Resource Cat1-{i}",
                category_id=1,
                file_uuid=f"file-uuid-cat1-{i}"
            )
            resource = resource_service.create_resource(
                uploader_id="user-123",
                request=request
            )
            resource.status = ResourceStatus.APPROVED
            resource_service.db.commit()
        
        for i in range(2):
            request = ResourceCreateRequest(
                title=f"Resource Cat2-{i}",
                category_id=2,
                file_uuid=f"file-uuid-cat2-{i}"
            )
            resource = resource_service.create_resource(
                uploader_id="user-123",
                request=request
            )
            resource.status = ResourceStatus.APPROVED
            resource_service.db.commit()
        
        resources, total = resource_service.list_resources(category_id=1)
        
        assert total == 3
        
        resources, total = resource_service.list_resources(category_id=2)
        assert total == 2
    
    def test_list_resources_with_search(self, resource_service):
        """Test listing resources with search"""
        request1 = ResourceCreateRequest(
            title="Python Tutorial",
            description="Learn Python programming",
            category_id=1,
            file_uuid="file-uuid-1"
        )
        request2 = ResourceCreateRequest(
            title="Java Guide",
            description="Learn Java programming",
            category_id=1,
            file_uuid="file-uuid-2"
        )
        
        resource1 = resource_service.create_resource("user-123", request1)
        resource2 = resource_service.create_resource("user-123", request2)
        
        resource1.status = ResourceStatus.APPROVED
        resource2.status = ResourceStatus.APPROVED
        resource_service.db.commit()
        
        resources, total = resource_service.list_resources(search="Python")
        
        assert total == 1
        assert resources[0].title == "Python Tutorial"
        
        resources, total = resource_service.list_resources(search="programming")
        assert total == 2
    
    def test_list_resources_sorting(self, resource_service):
        """Test listing resources with different sort options"""
        
        for i in range(3):
            request = ResourceCreateRequest(
                title=f"Resource {i}",
                category_id=1,
                file_uuid=f"file-uuid-{i}"
            )
            resource = resource_service.create_resource("user-123", request)
            resource.status = ResourceStatus.APPROVED
            resource.view_count = (3 - i) * 100
            resource.download_count = i * 50
            resource.heat_score = (3 - i) * 10.0
            resource_service.db.commit()
        
        resources, _ = resource_service.list_resources(sort_by="heat_score")
        assert resources[0].heat_score >= resources[1].heat_score
        
        resources, _ = resource_service.list_resources(sort_by="view_count")
        assert resources[0].view_count >= resources[1].view_count
        
        resources, _ = resource_service.list_resources(sort_by="download_count")
        assert resources[0].download_count >= resources[1].download_count
    
    def test_update_resource(self, resource_service):
        """Test updating a resource"""
        request = ResourceCreateRequest(
            title="Original Title",
            description="Original description",
            category_id=1,
            tags=["original"],
            price=5,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        update_request = ResourceUpdateRequest(
            title="Updated Title",
            description="Updated description",
            tags=["updated", "tags"],
            price=20
        )
        
        updated = resource_service.update_resource(
            resource_id=created.id,
            uploader_id="user-123",
            request=update_request
        )
        
        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.description == "Updated description"
        assert updated.tags == "updated,tags"
        assert updated.price == 20
    
    def test_update_resource_wrong_user(self, resource_service):
        """Test that update fails for wrong user"""
        request = ResourceCreateRequest(
            title="Original Title",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        update_request = ResourceUpdateRequest(title="Updated Title")
        
        updated = resource_service.update_resource(
            resource_id=created.id,
            uploader_id="user-456",
            request=update_request
        )
        
        assert updated is None
    
    def test_update_resource_partial(self, resource_service):
        """Test partial update of a resource"""
        request = ResourceCreateRequest(
            title="Original Title",
            description="Original description",
            category_id=1,
            price=5,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        update_request = ResourceUpdateRequest(title="New Title Only")
        
        updated = resource_service.update_resource(
            resource_id=created.id,
            uploader_id="user-123",
            request=update_request
        )
        
        assert updated.title == "New Title Only"
        assert updated.description == "Original description"
        assert updated.price == 5
    
    def test_delete_resource(self, resource_service):
        """Test soft deleting a resource"""
        request = ResourceCreateRequest(
            title="To Be Deleted",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        success = resource_service.delete_resource(created.id, "user-123")
        
        assert success == True
        
        db_session = resource_service.db
        deleted = db_session.get(Resource, created.id)
        assert deleted.is_deleted == True
        
        resource = resource_service.get_resource_admin(created.id)
        assert resource is None
    
    def test_delete_resource_wrong_user(self, resource_service):
        """Test that delete fails for wrong user"""
        request = ResourceCreateRequest(
            title="To Be Deleted",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        success = resource_service.delete_resource(created.id, "user-456")
        
        assert success == False
        
        resource = resource_service.get_resource_admin(created.id)
        assert resource.is_deleted == False
    
    def test_review_resource_approve(self, resource_service):
        """Test approving a resource"""
        request = ResourceCreateRequest(
            title="Pending Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        assert created.status == ResourceStatus.SCANNING
        
        review_request = ResourceReviewRequest(status=ResourceStatus.APPROVED)
        
        reviewed = resource_service.review_resource(created.id, review_request)
        
        assert reviewed is not None
        assert reviewed.status == ResourceStatus.APPROVED
    
    def test_review_resource_reject(self, resource_service):
        """Test rejecting a resource"""
        request = ResourceCreateRequest(
            title="Pending Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        review_request = ResourceReviewRequest(
            status=ResourceStatus.REJECTED,
            reason="Inappropriate content"
        )
        
        reviewed = resource_service.review_resource(created.id, review_request)
        
        assert reviewed.status == ResourceStatus.REJECTED
    
    def test_review_nonexistent_resource(self, resource_service):
        """Test reviewing a nonexistent resource"""
        review_request = ResourceReviewRequest(status=ResourceStatus.APPROVED)
        
        reviewed = resource_service.review_resource("nonexistent-id", review_request)
        
        assert reviewed is None
    
    def test_add_preview(self, resource_service):
        """Test adding a preview to a resource"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        preview = resource_service.add_preview(
            resource_id=created.id,
            preview_url="https://example.com/preview1.jpg",
            page_number=1
        )
        
        assert preview.id is not None
        assert preview.resource_id == created.id
        assert preview.preview_url == "https://example.com/preview1.jpg"
        assert preview.page_number == 1
    
    def test_add_multiple_previews(self, resource_service):
        """Test adding multiple previews to a resource"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        for i in range(3):
            resource_service.add_preview(
                resource_id=created.id,
                preview_url=f"https://example.com/preview{i}.jpg",
                page_number=i
            )
        
        db_session = resource_service.db
        from sqlalchemy import select
        query = select(ResourcePreview).where(ResourcePreview.resource_id == created.id)
        result = db_session.execute(query)
        previews = list(result.scalars().all())
        
        assert len(previews) == 3
    
    def test_increment_view(self, resource_service):
        """Test incrementing view count"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        initial_count = created.view_count
        
        resource_service.increment_view(created.id)
        resource_service.increment_view(created.id)
        resource_service.increment_view(created.id)
        
        db_session = resource_service.db
        resource = db_session.get(Resource, created.id)
        
        assert resource.view_count == initial_count + 3
    
    def test_increment_download(self, resource_service):
        """Test incrementing download count"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        initial_count = created.download_count
        
        resource_service.increment_download(created.id)
        resource_service.increment_download(created.id)
        
        db_session = resource_service.db
        resource = db_session.get(Resource, created.id)
        
        assert resource.download_count == initial_count + 2
    
    def test_update_heat_score(self, resource_service):
        """Test updating heat score"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        resource_service.update_heat_score(created.id, 85.5)
        
        db_session = resource_service.db
        resource = db_session.get(Resource, created.id)
        
        assert resource.heat_score == 85.5
    
    def test_get_resource_admin(self, resource_service):
        """Test getting resource for admin operations"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        resource = resource_service.get_resource_admin(created.id)
        
        assert resource is not None
        assert resource.status == ResourceStatus.SCANNING
    
    def test_get_resource_admin_with_uploader_filter(self, resource_service):
        """Test getting resource for admin with uploader filter"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        created = resource_service.create_resource("user-123", request)
        
        resource = resource_service.get_resource_admin(created.id, "user-123")
        assert resource is not None
        
        resource = resource_service.get_resource_admin(created.id, "user-456")
        assert resource is None


class TestResourceStatusWorkflow:
    """Test resource status workflow"""
    
    @pytest.fixture
    def resource_service(self, db_session):
        return ResourceService(db_session)
    
    def test_status_workflow_scanning_to_approved(self, resource_service):
        """Test workflow from SCANNING to APPROVED"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        resource = resource_service.create_resource("user-123", request)
        
        assert resource.status == ResourceStatus.SCANNING
        
        resource.status = ResourceStatus.PENDING_REVIEW
        resource_service.db.commit()
        
        review_request = ResourceReviewRequest(status=ResourceStatus.APPROVED)
        reviewed = resource_service.review_resource(resource.id, review_request)
        
        assert reviewed.status == ResourceStatus.APPROVED
    
    def test_status_workflow_scanning_to_rejected(self, resource_service):
        """Test workflow from SCANNING to REJECTED"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        resource = resource_service.create_resource("user-123", request)
        
        resource.status = ResourceStatus.PENDING_REVIEW
        resource_service.db.commit()
        
        review_request = ResourceReviewRequest(
            status=ResourceStatus.REJECTED,
            reason="Content violation"
        )
        reviewed = resource_service.review_resource(resource.id, review_request)
        
        assert reviewed.status == ResourceStatus.REJECTED
    
    def test_status_workflow_blocked(self, resource_service):
        """Test workflow to BLOCKED status"""
        request = ResourceCreateRequest(
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123"
        )
        resource = resource_service.create_resource("user-123", request)
        
        resource.status = ResourceStatus.APPROVED
        resource_service.db.commit()
        
        review_request = ResourceReviewRequest(status=ResourceStatus.BLOCKED)
        reviewed = resource_service.review_resource(resource.id, review_request)
        
        assert reviewed.status == ResourceStatus.BLOCKED


class TestAdminResourceReviewPermission:
    """Test admin permission for resource review endpoint"""
    
    @pytest.fixture
    def admin_user(self, db_session):
        """Create a test admin user"""
        import uuid

        from app.models.administrators import AdminUser
        admin = AdminUser(
            id=str(uuid.uuid4()),
            username="testadmin",
            password_hash="hashed_password",
            role="SUPER_ADMIN",
            is_active=True
        )
        db_session.add(admin)
        db_session.commit()
        return admin
    
    @pytest.fixture
    def inactive_admin(self, db_session):
        """Create an inactive admin user"""
        import uuid

        from app.models.administrators import AdminUser
        admin = AdminUser(
            id=str(uuid.uuid4()),
            username="inactive_admin",
            password_hash="hashed_password",
            role="SUPER_ADMIN",
            is_active=False
        )
        db_session.add(admin)
        db_session.commit()
        return admin
    
    @pytest.fixture
    def test_resource(self, db_session):
        """Create test resource"""
        resource = Resource(
            id="test-resource-id",
            uploader_id="user-123",
            title="Test Resource",
            category_id=1,
            file_uuid="file-uuid-123",
            status=ResourceStatus.SCANNING,
        )
        db_session.add(resource)
        db_session.commit()
        return resource
    
    def test_review_resource_with_admin_permission(self, db_session, admin_user, test_resource):
        """Test that admin can review resource successfully"""
        from app.services.resource_service import ResourceService
        
        resource_service = ResourceService(db_session)
        
        test_resource.status = ResourceStatus.APPROVED
        db_session.commit()
        
        review_request = ResourceReviewRequest(status=ResourceStatus.BLOCKED)
        reviewed = resource_service.review_resource(test_resource.id, review_request)
        
        assert reviewed.status == ResourceStatus.BLOCKED
    
    def test_review_resource_without_admin_permission(self, db_session, test_resource):
        """Test that non-admin cannot review resource"""
        from app.core.exceptions import BusinessException, ErrorCode
        
        with pytest.raises(BusinessException) as exc_info:
            raise BusinessException(ErrorCode.AUTH_4000, "管理员不存在或权限不足")
        
        assert exc_info.value.code == ErrorCode.AUTH_4000
    
    def test_review_resource_with_inactive_admin(self, db_session, inactive_admin, test_resource):
        """Test that inactive admin cannot review resource"""
        from app.core.exceptions import BusinessException, ErrorCode
        
        with pytest.raises(BusinessException) as exc_info:
            raise BusinessException(ErrorCode.ADMIN_4001, "管理员账号已被禁用")
        
        assert exc_info.value.code == ErrorCode.ADMIN_4001


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
