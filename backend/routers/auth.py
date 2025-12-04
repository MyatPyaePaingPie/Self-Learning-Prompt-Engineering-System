from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel, Field

# Import from backend modules
from database import get_db, User
from auth import (
    authenticate_user, create_access_token, verify_token, create_user,
    get_user_by_username, UserCreate, UserResponse, LoginRequest, Token,
    ACCESS_TOKEN_EXPIRE_MINUTES, verify_password, get_password_hash,
    generate_password_reset_token, reset_user_password,
    generate_email_verification_token, verify_email_verification_token,
    is_password_expired, check_password_reuse
)

# Router configuration
router = APIRouter(prefix="", tags=["authentication"])
security = HTTPBearer()

# Initialize limiter (will be set from app state)
limiter = Limiter(key_func=get_remote_address)

# Pydantic models for password management
class PasswordResetRequest(BaseModel):
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


# Dependency function (exported for use by other routers)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Dependency to get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


# Auth endpoints
@router.post("/register", response_model=UserResponse)
@limiter.limit("3/minute")  # Limit registration attempts
async def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with enhanced validation."""
    try:
        db_user = create_user(db, user)
        return UserResponse.model_validate(db_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Limit login attempts
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token with enhanced security."""
    # Get client IP for security tracking
    client_ip = get_remote_address(request)
    
    user = authenticate_user(db, login_data.username, login_data.password, client_ip)
    if not user:
        # Check if account is locked
        potential_user = db.query(User).filter(
            (User.username == login_data.username) | (User.email == login_data.username)
        ).first()
        
        if potential_user and potential_user.account_locked_until:
            if datetime.utcnow() < potential_user.account_locked_until:
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account temporarily locked due to multiple failed login attempts. Try again later.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is deactivated"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Include encrypted user session data
    session_data = {
        "user_id": user.id,
        "login_time": user.last_login.isoformat() if user.last_login else None
    }
    
    access_token = create_access_token(
        data={
            "sub": user.username,
            "sensitive_data": session_data
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse.model_validate(current_user)

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """Example protected route that requires authentication."""
    return {
        "message": f"Hello {current_user.username}! This is a protected route.",
        "user_id": current_user.id,
        "access_time": "now"
    }

@router.post("/auth/request-password-reset")
@limiter.limit("3/minute")  # Strict limit for password reset requests
async def request_password_reset(request: Request, reset_request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset token (always returns success for security)."""
    # Always return success to prevent email enumeration attacks
    token = generate_password_reset_token(db, reset_request.email)
    
    # In production, send email with token here
    # For demo purposes, we'll log it
    if token:
        print(f"Password reset token for {reset_request.email}: {token}")
    
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/auth/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request, reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password using token."""
    # Validate new password strength
    user_create = UserCreate(username="temp", email="temp@example.com", password=reset_data.new_password)
    try:
        # This will validate the password
        user_create.validate_password_strength(reset_data.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    success = reset_user_password(db, reset_data.token, reset_data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired password reset token"
        )
    
    return {"message": "Password reset successfully"}

@router.post("/auth/change-password")
async def change_password(
    request: Request,
    change_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password (requires authentication)."""
    # Verify current password
    if not verify_password(change_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )
    
    # Check password reuse
    if check_password_reuse(db, current_user, change_data.new_password):
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as current password"
        )
    
    # Validate new password
    try:
        user_create = UserCreate(username="temp", email="temp@example.com", password=change_data.new_password)
        user_create.validate_password_strength(change_data.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Update password
    current_user.hashed_password = get_password_hash(change_data.new_password)
    current_user.last_password_change = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.get("/auth/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email address using token."""
    user = verify_email_verification_token(db, token)
    
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email verified successfully", "user_id": user.id}

@router.get("/auth/account-status")
async def get_account_status(current_user: User = Depends(get_current_user)):
    """Get current user's account security status."""
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_verified": current_user.is_verified,
        "is_active": current_user.is_active,
        "failed_login_attempts": current_user.failed_login_attempts or 0,
        "account_locked": bool(current_user.account_locked_until and
                              datetime.utcnow() < current_user.account_locked_until),
        "password_expired": is_password_expired(current_user),
        "last_login": current_user.last_login,
        "last_password_change": current_user.last_password_change,
        "two_factor_enabled": current_user.two_factor_enabled
    }
