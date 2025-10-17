import os
from pydantic import BaseModel
from groq import Groq

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

def improve_prompt(original: str, strategy: str = "v1") -> ImprovedOut:
    """
    Improve a prompt using Groq's LLM API.
    
    Args:
        original: The original prompt to improve
        strategy: Strategy to use (v1, v2, ensemble)
    
    Returns:
        ImprovedOut with improved text, explanation, and source
    """
    # Initialize Groq client
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # System prompt for improvement
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

    # Call Groq API
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
            model="llama-3.3-70b-versatile",  # Fast and high-quality
            temperature=0.7,
            max_tokens=1024,
        )
        
        improved = chat_completion.choices[0].message.content.strip()
        
        # Generate explanation
        explanation = synth_explanation(original, improved)
        
        return ImprovedOut(
            text=improved, 
            explanation=explanation,
            source="groq/llama-3.3-70b"
        )
        
    except Exception as e:
        # Fallback to template if API fails
        print(f"⚠️ Groq API error: {e}. Falling back to template.")
        domain = detect_domain(original)
        task = original.strip()
        artifact = "answer"
        if "code" in original.lower(): 
            artifact = "code"
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