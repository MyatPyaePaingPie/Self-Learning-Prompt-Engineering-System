import sqlalchemy as sa
from sqlalchemy.orm import Session
from .models import Prompt, PromptVersion, JudgeScore, BestHead, SecurityInput
from packages.core.judge import Scorecard
import uuid

def create_prompt_row(session: Session, user_id: str | None, original_text: str) -> Prompt:
    """Create a new prompt record"""
    prompt = Prompt(user_id=user_id, original_text=original_text)
    session.add(prompt)
    session.flush()  # Get the ID without committing
    return prompt

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