from pydantic import BaseModel

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
    domain = detect_domain(original)
    task = original.strip()
    artifact = "answer"
    if "code" in original.lower(): artifact = "code"
    improved = TEMPLATE_V1.format(domain=domain, task=task, constraints="[time, tools, data sources]", artifact=artifact)
    return ImprovedOut(text=improved, explanation=synth_explanation(original, improved))