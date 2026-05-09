"""
Database configuration and session management.

data-model-spec: contains → polymorphic-nodes, typed-directed-edges
Reuses: Fastapi Sqlite Crud, Sqlite Schema Evolution
"""

import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# Default to SQLite in project root, override via env
DB_PATH = os.environ.get("SPEC_STUDIO_DB", os.path.join(os.path.dirname(__file__), "spec_studio.db"))
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

# Enable WAL mode + foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA cache_size=-8000")  # 8MB cache
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Safe to call multiple times."""
    Base.metadata.create_all(bind=engine)
