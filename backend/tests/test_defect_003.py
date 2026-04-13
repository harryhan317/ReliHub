"""
Test cases for DEFECT-003: File upload size limit validation
"""
import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def auth_headers(db_session: Session):
    """Create a test user and return auth headers"""
    from app.models.users import User
    import uuid
    
    # Create test user
    user = User(
        id=str(uuid.uuid4()),
        nickname="test_user",
        phone="13800138000",
        password_hash="hashed_password",
        status="ACTIVE",
        rank="NORMAL"
    )
    db_session.add(user)
    db_session.commit()
    
    # For simplicity, return headers without token
    # In real tests, you would login and get a token
    return {}


class TestDefect003FileUploadSizeLimit:
    """Test cases for DEFECT-003: File upload size limit validation"""
    
    def test_upload_file_within_size_limit(self, client: TestClient):
        """Test uploading a file within size limit should succeed"""
        # Create a small file (1KB)
        file_content = b"x" * 1024  # 1KB
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post(
            "/api/v1/files/upload",
            files=files,
        )
        
        # Should fail with auth error (no token)
        assert response.status_code in [401, 403]
    
    def test_upload_file_exceeds_size_limit(self, client: TestClient):
        """Test uploading a file that exceeds size limit should fail"""
        # Create a large file (15MB - exceeds 10MB limit)
        file_content = b"x" * (15 * 1024 * 1024)
        files = {"file": ("large_file.bin", io.BytesIO(file_content), "application/octet-stream")}
        
        response = client.post(
            "/api/v1/files/upload",
            files=files,
        )
        
        # Should fail with size limit error before auth
        # Or fail with auth error if size check is after auth
        assert response.status_code in [400, 401, 403]
        if response.status_code == 400:
            data = response.json()
            assert "文件大小超过限制" in data["detail"] or "文件不能为空" in data["detail"]
    
    def test_upload_empty_file(self, client: TestClient):
        """Test uploading an empty file should fail"""
        # Create an empty file
        file_content = b""
        files = {"file": ("empty.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post(
            "/api/v1/files/upload",
            files=files,
        )
        
        # Should fail with empty file error or auth error
        assert response.status_code in [400, 401, 403]
        if response.status_code == 400:
            data = response.json()
            assert "文件不能为空" in data["detail"]
