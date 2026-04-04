"""
Integration tests for Sprint B modules.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models import Base
from app.models.users import User
from app.core.security import get_password_hash

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine):
    """Create test database session"""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.commit()


@pytest.fixture(scope="function")
async def client(test_db):
    """Create test HTTP client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(test_db):
    """Create a test user"""
    user = User(
        user_uuid="test-user-uuid",
        username="testuser",
        email="test@example.com",
        phone="13800138000",
        hashed_password=get_password_hash("password123"),
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


# ── AI Module Tests ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_ai_session(client, test_user):
    """Test creating an AI session"""
    # Login first
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Create session
    response = await client.post(
        "/api/v1/ai/sessions",
        json={"title": "Test Session", "model_type": "general"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Session"
    assert data["model_type"] == "general"


@pytest.mark.asyncio
async def test_list_ai_sessions(client, test_user):
    """Test listing AI sessions"""
    # Login first
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # List sessions
    response = await client.get(
        "/api/v1/ai/sessions",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert "total" in data


# ── Resource Module Tests ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_resource(client, test_user):
    """Test creating a resource"""
    # Login first
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Create resource
    response = await client.post(
        "/api/v1/resources",
        json={
            "title": "Test Resource",
            "description": "A test resource",
            "category_id": 1,
            "price": 5,
            "file_uuid": "test-file-uuid"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Resource"
    assert data["status"] == "SCANNING"


@pytest.mark.asyncio
async def test_list_resources(client):
    """Test listing resources"""
    response = await client.get("/api/v1/resources")
    
    assert response.status_code == 200
    data = response.json()
    assert "resources" in data
    assert "total" in data


# ── Community Module Tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_topic(client, test_user):
    """Test creating a topic"""
    # Login first
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Create topic
    response = await client.post(
        "/api/v1/community/topics",
        json={
            "title": "Test Topic",
            "content": "This is a test topic content",
            "category_id": 1,
            "bounty_amount": 10
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Topic"
    assert data["bounty_amount"] == 10


@pytest.mark.asyncio
async def test_list_topics(client):
    """Test listing topics"""
    response = await client.get("/api/v1/community/topics")
    
    assert response.status_code == 200
    data = response.json()
    assert "topics" in data
    assert "total" in data


# ── Ledger Module Tests ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_balance(client, test_user):
    """Test getting user balance"""
    # Login first
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Get balance
    response = await client.get(
        "/api/v1/ledger/balance",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "gold_beans" in data
    assert "bonus_beans" in data
    assert "total_beans" in data


# ── Notification Module Tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_notifications(client, test_user):
    """Test getting notifications"""
    # Login first
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Get notifications
    response = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "notifications" in data
    assert "total" in data
    assert "unread_count" in data


# ── File Module Tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upload_file(client, test_user, tmp_path):
    """Test uploading a file"""
    # Login first
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test file content")
    
    # Upload file
    with open(test_file, "rb") as f:
        response = await client.post(
            "/api/v1/files/upload",
            files={"file": ("test.txt", f, "text/plain")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "file_uuid" in data
    assert "file_hash" in data
    assert "file_name" in data


# ── Integration Tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_full_resource_flow(client, test_user):
    """Test complete resource workflow"""
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # 1. Upload file
    file_content = b"Test resource content"
    response = await client.post(
        "/api/v1/files/upload",
        files={"file": ("resource.pdf", file_content, "application/pdf")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    file_uuid = response.json()["file_uuid"]
    
    # 2. Create resource
    response = await client.post(
        "/api/v1/resources",
        json={
            "title": "Test PDF Resource",
            "description": "A test PDF",
            "category_id": 1,
            "price": 10,
            "file_uuid": file_uuid
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    resource_id = response.json()["id"]
    
    # 3. Get resource
    response = await client.get(f"/api/v1/resources/{resource_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test PDF Resource"
    
    # 4. List resources
    response = await client.get("/api/v1/resources")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
