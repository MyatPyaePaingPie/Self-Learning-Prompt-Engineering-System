from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, JSON
import uuid, datetime as dt
from sqlalchemy import String, Integer, Text, DateTime, Float
from datetime import datetime

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

class PromptHistory(Base):
    __tablename__ = "prompt_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    original_prompt: Mapped[str] = mapped_column(Text)
    improved_prompt: Mapped[str] = mapped_column(Text)

    clarity: Mapped[int] = mapped_column(Integer, default=0)
    specificity: Mapped[int] = mapped_column(Integer, default=0)
    actionability: Mapped[int] = mapped_column(Integer, default=0)
    structure: Mapped[int] = mapped_column(Integer, default=0)
    context_use: Mapped[int] = mapped_column(Integer, default=0)
    total_score: Mapped[int] = mapped_column(Integer, default=0)

    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)

    model_version: Mapped[str] = mapped_column(String(50), default="gpt")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
