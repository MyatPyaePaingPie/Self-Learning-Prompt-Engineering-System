from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import sys
import logging
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

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router imports
from backend.routers import auth, prompts, security, temporal, storage, agents

app = FastAPI(
    title="Secure Authentication API",
    version="1.0.0",
    description="Production-ready authentication system with end-to-end encryption"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# Register routers
app.include_router(auth.router)
app.include_router(prompts.router)
app.include_router(security.router)
app.include_router(temporal.router)
app.include_router(storage.router)
app.include_router(agents.router)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
