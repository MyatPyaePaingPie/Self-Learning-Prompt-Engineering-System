# Temporal Analysis System Diagrams

**Supplementary Visual Documentation**  
**Week 12:** Temporal Prompt Learning & Causal Analysis

---

## 1. Temporal Model Diagram

### Conceptual Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     TEMPORAL ANALYSIS SYSTEM                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
        │   INPUT:     │ │  ANALYSIS:  │ │   OUTPUT:    │
        │   Version    │ │  Temporal   │ │   Insights   │
        │   History    │ │  Algorithms │ │   & Trends   │
        └──────────────┘ └─────────────┘ └──────────────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   STORAGE: Database   │
                    │   (PromptVersion +    │
                    │    JudgeScore)        │
                    └───────────────────────┘
```

---

## 2. Data Flow Architecture

```
┌──────────────┐
│   USER       │
│   (Frontend) │
└──────┬───────┘
       │ 1. Create/Edit Prompt
       ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND API (FastAPI)                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  POST /prompts/multi-agent-enhance                   │   │
│  │    ↓                                                 │   │
│  │  Create PromptVersion record                        │   │
│  │    - parent_version_id = previous version           │   │
│  │    - change_type = difflib classification           │   │
│  │    - change_magnitude = edit distance               │   │
│  │    - created_at = now()                             │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │ 2. Store Version
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  DATABASE (SQLAlchemy)                                       │
│  ┌──────────────┐        ┌──────────────┐                  │
│  │   prompts    │◄───┐   │ judge_scores │                  │
│  │              │    │   │              │                  │
│  │ - id         │    │   │ - clarity    │                  │
│  │ - user_id    │    │   │ - specificity│                  │
│  │ - text       │    │   │ - structure  │                  │
│  └──────────────┘    │   └──────┬───────┘                  │
│         ▲            │          │                           │
│         │ 1:N        │          │ 1:1                       │
│  ┌──────────────────────┐      │                           │
│  │  prompt_versions     │◄─────┘                           │
│  │                      │                                   │
│  │ - id                 │                                   │
│  │ - prompt_id (FK)     │                                   │
│  │ - parent_version_id  │◄──┐ Self-referential             │
│  │ - created_at         │   │ (version chain)               │
│  │ - change_type        │   │                               │
│  │ - change_magnitude   │───┘                               │
│  └──────────────────────┘                                   │
└───────────────────────────┬─────────────────────────────────┘
                            │ 3. Query Timeline
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  TEMPORAL ANALYSIS ENGINE (backend/temporal_analysis.py)     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  detect_trend(scores, timestamps)                    │   │
│  │    → Linear regression → "improving" / "degrading"   │   │
│  │                                                       │   │
│  │  detect_change_points(scores, threshold=0.2)         │   │
│  │    → Threshold comparison → [indices]                │   │
│  │                                                       │   │
│  │  compute_causal_hints(edges)                         │   │
│  │    → Group by change_type → avg score delta          │   │
│  │                                                       │   │
│  │  compute_statistics(scores)                          │   │
│  │    → avg, std, min, max, count                       │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │ 4. Return Results
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND VISUALIZATION (Streamlit)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Timeline Chart (Plotly)                             │   │
│  │    - X: Time, Y: Score                               │   │
│  │    - Trend line overlay                              │   │
│  │    - Change-point annotations                        │   │
│  │                                                       │   │
│  │  Version Graph (NetworkX)                            │   │
│  │    - Nodes: Versions (colored by score)              │   │
│  │    - Edges: Parent → child (labeled change_type)     │   │
│  │                                                       │   │
│  │  Causal Hints Bar Chart (Altair)                     │   │
│  │    - X: Change type, Y: Avg score delta              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Version Chain Structure (DAG)

### Example: 7-Version History

```
                    v0 (root)
                    │
                    │ [original: score=60]
                    │
                    ▼
                    v1
                    │
         [structure change: +8 pts → score=68]
                    │
         ┌──────────┴──────────┐
         │                     │
         ▼                     ▼
         v2                    v3
         │                     │
  [wording: +2 pts]     [length: +5 pts]
  [score=70]            [score=73]
         │                     │
         │                     ▼
         │                     v5
         │                     │
         │              [wording: +1 pt]
         │              [score=74]
         │
         ▼
         v4
         │
  [structure: +10 pts]
  [score=80]
         │
         ▼
         v6
         │
  [wording: -2 pts]
  [score=78]
```

**Observations:**
- **v4 branch:** Highest improvement (v2 → v4: +10 pts via structure)
- **v5 branch:** Moderate improvement (v3 → v5: +1 pt via wording)
- **v6:** Negative delta (v4 → v6: -2 pts) — over-optimization?

---

## 4. Trend Detection Visualization

### Linear Regression Model

```
Score
  100 │                                       ●
      │                                   ●
   80 │                               ●
      │                           ●
   60 │                       ●
      │                   ●
   40 │               ●
      │           ●
   20 │       ●
      │   ●
    0 │●──────────────────────────────────────▶ Time
      0   5  10  15  20  25  30  35  40  45  (days)

Legend:
  ● = Actual score data point
  Line = Linear regression fit: score = β₀ + β₁·t
  β₀ (intercept) = 58.5
  β₁ (slope) = +0.45 pts/day
  Classification: "Improving" (slope > 0.05)
```

---

## 5. Change-Point Detection

### Threshold-Based Algorithm

```
Score
  100 │
      │
   80 │                   ▲
      │                   │ Change-point
   60 │     ●────●────●   │   ●────●────●
      │                   │
   40 │                   ▼
      │                   (Δ = 22 pts > threshold)
   20 │
      │
    0 │─────────────────────────────────────▶ Time

Threshold = 20 pts (0.2 × 100)
Change-points detected: [index 3]
```

---

## 6. Causal Hints Correlation

### Edit Type Effectiveness Ranking

```
┌────────────────────────────────────────────┐
│  Change Type    Avg Δ Score   Occurrences  │
├────────────────────────────────────────────┤
│  structure      ██████████ +5.2      12    │
│  length         ████ +2.8             8    │
│  wording        ██ +1.3              25    │
│  other          ▌ -0.5                5    │
└────────────────────────────────────────────┘

Interpretation:
  - Structure changes: Most effective (+5.2 avg)
  - Wording changes: Frequent but low impact (+1.3 avg)
  - Other changes: Slightly harmful (-0.5 avg)
```

---

## 7. Temporal Patterns Classification

### Pattern 1: Progressive Improvement

```
Score
   90 │                               ●────●
      │                           ●
   70 │                   ●───●
      │           ●───●
   50 │   ●───●
      │
   30 │●
      └───────────────────────────────────────▶ Time
   Pattern: Monotonic increase
   Edit sequence: Structure → Wording → Polish
   Frequency: ~60% of prompts
```

### Pattern 2: Exploration Phase (Oscillation)

```
Score
   90 │       ●                   ●
      │               ●
   70 │                               ●
      │   ●               ●
   50 │           ●
      │
   30 │
      └───────────────────────────────────────▶ Time
   Pattern: Trial-and-error cycles
   Edit sequence: Experiment → Fail → Learn → Succeed
   Frequency: ~25% of prompts
```

### Pattern 3: Plateau Effect

```
Score
   90 │           ●───●───●───●───●───●
      │       ●
   70 │   ●
      │
   50 │●
      │
   30 │
      └───────────────────────────────────────▶ Time
   Pattern: Rapid rise then stabilization
   Edit sequence: Major rewrite → Diminishing returns
   Frequency: ~10% of prompts
```

### Pattern 4: Degradation

```
Score
   90 │●
      │   ●
   70 │       ●
      │           ●
   50 │               ●
      │                   ●
   30 │                       ●
      └───────────────────────────────────────▶ Time
   Pattern: Monotonic decrease
   Cause: Over-optimization, complexity creep
   Frequency: ~5% of prompts
```

---

## 8. Database ER Diagram (Extended)

```
┌─────────────────────┐
│      users          │
│─────────────────────│
│ id (int) PK         │
│ username (str)      │
│ email (str)         │
│ password_hash (str) │
│ created_at (dt)     │
└─────────┬───────────┘
          │ 1:N
          ▼
┌─────────────────────┐
│      prompts        │
│─────────────────────│
│ id (UUID) PK        │
│ user_id (int) FK    │◄─────── User ownership
│ request_id (str)    │
│ original_text (str) │
│ created_at (dt)     │
└─────────┬───────────┘
          │ 1:N
          ▼
┌──────────────────────────┐
│   prompt_versions        │
│──────────────────────────│
│ id (UUID) PK             │
│ prompt_id (UUID) FK      │
│ parent_version_id (UUID?)│◄─┐ Self-referential
│ version_no (int)         │  │ (version chain)
│ text (str)               │  │
│ explanation (JSON)       │  │
│ source (str)             │  │
│ created_at (dt)          │  │
│ ↓ TEMPORAL FIELDS        │  │
│ change_type (enum)       │  │
│ change_magnitude (float) │──┘
└─────────┬────────────────┘
          │ 1:1
          ▼
┌─────────────────────┐
│   judge_scores      │
│─────────────────────│
│ id (UUID) PK        │
│ prompt_version_id   │
│   (UUID) FK         │
│ clarity (float)     │
│ specificity (float) │
│ actionability (flt) │
│ structure (float)   │
│ context_use (float) │
│ feedback (JSON)     │
│ created_at (dt)     │
└─────────────────────┘
```

---

## 9. Algorithm Flowchart: Trend Detection

```
┌─────────────────────┐
│  START              │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│ Input: scores[], timestamps[]│
└──────────┬──────────────────┘
           │
           ▼
    ┌─────────────┐
    │ len < 2?    │──YES──┐
    └──────┬──────┘       │
           │ NO            │
           ▼               │
┌──────────────────────────┐ │
│ Convert timestamps to    │ │
│ numeric (seconds since   │ │
│ epoch)                   │ │
└──────────┬───────────────┘ │
           │                 │
           ▼                 │
┌──────────────────────────┐ │
│ Linear Regression:       │ │
│   slope, intercept,      │ │
│   r_value, p_value       │ │
└──────────┬───────────────┘ │
           │                 │
           ▼                 │
    ┌─────────────┐          │
    │ slope > 0.05│──YES──┐  │
    └──────┬──────┘       │  │
           │ NO           │  │
           ▼              │  │
    ┌──────────────┐     │  │
    │ slope < -0.05│─YES─┤  │
    └──────┬───────┘     │  │
           │ NO          │  │
           ▼             │  │
     ┌──────────┐       │  │
     │ "stable" │       │  │
     └────┬─────┘       │  │
          │             │  │
          │      ┌──────▼──▼────────┐
          └─────▶│ "improving"      │
                 │ "degrading"      │
                 └────────┬──────────┘
                          │
                          ▼
                   ┌────────────┐
                   │  RETURN    │
                   └────────────┘
```

---

## 10. API Request/Response Flow

### Example: GET /api/temporal/timeline

```
┌─────────────┐
│   CLIENT    │
└──────┬──────┘
       │ HTTP GET /api/temporal/timeline?prompt_id=123&start=2025-11-01&end=2025-12-01
       │ Headers: Authorization: Bearer <JWT_TOKEN>
       ▼
┌─────────────────────────────────────┐
│   BACKEND (FastAPI)                 │
│                                     │
│  1. Verify JWT → extract user_id   │
│  2. Validate prompt ownership:      │
│     SELECT * FROM prompts           │
│     WHERE id = 123                  │
│       AND user_id = <user_id>      │
│  3. Query versions in time range:   │
│     SELECT * FROM prompt_versions   │
│     WHERE prompt_id = 123           │
│       AND created_at BETWEEN ...    │
│  4. Query judge scores:             │
│     SELECT * FROM judge_scores      │
│     WHERE version_id IN (...)       │
│  5. Compute average scores          │
│  6. Build timeline array            │
└──────────┬──────────────────────────┘
           │
           ▼ HTTP 200 OK
┌─────────────────────────────────────┐
│   RESPONSE (JSON)                   │
│                                     │
│ [                                   │
│   {                                 │
│     "timestamp": "2025-11-01T10:00",│
│     "score": 65.0,                  │
│     "version_id": "uuid-v1",        │
│     "change_type": "structure"      │
│   },                                │
│   {                                 │
│     "timestamp": "2025-11-05T14:30",│
│     "score": 72.5,                  │
│     "version_id": "uuid-v2",        │
│     "change_type": "wording"        │
│   }                                 │
│ ]                                   │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│   FRONTEND (Streamlit/Plotly)       │
│                                     │
│  1. Parse JSON response             │
│  2. Create Plotly figure            │
│  3. Plot scatter: (timestamp, score)│
│  4. Render in Streamlit             │
└─────────────────────────────────────┘
```

---

**End of Diagrams**

*Visual documentation for Week 12 temporal analysis system.*

