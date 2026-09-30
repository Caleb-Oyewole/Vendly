"""
Replaces the old raw-sqlite3 database.py. Spec section 3 requires SQLAlchemy 2
models running on SQLite in dev and Postgres (Neon) in deploy, switched purely
by DATABASE_URL -- no code change between environments.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from app.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # Needed because FastAPI can use the connection across threads.
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency yielding an ORM session per request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Creates all tables on startup if they don't already exist."""
    # Import models here (not at module top) so they register on Base
    # before create_all runs, without causing a circular import.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
