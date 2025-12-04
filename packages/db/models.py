from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, JSON
import uuid, datetime as dt

class Base(DeclarativeBase): pass

class Prompt(Base):
    __tablename__ = "prompts"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str | None]
    original_text: Mapped[str]
    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.utcnow)

class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    prompt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"))
    version_no: Mapped[int]
    text: Mapped[str]
    explanation: Mapped[dict] = mapped_column(JSON)
    source: Mapped[str]
    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.utcnow)
    # Temporal fields for Week 12
    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("prompt_versions.id", ondelete="SET NULL"), default=None)
    change_type: Mapped[str] = mapped_column(default="other")  # "structure", "wording", "length", "other"
    change_magnitude: Mapped[float] = mapped_column(default=0.0)  # 0-1 normalized edit distance

class JudgeScore(Base):
    __tablename__ = "judge_scores"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    prompt_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prompt_versions.id", ondelete="CASCADE"))
    clarity: Mapped[float]
    specificity: Mapped[float]
    actionability: Mapped[float]
    structure: Mapped[float]
    context_use: Mapped[float]
    feedback: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.utcnow)

class BestHead(Base):
    __tablename__ = "best_heads"
    prompt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"), primary_key=True)
    prompt_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prompt_versions.id", ondelete="CASCADE"))
    score: Mapped[float]
    updated_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.utcnow)

class SecurityInput(Base):
    __tablename__ = "security_inputs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str | None]
    input_text: Mapped[str]
    risk_score: Mapped[float]  # 0-100
    label: Mapped[str]  # "safe", "low-risk", "medium-risk", "high-risk", "blocked"
    is_blocked: Mapped[bool]
    analysis_metadata: Mapped[dict | None] = mapped_column(JSON, default=None)  # Additional analysis details
    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.utcnow)