from pydantic import BaseModel

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

def judge_prompt(text: str, rubric=None) -> Scorecard:
    r = RUBRIC if rubric is None else rubric
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

    fb["summary"] = "Heuristic scoring v1. Add LLM judge for nuance."

    # ✅ compute total as a real float before returning
    total = float(
        scores["clarity"]
        + scores["specificity"]
        + scores["actionability"]
        + scores["structure"]
        + scores["context_use"]
    )

    return Scorecard(**scores, feedback=fb, total=total)
