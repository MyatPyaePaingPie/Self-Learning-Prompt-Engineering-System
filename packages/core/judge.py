import os
import json
from pydantic import BaseModel
from groq import Groq

RUBRIC = {
    "clarity": {"weight": 1.0, "checks": ["clear role", "purpose stated", "no ambiguity"]},
    "specificity": {"weight": 1.0, "checks": ["concrete outputs", "constraints", "examples/edge-cases"]},
    "actionability": {"weight": 1.0, "checks": ["step-by-step", "inputs named", "decision points"]},
    "structure": {"weight": 1.0, "checks": ["sections", "bullets", "headings/placeholders"]},
    "context_use": {"weight": 1.0, "checks": ["preserves intent", "adds necessary context only"]},
}

class Scorecard(BaseModel):
    clarity: float
    specificity: float
    actionability: float
    structure: float
    context_use: float
    feedback: dict
    total: float  # ✅ numeric field only

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        if not data.get("total"):
            data["total"] = (
                self.clarity
                + self.specificity
                + self.actionability
                + self.structure
                + self.context_use
            )
        return data

def _contains_any(s, keys):
    return any(k.lower() in s.lower() for k in keys)

def _heuristic_judge(text: str) -> Scorecard:
    """Fallback heuristic scoring when LLM is unavailable"""
    scores = {k: 0 for k in RUBRIC.keys()}
    fb = {"pros": [], "cons": [], "summary": ""}

    if _contains_any(text, ["You are a", "Task:"]):
        scores["clarity"] += 2
        fb["pros"].append("Clear role and task.")
    if _contains_any(text, ["Deliverables", "Final"]):
        scores["specificity"] += 2
    if _contains_any(text, ["step-by-step", "steps", "Plan"]):
        scores["actionability"] += 2
    if _contains_any(text, ["Constraints", "If information is missing"]):
        scores["context_use"] += 2
    if _contains_any(text, ["- ", "\n\n"]):
        scores["structure"] += 2

    for k in scores:
        scores[k] = min(10, max(0, scores[k] * 2.5))

    fb["summary"] = "Heuristic scoring (fallback mode)."

    total = float(
        scores["clarity"]
        + scores["specificity"]
        + scores["actionability"]
        + scores["structure"]
        + scores["context_use"]
    )

    return Scorecard(**scores, feedback=fb, total=total)

def judge_prompt(text: str, rubric=None) -> Scorecard:
    """
    Judge a prompt using LLM-based evaluation.
    Falls back to heuristic scoring if API is unavailable.
    
    Args:
        text: The prompt text to judge
        rubric: Optional custom rubric (currently unused)
    
    Returns:
        Scorecard with scores (0-10) for each criterion
    """
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        system_prompt = """You are an expert prompt evaluator. Score prompts on 5 criteria (0-10 scale):

1. **Clarity** (0-10): Is the role/purpose clear? Any ambiguity?
2. **Specificity** (0-10): Are outputs, constraints, and examples concrete?
3. **Actionability** (0-10): Are there clear steps, inputs, and decision points?
4. **Structure** (0-10): Is it well-organized with sections, bullets, headings?
5. **Context Use** (0-10): Does it provide necessary context without overwhelming?

Return ONLY a JSON object with this exact structure:
{
  "clarity": <float 0-10>,
  "specificity": <float 0-10>,
  "actionability": <float 0-10>,
  "structure": <float 0-10>,
  "context_use": <float 0-10>,
  "pros": ["<strength 1>", "<strength 2>"],
  "cons": ["<weakness 1>", "<weakness 2>"],
  "summary": "<one sentence overall assessment>"
}"""

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Evaluate this prompt:\n\n{text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,  # Lower temp for more consistent scoring
            max_tokens=512,
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        # Handle markdown code blocks if LLM wraps response
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
            
        result = json.loads(result_text)
        
        # Extract scores and feedback
        scores = {
            "clarity": float(result["clarity"]),
            "specificity": float(result["specificity"]),
            "actionability": float(result["actionability"]),
            "structure": float(result["structure"]),
            "context_use": float(result["context_use"]),
        }
        
        feedback = {
            "pros": result.get("pros", []),
            "cons": result.get("cons", []),
            "summary": result.get("summary", "LLM-based evaluation")
        }
        
        total = sum(scores.values())
        
        return Scorecard(**scores, feedback=feedback, total=total)
        
    except Exception as e:
        print(f"⚠️ LLM judge error: {e}. Falling back to heuristic scoring.")
        return _heuristic_judge(text)
