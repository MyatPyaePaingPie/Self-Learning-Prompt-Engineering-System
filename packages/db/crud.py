# crud.py
"""
crud.py
Database helper functions for creating and retrieving prompt logs.
"""


import sqlalchemy as sa
from sqlalchemy.orm import Session
from .models import Prompt, PromptVersion, JudgeScore, BestHead
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