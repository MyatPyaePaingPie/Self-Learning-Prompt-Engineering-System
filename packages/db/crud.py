import sqlalchemy as sa
from sqlalchemy.orm import Session
from .models import Prompt, PromptVersion, JudgeScore, BestHead
from packages.core.judge import Scorecard
from packages.db import models
from datetime import datetime
import csv
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


def create_history_record(db: Session, record_data: dict):
    history = models.PromptHistory(**record_data)
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_all_history(db: Session, sort_by="created_at", order="desc"):
    model = models.PromptHistory
    field = getattr(model, sort_by)
    if order == "asc":
        return db.query(model).order_by(field.asc()).all()
    else:
        return db.query(model).order_by(field.desc()).all()


def export_history_to_csv(db: Session, file_path="history_export.csv"):
    history = db.query(models.PromptHistory).all()

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "original_prompt", "improved_prompt",
            "clarity", "specificity", "actionability", "structure", "context_use",
            "total_score",
            "input_tokens", "output_tokens",
            "model_version", "created_at"
        ])

        for h in history:
            writer.writerow([
                h.id, h.original_prompt, h.improved_prompt,
                h.clarity, h.specificity, h.actionability, h.structure, h.context_use,
                h.total_score,
                h.input_tokens, h.output_tokens,
                h.model_version, h.created_at
            ])

    return file_path