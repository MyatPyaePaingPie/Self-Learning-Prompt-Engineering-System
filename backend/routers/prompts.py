from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import logging

# Database imports
from database import get_db, User
from packages.db.session import get_session
from packages.db.models import Prompt, PromptVersion, JudgeScore
from packages.db.crud import (
    create_prompt_row,
    create_version_row,
    create_judge_score_row,
    create_token_usage_row,
    create_feedback_row,
    create_security_input_row,
    get_prompt_by_request_id,
    get_agent_effectiveness_from_feedback,
    get_token_usage_by_user,
    maybe_update_best_head
)

# Crypto and auth
from crypto import encrypt_sensitive_data
from slowapi import Limiter
from slowapi.util import get_remote_address

# Agent modules
from packages.core.agent_registry import AgentRegistry
from packages.core.agent_coordinator import AgentCoordinator
from packages.core.judge import Scorecard
from packages.core.token_tracker import TokenTracker, TokenUsage
from packages.core.security_analyzer import SecurityAnalyzer, SecurityAssessment
from storage.file_storage import FileStorage

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# Router definition (no prefix - endpoints specify full paths)
router = APIRouter(tags=["prompts"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PromptInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class PromptResponse(BaseModel):
    id: str
    original_text: str
    enhanced_text: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: str
    user_id: int

class PromptEnhanceRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    enhancement_type: str = Field(default="general", pattern="^(general|creative|technical|persuasive|clear)$")
    context: Optional[str] = Field(None, max_length=1000)

class FeedbackRequest(BaseModel):
    """Request model for user feedback on multi-agent results (Darwinian Evolution - Phase 1)"""
    request_id: str = Field(..., min_length=1, max_length=100, description="Unique request ID")
    user_choice: str = Field(..., pattern="^(original|single|multi)$", description="User's choice")
    judge_winner: str = Field(..., description="Agent selected by judge")
    agent_winner: str = Field(..., description="Agent to credit based on user choice")

# ============================================================================
# SINGLETON GETTERS
# ============================================================================

# Singleton coordinator (uses registry internally)
_multi_agent_coordinator = None
# Singleton file storage (Week 11 - Phase 2)
_file_storage = None

def get_multi_agent_coordinator() -> AgentCoordinator:
    """Get coordinator with default agents (syntax, structure, domain)"""
    global _multi_agent_coordinator
    
    if not _multi_agent_coordinator:
        _multi_agent_coordinator = AgentCoordinator()  # Uses default agents from registry
    
    return _multi_agent_coordinator

def get_file_storage() -> FileStorage:
    """Get file storage singleton"""
    global _file_storage
    
    if not _file_storage:
        # Initialize with storage directory
        import os
        storage_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage")
        _file_storage = FileStorage(base_dir=storage_dir)
    
    return _file_storage

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def apply_prompt_enhancement(text: str, enhancement_type: str, context: Optional[str] = None) -> str:
    """Apply prompt enhancement using structured template approach."""
    
    TEMPLATE_V1 = """You are a senior {domain} expert.
Task: {task}
Deliverables:
- Clear, step-by-step plan
- Examples and edge-cases
- Final {artifact} ready to use
Constraints: {constraints}
If information is missing, list precise clarifying questions first, then proceed with best assumptions."""

    # Analyze the input text to extract components
    domain, task, artifact, constraints = analyze_prompt_components(text, enhancement_type, context)
    
    # Apply the template
    enhanced_prompt = TEMPLATE_V1.format(
        domain=domain,
        task=task,
        artifact=artifact,
        constraints=constraints
    )
    
    return enhanced_prompt

def analyze_prompt_components(text: str, enhancement_type: str, context: Optional[str] = None) -> tuple:
    """Analyze user input to extract domain, task, artifact, and constraints."""
    
    # Domain mapping based on enhancement type and content analysis
    domain_mapping = {
        "technical": "Software Engineering",
        "creative": "Creative Writing",
        "persuasive": "Marketing & Communications",
        "clear": "Technical Communication",
        "general": "Problem Solving"
    }
    
    # Extract or infer domain
    domain = domain_mapping.get(enhancement_type, "Subject Matter")
    
    # If context provides domain info, use it
    if context:
        context_lower = context.lower()
        if any(word in context_lower for word in ["software", "programming", "code", "development"]):
            domain = "Software Engineering"
        elif any(word in context_lower for word in ["writing", "story", "creative", "content"]):
            domain = "Creative Writing"
        elif any(word in context_lower for word in ["marketing", "sales", "business"]):
            domain = "Marketing & Strategy"
        elif any(word in context_lower for word in ["research", "analysis", "academic"]):
            domain = "Research & Analysis"
    
    # Clean and structure the task
    task = text.strip()
    if not task.endswith(('.', '!', '?')):
        task += "."
    
    # Determine artifact type based on content
    text_lower = text.lower()
    if any(word in text_lower for word in ["write", "create", "generate", "compose"]):
        if any(word in text_lower for word in ["code", "script", "program", "function"]):
            artifact = "code implementation"
        elif any(word in text_lower for word in ["story", "article", "content", "copy"]):
            artifact = "written content"
        elif any(word in text_lower for word in ["plan", "strategy", "proposal"]):
            artifact = "strategic plan"
        else:
            artifact = "deliverable"
    elif any(word in text_lower for word in ["analyze", "research", "investigate"]):
        artifact = "analysis report"
    elif any(word in text_lower for word in ["design", "build", "develop"]):
        artifact = "design specification"
    else:
        artifact = "solution"
    
    # Set appropriate constraints based on enhancement type
    constraint_mapping = {
        "technical": "Follow best practices, include error handling, ensure scalability",
        "creative": "Maintain originality, engage target audience, stay within brand guidelines",
        "persuasive": "Use evidence-based arguments, address counterpoints, include clear call-to-action",
        "clear": "Use simple language, logical structure, avoid jargon unless necessary",
        "general": "Be comprehensive yet concise, consider multiple perspectives"
    }
    
    constraints = constraint_mapping.get(enhancement_type, "Be thorough and practical")
    
    # Add context-specific constraints
    if context:
        constraints += f". Additional context: {context}"
    
    return domain, task, artifact, constraints

# ============================================================================
# AUTHENTICATION DEPENDENCY
# ============================================================================

# Import get_current_user from auth router
from routers.auth import get_current_user

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/prompts/enhance")
@limiter.limit("10/minute")
async def enhance_prompt(
    request: Request,
    prompt_data: PromptEnhanceRequest,
    current_user: User = Depends(get_current_user)
):
    """Enhance a text prompt using AI optimization techniques."""
    try:
        # SECURITY ANALYSIS (Phase 2 - 2025-12-05)
        analyzer = SecurityAnalyzer()
        security_assessment = analyzer.analyze(prompt_data.text)
        
        # Save security input to database (PT:2 Database-First)
        with get_session() as session:
            create_security_input_row(
                session=session,
                user_id=str(current_user.id),
                input_text=prompt_data.text,
                risk_score=security_assessment.risk_score,
                label=security_assessment.label,
                is_blocked=security_assessment.is_blocked,
                analysis_metadata=security_assessment.analysis_metadata
            )
            session.commit()
        
        # Block high-risk prompts
        if security_assessment.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Security Risk Detected",
                    "message": f"This prompt has been flagged as {security_assessment.label} (risk score: {security_assessment.risk_score:.1f}).",
                    "risk_score": security_assessment.risk_score,
                    "label": security_assessment.label
                }
            )
        
        # Encrypt the original prompt for storage
        encrypted_text = encrypt_sensitive_data(prompt_data.text)
        
        # Apply prompt enhancement logic based on type
        enhanced_text = apply_prompt_enhancement(
            prompt_data.text,
            prompt_data.enhancement_type,
            prompt_data.context
        )
        
        # Create response with encrypted data
        prompt_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "data": {
                "id": prompt_id,
                "original_text": prompt_data.text,
                "enhanced_text": enhanced_text,
                "enhancement_type": prompt_data.enhancement_type,
                "created_at": datetime.utcnow().isoformat(),
                "user_id": current_user.id
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prompt enhancement failed"
        )

@router.get("/api/prompts")
async def get_user_prompts(
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """Get authenticated user's prompts."""
    try:
        with get_session() as session:
            prompts = session.query(Prompt).filter(
                Prompt.user_id == str(current_user.id)
            ).order_by(Prompt.created_at.desc()).limit(limit).all()
            
            return {
                "success": True,
                "data": [
                    {
                        "id": str(p.id),
                        "original_text": p.original_text,
                        "created_at": p.created_at.isoformat(),
                        "user_id": p.user_id
                    }
                    for p in prompts
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/tokens")
async def get_user_token_history(
    current_user: User = Depends(get_current_user),
    limit: int = 100
):
    """
    Get authenticated user's token usage history (Database-First Pattern 2025-12-04).
    Returns all token records for the user across all prompts and versions.
    """
    try:
        with get_session() as session:
            token_records = get_token_usage_by_user(session, str(current_user.id), limit=limit)
            
            return {
                "success": True,
                "data": [
                    {
                        "id": str(record.id),
                        "prompt_version_id": str(record.prompt_version_id),
                        "prompt_tokens": record.prompt_tokens,
                        "completion_tokens": record.completion_tokens,
                        "total_tokens": record.total_tokens,
                        "model": record.model,
                        "cost_usd": record.cost_usd,
                        "created_at": record.created_at.isoformat()
                    }
                    for record in token_records
                ],
                "total_records": len(token_records),
                "total_tokens": sum(r.total_tokens for r in token_records),
                "total_cost": sum(r.cost_usd for r in token_records)
            }
    except Exception as e:
        logger.error(f"Failed to get token history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get token history: {str(e)}")

@router.post("/prompts/save")
@limiter.limit("20/minute")
async def save_prompt(
    request: Request,
    prompt_data: PromptInput,
    current_user: User = Depends(get_current_user)
):
    """Save a prompt to user's collection."""
    try:
        # SECURITY ANALYSIS (Phase 2 - 2025-12-05)
        analyzer = SecurityAnalyzer()
        security_assessment = analyzer.analyze(prompt_data.text)
        
        # Save security input to database (PT:2 Database-First)
        with get_session() as session:
            create_security_input_row(
                session=session,
                user_id=str(current_user.id),
                input_text=prompt_data.text,
                risk_score=security_assessment.risk_score,
                label=security_assessment.label,
                is_blocked=security_assessment.is_blocked,
                analysis_metadata=security_assessment.analysis_metadata
            )
            session.commit()
        
        # Block high-risk prompts
        if security_assessment.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Security Risk Detected",
                    "message": f"Cannot save high-risk prompt (risk score: {security_assessment.risk_score:.1f}).",
                    "risk_score": security_assessment.risk_score,
                    "label": security_assessment.label
                }
            )
        
        # Encrypt sensitive prompt data
        encrypted_text = encrypt_sensitive_data(prompt_data.text)
        
        prompt_id = str(uuid.uuid4())
        
        # In a real implementation, this would be saved to database
        return {
            "success": True,
            "data": {
                "id": prompt_id,
                "text": prompt_data.text,
                "category": prompt_data.category,
                "tags": prompt_data.tags or [],
                "created_at": datetime.utcnow().isoformat(),
                "user_id": current_user.id
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save prompt"
        )

@router.get("/prompts/my-prompts")
async def get_user_prompts_legacy(current_user: User = Depends(get_current_user)):
    """Get all prompts belonging to the current user."""
    # In a real implementation, this would query the database
    return {
        "success": True,
        "data": {
            "prompts": [],
            "total": 0,
            "user_id": current_user.id
        }
    }

@router.post("/prompts/multi-agent-enhance")
@limiter.limit("5/minute")  # Lower limit (3 LLM calls per request)
async def multi_agent_enhance(
    request: Request,
    prompt_data: PromptEnhanceRequest,
    current_user: User = Depends(get_current_user)
):
    """Enhance prompt using multi-agent collaboration (Week 11)."""
    try:
        # SECURITY ANALYSIS (Phase 2 - 2025-12-05)
        # Analyze prompt for security risks BEFORE LLM processing
        analyzer = SecurityAnalyzer()  # Uses default keywords and threshold=80
        security_assessment = analyzer.analyze(prompt_data.text)
        
        # Save security input to database (PT:2 Database-First)
        with get_session() as session:
            create_security_input_row(
                session=session,
                user_id=str(current_user.id),
                input_text=prompt_data.text,
                risk_score=security_assessment.risk_score,
                label=security_assessment.label,
                is_blocked=security_assessment.is_blocked,
                analysis_metadata=security_assessment.analysis_metadata
            )
            session.commit()
        
        # Block high-risk prompts (risk_score >= 80)
        if security_assessment.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Security Risk Detected",
                    "message": f"This prompt has been flagged as {security_assessment.label} (risk score: {security_assessment.risk_score:.1f}).",
                    "risk_score": security_assessment.risk_score,
                    "label": security_assessment.label,
                    "matched_keywords": security_assessment.analysis_metadata.get("matched_keywords", {})
                }
            )
        
        # Get coordinator (uses registry internally)
        coordinator = get_multi_agent_coordinator()
        decision = await coordinator.coordinate(prompt_data.text)
        
        # Generate request ID for tracking (BEFORE database save)
        request_id = str(uuid.uuid4())
        
        # SAVE PROMPT TO DATABASE WITH USER_ID AND REQUEST_ID
        with get_session() as session:
            # Create prompt record with user_id and request_id
            prompt = create_prompt_row(
                session=session,
                user_id=str(current_user.id),  # USER-SPECIFIC
                original_text=prompt_data.text,
                request_id=request_id  # For feedback linkage
            )
            
            # Create version for original prompt
            original_version = create_version_row(
                session=session,
                prompt_id=prompt.id,
                version_no=1,
                text=prompt_data.text,
                explanation={"source": "user_input", "enhancement_type": prompt_data.enhancement_type},
                source="user_input"
            )
            
            # SAVE TOKEN USAGE FOR ORIGINAL PROMPT (Database-First Pattern 2025-12-04)
            # Track original prompt tokens (estimate based on text)
            tracker = TokenTracker()
            original_tokens = tracker.count_tokens(prompt_data.text)
            original_token_usage = TokenUsage(
                prompt_tokens=original_tokens,
                completion_tokens=0,  # No completion for original (just the prompt itself)
                total_tokens=original_tokens,
                model="user_input",  # Source is user input
                timestamp=datetime.now(),
                cost_usd=0.0  # No cost for user input
            )
            create_token_usage_row(session, original_version.id, original_token_usage)
            
            # SAVE INDIVIDUAL AGENT VERSIONS (Fix for Agent Effectiveness Dashboard)
            # Create version for EACH agent (syntax, structure, domain) so dashboard can track effectiveness
            version_no = 2
            winning_version_id = None
            
            for agent_result in decision.agent_results:
                agent_version = create_version_row(
                    session=session,
                    prompt_id=prompt.id,
                    version_no=version_no,
                    text=agent_result.suggestions.improved_prompt,
                    explanation={
                        "source": agent_result.agent_name,
                        "analysis": {
                            "score": agent_result.analysis.score,
                            "strengths": agent_result.analysis.strengths,
                            "weaknesses": agent_result.analysis.weaknesses
                        },
                        "confidence": agent_result.suggestions.confidence,
                        "suggestions": agent_result.suggestions.suggestions
                    },
                    source=agent_result.agent_name  # ← Key: "syntax"/"structure"/"domain"
                )
                
                # Save token usage for this agent's execution
                if agent_result.token_usage:
                    agent_token_usage = TokenUsage(
                        prompt_tokens=agent_result.token_usage.get("prompt_tokens", 0),
                        completion_tokens=agent_result.token_usage.get("completion_tokens", 0),
                        total_tokens=agent_result.token_usage.get("total_tokens", 0),
                        model=agent_result.token_usage.get("model", agent_result.agent_name),
                        timestamp=datetime.now(),
                        cost_usd=agent_result.token_usage.get("cost_usd", 0.0)
                    )
                    create_token_usage_row(session, agent_version.id, agent_token_usage)
                
                # Create judge score from agent's analysis (map 0-10 score to 0-20 per category)
                # Agent score is 0-10, judge expects 5 categories each 0-20
                score_per_category = (agent_result.analysis.score / 10.0) * 20.0
                agent_scorecard = Scorecard(
                    clarity=score_per_category,
                    specificity=score_per_category,
                    actionability=score_per_category,
                    structure=score_per_category,
                    context_use=score_per_category,
                    feedback={"agent": agent_result.agent_name, "confidence": agent_result.suggestions.confidence},
                    total=agent_result.analysis.score * 10.0  # 0-10 → 0-100
                )
                create_judge_score_row(session, agent_version.id, agent_scorecard)
                
                # Track winning version for best_head marking
                if agent_result.agent_name == decision.selected_agent:
                    winning_version_id = agent_version.id
                
                version_no += 1
            
            # Mark winning agent's version as best_head
            if winning_version_id:
                winning_score = next(
                    r.analysis.score * 10.0 for r in decision.agent_results 
                    if r.agent_name == decision.selected_agent
                )
                maybe_update_best_head(session, prompt.id, winning_version_id, winning_score)
            
            session.commit()
            prompt_id = str(prompt.id)
        
        # Add model info to response
        agent_results_with_models = []
        for result in decision.agent_results:
            result_dict = result.dict()
            
            # Add model info from registry
            metadata = AgentRegistry.get_metadata(result.agent_name)
            if metadata:
                result_dict["model_used"] = {
                    "model_id": metadata.model_config.model_id,
                    "display_name": metadata.model_config.display_name,
                    "speed": metadata.model_config.speed.value,
                    "cost": metadata.model_config.cost.value
                }
            agent_results_with_models.append(result_dict)
        
        # Database-First Pattern (2025-12-04):
        # Prompts now saved to PostgreSQL with user_id
        # CSV export is manual via POST /api/storage/export-multi-agent
        
        return {
            "success": True,
            "data": {
                "request_id": request_id,
                "prompt_id": prompt_id,  # NEW: Database ID
                "original_text": prompt_data.text,
                "enhanced_text": decision.final_prompt,
                "selected_agent": decision.selected_agent,
                "decision_rationale": decision.decision_rationale,
                "agent_results": agent_results_with_models,
                "vote_breakdown": decision.vote_breakdown,
                "token_usage": decision.token_usage,  # Per-agent token usage
                "total_cost_usd": decision.total_cost_usd,  # Total cost across all agents
                "total_tokens": decision.total_tokens,  # Total tokens across all agents
                "created_at": datetime.utcnow().isoformat(),
                "user_id": current_user.id
            }
        }
    except Exception as e:
        logger.error(f"Multi-agent enhancement failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-agent enhancement failed: {str(e)}"
        )

@router.post("/prompts/feedback")
@limiter.limit("20/minute")  # Higher limit for feedback (lightweight operation)
async def record_user_feedback(
    request: Request,
    feedback: FeedbackRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Record user feedback on multi-agent results (Darwinian Evolution - Phase 1).
    
    Database-First Pattern (2025-12-04):
    - Saves feedback to PostgreSQL (not CSV)
    - Links feedback to prompt via request_id
    - User-specific feedback tracking
    
    This endpoint enables the system to learn from user preferences by tracking
    which enhancement method (original, single-agent, or multi-agent) the user
    found most effective. This data is used to:
    - Calculate agent effectiveness over time
    - Adjust agent weights in future decisions (Phase 2)
    - Improve system performance through evolutionary learning
    """
    try:
        # Validate inputs
        if feedback.user_choice not in ["original", "single", "multi"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_choice. Must be 'original', 'single', or 'multi'"
            )
        
        # Database-First Pattern: Save to PostgreSQL (not CSV)
        with get_session() as session:
            # Find prompt by request_id
            prompt = get_prompt_by_request_id(session, feedback.request_id)
            
            if not prompt:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Request ID not found: {feedback.request_id}"
                )
            
            # Verify prompt belongs to current user (security)
            if prompt.user_id != str(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot submit feedback for another user's prompt"
                )
            
            # Create feedback record in database
            feedback_record = create_feedback_row(
                session=session,
                request_id=feedback.request_id,
                user_id=str(current_user.id),
                prompt_id=prompt.id,
                user_choice=feedback.user_choice,
                judge_winner=feedback.judge_winner,
                agent_winner=feedback.agent_winner
            )
            
            session.commit()
        
        return {
            "success": True,
            "message": "Feedback recorded successfully",
            "data": {
                "request_id": feedback.request_id,
                "user_choice": feedback.user_choice,
                "agent_winner": feedback.agent_winner,
                "judge_correct": feedback.judge_winner == feedback.agent_winner
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record feedback: {str(e)}"
        )

@router.get("/prompts/available-agents")
async def get_available_agents(current_user: User = Depends(get_current_user)):
    """Get list of available agents and their model configurations."""
    try:
        agents = []
        for agent_name in AgentRegistry.get_all_agents():
            metadata = AgentRegistry.get_metadata(agent_name)
            if metadata:
                agents.append({
                    "name": agent_name,
                    "display_name": metadata.display_name,
                    "description": metadata.description,
                    "focus_areas": metadata.focus_areas,
                    "model": {
                        "model_id": metadata.model_config.model_id,
                        "display_name": metadata.model_config.display_name,
                        "speed": metadata.model_config.speed.value,
                        "cost": metadata.model_config.cost.value,
                        "use_case": metadata.model_config.use_case
                    }
                })
        
        return {
            "success": True,
            "data": {"agents": agents}
        }
    except Exception as e:
        logger.error(f"Failed to get available agents: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available agents"
        )

@router.get("/prompts/agent-effectiveness")
async def get_agent_effectiveness(current_user: User = Depends(get_current_user)):
    """
    Get agent effectiveness statistics (Week 11 - Phase 2).
    
    Database-First Pattern (2025-12-04):
    - Reads from user_feedback table in PostgreSQL
    - No longer uses CSV files
    - User-specific data only
    """
    try:
        with get_session() as session:
            effectiveness = get_agent_effectiveness_from_feedback(
                session=session,
                user_id=str(current_user.id)
            )
        
        return {
            "success": True,
            "data": effectiveness
        }
    except Exception as e:
        logger.error(f"Failed to get agent effectiveness: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agent effectiveness"
        )
