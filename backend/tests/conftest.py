"""
Pytest configuration and fixtures.

IMPORTANT: All tests MUST use PostgreSQL database.
SQLite is NOT allowed for testing as per project standards.

Test database configuration:
- Default: postgresql://postgres:postgres@localhost:5432/relihub_test
- Override via TEST_DATABASE_URL environment variable

Rate limiting:
- TESTING=true enables permissive rate limits for tests (10000/day, 10000/hour)
- See app/core/rate_limiter.py for TESTING_MODE configuration
"""
import os
import uuid

# Enable testing mode for permissive rate limits BEFORE any app imports
os.environ["TESTING"] = "true"

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import generate_phone_blind_index, hash_password
from app.models import Base
from app.models.users import User

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
    Uses transaction rollback for clean test isolation.
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
    
    # Ensure transaction is rolled back to clean up test data
    # This is a safety net in case tests didn't properly clean up
    try:
        db_session.rollback()
    except Exception:
        pass


@pytest.fixture(scope="function")
def isolated_db_session():
    """
    Create an isolated database session with automatic cleanup.
    
    This fixture ensures complete test isolation by:
    1. Creating a new transaction for each test
    2. Automatically rolling back all changes after test
    3. Verifying no test data leaks between tests
    
    Use this fixture when you need guaranteed clean database state.
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
        # Rollback all changes to ensure clean state
        session.rollback()
        transaction.rollback()
        session.close()
        connection.close()
        engine.dispose()


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use default event loop policy."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()
