from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import logging
from packages.core.engine import improve_prompt
from packages.core.judge import judge_prompt
from packages.core.learning import update_rules
from packages.core.learning import update_rules, should_keep_or_revert

from packages.db.session import get_session
from packages.db.crud import *
import sqlalchemy as sa
import sys, os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Week 6: File storage integration for version tracking
from storage.file_storage import FileStorage
storage = FileStorage("storage")

app = FastAPI(title="Self-Learning Prompt Engineering System", version="1.0.0")

class CreatePromptIn(BaseModel):
    userId: str | None = None
    text: str

class ImprovePromptIn(BaseModel):
    strategy: str = "v1"  # "v1" | "v2" | "ensemble"

class JudgePromptIn(BaseModel):
    rubric: dict | None = None

class CreatePromptResponse(BaseModel):
    promptId: str
    versionId: str
    versionNo: int
    improved: str
    explanation: dict
    judge: dict

class PromptDetailsResponse(BaseModel):
    original: dict
    best: dict
    history: list[dict]


@app.get("/")
def read_root():
    return {"message": "Self-Learning Prompt Engineering System API", "version": "1.0.0"}

@app.post("/v1/prompts", response_model=CreatePromptResponse)
def create_prompt(payload: CreatePromptIn):
    """Create a new prompt and automatically generate first improvement"""
    try:
        with get_session() as s:
            # Create prompt and original version (v0)
            prompt = create_prompt_row(s, payload.userId, payload.text)
            v0 = create_version_row(s, prompt.id, 0, payload.text, 
                                  explanation={"bullets":["Original"]}, source="original")
            
            # Generate improvement (v1)
            improved = improve_prompt(payload.text, strategy="v1")
            v1 = create_version_row(s, prompt.id, 1, improved.text, improved.explanation, source=improved.source)
            
            # Judge the improvement
            score = judge_prompt(improved.text, rubric=None)
            judge_data = score.model_dump() if hasattr(score, "model_dump") else score
            create_judge_score_row(s, v1.id, score)
            
            # Update best head if score is good
            maybe_update_best_head(s, prompt.id, v1.id, score.total)
            
            s.commit()
            
            # Week 6: Save versions to file storage with timestamps
            try:
                storage.save_version_to_csv(prompt.id, v0)
                storage.save_version_to_csv(prompt.id, v1)
            except Exception as e:
                # Log warning but don't fail API request - file storage is supplementary
                print(f"⚠️  Warning: Failed to save versions to CSV: {e}")
            
            return CreatePromptResponse(
                promptId=str(prompt.id),
                versionId=str(v1.id),
                versionNo=1,
                improved=improved.text,
                explanation=improved.explanation,
                judge=score.model_dump()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/prompts/{prompt_id}/improve")
def improve_existing_prompt(prompt_id: str, payload: ImprovePromptIn):
    """Generate a new improvement for an existing prompt"""
    try:
        with get_session() as s:
            prompt = get_prompt_by_id(s, uuid.UUID(prompt_id))
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")
            
            # Get current versions to determine next version number
            versions = get_prompt_versions(s, prompt.id)
            next_version = len(versions)
            
            # Generate improvement
            improved = improve_prompt(prompt.original_text, strategy=payload.strategy)
            new_version = create_version_row(s, prompt.id, next_version, 
                                           improved.text, improved.explanation, source=improved.source)
            
            # Judge the improvement
            score = judge_prompt(improved.text, rubric=None)
            judge_data = score.model_dump() if hasattr(score, "model_dump") else score
            create_judge_score_row(s, new_version.id, score)
            
            # Update best head if score is better
            maybe_update_best_head(s, prompt.id, new_version.id, score.total)
            
            s.commit()
            
            # Week 6: Save new version to file storage with timestamp
            try:
                storage.save_version_to_csv(prompt.id, new_version)
            except Exception as e:
                # Log warning but don't fail API request - file storage is supplementary
                print(f"⚠️  Warning: Failed to save version to CSV: {e}")
            
            return {
                "versionId": str(new_version.id),
                "versionNo": next_version,
                "text": improved.text,
                "explanation": improved.explanation,
                "judge": score.model_dump()
            }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid prompt ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/versions/{version_id}/judge")
def judge_version(version_id: str, payload: JudgePromptIn):
    """Re-judge a specific prompt version"""
    try:
        with get_session() as s:
            # Get the version to judge
            version = s.execute(
                sa.select(PromptVersion).where(PromptVersion.id == uuid.UUID(version_id))
            ).scalar_one_or_none()
            
            if not version:
                raise HTTPException(status_code=404, detail="Version not found")
            
            # Judge the version
            score = judge_prompt(version.text, rubric=payload.rubric)
            create_judge_score_row(s, version.id, score)
            
            s.commit()
            
            judge_data = score.model_dump() if hasattr(score, "model_dump") else score

            return {"scorecard": judge_data}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid version ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/prompts/{prompt_id}/learn")
def learn_from_prompt(prompt_id: str):
    """Aggregates all judged versions for a prompt and updates learning state.
    Uses historical version scores to refine prompt-improvement strategies."""

    try:
        with get_session() as s:
            prompt = get_prompt_by_id(s, uuid.UUID(prompt_id))
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")
            
            # Get all versions and their scores for learning
            versions = get_prompt_versions(s, prompt.id)
            history = []
            for version in versions:
                scores = s.execute(
                    sa.select(JudgeScore).where(JudgeScore.prompt_version_id == version.id)
                ).scalars().all()
                for score in scores:
                    history.append({
                        "text": version.text,
                        "scorecard": {
                            "clarity": score.clarity,
                            "specificity": score.specificity,
                            "actionability": score.actionability,
                            "structure": score.structure,
                            "context_use": score.context_use,
                            "total": score.clarity + score.specificity + score.actionability + score.structure + score.context_use,
                            "feedback": score.feedback
                        }
                    })
            
            # Update learning rules
            new_state = update_rules(history)
            
            past_scores = [h["scorecard"]["total"] for h in history[:-1]] if len(history) > 1 else []
            latest_score = history[-1]["scorecard"]["total"] if history else 0
            decision = should_keep_or_revert(past_scores, latest_score)

            if decision == "revert":
                print("🔁 Reverting to previous best version.")
            else:
                print("✅ Keeping latest version as best.")

            return {
                "message": "Learning rules updated",
                "decision": decision,
                "state": new_state.__dict__,
            }
            #return {"message": "Learning rules updated", "state": new_state.__dict__}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid prompt ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/prompts/{prompt_id}", response_model=PromptDetailsResponse)
def get_prompt_details(prompt_id: str):
    """Get prompt details with original, best version, and history"""
    try:
        with get_session() as s:
            prompt = get_prompt_by_id(s, uuid.UUID(prompt_id))
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")
            
            # Get all versions
            versions = get_prompt_versions(s, prompt.id)
            
            # Get best head
            best_head = get_best_head(s, prompt.id)
            
            # Build response
            original = {
                "text": prompt.original_text,
                "created_at": prompt.created_at.isoformat()
            }
            
            best = None
            if best_head:
                best_version = s.execute(
                    sa.select(PromptVersion).where(PromptVersion.id == best_head.prompt_version_id)
                ).scalar_one()
                best = {
                    "versionId": str(best_version.id),
                    "versionNo": best_version.version_no,
                    "text": best_version.text,
                    "explanation": best_version.explanation,
                    "score": best_head.score
                }
            
            # Build history
            history = []
            for version in versions:
                scores = s.execute(
                    sa.select(JudgeScore).where(JudgeScore.prompt_version_id == version.id)
                ).scalars().all()
                
                version_data = {
                    "versionId": str(version.id),
                    "versionNo": version.version_no,
                    "text": version.text,
                    "explanation": version.explanation,
                    "source": version.source,
                    "created_at": version.created_at.isoformat(),
                    "scores": [
                        {
                            "clarity": score.clarity,
                            "specificity": score.specificity,
                            "actionability": score.actionability,
                            "structure": score.structure,
                            "context_use": score.context_use,
                            "total": score.clarity + score.specificity + score.actionability + score.structure + score.context_use,
                            "feedback": score.feedback
                        } for score in scores
                    ]
                }
                history.append(version_data)
            
            return PromptDetailsResponse(
                original=original,
                best=best or {},
                history=history
            )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid prompt ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/metrics")
def get_metrics():
    """Get system metrics for monitoring.
    Currently a placeholder — will be expanded in future weeks"""
    return {
        "message": "Metrics endpoint - TODO: implement actual metrics collection",
        "status": "placeholder"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)