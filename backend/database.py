from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root (not backend/.env)
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

# Database setup - Use AUTH_DATABASE_URL for authentication database
AUTH_DATABASE_URL = os.getenv("AUTH_DATABASE_URL", "sqlite:///./auth_system.db")
engine = create_engine(AUTH_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Enhanced Security Fields
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime, nullable=True)
    last_password_change = Column(DateTime, default=datetime.utcnow)
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    two_factor_secret = Column(String, nullable=True)
    two_factor_enabled = Column(Boolean, default=False)
    login_ip_history = Column(String, nullable=True)  # JSON string of recent IPs

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()