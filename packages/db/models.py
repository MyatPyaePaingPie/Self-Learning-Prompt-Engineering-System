from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, JSON, String
import uuid, datetime as dt

class Base(DeclarativeBase): pass

class User(Base):
    """User model for authentication with username/password"""
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[str] = mapped_column(String, default=lambda: dt.datetime.utcnow().isoformat())

class Prompt(Base):
    __tablename__ = "prompts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    original_text: Mapped[str]
    created_at: Mapped[str] = mapped_column(String, default=lambda: dt.datetime.utcnow().isoformat())

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