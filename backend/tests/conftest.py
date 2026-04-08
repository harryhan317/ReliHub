"""
Pytest configuration and fixtures.

IMPORTANT: All tests MUST use PostgreSQL database.
SQLite is NOT allowed for testing as per project standards.

Test database configuration:
- Default: postgresql://postgres:postgres@localhost:5432/relihub_test
- Override via TEST_DATABASE_URL environment variable
"""
import os
import uuid
import pytest
import pytest_asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.models import Base
from app.models.users import User
from app.core.security import hash_password, generate_phone_blind_index

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/relihub_test"
)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh PostgreSQL database session for each test.
    
    Uses PostgreSQL test database for realistic testing.
    Each test gets a clean database state via transaction rollback.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    connection = engine.connect()
    transaction = connection.begin()
    
    Base.metadata.create_all(connection)
    
    SessionLocal = sessionmaker(
        bind=connection,
        class_=Session,
        expire_on_commit=False,
        future=True,
    )
    
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


@pytest.fixture(scope="function")
def db_engine():
    """
    Create a PostgreSQL engine for tests that need direct engine access.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    Base.metadata.create_all(engine)
    
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture(scope="function")
def test_engine():
    """
    Alias for db_engine for backward compatibility.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(engine)
    
    yield engine
    
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def test_db(test_engine):
    """
    Create a test database session from test_engine.
    For backward compatibility with existing tests.
    """
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    
    yield session
    
    session.commit()
    session.close()


@pytest_asyncio.fixture(scope="function")
async def async_db_session():
    """
    Create a fresh async database session for async tests.
    
    Uses PostgreSQL test database for realistic testing.
    """
    async_url = TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        async_url,
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        future=True
    )
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
    
    await engine.dispose()


@pytest.fixture
def test_user(db_session):
    """Create a standard test user."""
    phone = "13800138000"
    user = User(
        id=str(uuid.uuid4()),
        phone=phone,
        phone_blind_index=generate_phone_blind_index(phone),
        nickname="test_user",
        password_hash=hash_password("TestPassword123!"),
        status="ACTIVE",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def client(db_session):
    """
    Create a test client with database session override.
    """
    from app.db.session import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    from app.main import app
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use default event loop policy."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()
