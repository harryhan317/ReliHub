"""
Integration tests for File Management module.

Tests:
1. File Upload/Download
   - Different file types (documents, images, videos)
   - Different file sizes
   - Deduplication by hash
   - Error handling

2. File Usage Records
   - Create usage records
   - Query usage records
   - Reference counting

3. Storage Quota
   - User quota tracking
   - Quota enforcement
   - Quota warnings

4. File Lifecycle
   - Soft delete
   - Access control
   - Status management

Database: PostgreSQL (uses shared fixtures from conftest.py)
"""

import hashlib
import uuid

import pytest

from app.models.file_meta import (
    FileStatus,
    LifecycleStatus,
    TargetType,
)
from app.models.users import User
from app.services.file_service import FileService


class TestFileUpload:
    """Test file upload functionality"""
    
    @pytest.fixture
    def file_service(self, db_session):
        """Create FileService instance"""
        return FileService(db_session)
    
    @pytest.fixture
    def test_user(self, db_session):
        """Create test user"""
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138000",
            nickname="test_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_create_file_meta_basic(self, file_service, test_user):
        """Test basic file metadata creation"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"test content").hexdigest()
        
        file_meta = file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/test.pdf",
            file_name="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            uploader_uid=test_user.id,
        )
        
        assert file_meta.file_uuid == file_uuid
        assert file_meta.file_hash == file_hash
        assert file_meta.file_name == "test.pdf"
        assert file_meta.file_size == 1024
        assert file_meta.mime_type == "application/pdf"
        assert file_meta.ref_counts == 1
        assert file_meta.status == FileStatus.SCANNING.value
        assert file_meta.lifecycle_status == LifecycleStatus.ACTIVE.value
        assert file_meta.uploader_uid == test_user.id
    
    def test_upload_document_file(self, file_service, test_user):
        """Test uploading document file (PDF, DOC, DOCX)"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"document content").hexdigest()
        
        file_meta = file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/document.pdf",
            file_name="document.pdf",
            file_size=2048,
            mime_type="application/pdf",
            uploader_uid=test_user.id,
        )
        
        assert file_meta.mime_type == "application/pdf"
        assert file_meta.file_name.endswith(".pdf")
    
    def test_upload_image_file(self, file_service, test_user):
        """Test uploading image file (JPG, PNG, GIF)"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"image content").hexdigest()
        
        file_meta = file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/image.jpg",
            file_name="image.jpg",
            file_size=512,
            mime_type="image/jpeg",
            uploader_uid=test_user.id,
        )
        
        assert file_meta.mime_type == "image/jpeg"
        assert file_meta.file_name.endswith(".jpg")
    
    def test_upload_video_file(self, file_service, test_user):
        """Test uploading video file (MP4, AVI)"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"video content").hexdigest()
        
        file_meta = file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/video.mp4",
            file_name="video.mp4",
            file_size=10485760,
            mime_type="video/mp4",
            uploader_uid=test_user.id,
        )
        
        assert file_meta.mime_type == "video/mp4"
        assert file_meta.file_size == 10485760
    
    def test_upload_small_file(self, file_service, test_user):
        """Test uploading small file (< 1KB)"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"small").hexdigest()
        
        file_meta = file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/small.txt",
            file_name="small.txt",
            file_size=100,
            mime_type="text/plain",
            uploader_uid=test_user.id,
        )
        
        assert file_meta.file_size == 100
    
    def test_upload_medium_file(self, file_service, test_user):
        """Test uploading medium file (1MB - 10MB)"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"medium" * 100000).hexdigest()
        
        file_meta = file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/medium.zip",
            file_name="medium.zip",
            file_size=5242880,
            mime_type="application/zip",
            uploader_uid=test_user.id,
        )
        
        assert file_meta.file_size == 5242880
    
    def test_upload_large_file(self, file_service, test_user):
        """Test uploading large file (10MB - 50MB)"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"large" * 1000000).hexdigest()
        
        file_meta = file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/large.zip",
            file_name="large.zip",
            file_size=52428800,
            mime_type="application/zip",
            uploader_uid=test_user.id,
        )
        
        assert file_meta.file_size == 52428800
    
    def test_upload_duplicate_file_deduplication(self, file_service, test_user):
        """Test that duplicate files are deduplicated by hash"""
        file_hash = hashlib.sha256(b"same content").hexdigest()
        
        file_uuid1 = str(uuid.uuid4())
        file_meta1 = file_service.create_file_meta(
            file_uuid=file_uuid1,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid1}/file1.txt",
            file_name="file1.txt",
            file_size=100,
            mime_type="text/plain",
            uploader_uid=test_user.id,
        )
        
        existing = file_service.get_file_by_hash(file_hash)
        assert existing is not None
        assert existing.file_uuid == file_uuid1
    
    def test_get_file_by_uuid(self, file_service, test_user):
        """Test retrieving file by UUID"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"test").hexdigest()
        
        file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/test.txt",
            file_name="test.txt",
            file_size=100,
            mime_type="text/plain",
            uploader_uid=test_user.id,
        )
        
        retrieved = file_service.get_file_by_uuid(file_uuid)
        
        assert retrieved is not None
        assert retrieved.file_uuid == file_uuid
        assert retrieved.file_name == "test.txt"
    
    def test_get_file_by_uuid_not_found(self, file_service):
        """Test retrieving non-existent file"""
        retrieved = file_service.get_file_by_uuid("non-existent-uuid")
        assert retrieved is None
    
    def test_get_file_by_hash(self, file_service, test_user):
        """Test retrieving file by hash"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"unique content").hexdigest()
        
        file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/unique.txt",
            file_name="unique.txt",
            file_size=100,
            mime_type="text/plain",
            uploader_uid=test_user.id,
        )
        
        retrieved = file_service.get_file_by_hash(file_hash)
        
        assert retrieved is not None
        assert retrieved.file_hash == file_hash


class TestFileDownload:
    """Test file download functionality"""
    
    @pytest.fixture
    def file_service(self, db_session):
        return FileService(db_session)
    
    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138001",
            nickname="download_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.fixture
    def test_file(self, file_service, test_user):
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"download test").hexdigest()
        
        return file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/download.txt",
            file_name="download.txt",
            file_size=500,
            mime_type="text/plain",
            uploader_uid=test_user.id,
        )
    
    def test_check_file_access_owner(self, file_service, test_user, test_file):
        """Test that file owner has access"""
        has_access = file_service.check_file_access(
            test_file.file_uuid,
            test_user.id
        )
        assert has_access is True
    
    def test_check_file_access_non_owner(self, file_service, test_file):
        """Test that non-owner without usage record has no access"""
        has_access = file_service.check_file_access(
            test_file.file_uuid,
            "non-owner-user-id"
        )
        assert has_access is False
    
    def test_check_file_access_with_usage_record(self, file_service, test_user, test_file):
        """Test that user with usage record has access"""
        other_user_id = str(uuid.uuid4())
        
        file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="target-123",
            target_type=TargetType.RESOURCE,
            user_id=other_user_id,
        )
        
        has_access = file_service.check_file_access(
            test_file.file_uuid,
            other_user_id
        )
        assert has_access is True
    
    def test_check_file_access_deleted_file(self, file_service, test_user, test_file):
        """Test that deleted files cannot be accessed"""
        test_file.lifecycle_status = LifecycleStatus.SOFT_DELETED.value
        file_service.db.commit()
        
        has_access = file_service.check_file_access(
            test_file.file_uuid,
            test_user.id
        )
        assert has_access is False


class TestFileUsageRecords:
    """Test file usage record functionality"""
    
    @pytest.fixture
    def file_service(self, db_session):
        return FileService(db_session)
    
    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138002",
            nickname="usage_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.fixture
    def test_file(self, file_service, test_user):
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"usage test").hexdigest()
        
        return file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/usage.txt",
            file_name="usage.txt",
            file_size=300,
            mime_type="text/plain",
            uploader_uid=test_user.id,
        )
    
    def test_create_file_usage_resource(self, file_service, test_file, test_user):
        """Test creating usage record for resource"""
        usage = file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="resource-123",
            target_type=TargetType.RESOURCE,
            user_id=test_user.id,
        )
        
        assert usage.id is not None
        assert usage.file_uuid == test_file.file_uuid
        assert usage.target_id == "resource-123"
        assert usage.target_type == TargetType.RESOURCE.value
    
    def test_create_file_usage_conversation(self, file_service, test_file, test_user):
        """Test creating usage record for conversation"""
        usage = file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="conversation-456",
            target_type=TargetType.CONVERSATION,
            user_id=test_user.id,
        )
        
        assert usage.target_type == TargetType.CONVERSATION.value
    
    def test_create_file_usage_topic(self, file_service, test_file, test_user):
        """Test creating usage record for topic"""
        usage = file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="topic-789",
            target_type=TargetType.TOPIC,
            user_id=test_user.id,
        )
        
        assert usage.target_type == TargetType.TOPIC.value
    
    def test_create_duplicate_usage_record(self, file_service, test_file, test_user):
        """Test that duplicate usage records return existing record"""
        usage1 = file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="target-123",
            target_type=TargetType.RESOURCE,
            user_id=test_user.id,
        )
        
        usage2 = file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="target-123",
            target_type=TargetType.RESOURCE,
            user_id=test_user.id,
        )
        
        assert usage1.id == usage2.id
    
    def test_usage_increments_ref_count(self, file_service, test_file, test_user):
        """Test that creating usage increments reference count"""
        initial_count = test_file.ref_counts
        
        file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="target-123",
            target_type=TargetType.RESOURCE,
            user_id=test_user.id,
        )
        
        file_service.db.refresh(test_file)
        assert test_file.ref_counts == initial_count + 1
    
    def test_get_file_usages(self, file_service, test_file, test_user):
        """Test retrieving all usage records for a file"""
        file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="resource-1",
            target_type=TargetType.RESOURCE,
            user_id=test_user.id,
        )
        
        file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="conversation-1",
            target_type=TargetType.CONVERSATION,
            user_id=test_user.id,
        )
        
        file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="topic-1",
            target_type=TargetType.TOPIC,
            user_id=test_user.id,
        )
        
        usages = file_service.get_file_usages(test_file.file_uuid)
        
        assert len(usages) == 3
    
    def test_usage_record_user_tracking(self, file_service, test_file, test_user):
        """Test that usage records track user correctly"""
        other_user_id = str(uuid.uuid4())
        
        usage = file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="target-123",
            target_type=TargetType.RESOURCE,
            user_id=other_user_id,
        )
        
        assert usage.user_id == other_user_id


class TestStorageQuota:
    """Test storage quota functionality"""
    
    @pytest.fixture
    def file_service(self, db_session):
        return FileService(db_session)
    
    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138003",
            nickname="quota_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_get_user_files(self, file_service, test_user):
        """Test retrieving user's uploaded files"""
        for i in range(5):
            file_uuid = str(uuid.uuid4())
            file_hash = hashlib.sha256(f"file{i}".encode()).hexdigest()
            
            file_service.create_file_meta(
                file_uuid=file_uuid,
                file_hash=file_hash,
                oss_path=f"/uploads/{file_uuid}/file{i}.txt",
                file_name=f"file{i}.txt",
                file_size=100 * (i + 1),
                mime_type="text/plain",
                uploader_uid=test_user.id,
            )
        
        files, total = file_service.get_user_files(test_user.id)
        
        assert total == 5
        assert len(files) == 5
    
    def test_get_user_files_pagination(self, file_service, test_user):
        """Test pagination for user files"""
        for i in range(25):
            file_uuid = str(uuid.uuid4())
            file_hash = hashlib.sha256(f"file{i}".encode()).hexdigest()
            
            file_service.create_file_meta(
                file_uuid=file_uuid,
                file_hash=file_hash,
                oss_path=f"/uploads/{file_uuid}/file{i}.txt",
                file_name=f"file{i}.txt",
                file_size=100,
                mime_type="text/plain",
                uploader_uid=test_user.id,
            )
        
        files_page1, total1 = file_service.get_user_files(test_user.id, page=1, page_size=10)
        files_page2, total2 = file_service.get_user_files(test_user.id, page=2, page_size=10)
        files_page3, total3 = file_service.get_user_files(test_user.id, page=3, page_size=10)
        
        assert total1 == 25
        assert len(files_page1) == 10
        assert len(files_page2) == 10
        assert len(files_page3) == 5
    
    def test_get_user_files_excludes_deleted(self, file_service, test_user):
        """Test that deleted files are excluded from user files list"""
        for i in range(3):
            file_uuid = str(uuid.uuid4())
            file_hash = hashlib.sha256(f"file{i}".encode()).hexdigest()
            
            file_meta = file_service.create_file_meta(
                file_uuid=file_uuid,
                file_hash=file_hash,
                oss_path=f"/uploads/{file_uuid}/file{i}.txt",
                file_name=f"file{i}.txt",
                file_size=100,
                mime_type="text/plain",
                uploader_uid=test_user.id,
            )
            
            if i == 1:
                file_meta.lifecycle_status = LifecycleStatus.SOFT_DELETED.value
                file_service.db.commit()
        
        files, total = file_service.get_user_files(test_user.id)
        
        assert total == 2
        assert len(files) == 2
    
    def test_calculate_user_storage_usage(self, file_service, test_user):
        """Test calculating total storage used by user"""
        total_size = 0
        for i in range(3):
            file_uuid = str(uuid.uuid4())
            file_hash = hashlib.sha256(f"file{i}".encode()).hexdigest()
            file_size = 1024 * (i + 1)
            total_size += file_size
            
            file_service.create_file_meta(
                file_uuid=file_uuid,
                file_hash=file_hash,
                oss_path=f"/uploads/{file_uuid}/file{i}.txt",
                file_name=f"file{i}.txt",
                file_size=file_size,
                mime_type="text/plain",
                uploader_uid=test_user.id,
            )
        
        files, _ = file_service.get_user_files(test_user.id)
        calculated_size = sum(f.file_size for f in files)
        
        assert calculated_size == total_size


class TestFileLifecycle:
    """Test file lifecycle management"""
    
    @pytest.fixture
    def file_service(self, db_session):
        return FileService(db_session)
    
    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138004",
            nickname="lifecycle_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.fixture
    def test_file(self, file_service, test_user):
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"lifecycle test").hexdigest()
        
        return file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/lifecycle.txt",
            file_name="lifecycle.txt",
            file_size=200,
            mime_type="text/plain",
            uploader_uid=test_user.id,
        )
    
    def test_soft_delete_file(self, file_service, test_file, test_user):
        """Test soft deleting a file"""
        success = file_service.delete_file(test_file.file_uuid, test_user.id)
        
        assert success is True
        
        file_service.db.refresh(test_file)
        assert test_file.lifecycle_status == LifecycleStatus.SOFT_DELETED.value
    
    def test_soft_delete_by_non_owner(self, file_service, test_file):
        """Test that non-owner cannot delete file"""
        success = file_service.delete_file(test_file.file_uuid, "non-owner-id")
        
        assert success is False
        
        file_service.db.refresh(test_file)
        assert test_file.lifecycle_status == LifecycleStatus.ACTIVE.value
    
    def test_update_file_status_to_normal(self, file_service, test_file):
        """Test updating file status to NORMAL"""
        success = file_service.update_file_status(
            test_file.file_uuid,
            FileStatus.NORMAL
        )
        
        assert success is True
        
        file_service.db.refresh(test_file)
        assert test_file.status == FileStatus.NORMAL.value
    
    def test_update_file_status_to_blocked(self, file_service, test_file):
        """Test updating file status to BLOCKED"""
        success = file_service.update_file_status(
            test_file.file_uuid,
            FileStatus.BLOCKED
        )
        
        assert success is True
        
        file_service.db.refresh(test_file)
        assert test_file.status == FileStatus.BLOCKED.value
    
    def test_update_file_status_to_isolated(self, file_service, test_file):
        """Test updating file status to ISOLATED"""
        success = file_service.update_file_status(
            test_file.file_uuid,
            FileStatus.ISOLATED
        )
        
        assert success is True
        
        file_service.db.refresh(test_file)
        assert test_file.status == FileStatus.ISOLATED.value
    
    def test_update_nonexistent_file_status(self, file_service):
        """Test updating status of non-existent file"""
        success = file_service.update_file_status(
            "non-existent-uuid",
            FileStatus.NORMAL
        )
        
        assert success is False
    
    def test_file_status_workflow(self, file_service, test_file):
        """Test complete file status workflow"""
        assert test_file.status == FileStatus.SCANNING.value
        
        file_service.update_file_status(test_file.file_uuid, FileStatus.NORMAL)
        file_service.db.refresh(test_file)
        assert test_file.status == FileStatus.NORMAL.value
        
        file_service.update_file_status(test_file.file_uuid, FileStatus.SUSPICIOUS)
        file_service.db.refresh(test_file)
        assert test_file.status == FileStatus.SUSPICIOUS.value
        
        file_service.update_file_status(test_file.file_uuid, FileStatus.BLOCKED)
        file_service.db.refresh(test_file)
        assert test_file.status == FileStatus.BLOCKED.value


class TestFileAccessControl:
    """Test file access control"""
    
    @pytest.fixture
    def file_service(self, db_session):
        return FileService(db_session)
    
    @pytest.fixture
    def owner_user(self, db_session):
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138005",
            nickname="owner_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.fixture
    def other_user(self, db_session):
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138006",
            nickname="other_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.fixture
    def test_file(self, file_service, owner_user):
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"access control test").hexdigest()
        
        return file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/access.txt",
            file_name="access.txt",
            file_size=150,
            mime_type="text/plain",
            uploader_uid=owner_user.id,
        )
    
    def test_owner_has_access(self, file_service, test_file, owner_user):
        """Test that file owner has access"""
        has_access = file_service.check_file_access(
            test_file.file_uuid,
            owner_user.id
        )
        assert has_access is True
    
    def test_non_owner_no_access(self, file_service, test_file, other_user):
        """Test that non-owner without usage record has no access"""
        has_access = file_service.check_file_access(
            test_file.file_uuid,
            other_user.id
        )
        assert has_access is False
    
    def test_user_with_usage_has_access(self, file_service, test_file, other_user):
        """Test that user with usage record has access"""
        file_service.create_file_usage(
            file_uuid=test_file.file_uuid,
            target_id="resource-123",
            target_type=TargetType.RESOURCE,
            user_id=other_user.id,
        )
        
        has_access = file_service.check_file_access(
            test_file.file_uuid,
            other_user.id
        )
        assert has_access is True
    
    def test_deleted_file_no_access(self, file_service, test_file, owner_user):
        """Test that deleted files cannot be accessed"""
        test_file.lifecycle_status = LifecycleStatus.SOFT_DELETED.value
        file_service.db.commit()
        
        has_access = file_service.check_file_access(
            test_file.file_uuid,
            owner_user.id
        )
        assert has_access is False


class TestFileErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def file_service(self, db_session):
        return FileService(db_session)
    
    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138007",
            nickname="error_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_get_nonexistent_file(self, file_service):
        """Test retrieving non-existent file"""
        result = file_service.get_file_by_uuid("nonexistent-uuid")
        assert result is None
    
    def test_get_file_by_nonexistent_hash(self, file_service):
        """Test retrieving file by non-existent hash"""
        result = file_service.get_file_by_hash("nonexistent-hash")
        assert result is None
    
    def test_delete_nonexistent_file(self, file_service, test_user):
        """Test deleting non-existent file"""
        result = file_service.delete_file("nonexistent-uuid", test_user.id)
        assert result is False
    
    def test_delete_file_wrong_user(self, file_service, test_user):
        """Test deleting file with wrong user"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"test").hexdigest()
        
        file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/test.txt",
            file_name="test.txt",
            file_size=100,
            mime_type="text/plain",
            uploader_uid=test_user.id,
        )
        
        result = file_service.delete_file(file_uuid, "wrong-user-id")
        assert result is False
    
    def test_update_status_nonexistent_file(self, file_service):
        """Test updating status of non-existent file"""
        result = file_service.update_file_status(
            "nonexistent-uuid",
            FileStatus.NORMAL
        )
        assert result is False
    
    def test_get_usages_nonexistent_file(self, file_service):
        """Test getting usages for non-existent file"""
        usages = file_service.get_file_usages("nonexistent-uuid")
        assert usages == []


class TestFileConcurrency:
    """Test concurrent file operations"""
    
    @pytest.fixture
    def file_service(self, db_session):
        return FileService(db_session)
    
    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id=str(uuid.uuid4()),
            phone="13800138008",
            nickname="concurrent_user",
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_multiple_usage_records_same_file(self, file_service, test_user):
        """Test creating multiple usage records for same file"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"concurrent test").hexdigest()
        
        file_meta = file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/concurrent.txt",
            file_name="concurrent.txt",
            file_size=100,
            mime_type="text/plain",
            uploader_uid=test_user.id,
        )
        
        initial_ref_count = file_meta.ref_counts
        
        for i in range(5):
            file_service.create_file_usage(
                file_uuid=file_uuid,
                target_id=f"target-{i}",
                target_type=TargetType.RESOURCE,
                user_id=f"user-{i}",
            )
        
        file_service.db.refresh(file_meta)
        assert file_meta.ref_counts == initial_ref_count + 5
    
    def test_reference_count_accuracy(self, file_service, test_user):
        """Test that reference count is accurate"""
        file_uuid = str(uuid.uuid4())
        file_hash = hashlib.sha256(b"ref count test").hexdigest()
        
        file_meta = file_service.create_file_meta(
            file_uuid=file_uuid,
            file_hash=file_hash,
            oss_path=f"/uploads/{file_uuid}/refcount.txt",
            file_name="refcount.txt",
            file_size=100,
            mime_type="text/plain",
            uploader_uid=test_user.id,
        )
        
        assert file_meta.ref_counts == 1
        
        for i in range(3):
            file_service.create_file_usage(
                file_uuid=file_uuid,
                target_id=f"target-{i}",
                target_type=TargetType.RESOURCE,
                user_id=test_user.id,
            )
        
        file_service.db.refresh(file_meta)
        assert file_meta.ref_counts == 4
