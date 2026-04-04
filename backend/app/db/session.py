import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base

# Use SQLite for local dev if PostgreSQL is not available
_db_url = settings.DATABASE_URL
if "db:5432" in _db_url or "localhost:5432" in _db_url:
    _sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "relihub_dev.db")
    _db_url = f"sqlite:///{_sqlite_path}"

engine = create_engine(_db_url, connect_args={"check_same_thread": False} if "sqlite" in _db_url else {})

# Create all tables on startup (SQLite dev mode)
if "sqlite" in _db_url:
    # Import all models so Base.metadata knows about them
    from app.models.users import User  # noqa: F401
    from app.models.resources import Resource  # noqa: F401
    from app.models.ledger import CocoaBeanLedger, ReputationLog  # noqa: F401
    from app.models.administrators import AdminUser, AdminAuditLog  # noqa: F401
    Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
