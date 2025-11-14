import os
import time
import logging
from pydantic import BaseModel
from groq import Groq
from datetime import datetime
from packages.core.token_tracker import TokenTracker, TokenUsage
from packages.db.session import get_db
from packages.db.crud import create_history_record
from packages.core.judge import score_prompt
from packages.core.token_tracker import TokenTracker


logger = logging.getLogger(__name__)
tracker = TokenTracker()

TEMPLATE_V1 = """You are a senior {domain} expert.
Task: {task}
Deliverables:
- Clear, step-by-step plan
- Examples and edge-cases
- Final {artifact} ready to use
Constraints: {constraints}
If information is missing, list precise clarifying questions first, then proceed with best assumptions."""

def detect_domain(original: str) -> str:
    if "code" in original.lower() or "python" in original.lower():
        return "Python developer"
    if "marketing" in original.lower():
        return "marketing strategist"
    return "subject-matter"

def synth_explanation(original: str, improved: str) -> dict:
    return {
        "bullets": [
            "Added explicit role for the assistant",
            "Specified deliverables and output artifact",
            "Inserted constraint section",
            "Required clarifying questions before solution"
        ],
        "diffs": [{"from": original, "to": improved}]
    }

class ImprovedOut(BaseModel):
    text: str
    explanation: dict
    source: str = "engine/v1"

def fallback_to_template(original: str) -> ImprovedOut:
    """Fallback to template-based improvement when LLM is unavailable."""
    domain = detect_domain(original)
    task = original.strip()
    artifact = "code" if "code" in original.lower() else "answer"
    improved = TEMPLATE_V1.format(
        domain=domain,
        task=task,
        constraints="[time, tools, data sources]",
        artifact=artifact
    )
    return ImprovedOut(
        text=improved,
        explanation=synth_explanation(original, improved),
        source="template/fallback"
    )

def generate_llm_output(prompt: str, max_retries: int = 3) -> tuple[str, TokenUsage]:
    """
    Generate LLM output for a given prompt using Groq's API and track token usage.
    
    Args:
        prompt: The prompt to send to the LLM
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        Tuple of (output_text, token_usage)
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    for attempt in range(max_retries):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=2048,
            )
            
            output = chat_completion.choices[0].message.content.strip()
            
            # Track usage
            usage = tracker.track_llm_call(prompt, output, "llama-3.3-70b-versatile")
            
            return output, usage
            
        except Exception as e:
            error_msg = str(e)
            wait_time = 2 ** attempt if attempt < max_retries - 1 else 0
            
            if attempt == max_retries - 1:
                logger.error(f"All {max_retries} attempts failed for LLM output generation.", exc_info=True)
                # Return error with zero tokens
                return "[Error: Unable to generate response. Please try again.]", TokenUsage(
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    model="llama-3.3-70b-versatile",
                    timestamp=datetime.now(),
                    cost_usd=0.0
                )
            
            if wait_time > 0:
                logger.info(f"Retrying LLM output generation in {wait_time} seconds...")
                time.sleep(wait_time)

def improve_prompt(original: str, strategy: str = "v1", max_retries: int = 3) -> tuple[ImprovedOut, TokenUsage]:
    """
    Improve a prompt using Groq's LLM API with retry logic and error handling, and track token usage.
    
    Args:
        original: The original prompt to improve
        strategy: Strategy to use (v1, v2, ensemble)
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        Tuple of (ImprovedOut, token_usage)
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    system_prompt = """You are an expert prompt engineer. Your job is to improve prompts by making them:
- More clear and specific
- More actionable with concrete deliverables
- Better structured with explicit constraints
- More likely to produce high-quality responses

When improving a prompt:
1. Add explicit role/persona for the AI
2. Specify expected output format
3. Include relevant constraints
4. Add examples if helpful
5. Request clarifying questions if context is missing

Return ONLY the improved prompt, nothing else."""

    # Retry loop with exponential backoff
    for attempt in range(max_retries):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Improve this prompt:\n\n{original}"
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1024,
            )
            
            improved = chat_completion.choices[0].message.content.strip()
            explanation = synth_explanation(original, improved)
            
            # Track usage
            usage = tracker.track_llm_call(
                system_prompt + "\n\nImprove this prompt:\n\n" + original,
                improved,
                "llama-3.3-70b-versatile"
            )
            
            return ImprovedOut(
                text=improved,
                explanation=explanation,
                source="groq/llama-3.3-70b"
            ), usage
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Determine wait time based on error type
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                # Rate limit - wait longer
                wait_time = 30 if attempt < max_retries - 1 else 0
                logger.warning(
                    f"Rate limit hit (attempt {attempt + 1}/{max_retries})",
                    extra={"error": error_msg}
                )
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                # Connection error - exponential backoff
                wait_time = 2 ** attempt if attempt < max_retries - 1 else 0
                logger.warning(
                    f"Connection error (attempt {attempt + 1}/{max_retries}): {error_msg}",
                    extra={"error_type": error_type}
                )
            else:
                # Other errors - standard backoff
                wait_time = 2 ** attempt if attempt < max_retries - 1 else 0
                logger.warning(
                    f"Groq API error (attempt {attempt + 1}/{max_retries}): {error_type}: {error_msg}",
                    extra={"prompt_length": len(original), "attempt": attempt}
                )
            
            # If this was the last attempt, fall back to template
            if attempt == max_retries - 1:
                logger.error(
                    f"All {max_retries} attempts failed. Falling back to template.",
                    exc_info=True
                )
                # Return fallback with zero tokens
                return fallback_to_template(original), TokenUsage(
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    model="template/fallback",
                    timestamp=datetime.now(),
                    cost_usd=0.0
                )
            
            # Wait before retry
            if wait_time > 0:
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)


def improve_prompt_and_store(prompt: str):
    improved = improve_prompt(prompt)

    # 🔵 ADDED — compute scores
    scores = score_prompt(improved)

    # 🔵 ADDED — compute token usage
    tracker = TokenTracker()
    token_usage = tracker.get_usage()

    # 🔵 ADDED — history payload
    record_data = {
        "original_prompt": prompt,
        "improved_prompt": improved,
        "clarity": scores.clarity,
        "specificity": scores.specificity,
        "actionability": scores.actionability,
        "structure": scores.structure,
        "context_use": scores.context_use,
        "total_score": scores.total,
        "input_tokens": token_usage.input_tokens,
        "output_tokens": token_usage.output_tokens,
        "model_version": "gpt-4.1-mini"
    }

    # 🔵 ADDED — save to DB
    db = next(get_db())
    create_history_record(db, record_data)

    return improved
