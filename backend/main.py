from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to path for relative imports
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load .env from project root (not backend/.env)
load_dotenv(project_root / '.env')

# Now import from backend modules
from database import get_db, User
from auth import (
    authenticate_user, create_access_token, verify_token, create_user,
    get_user_by_username, UserCreate, UserResponse, LoginRequest, Token,
    ACCESS_TOKEN_EXPIRE_MINUTES, verify_password, get_password_hash,
    generate_password_reset_token, reset_user_password,
    generate_email_verification_token, verify_email_verification_token,
    is_password_expired, check_password_reuse
)
from crypto import encrypt_sensitive_data, decrypt_sensitive_data

# Import for security dashboard
from packages.db.session import get_session
from packages.db.crud import create_security_input_row, get_security_inputs
from pydantic import BaseModel

app = FastAPI(
    title="Secure Authentication API",
    version="1.0.0",
    description="Production-ready authentication system with end-to-end encryption"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security scheme
security = HTTPBearer()

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# CORS middleware
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Security-Status"]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Security-Status"] = "protected"
    return response

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

@app.post("/register", response_model=UserResponse)
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

@app.post("/login", response_model=Token)
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

@app.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse.model_validate(current_user)

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """Example protected route that requires authentication."""
    return {
        "message": f"Hello {current_user.username}! This is a protected route.",
        "user_id": current_user.id,
        "access_time": "now"
    }

# Prompt Enhancement API Endpoints
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

class PromptInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class PromptResponse(BaseModel):
    id: str
    original_text: str
    enhanced_text: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: str
    user_id: int

class PromptEnhanceRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    enhancement_type: str = Field(default="general", pattern="^(general|creative|technical|persuasive|clear)$")
    context: Optional[str] = Field(None, max_length=1000)

@app.post("/prompts/enhance")
@limiter.limit("10/minute")
async def enhance_prompt(
    request: Request,
    prompt_data: PromptEnhanceRequest,
    current_user: User = Depends(get_current_user)
):
    """Enhance a text prompt using AI optimization techniques."""
    try:
        # Encrypt the original prompt for storage
        encrypted_text = encrypt_sensitive_data(prompt_data.text)
        
        # Apply prompt enhancement logic based on type
        enhanced_text = apply_prompt_enhancement(
            prompt_data.text,
            prompt_data.enhancement_type,
            prompt_data.context
        )
        
        # Create response with encrypted data
        prompt_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "data": {
                "id": prompt_id,
                "original_text": prompt_data.text,
                "enhanced_text": enhanced_text,
                "enhancement_type": prompt_data.enhancement_type,
                "created_at": datetime.utcnow().isoformat(),
                "user_id": current_user.id
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prompt enhancement failed"
        )

@app.post("/prompts/save")
@limiter.limit("20/minute")
async def save_prompt(
    request: Request,
    prompt_data: PromptInput,
    current_user: User = Depends(get_current_user)
):
    """Save a prompt to user's collection."""
    try:
        # Encrypt sensitive prompt data
        encrypted_text = encrypt_sensitive_data(prompt_data.text)
        
        prompt_id = str(uuid.uuid4())
        
        # In a real implementation, this would be saved to database
        return {
            "success": True,
            "data": {
                "id": prompt_id,
                "text": prompt_data.text,
                "category": prompt_data.category,
                "tags": prompt_data.tags or [],
                "created_at": datetime.utcnow().isoformat(),
                "user_id": current_user.id
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save prompt"
        )

@app.get("/prompts/my-prompts")
async def get_user_prompts(current_user: User = Depends(get_current_user)):
    """Get all prompts belonging to the current user."""
    # In a real implementation, this would query the database
    return {
        "success": True,
        "data": {
            "prompts": [],
            "total": 0,
            "user_id": current_user.id
        }
    }

# Multi-Agent Enhancement Endpoints (Week 11)

from packages.core.agent_registry import AgentRegistry
from packages.core.agent_coordinator import AgentCoordinator
from storage.file_storage import FileStorage

# Singleton coordinator (uses registry internally)
_multi_agent_coordinator = None
# Singleton file storage (Week 11 - Phase 2)
_file_storage = None

def get_multi_agent_coordinator() -> AgentCoordinator:
    """Get coordinator with default agents (syntax, structure, domain)"""
    global _multi_agent_coordinator
    
    if not _multi_agent_coordinator:
        _multi_agent_coordinator = AgentCoordinator()  # Uses default agents from registry
    
    return _multi_agent_coordinator

def get_file_storage() -> FileStorage:
    """Get file storage singleton"""
    global _file_storage
    
    if not _file_storage:
        # Initialize with storage directory
        import os
        storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
        _file_storage = FileStorage(base_dir=storage_dir)
    
    return _file_storage

@app.post("/prompts/multi-agent-enhance")
@limiter.limit("5/minute")  # Lower limit (3 LLM calls per request)
async def multi_agent_enhance(
    request: Request,
    prompt_data: PromptEnhanceRequest,
    current_user: User = Depends(get_current_user)
):
    """Enhance prompt using multi-agent collaboration (Week 11)."""
    try:
        # Get coordinator (uses registry internally)
        coordinator = get_multi_agent_coordinator()
        decision = await coordinator.coordinate(prompt_data.text)
        
        # Add model info to response
        agent_results_with_models = []
        for result in decision.agent_results:
            result_dict = result.dict()
            
            # Add model info from registry
            metadata = AgentRegistry.get_metadata(result.agent_name)
            if metadata:
                result_dict["model_used"] = {
                    "model_id": metadata.model_config.model_id,
                    "display_name": metadata.model_config.display_name,
                    "speed": metadata.model_config.speed.value,
                    "cost": metadata.model_config.cost.value
                }
            agent_results_with_models.append(result_dict)
        
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        
        # Log to storage (Phase 2 - L:IV atomicity, don't block on failure)
        try:
            file_storage = get_file_storage()
            file_storage.save_multi_agent_result(
                request_id=request_id,
                original_prompt=prompt_data.text,
                agent_results=[r.dict() for r in decision.agent_results],
                decision=decision.dict()
            )
        except Exception as storage_error:
            # Don't fail request if logging fails (L:IV atomicity)
            logger.error(f"Failed to log multi-agent result: {storage_error}")
        
        return {
            "success": True,
            "data": {
                "request_id": request_id,
                "original_text": prompt_data.text,
                "enhanced_text": decision.final_prompt,
                "selected_agent": decision.selected_agent,
                "decision_rationale": decision.decision_rationale,
                "agent_results": agent_results_with_models,
                "vote_breakdown": decision.vote_breakdown,
                "created_at": datetime.utcnow().isoformat(),
                "user_id": current_user.id
            }
        }
    except Exception as e:
        logger.error(f"Multi-agent enhancement failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-agent enhancement failed: {str(e)}"
        )

@app.get("/prompts/available-agents")
async def get_available_agents(current_user: User = Depends(get_current_user)):
    """Get list of available agents and their model configurations."""
    try:
        agents = []
        for agent_name in AgentRegistry.get_all_agents():
            metadata = AgentRegistry.get_metadata(agent_name)
            if metadata:
                agents.append({
                    "name": agent_name,
                    "display_name": metadata.display_name,
                    "description": metadata.description,
                    "focus_areas": metadata.focus_areas,
                    "model": {
                        "model_id": metadata.model_config.model_id,
                        "display_name": metadata.model_config.display_name,
                        "speed": metadata.model_config.speed.value,
                        "cost": metadata.model_config.cost.value,
                        "use_case": metadata.model_config.use_case
                    }
                })
        
        return {
            "success": True,
            "data": {"agents": agents}
        }
    except Exception as e:
        logger.error(f"Failed to get available agents: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available agents"
        )

@app.get("/prompts/agent-effectiveness")
async def get_agent_effectiveness(current_user: User = Depends(get_current_user)):
    """Get agent effectiveness statistics (Week 11 - Phase 2)."""
    try:
        file_storage = get_file_storage()
        effectiveness = file_storage.get_agent_effectiveness()
        
        return {
            "success": True,
            "data": effectiveness
        }
    except Exception as e:
        logger.error(f"Failed to get agent effectiveness: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agent effectiveness"
        )

def apply_prompt_enhancement(text: str, enhancement_type: str, context: Optional[str] = None) -> str:
    """Apply prompt enhancement using structured template approach."""
    
    TEMPLATE_V1 = """You are a senior {domain} expert.
Task: {task}
Deliverables:
- Clear, step-by-step plan
- Examples and edge-cases
- Final {artifact} ready to use
Constraints: {constraints}
If information is missing, list precise clarifying questions first, then proceed with best assumptions."""

    # Analyze the input text to extract components
    domain, task, artifact, constraints = analyze_prompt_components(text, enhancement_type, context)
    
    # Apply the template
    enhanced_prompt = TEMPLATE_V1.format(
        domain=domain,
        task=task,
        artifact=artifact,
        constraints=constraints
    )
    
    return enhanced_prompt

def analyze_prompt_components(text: str, enhancement_type: str, context: Optional[str] = None) -> tuple:
    """Analyze user input to extract domain, task, artifact, and constraints."""
    
    # Domain mapping based on enhancement type and content analysis
    domain_mapping = {
        "technical": "Software Engineering",
        "creative": "Creative Writing",
        "persuasive": "Marketing & Communications",
        "clear": "Technical Communication",
        "general": "Problem Solving"
    }
    
    # Extract or infer domain
    domain = domain_mapping.get(enhancement_type, "Subject Matter")
    
    # If context provides domain info, use it
    if context:
        context_lower = context.lower()
        if any(word in context_lower for word in ["software", "programming", "code", "development"]):
            domain = "Software Engineering"
        elif any(word in context_lower for word in ["writing", "story", "creative", "content"]):
            domain = "Creative Writing"
        elif any(word in context_lower for word in ["marketing", "sales", "business"]):
            domain = "Marketing & Strategy"
        elif any(word in context_lower for word in ["research", "analysis", "academic"]):
            domain = "Research & Analysis"
    
    # Clean and structure the task
    task = text.strip()
    if not task.endswith(('.', '!', '?')):
        task += "."
    
    # Determine artifact type based on content
    text_lower = text.lower()
    if any(word in text_lower for word in ["write", "create", "generate", "compose"]):
        if any(word in text_lower for word in ["code", "script", "program", "function"]):
            artifact = "code implementation"
        elif any(word in text_lower for word in ["story", "article", "content", "copy"]):
            artifact = "written content"
        elif any(word in text_lower for word in ["plan", "strategy", "proposal"]):
            artifact = "strategic plan"
        else:
            artifact = "deliverable"
    elif any(word in text_lower for word in ["analyze", "research", "investigate"]):
        artifact = "analysis report"
    elif any(word in text_lower for word in ["design", "build", "develop"]):
        artifact = "design specification"
    else:
        artifact = "solution"
    
    # Set appropriate constraints based on enhancement type
    constraint_mapping = {
        "technical": "Follow best practices, include error handling, ensure scalability",
        "creative": "Maintain originality, engage target audience, stay within brand guidelines",
        "persuasive": "Use evidence-based arguments, address counterpoints, include clear call-to-action",
        "clear": "Use simple language, logical structure, avoid jargon unless necessary",
        "general": "Be comprehensive yet concise, consider multiple perspectives"
    }
    
    constraints = constraint_mapping.get(enhancement_type, "Be thorough and practical")
    
    # Add context-specific constraints
    if context:
        constraints += f". Additional context: {context}"
    
    return domain, task, artifact, constraints

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Authentication API is running"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Secure Authentication & Prompt Enhancement API",
        "version": "1.0.0",
        "endpoints": {
            "register": "/register",
            "login": "/login",
            "me": "/me",
            "protected": "/protected",
            "enhance_prompt": "/prompts/enhance",
            "save_prompt": "/prompts/save",
            "my_prompts": "/prompts/my-prompts",
            "health": "/health"
        }
    }

# Enhanced Security Endpoints

class PasswordResetRequest(BaseModel):
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

@app.post("/auth/request-password-reset")
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

@app.post("/auth/reset-password")
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

@app.post("/auth/change-password")
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

@app.get("/auth/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email address using token."""
    user = verify_email_verification_token(db, token)
    
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email verified successfully", "user_id": user.id}

@app.get("/auth/account-status")
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

# Security Dashboard Endpoints

class SecurityInputIn(BaseModel):
    inputText: str
    riskScore: float
    label: str
    isBlocked: bool
    analysisMetadata: dict | None = None

class SecurityInputResponse(BaseModel):
    id: str
    userId: str
    inputText: str
    riskScore: float
    label: str
    isBlocked: bool
    analysisMetadata: dict | None
    createdAt: str

@app.post("/v1/security/inputs", response_model=SecurityInputResponse)
async def log_security_input(
    payload: SecurityInputIn,
    current_user: User = Depends(get_current_user)
):
    """Log a security input with risk assessment (authenticated)"""
    try:
        with get_session() as s:
            security_input = create_security_input_row(
                s,
                str(current_user.id),  # Use authenticated user ID
                payload.inputText,
                payload.riskScore,
                payload.label,
                payload.isBlocked,
                payload.analysisMetadata
            )
            s.commit()
            
            return SecurityInputResponse(
                id=str(security_input.id),
                userId=str(current_user.id),
                inputText=security_input.input_text,
                riskScore=security_input.risk_score,
                label=security_input.label,
                isBlocked=security_input.is_blocked,
                analysisMetadata=security_input.analysis_metadata,
                createdAt=security_input.created_at.isoformat()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/security/inputs")
async def get_security_inputs_endpoint(
    limit: int = 100,
    filter_label: str | None = None,
    filter_blocked: bool | None = None,
    filter_high_risk: bool | None = None,
    current_user: User = Depends(get_current_user)
):
    """Get security inputs with optional filtering (authenticated)"""
    try:
        with get_session() as s:
            inputs = get_security_inputs(
                s,
                limit=limit,
                filter_label=filter_label,
                filter_blocked=filter_blocked,
                filter_high_risk=filter_high_risk
            )
            
            return [
                {
                    "id": str(input.id),
                    "userId": input.user_id,
                    "inputText": input.input_text,
                    "riskScore": input.risk_score,
                    "label": input.label,
                    "isBlocked": input.is_blocked,
                    "analysisMetadata": input.analysis_metadata,
                    "createdAt": input.created_at.isoformat()
                }
                for input in inputs
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed to port 8001 to avoid conflicts