from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from auth import get_current_user, User
from packages.db.session import get_session
from packages.db.crud import get_agent_effectiveness_stats

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Initialize limiter (will use app.state.limiter from main)
limiter = Limiter(key_func=get_remote_address)

# Endpoints

@router.get("/effectiveness")
@limiter.limit("20/minute")
async def get_agent_effectiveness(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Query agent effectiveness from database (not CSV).
    
    Database-First Pattern:
    - Queries PostgreSQL directly
    - No CSV reads
    """
    try:
        effectiveness = get_agent_effectiveness_stats(session)
        
        return {
            "success": True,
            "effectiveness": effectiveness
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
