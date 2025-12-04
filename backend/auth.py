from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from database import User
from crypto import encrypt_sensitive_data, decrypt_sensitive_data
import os
import re
import secrets
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root (not backend/.env)
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Password hashing context using Argon2 (more secure than bcrypt)
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=6)
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password meets simplified security requirements."""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r"[A-Za-z]", v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with enhanced security."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add additional security claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_hex(16),  # JWT ID for token tracking
        "type": "access_token"
    })
    
    # Encrypt sensitive data in the token
    if "sensitive_data" in to_encode:
        to_encode["sensitive_data"] = encrypt_sensitive_data(to_encode["sensitive_data"])
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token with enhanced security checks."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != "access_token":
            return None
            
        username: str = payload.get("sub")
        if username is None:
            return None
            
        # Additional security checks
        issued_at = payload.get("iat")
        if issued_at is None:
            return None
            
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        return None

def authenticate_user(db: Session, username: str, password: str, client_ip: str = None) -> Optional[User]:
    """Authenticate a user by username/email and password with enhanced security."""
    # Try to find user by username or email
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return None
    
    # Check if account is locked
    if is_account_locked(user):
        return None
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        # Increment failed login attempts
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        
        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        db.commit()
        return None
    
    # Successful login - reset failed attempts
    user.failed_login_attempts = 0
    user.account_locked_until = None
    user.last_login = datetime.utcnow()
    
    # Track login IP (store last 10 IPs as JSON)
    if client_ip:
        update_login_ip_history(user, client_ip)
    
    db.commit()
    return user

def is_account_locked(user: User) -> bool:
    """Check if user account is currently locked."""
    if not user.account_locked_until:
        return False
    return datetime.utcnow() < user.account_locked_until

def update_login_ip_history(user: User, client_ip: str):
    """Update user's login IP history."""
    import json
    
    try:
        ip_history = json.loads(user.login_ip_history or "[]")
    except (json.JSONDecodeError, TypeError):
        ip_history = []
    
    # Add new IP with timestamp
    ip_entry = {
        "ip": client_ip,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Remove IP if it already exists
    ip_history = [entry for entry in ip_history if entry["ip"] != client_ip]
    
    # Add new entry at the beginning
    ip_history.insert(0, ip_entry)
    
    # Keep only last 10 entries
    ip_history = ip_history[:10]
    
    user.login_ip_history = json.dumps(ip_history)

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise ValueError("User with this username or email already exists")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()

def generate_password_reset_token(db: Session, email: str) -> Optional[str]:
    """Generate a password reset token for user."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    # Generate secure token
    reset_token = secrets.token_urlsafe(32)
    
    # Store token hash in database (more secure than storing plain token)
    user.password_reset_token = get_password_hash(reset_token)
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    
    db.commit()
    return reset_token

def verify_password_reset_token(db: Session, token: str) -> Optional[User]:
    """Verify password reset token and return user if valid."""
    if not token:
        return None
    
    # Find user with valid reset token
    users_with_tokens = db.query(User).filter(
        User.password_reset_token.isnot(None),
        User.password_reset_expires > datetime.utcnow()
    ).all()
    
    for user in users_with_tokens:
        if verify_password(token, user.password_reset_token):
            return user
    
    return None

def reset_user_password(db: Session, token: str, new_password: str) -> bool:
    """Reset user password using valid token."""
    user = verify_password_reset_token(db, token)
    if not user:
        return False
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    user.last_password_change = datetime.utcnow()
    
    # Reset failed login attempts
    user.failed_login_attempts = 0
    user.account_locked_until = None
    
    db.commit()
    return True

def generate_email_verification_token(user_id: int) -> str:
    """Generate email verification token."""
    data = {
        "sub": str(user_id),
        "type": "email_verification",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_email_verification_token(db: Session, token: str) -> Optional[User]:
    """Verify email verification token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "email_verification":
            return None
        
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        
        if user and not user.is_verified:
            user.is_verified = True
            db.commit()
        
        return user
    except (JWTError, ValueError):
        return None

def check_password_reuse(db: Session, user: User, new_password: str) -> bool:
    """Check if new password was recently used (prevent password reuse)."""
    # In a production system, you'd store password history
    # For now, just check against current password
    return verify_password(new_password, user.hashed_password)

def is_password_expired(user: User, max_age_days: int = 90) -> bool:
    """Check if user's password has expired."""
    if not user.last_password_change:
        return True
    
    age = datetime.utcnow() - user.last_password_change
    return age.days > max_age_days