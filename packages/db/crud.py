import sqlalchemy as sa
from sqlalchemy.orm import Session
from .models import Prompt, PromptVersion, JudgeScore, BestHead, SecurityInput, UserFeedback
from packages.core.judge import Scorecard
import uuid

def create_prompt_row(session: Session, user_id: str | None, original_text: str, request_id: str | None = None) -> Prompt:
    """Create a new prompt record"""
    prompt = Prompt(user_id=user_id, original_text=original_text, request_id=request_id)
    session.add(prompt)
    session.flush()  # Get the ID without committing
    return prompt

def get_prompt_by_request_id(session: Session, request_id: str) -> Prompt | None:
    """Get prompt by request_id"""
    return session.execute(
        sa.select(Prompt).where(Prompt.request_id == request_id)
    ).scalar_one_or_none()

def create_version_row(session: Session, prompt_id: uuid.UUID, version_no: int, 
                      text: str, explanation: dict, source: str) -> PromptVersion:
    """Create a new prompt version record"""
    version = PromptVersion(
        prompt_id=prompt_id,
        version_no=version_no,
        text=text,
        explanation=explanation,
        source=source
    )
    session.add(version)
    session.flush()  # Get the ID without committing
    return version

def create_judge_score_row(session: Session, version_id: uuid.UUID, scorecard: Scorecard) -> JudgeScore:
    """Create a new judge score record"""
    score = JudgeScore(
        prompt_version_id=version_id,
        clarity=scorecard.clarity,
        specificity=scorecard.specificity,
        actionability=scorecard.actionability,
        structure=scorecard.structure,
        context_use=scorecard.context_use,
        feedback=scorecard.feedback
    )
    session.add(score)
    session.flush()  # Get the ID without committing
    return score

def maybe_update_best_head(session: Session, prompt_id: uuid.UUID, version_id: uuid.UUID, score: float):
    """Update best head if score is better than current best"""
    bh = session.execute(sa.select(BestHead).where(BestHead.prompt_id==prompt_id)).scalar_one_or_none()
    if not bh or score >= bh.score:
        if not bh:
            bh = BestHead(prompt_id=prompt_id, prompt_version_id=version_id, score=score)
            session.add(bh)
        else:
            bh.prompt_version_id = version_id
            bh.score = score

def get_prompt_by_id(session: Session, prompt_id: uuid.UUID) -> Prompt | None:
    """Get prompt by ID"""
    return session.execute(sa.select(Prompt).where(Prompt.id==prompt_id)).scalar_one_or_none()

def get_prompt_versions(session: Session, prompt_id: uuid.UUID) -> list[PromptVersion]:
    """Get all versions for a prompt"""
    return session.execute(
        sa.select(PromptVersion)
        .where(PromptVersion.prompt_id==prompt_id)
        .order_by(PromptVersion.version_no)
    ).scalars().all()

def get_best_head(session: Session, prompt_id: uuid.UUID) -> BestHead | None:
    """Get the best version for a prompt"""
    return session.execute(sa.select(BestHead).where(BestHead.prompt_id==prompt_id)).scalar_one_or_none()

def create_security_input_row(session: Session, user_id: str | None, input_text: str, 
                              risk_score: float, label: str, is_blocked: bool, 
                              analysis_metadata: dict | None = None) -> SecurityInput:
    """Create a new security input record"""
    security_input = SecurityInput(
        user_id=user_id,
        input_text=input_text,
        risk_score=risk_score,
        label=label,
        is_blocked=is_blocked,
        analysis_metadata=analysis_metadata
    )
    session.add(security_input)
    session.flush()  # Get the ID without committing
    return security_input

def get_security_inputs(session: Session, limit: int = 100, 
                       filter_label: str | None = None, 
                       filter_blocked: bool | None = None,
                       filter_high_risk: bool | None = None) -> list[SecurityInput]:
    """Get security inputs with optional filtering"""
    query = sa.select(SecurityInput).order_by(SecurityInput.created_at.desc())
    
    if filter_label:
        query = query.where(SecurityInput.label == filter_label)
    
    if filter_blocked is not None:
        query = query.where(SecurityInput.is_blocked == filter_blocked)
    
    if filter_high_risk:
        query = query.where(SecurityInput.risk_score >= 70.0)
    
    query = query.limit(limit)
    return session.execute(query).scalars().all()

# ============================================================================
# STORAGE CONSOLIDATION PHASE 1: Database-First CRUD Functions
# Added: 2025-12-04
# Purpose: Single source of truth - all data queries go through database
# ============================================================================

def get_all_prompt_versions(session: Session, limit: int = 1000) -> list[PromptVersion]:
    """
    Get all prompt versions for CSV export.
    Used by export_multi_agent_results_to_csv() in storage layer.
    """
    return session.execute(
        sa.select(PromptVersion)
        .order_by(PromptVersion.created_at.desc())
        .limit(limit)
    ).scalars().all()

def get_prompt_versions_by_source(session: Session, source: str, limit: int = 1000) -> list[PromptVersion]:
    """
    Get versions by agent source (syntax, structure, domain).
    Used for agent-specific analysis.
    """
    return session.execute(
        sa.select(PromptVersion)
        .where(PromptVersion.source == source)
        .order_by(PromptVersion.created_at.desc())
        .limit(limit)
    ).scalars().all()

def get_prompt_version_chain(session: Session, prompt_id: uuid.UUID) -> list[PromptVersion]:
    """
    Get version chain ordered by timestamp (parent→child).
    Used for temporal analysis and version chain visualization.
    """
    return session.execute(
        sa.select(PromptVersion)
        .where(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.created_at)
    ).scalars().all()

def get_agent_effectiveness_stats(session: Session) -> dict[str, dict]:
    """
    Calculate agent effectiveness statistics.
    Returns: {"syntax": {"wins": 10, "total": 30, "win_rate": 0.33, "avg_score": 8.5}, ...}
    """
    try:
        # Get all versions
        versions = session.execute(sa.select(PromptVersion)).scalars().all()
        
        # Handle empty database gracefully
        if not versions:
            return {}
        
        # Calculate stats per agent
        stats = {}
        for version in versions:
            source = version.source
            if not source:  # Skip versions without source
                continue
                
            if source not in stats:
                stats[source] = {"wins": 0, "total": 0, "scores": []}
            
            stats[source]["total"] += 1
            
            # Get score for this version
            try:
                score_row = session.execute(
                    sa.select(JudgeScore).where(JudgeScore.prompt_version_id == version.id)
                ).scalar_one_or_none()
                
                if score_row:
                    total_score = (score_row.clarity + score_row.specificity + 
                                  score_row.actionability + score_row.structure + 
                                  score_row.context_use)
                    stats[source]["scores"].append(total_score)
                    
                    # Check if this is the best version for its prompt
                    best = session.execute(
                        sa.select(BestHead).where(BestHead.prompt_id == version.prompt_id)
                    ).scalar_one_or_none()
                    
                    if best and best.prompt_version_id == version.id:
                        stats[source]["wins"] += 1
            except Exception as e:
                # Skip this version if score query fails
                continue
        
        # Calculate win rates and averages
        for source in stats:
            total = stats[source]["total"]
            wins = stats[source]["wins"]
            scores = stats[source]["scores"]
            
            stats[source]["win_rate"] = wins / total if total > 0 else 0.0
            stats[source]["avg_score"] = sum(scores) / len(scores) if scores else 0.0
            del stats[source]["scores"]  # Remove raw scores from output
        
        return stats
    except Exception as e:
        # Return empty dict on any error
        return {}

def get_temporal_statistics(session: Session, prompt_id: uuid.UUID) -> dict:
    """
    Calculate temporal statistics for a prompt.
    Returns: {
        "trend": "improving" | "degrading" | "stable",
        "avg_score": float,
        "score_range": [min, max],
        "version_count": int,
        "time_span_days": float
    }
    """
    versions = get_prompt_version_chain(session, prompt_id)
    
    if not versions:
        return {"trend": "stable", "avg_score": 0.0, "score_range": [0, 0], 
                "version_count": 0, "time_span_days": 0.0}
    
    # Get scores for all versions
    scores = []
    for version in versions:
        score_row = session.execute(
            sa.select(JudgeScore).where(JudgeScore.prompt_version_id == version.id)
        ).scalar_one_or_none()
        
        if score_row:
            total_score = (score_row.clarity + score_row.specificity + 
                          score_row.actionability + score_row.structure + 
                          score_row.context_use)
            scores.append(total_score)
    
    # Calculate trend
    if len(scores) < 2:
        trend = "stable"
    else:
        first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
        second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
        
        if second_half_avg > first_half_avg * 1.1:
            trend = "improving"
        elif second_half_avg < first_half_avg * 0.9:
            trend = "degrading"
        else:
            trend = "stable"
    
    # Calculate time span
    time_span = (versions[-1].created_at - versions[0].created_at).total_seconds() / 86400
    
    return {
        "trend": trend,
        "avg_score": sum(scores) / len(scores) if scores else 0.0,
        "score_range": [min(scores), max(scores)] if scores else [0, 0],
        "version_count": len(versions),
        "time_span_days": time_span
    }

def get_causal_edges(session: Session, prompt_id: uuid.UUID) -> list[dict]:
    """
    Get causal edges (parent→child transitions with score deltas).
    Returns: [{"from_version_id": UUID, "to_version_id": UUID, 
               "change_type": str, "score_delta": float, "time_delta": str}, ...]
    """
    versions = get_prompt_version_chain(session, prompt_id)
    edges = []
    
    for version in versions:
        if version.parent_version_id is None:
            continue
        
        # Get parent version
        parent = session.execute(
            sa.select(PromptVersion).where(PromptVersion.id == version.parent_version_id)
        ).scalar_one_or_none()
        
        if not parent:
            continue
        
        # Get scores
        version_score_row = session.execute(
            sa.select(JudgeScore).where(JudgeScore.prompt_version_id == version.id)
        ).scalar_one_or_none()
        
        parent_score_row = session.execute(
            sa.select(JudgeScore).where(JudgeScore.prompt_version_id == parent.id)
        ).scalar_one_or_none()
        
        if not version_score_row or not parent_score_row:
            continue
        
        version_total = (version_score_row.clarity + version_score_row.specificity + 
                        version_score_row.actionability + version_score_row.structure + 
                        version_score_row.context_use)
        parent_total = (parent_score_row.clarity + parent_score_row.specificity + 
                       parent_score_row.actionability + parent_score_row.structure + 
                       parent_score_row.context_use)
        
        time_delta = version.created_at - parent.created_at
        
        edges.append({
            "from_version_id": str(parent.id),
            "to_version_id": str(version.id),
            "change_type": version.change_type,
            "score_delta": version_total - parent_total,
            "time_delta": str(time_delta)
        })
    
    return edges

def get_score_trends(session: Session, prompt_id: uuid.UUID) -> list[tuple]:
    """
    Get (timestamp, score) tuples for timeline visualization.
    Returns: [(datetime, float), ...]
    """
    versions = get_prompt_version_chain(session, prompt_id)
    trends = []
    
    for version in versions:
        score_row = session.execute(
            sa.select(JudgeScore).where(JudgeScore.prompt_version_id == version.id)
        ).scalar_one_or_none()
        
        if score_row:
            total_score = (score_row.clarity + score_row.specificity + 
                          score_row.actionability + score_row.structure + 
                          score_row.context_use)
            trends.append((version.created_at, total_score))
    
    return trends

def get_change_type_correlations(session: Session, prompt_id: uuid.UUID) -> dict[str, float]:
    """
    Calculate average score delta per change_type.
    Returns: {"structure": 2.5, "wording": -0.3, "length": 1.2, "other": 0.0}
    """
    edges = get_causal_edges(session, prompt_id)
    
    correlations = {"structure": [], "wording": [], "length": [], "other": []}
    
    for edge in edges:
        change_type = edge["change_type"]
        score_delta = edge["score_delta"]
        
        if change_type in correlations:
            correlations[change_type].append(score_delta)
    
    # Calculate averages
    return {
        change_type: (sum(deltas) / len(deltas) if deltas else 0.0)
        for change_type, deltas in correlations.items()
    }

# ============================================================================
# USER FEEDBACK CRUD (Added 2025-12-04)
# ============================================================================

def create_feedback_row(
    session: Session,
    request_id: str,
    user_id: str,
    prompt_id: uuid.UUID,
    user_choice: str,
    judge_winner: str,
    agent_winner: str
) -> UserFeedback:
    """Create a new user feedback record"""
    feedback = UserFeedback(
        request_id=request_id,
        user_id=user_id,
        prompt_id=prompt_id,
        user_choice=user_choice,
        judge_winner=judge_winner,
        agent_winner=agent_winner,
        judge_correct=(judge_winner == agent_winner)
    )
    session.add(feedback)
    session.flush()  # Get the ID without committing
    return feedback

def get_feedback_by_request_id(session: Session, request_id: str) -> UserFeedback | None:
    """Get feedback by request_id"""
    return session.execute(
        sa.select(UserFeedback).where(UserFeedback.request_id == request_id)
    ).scalar_one_or_none()

def get_feedback_by_user(session: Session, user_id: str, limit: int = 100) -> list[UserFeedback]:
    """Get all feedback for a specific user"""
    return session.execute(
        sa.select(UserFeedback)
        .where(UserFeedback.user_id == user_id)
        .order_by(UserFeedback.created_at.desc())
        .limit(limit)
    ).scalars().all()

def get_agent_effectiveness_from_feedback(session: Session, user_id: str | None = None) -> dict:
    """
    Calculate agent effectiveness from user feedback.
    
    Returns dict with agent names as keys and effectiveness metrics as values.
    """
    query = sa.select(UserFeedback)
    if user_id:
        query = query.where(UserFeedback.user_id == user_id)
    
    feedback_records = session.execute(query).scalars().all()
    
    if not feedback_records:
        return {}
    
    # Count wins per agent
    agent_wins = {}
    total_feedback = len(feedback_records)
    
    for feedback in feedback_records:
        agent = feedback.agent_winner
        if agent not in agent_wins:
            agent_wins[agent] = 0
        agent_wins[agent] += 1
    
    # Calculate effectiveness (win rate)
    effectiveness = {}
    for agent, wins in agent_wins.items():
        effectiveness[agent] = {
            "wins": wins,
            "total": total_feedback,
            "effectiveness": wins / total_feedback if total_feedback > 0 else 0.0
        }
    
    return effectiveness