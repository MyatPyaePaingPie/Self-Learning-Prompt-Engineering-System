from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.routers.auth import get_current_user
from database import User
from packages.db.session import get_session
from packages.db.crud import create_security_input_row, get_security_inputs

router = APIRouter(prefix="/v1/security", tags=["security"])

# Pydantic Models

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

# Endpoints

@router.post("/inputs", response_model=SecurityInputResponse)
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

@router.get("/inputs")
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
