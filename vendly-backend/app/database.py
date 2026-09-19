from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Set up SQLite database connection file
DATABASE_URL = "sqlite:///./vendly.db"

# Engine connects Python to SQLite; check_same_thread is needed for SQLite with FastAPI threads
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal creates fresh database sessions per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class used by all ORM models to map tables
Base = declarative_base()

# Dependency function to provide a database session to API endpoints and close it when done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()