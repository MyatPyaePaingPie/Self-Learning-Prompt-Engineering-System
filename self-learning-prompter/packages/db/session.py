from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

# Database URL from environment or default to local PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/prompter_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_session():
    """Context manager for database sessions"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()