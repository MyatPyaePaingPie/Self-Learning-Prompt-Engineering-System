# Repo Layout (create exactly this)

```
self-learning-prompter/
├─ apps/
│  ├─ api/                # FastAPI service (Prompt Engineer, Judge, Memory)
│  └─ web/                # Next.js (or simple React) UI
├─ packages/
│  ├─ core/               # Shared Python lib: rewrite strategies, judge rubric, learning
│  └─ db/                 # SQL migrations + DB access layer
├─ infra/
│  ├─ docker/             # Dockerfiles
│  └─ github/             # GitHub Actions
├─ tests/
│  ├─ unit/
│  └─ e2e/
└─ README.md
```

# Branching & daily flow (keep it simple)

1. Create `develop` from `main`.
2. Work in `feature/<short-name>`.
3. Push small commits. Open PR to `develop` every Thu; squash-merge after review.
4. Promote `develop` → `main` after green tests.

---

# 1) Database: schema + migrations

## SQL (Postgres)

Create these tables first (use a migration tool like Alembic).

```sql
-- 001_init.sql
CREATE TABLE prompts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT,
  original_text TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE prompt_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt_id UUID NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
  version_no INT NOT NULL,               -- 0 = original, 1..n = rewrites
  text TEXT NOT NULL,
  explanation JSONB NOT NULL,            -- {bullets: [...], diffs: [...]} 
  source TEXT NOT NULL,                  -- 'original' | 'engine/vX'
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (prompt_id, version_no)
);

CREATE TABLE judge_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt_version_id UUID NOT NULL REFERENCES prompt_versions(id) ON DELETE CASCADE,
  clarity NUMERIC NOT NULL CHECK (clarity BETWEEN 0 AND 10),
  specificity NUMERIC NOT NULL CHECK (specificity BETWEEN 0 AND 10),
  actionability NUMERIC NOT NULL CHECK (actionability BETWEEN 0 AND 10),
  structure NUMERIC NOT NULL CHECK (structure BETWEEN 0 AND 10),
  context_use NUMERIC NOT NULL CHECK (context_use BETWEEN 0 AND 10),
  total NUMERIC GENERATED ALWAYS AS (clarity+specificity+actionability+structure+context_use) STORED,
  feedback JSONB NOT NULL,               -- {pros:[], cons:[], summary:""}
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE best_heads (
  prompt_id UUID PRIMARY KEY REFERENCES prompts(id) ON DELETE CASCADE,
  prompt_version_id UUID NOT NULL REFERENCES prompt_versions(id) ON DELETE CASCADE,
  score NUMERIC NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_prompt_versions_prompt ON prompt_versions(prompt_id);
CREATE INDEX idx_judge_scores_pv ON judge_scores(prompt_version_id);
```

## Python ORM models (SQLAlchemy, packages/db/models.py)

```python
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
```

---

# 2) API Contracts (FastAPI, apps/api)

## REST Endpoints

| Method | Path                             | Body              | Returns                                                               |              |                                             |
| ------ | -------------------------------- | ----------------- | --------------------------------------------------------------------- | ------------ | ------------------------------------------- |
| POST   | `/v1/prompts`                    | `{userId?, text}` | `{promptId, versionNo:0, versionId, improved?, explanation?, judge?}` |              |                                             |
| POST   | `/v1/prompts/{promptId}/improve` | `{strategy?:"v1"  | "v2"                                                                  | "ensemble"}` | `{versionId, versionNo, text, explanation}` |
| POST   | `/v1/versions/{versionId}/judge` | `{rubric?}`       | `{scorecard}`                                                         |              |                                             |
| POST   | `/v1/prompts/{promptId}/learn`   | `{}`              |                                                                       |              |                                             |
| GET    | `/v1/prompts/{promptId}`         | —                 | `{original, best, history[]}`                                         |              |                                             |

**Step order on POST /v1/prompts**

1. insert `prompts` + `prompt_versions`(version_no=0).
2. run Prompt Engineer → create v1.
3. judge v1.
4. set `best_heads` to v1 if score > baseline.
5. respond with everything needed for UI.

## FastAPI skeleton (apps/api/main.py)

```python
from fastapi import FastAPI
from pydantic import BaseModel
from packages.core.engine import improve_prompt
from packages.core.judge import judge_prompt
from packages.core.learning import update_rules
from packages.db.session import get_session
from packages.db.crud import *

app = FastAPI()

class CreatePromptIn(BaseModel):
    userId: str | None = None
    text: str

@app.post("/v1/prompts")
def create_prompt(payload: CreatePromptIn):
    with get_session() as s:
        prompt = create_prompt_row(s, payload.userId, payload.text)
        v0 = create_version_row(s, prompt.id, 0, payload.text, explanation={"bullets":["Original"]}, source="original")
        improved = improve_prompt(payload.text, strategy="v1")
        v1 = create_version_row(s, prompt.id, 1, improved.text, improved.explanation, source=improved.source)
        score = judge_prompt(improved.text, rubric=None)
        create_judge_score_row(s, v1.id, score)
        maybe_update_best_head(s, prompt.id, v1.id, score.total)
        s.commit()
        return {
            "promptId": str(prompt.id),
            "versionId": str(v1.id),
            "versionNo": 1,
            "improved": improved.text,
            "explanation": improved.explanation,
            "judge": score.model_dump()
        }
```

---

# 3) Prompt Engineer: rewrite strategies (packages/core/engine.py)

## Strategy rules (start simple, expand later)

* Always set a relevant role (domain-expert).
* Ask for the minimal needed context via placeholders `[task]`, `[constraints]`, `[output format]`.
* Require concrete outputs (bullets, steps, code blocks).
* Add evaluation criteria (“consider edge cases”, “explain trade-offs”).
* Constrain tone/style if helpful.

## Code scaffold

```python
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
```

> Later add `strategy="ensemble"` that generates 2–3 variants (e.g., role-driven, format-driven, question-first), then auto-pick the best via the Judge.

---

# 4) Judge: rubric, scoring, and feedback (packages/core/judge.py)

## Rubric (JSON you can edit without code changes)

```python
RUBRIC = {
  "clarity":   {"weight": 1.0, "checks": ["clear role", "purpose stated", "no ambiguity"]},
  "specificity":{"weight":1.0, "checks": ["concrete outputs", "constraints", "examples/edge-cases"]},
  "actionability":{"weight":1.0, "checks": ["step-by-step", "inputs named", "decision points"]},
  "structure":{"weight":1.0, "checks": ["sections", "bullets", "headings/placeholders"]},
  "context_use":{"weight":1.0, "checks": ["preserves intent", "adds necessary context only"]}
}
```

## Scoring function (LLM or heuristic first)

Start with deterministic heuristics for bootstrapping; later swap to an LLM call with a strict JSON output schema.

```python
from pydantic import BaseModel

class Scorecard(BaseModel):
    clarity: float; specificity: float; actionability: float; structure: float; context_use: float
    feedback: dict
    @property
    def total(self): return self.clarity+self.specificity+self.actionability+self.structure+self.context_use

def _contains_any(s, keys): return any(k.lower() in s.lower() for k in keys)

def judge_prompt(text: str, rubric=None) -> Scorecard:
    r = RUBRIC if rubric is None else rubric
    scores = {"clarity":0, "specificity":0, "actionability":0, "structure":0, "context_use":0}
    fb = {"pros":[], "cons":[], "summary":""}

    if _contains_any(text, ["You are a","Task:"]): scores["clarity"] += 2; fb["pros"].append("Clear role and task.")
    if _contains_any(text, ["Deliverables","Final"]): scores["specificity"] += 2
    if _contains_any(text, ["step-by-step","steps","Plan"]): scores["actionability"] += 2
    if _contains_any(text, ["Constraints","If information is missing"]): scores["context_use"] += 2
    if _contains_any(text, ["- ","\n\n"]): scores["structure"] += 2

    for k in scores: scores[k] = min(10, max(0, scores[k]*2.5))  # scale to 0..10

    fb["summary"] = "Heuristic scoring v1. Add LLM judge for nuance."
    return Scorecard(**scores, feedback=fb)
```

> Swap in an LLM: prompt it with the rubric and the original+improved; require JSON output `{scores:{...}, feedback:{...}}`. Validate with Pydantic before saving.

---

# 5) Memory & Learning Loop (packages/core/learning.py)

## Policy

* Keep `best_heads` per prompt.
* Only adopt a new version if `score.total >= best.score + margin` (start `margin=0`).
* Track feature usage → adjust rewrite template.

## Code (simple rule-update)

```python
from dataclasses import dataclass

@dataclass
class LearningState:
    require_role: bool = True
    require_deliverables: bool = True
    require_constraints: bool = True
    require_questions_first: bool = True

STATE = LearningState()

def update_rules(history: list[dict]) -> LearningState:
    """
    history: [{text, scorecard:{...}}]
    Simple signal: if versions with 'Constraints:' consistently score higher,
    lock this element in; else consider relaxing.
    """
    # placeholder: compute deltas, toggle flags. For now, keep defaults.
    return STATE
```

## Best-head update (packages/db/crud.py)

```python
def maybe_update_best_head(session, prompt_id, version_id, score):
    bh = session.execute(sa.select(BestHead).where(BestHead.prompt_id==prompt_id)).scalar_one_or_none()
    if not bh or score >= bh.score:
        if not bh:
            bh = BestHead(prompt_id=prompt_id, prompt_version_id=version_id, score=score)
            session.add(bh)
        else:
            bh.prompt_version_id = version_id
            bh.score = score
```

---

# 6) UI (apps/web)

Keep it super simple first.

## Pages

* `/` — textarea to submit original prompt; POST to `/v1/prompts`.
* `/p/[id]` — show Original vs Improved, explanation bullets, judge score, “Improve again” button (calls `/improve`).

## Data contract (expect from API)

```ts
type Explanation = { bullets: string[]; diffs: {from:string,to:string}[] };
type Scorecard = { clarity:number; specificity:number; actionability:number; structure:number; context_use:number; total:number; feedback:{pros:string[],cons:string[],summary:string} };
type CreatePromptResp = { promptId:string; versionId:string; versionNo:number; improved:string; explanation:Explanation; judge:Scorecard };
```

---

# 7) Deterministic E2E Path (so demos never crash)

1. If LLM providers are down, fallback to heuristic Prompt Engineer (template) + heuristic Judge (above).
2. Make all network calls time-boxed (2.0s); on timeout, fallback to heuristic path.
3. Cache most recent improved version in memory for instant re-render if DB is slow.
4. Use `uvicorn --workers=2` minimum; set connection pool size in SQLAlchemy.

---

# 8) Metrics & Logging

| Metric                   | How to Compute                            | Where             |
| ------------------------ | ----------------------------------------- | ----------------- |
| Avg Judge Total (weekly) | `AVG(judge_scores.total)` grouped by week | SQL view          |
| Win Rate                 | `% versions where total > previous best`  | SQL               |
| Rollback Rate            | `% improvements rejected`                 | SQL               |
| Time to Result           | API latency from submit→response          | API middleware    |
| Heuristic vs LLM Usage   | Counter in judge & engine                 | Prometheus / logs |

Add a simple `/v1/metrics` endpoint returning JSON for a dashboard later.

---

# 9) Tests (drop in now, keep green)

## Unit tests (tests/unit/test_engine.py)

```python
def test_improve_adds_role_and_sections():
    from packages.core.engine import improve_prompt
    out = improve_prompt("help me code a parser in python")
    assert "You are a senior" in out.text
    assert "Deliverables:" in out.text
    assert out.explanation["bullets"]
```

## Unit tests (tests/unit/test_judge.py)

```python
def test_judge_scales_scores_0_10():
    from packages.core.judge import judge_prompt
    s = judge_prompt("You are a senior... Task: X\nDeliverables:\n- step-by-step\nConstraints:")
    for k in ["clarity","specificity","actionability","structure","context_use"]:
        assert 0 <= getattr(s, k) <= 10
    assert s.total <= 50
```

## E2E test (tests/e2e/test_flow.py)

```python
def test_full_flow(client):
    r = client.post("/v1/prompts", json={"text":"Help me code"})
    assert r.status_code == 200
    data = r.json()
    assert "improved" in data and "judge" in data
```

---

# 10) CI/CD (infra/github/workflows/ci.yml)

* Lint + type check + tests.

```yaml
name: ci
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with: { python-version: '3.11' }
    - run: pip install -r requirements.txt
    - run: pytest -q
```

---

# 11) Docker (infra/docker)

**api/Dockerfile**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

# 12) Initial “done today” steps (copy/paste sequence)

1. **Scaffold repo**

```
mkdir -p self-learning-prompter/{apps/api,apps/web,packages/{core,db},infra/{docker,github},tests/{unit,e2e}}
git init
```

2. **Add requirements**

```
echo "
fastapi
uvicorn
pydantic
sqlalchemy
psycopg[binary]
alembic
pytest
" > requirements.txt
```

3. **Create DB models + migrations** (paste SQL from above into `packages/db/migrations/001_init.sql`; run with your tool or Alembic migration).

4. **Implement**:

   * `packages/core/engine.py` (template version above)
   * `packages/core/judge.py` (heuristic version above)
   * `packages/core/learning.py` (stub above)
   * `apps/api/main.py` (endpoint above)
   * `packages/db/session.py` (SQLAlchemy engine + session factory)
   * `packages/db/crud.py` (create/read helpers and best-head update)

5. **Run API locally**

```
uvicorn apps.api.main:app --reload
```

6. **Add tests** (paste snippets above) and run:

```
pytest -q
```

7. **Wire minimal UI** (optional day-1): simple HTML form posting to `/v1/prompts`, render JSON response side-by-side.

---

# 13) Upgrades (after baseline is stable)

| Upgrade             | Actionable Step                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------- |
| LLM Prompt Engineer | Add `engine_llm.py` with provider client; try 2 rewrite styles; pick by Judge.                                |
| LLM Judge           | Prompt LLM with rubric; require JSON; validate with Pydantic; store raw + parsed.                             |
| Ensemble & A/B      | Generate (role-first, output-format-first, questions-first); judge all; keep best; log losers.                |
| Adaptive Rules      | From top-quartile versions, mine patterns (regex for “Constraints:”, “Deliverables:”); adjust template flags. |
| Analytics UI        | Build `/admin` page with weekly score trend, win rate, rollback rate.                                         |
| Caching             | Memoize heuristic judge to ensure <30ms scoring.                                                              |
| Rate Limits         | Per user ID/IP to protect APIs.                                                                               |
| Observability       | Add request IDs, structured logs, error budgets.                                                              |

---

# 14) Canonical Example (what the system should output)

**Input**: `Help me code.`

**Improved**:

```
You are a senior Python developer.
Task: Help me design and implement clean, well-commented Python code for [task].
Deliverables:
- Step-by-step plan with rationale
- Working code examples with docstrings and tests
- Edge cases and performance notes
Constraints: [Python version], [libraries allowed], [time], [I/O limits]
If information is missing, list 3–5 clarifying questions first, then proceed with reasonable assumptions.
```

**Explanation** (store in `explanation`):

* Added expert role and explicit task.
* Required concrete deliverables and tests.
* Introduced constraints placeholder to focus scope.
* Forced clarifying questions before solution.

**Judge**:

* `{clarity:8, specificity:8, actionability:8, structure:8, context_use:8, total:40, feedback:{...}}`

---

# 15) Non-negotiables (bake into code)

* Always store the original (version_no=0).
* Never overwrite best without scoring check.
* Deterministic fallback path (no provider → heuristics).
* Explanations are mandatory for any rewrite.
* JSON schema enforcement on LLM judge output.

