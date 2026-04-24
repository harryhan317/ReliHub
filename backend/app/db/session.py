import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Base

_db_url = settings.DATABASE_URL

_use_sqlite = False
if "sqlite" in _db_url:
    _use_sqlite = True
elif "db:5432" in _db_url or "localhost:5432" in _db_url:
    try:
        import psycopg2
        conn = psycopg2.connect(_db_url.replace("postgresql://", "postgresql://").replace("+psycopg2", ""))
        conn.close()
    except Exception:
        _sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "relihub_dev.db")
        _db_url = f"sqlite:///{_sqlite_path}"
        _use_sqlite = True

engine = create_engine(_db_url, connect_args={"check_same_thread": False} if "sqlite" in _db_url else {})

if _use_sqlite:
    from app.models.administrators import AdminAuditLog, AdminUser  # noqa: F401
    from app.models.ledger import PointLedger  # noqa: F401
    from app.models.resources import Resource  # noqa: F401
    from app.models.users import User  # noqa: F401
    Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
