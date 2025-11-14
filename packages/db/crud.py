import sqlalchemy as sa
from sqlalchemy.orm import Session
from .models import User, Prompt, PromptVersion, JudgeScore, BestHead
from packages.core.judge import Scorecard
import uuid

def create_user_row(session: Session, username: str, password_hash: str) -> User:
    """Create a new user record"""
    user = User(username=username, password_hash=password_hash)
    session.add(user)
    session.flush()  # Get the ID without committing
    return user

def get_user_by_username(session: Session, username: str) -> User | None:
    """Get user by username"""
    return session.execute(sa.select(User).where(User.username == username)).scalar_one_or_none()

def get_user_by_id(session: Session, user_id: str) -> User | None:
    """Get user by ID"""
    return session.execute(sa.select(User).where(User.id == user_id)).scalar_one_or_none()

def create_prompt_row(session: Session, user_id: str | None, original_text: str) -> Prompt:
    """Create a new prompt record"""
    prompt = Prompt(user_id=user_id, original_text=original_text)
    session.add(prompt)
    session.flush()  # Get the ID without committing
    return prompt

def create_version_row(session: Session, prompt_id: str, version_no: int,
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

def create_judge_score_row(session: Session, version_id: str, scorecard: Scorecard) -> JudgeScore:
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

def maybe_update_best_head(session: Session, prompt_id: str, version_id: str, score: float):
    """Update best head if score is better than current best"""
    bh = session.execute(sa.select(BestHead).where(BestHead.prompt_id==prompt_id)).scalar_one_or_none()
    if not bh or score >= bh.score:
        if not bh:
            bh = BestHead(prompt_id=prompt_id, prompt_version_id=version_id, score=score)
            session.add(bh)
        else:
            bh.prompt_version_id = version_id
            bh.score = score

def get_prompt_by_id(session: Session, prompt_id: str) -> Prompt | None:
    """Get prompt by ID"""
    return session.execute(sa.select(Prompt).where(Prompt.id==prompt_id)).scalar_one_or_none()

def get_prompt_versions(session: Session, prompt_id: str) -> list[PromptVersion]:
    """Get all versions for a prompt"""
    return session.execute(
        sa.select(PromptVersion)
        .where(PromptVersion.prompt_id==prompt_id)
        .order_by(PromptVersion.version_no)
    ).scalars().all()

def get_best_head(session: Session, prompt_id: str) -> BestHead | None:
    """Get the best version for a prompt"""
    return session.execute(sa.select(BestHead).where(BestHead.prompt_id==prompt_id)).scalar_one_or_none()