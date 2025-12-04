from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import sys
from pathlib import Path
import uuid
import random

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.routers.auth import get_current_user
from database import User
from packages.db.session import get_session
from packages.db.models import Prompt, PromptVersion, JudgeScore
from temporal_analysis import (
    detect_trend, detect_change_points, compute_statistics, 
    compute_causal_hints, compute_score_velocity
)

router = APIRouter(prefix="/api/temporal", tags=["temporal"])

# Pydantic Models

class SyntheticDataRequest(BaseModel):
    prompt_id: str
    days: int = 30
    versions_per_day: int = 2

# Endpoints

@router.get("/timeline")
async def get_temporal_timeline(
    prompt_id: str,
    start: str,
    end: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get temporal timeline of prompt versions with scores.
    
    Args:
        prompt_id: UUID of the prompt
        start: Start date (ISO 8601 format)
        end: End date (ISO 8601 format)
        
    Returns:
        List of tuples: [(timestamp, score, version_id, change_type), ...]
    """
    try:
        # Parse dates
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
        
        # Query database for versions in time range
        with get_session() as session:
            # SECURITY: Verify prompt belongs to current user
            prompt = session.query(Prompt).filter(
                Prompt.id == uuid.UUID(prompt_id),
                Prompt.user_id == str(current_user.id)
            ).first()
            
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found or access denied")
            
            versions = session.query(PromptVersion).filter(
                PromptVersion.prompt_id == uuid.UUID(prompt_id),
                PromptVersion.created_at >= start_date,
                PromptVersion.created_at <= end_date
            ).order_by(PromptVersion.created_at).all()
            
            if not versions:
                return []
            
            # Get judge scores for each version
            timeline = []
            for version in versions:
                judge_score = session.query(JudgeScore).filter(
                    JudgeScore.prompt_version_id == version.id
                ).first()
                
                if judge_score:
                    # Calculate average score
                    avg_score = (
                        judge_score.clarity + 
                        judge_score.specificity + 
                        judge_score.actionability + 
                        judge_score.structure + 
                        judge_score.context_use
                    ) / 5.0
                    
                    timeline.append({
                        "timestamp": version.created_at.isoformat(),
                        "score": avg_score,
                        "version_id": str(version.id),
                        "change_type": version.change_type
                    })
            
            return timeline
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_temporal_statistics(
    prompt_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get temporal statistics for prompt evolution.
    
    Args:
        prompt_id: UUID of the prompt
        
    Returns:
        Dict with trend, avg_score, score_std, total_versions
    """
    try:
        with get_session() as session:
            # SECURITY: Verify prompt belongs to current user
            prompt = session.query(Prompt).filter(
                Prompt.id == uuid.UUID(prompt_id),
                Prompt.user_id == str(current_user.id)
            ).first()
            
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found or access denied")
            
            # Query all versions for this prompt
            versions = session.query(PromptVersion).filter(
                PromptVersion.prompt_id == uuid.UUID(prompt_id)
            ).order_by(PromptVersion.created_at).all()
            
            if not versions:
                raise HTTPException(status_code=404, detail="No versions found for this prompt")
            
            # Get scores and timestamps
            scores = []
            timestamps = []
            
            for version in versions:
                judge_score = session.query(JudgeScore).filter(
                    JudgeScore.prompt_version_id == version.id
                ).first()
                
                if judge_score:
                    avg_score = (
                        judge_score.clarity + 
                        judge_score.specificity + 
                        judge_score.actionability + 
                        judge_score.structure + 
                        judge_score.context_use
                    ) / 5.0
                    
                    scores.append(avg_score)
                    timestamps.append(version.created_at)
            
            # Compute statistics
            stats = compute_statistics(scores)
            trend = detect_trend(scores, timestamps)
            
            return {
                "trend": trend,
                "avg_score": stats["avg"],
                "score_std": stats["std"],
                "total_versions": len(versions),
                "min_score": stats["min"],
                "max_score": stats["max"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/causal-hints")
async def get_causal_hints(
    prompt_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get causal hints showing correlation between change types and score deltas.
    
    Args:
        prompt_id: UUID of the prompt
        
    Returns:
        List of dicts: [{"change_type": str, "avg_score_delta": float, "occurrence_count": int}, ...]
    """
    try:
        with get_session() as session:
            # SECURITY: Verify prompt belongs to current user
            prompt = session.query(Prompt).filter(
                Prompt.id == uuid.UUID(prompt_id),
                Prompt.user_id == str(current_user.id)
            ).first()
            
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found or access denied")
            
            # Query all versions for this prompt
            versions = session.query(PromptVersion).filter(
                PromptVersion.prompt_id == uuid.UUID(prompt_id)
            ).order_by(PromptVersion.created_at).all()
            
            if not versions:
                raise HTTPException(status_code=404, detail="No versions found for this prompt")
            
            # Build edges (parent -> child transitions)
            edges = []
            version_scores = {}
            
            # First pass: Get all scores
            for version in versions:
                judge_score = session.query(JudgeScore).filter(
                    JudgeScore.prompt_version_id == version.id
                ).first()
                
                if judge_score:
                    avg_score = (
                        judge_score.clarity + 
                        judge_score.specificity + 
                        judge_score.actionability + 
                        judge_score.structure + 
                        judge_score.context_use
                    ) / 5.0
                    version_scores[version.id] = avg_score
            
            # Second pass: Build edges
            for version in versions:
                if version.parent_version_id and version.parent_version_id in version_scores:
                    parent_score = version_scores[version.parent_version_id]
                    child_score = version_scores.get(version.id)
                    
                    if child_score is not None:
                        score_delta = child_score - parent_score
                        edges.append((version.change_type, score_delta))
            
            # Compute causal hints
            hints = compute_causal_hints(edges)
            
            return hints
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-synthetic")
async def generate_synthetic_history(
    request: SyntheticDataRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate synthetic prompt version history for testing.
    
    Args:
        request: SyntheticDataRequest with prompt_id, days, versions_per_day
        
    Returns:
        Dict with created_versions count
    """
    try:
        with get_session() as session:
            # SECURITY: Verify prompt exists and belongs to current user
            prompt = session.query(Prompt).filter(
                Prompt.id == uuid.UUID(request.prompt_id),
                Prompt.user_id == str(current_user.id)
            ).first()
            
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found or access denied")
            
            # Generate synthetic versions
            total_versions = request.days * request.versions_per_day
            created_count = 0
            previous_version_id = None
            previous_text = prompt.original_text
            
            # Start with base score and trend upward
            base_score = 60.0
            score_increment = 20.0 / total_versions  # Increase 20 points over time
            
            change_types = ["structure", "wording", "length", "other"]
            
            for day in range(request.days):
                for version_num in range(request.versions_per_day):
                    # Calculate timestamp (spread across days)
                    from datetime import timedelta
                    hours_offset = day * 24 + (version_num * 24 / request.versions_per_day)
                    version_date = datetime.utcnow() - timedelta(days=request.days - day, hours=hours_offset)
                    
                    # Generate version text (simple modification)
                    version_text = f"{previous_text} [v{created_count + 1}]"
                    
                    # Compute change type and magnitude
                    change_type = random.choice(change_types)
                    change_magnitude = random.uniform(0.1, 0.5)
                    
                    # Create version
                    new_version = PromptVersion(
                        id=uuid.uuid4(),
                        prompt_id=uuid.UUID(request.prompt_id),
                        version_no=created_count + 1,
                        text=version_text,
                        explanation={"synthetic": True, "generated_at": datetime.utcnow().isoformat()},
                        source="synthetic_generator",
                        created_at=version_date,
                        parent_version_id=previous_version_id,
                        change_type=change_type,
                        change_magnitude=change_magnitude
                    )
                    session.add(new_version)
                    
                    # Create judge score (trending upward with some noise)
                    current_score = base_score + (created_count * score_increment) + random.uniform(-5, 5)
                    current_score = max(0, min(100, current_score))  # Clamp to 0-100
                    
                    judge_score = JudgeScore(
                        id=uuid.uuid4(),
                        prompt_version_id=new_version.id,
                        clarity=current_score,
                        specificity=current_score,
                        actionability=current_score,
                        structure=current_score,
                        context_use=current_score,
                        feedback={"synthetic": True},
                        created_at=version_date
                    )
                    session.add(judge_score)
                    
                    previous_version_id = new_version.id
                    previous_text = version_text
                    created_count += 1
            
            session.commit()
            
            return {
                "created_versions": created_count,
                "prompt_id": request.prompt_id,
                "days": request.days,
                "versions_per_day": request.versions_per_day
            }
            
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
