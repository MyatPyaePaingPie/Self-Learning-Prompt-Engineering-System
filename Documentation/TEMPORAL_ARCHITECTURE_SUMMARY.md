# Team Temporal Architecture Summary

**Team Members:** Paing (Backend), Atang (Storage), Bellul (Frontend)  
**Week:** 12 (Nov 28 – Dec 4, 2025)  
**Project:** Self-Learning Prompt Engineering System

---

## Version Structure Format

**Database Schema (SQLAlchemy ORM):**

```python
class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    
    # Primary identification
    id: UUID                    # Unique version identifier
    prompt_id: UUID             # Foreign key to parent prompt
    version_no: int             # Sequential version number (0, 1, 2, ...)
    
    # Content
    text: str                   # Full prompt text (not delta-encoded)
    explanation: dict (JSON)    # Change explanation and metadata
    source: str                 # Provenance: "user_edit", "agent_enhancement", "synthetic"
    
    # Temporal metadata
    created_at: datetime        # High-precision timestamp (microseconds)
    parent_version_id: UUID?    # Self-referential FK (null for root)
    change_type: str            # "structure", "wording", "length", "other"
    change_magnitude: float     # 0.0-1.0 (normalized edit distance)
```

**Data Structure (Directed Acyclic Graph):**

```
Root (v0)
    ├─→ v1 [structure, Δt=2h, Δscore=+5]
    │   ├─→ v3 [wording, Δt=1d, Δscore=+2]
    │   └─→ v4 [length, Δt=1d, Δscore=-1]
    └─→ v2 [other, Δt=6h, Δscore=+1]
```

**Key Properties:**
- **Acyclic:** No version can be its own ancestor (validated on insert)
- **Temporal consistency:** `child.created_at > parent.created_at` (enforced)
- **Full text storage:** Each version is self-contained (no reconstruction needed)

---

## Metadata Captured Per Revision

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `id` | UUID | Unique identifier | `550e8400-e29b-41d4-a716-446655440000` |
| `prompt_id` | UUID | Links to parent prompt | `123e4567-e89b-12d3-a456-426614174000` |
| `version_no` | int | Sequential counter | `0, 1, 2, 3, ...` |
| `text` | str | Full prompt content | `"Write a Python function to..."` |
| `explanation` | JSON | Change rationale | `{"reason": "Added error handling", "bullets": [...]}` |
| `source` | str | Who/what created it | `"user_edit"`, `"syntax_agent"`, `"synthetic"` |
| `created_at` | datetime | When created | `2025-12-04T14:23:45.123456Z` |
| `parent_version_id` | UUID? | Previous version | `null` (root) or UUID |
| `change_type` | enum | Edit classification | `"structure"`, `"wording"`, `"length"`, `"other"` |
| `change_magnitude` | float | How different (0-1) | `0.35` (35% changed) |

**Derived Metadata (Not Stored):**
- `score_delta`: Computed from JudgeScore table
- `time_delta`: Computed from timestamps
- `depth`: Distance from root in version tree

---

## Method for Linking Changes to Score Differences

**Step 1: Build Version Chain**

```sql
-- Query versions with parent-child links
SELECT v.id, v.parent_version_id, v.created_at, v.change_type
FROM prompt_versions v
WHERE v.prompt_id = ?
ORDER BY v.created_at;
```

**Step 2: Fetch Judge Scores**

```sql
-- Get score for each version
SELECT js.prompt_version_id,
       (js.clarity + js.specificity + js.actionability + 
        js.structure + js.context_use) / 5.0 AS avg_score
FROM judge_scores js;
```

**Step 3: Compute Score Deltas**

```python
# Build edges: (parent, child) pairs
edges = []
for version in versions:
    if version.parent_version_id:
        parent_score = scores[version.parent_version_id]
        child_score = scores[version.id]
        score_delta = child_score - parent_score
        
        edges.append({
            "from": version.parent_version_id,
            "to": version.id,
            "change_type": version.change_type,
            "score_delta": score_delta,
            "time_delta": version.created_at - parent.created_at
        })
```

**Step 4: Aggregate by Change Type**

```python
# Group edges by change_type
groups = defaultdict(list)
for edge in edges:
    groups[edge["change_type"]].append(edge["score_delta"])

# Compute average score delta per change type
causal_hints = [
    {
        "change_type": change_type,
        "avg_score_delta": mean(deltas),
        "occurrence_count": len(deltas)
    }
    for change_type, deltas in groups.items()
]

# Sort by effectiveness (highest score improvement first)
causal_hints.sort(key=lambda x: x["avg_score_delta"], reverse=True)
```

**Output Example:**

```json
[
  {"change_type": "structure", "avg_score_delta": +5.2, "occurrence_count": 12},
  {"change_type": "length", "avg_score_delta": +2.8, "occurrence_count": 8},
  {"change_type": "wording", "avg_score_delta": +1.3, "occurrence_count": 25}
]
```

---

## Visualization Plan

### **1. Timeline View** (Primary)

**Purpose:** Show prompt evolution chronologically

**Components:**
- **X-axis:** Time (days/weeks)
- **Y-axis:** Judge score (0-100)
- **Data points:** Versions (circles sized by change_magnitude)
- **Line:** Trend line (linear regression)
- **Annotations:** Change-points (vertical lines with labels)

**Interactions:**
- Hover over point → Show tooltip (version_no, change_type, score, timestamp)
- Click point → Display full prompt text diff
- Zoom/pan → Navigate long histories

**Implementation:** Streamlit + Plotly

```python
import plotly.express as px

fig = px.scatter(
    timeline_data,
    x='timestamp',
    y='score',
    color='change_type',
    size='change_magnitude',
    hover_data=['version_no', 'change_type'],
    title='Prompt Evolution Timeline'
)
fig.add_scatter(x=timestamps, y=trend_line, mode='lines', name='Trend')
```

### **2. Version Graph** (Secondary)

**Purpose:** Visualize version relationships (DAG)

**Components:**
- **Nodes:** Versions (colored by score: red=low, green=high)
- **Edges:** Parent → child arrows (labeled with change_type)
- **Layout:** Top-to-bottom (chronological flow)

**Interactions:**
- Hover over node → Show version details
- Click edge → Show text diff
- Highlight path → Trace lineage from root to selected version

**Implementation:** Streamlit + Graphviz or NetworkX

```python
import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()
for edge in edges:
    G.add_edge(edge['from'], edge['to'], label=edge['change_type'])

pos = nx.spring_layout(G)
nx.draw(G, pos, node_color=scores, cmap='RdYlGn', with_labels=True)
```

### **3. Causal Hints Bar Chart** (Tertiary)

**Purpose:** Rank edit types by effectiveness

**Components:**
- **X-axis:** Change type
- **Y-axis:** Average score delta
- **Bars:** Colored by sign (green=positive, red=negative)
- **Labels:** Occurrence count

**Implementation:** Streamlit + Altair

```python
import altair as alt

chart = alt.Chart(causal_hints_df).mark_bar().encode(
    x='change_type:N',
    y='avg_score_delta:Q',
    color=alt.condition(
        alt.datum.avg_score_delta > 0,
        alt.value('green'),
        alt.value('red')
    ),
    tooltip=['change_type', 'avg_score_delta', 'occurrence_count']
)
```

### **4. Statistics Dashboard** (Supplementary)

**Metrics Displayed:**
- **Trend:** "Improving" / "Degrading" / "Stable" (with slope)
- **Average Score:** `72.5` (± 5.2 std dev)
- **Total Versions:** `45`
- **Score Range:** `[55.0, 85.0]`
- **Velocity:** `+2.3 points/day`

**Implementation:** Streamlit metric widgets

```python
col1, col2, col3 = st.columns(3)
col1.metric("Trend", "Improving ↑", delta="+2.3 pts/day")
col2.metric("Average Score", "72.5", delta="+5.2")
col3.metric("Total Versions", "45")
```

---

## API Endpoints Summary

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/api/temporal/timeline` | GET | Version sequence | `[(timestamp, score, version_id, change_type), ...]` |
| `/api/temporal/statistics` | GET | Trend & stats | `{trend, avg_score, score_std, total_versions}` |
| `/api/temporal/causal-hints` | GET | Correlation analysis | `[{change_type, avg_score_delta, count}, ...]` |
| `/api/temporal/generate-synthetic` | POST | Create test data | `{created_versions, prompt_id, days}` |

**Authentication:** All endpoints require JWT token (`Authorization: Bearer <token>`)

**Query Parameters:**
- `prompt_id` (required): UUID of the prompt
- `start`, `end` (optional, timeline only): ISO 8601 date range

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI + Python | REST API endpoints |
| **Analysis** | scipy, numpy | Statistical algorithms |
| **Database** | SQLAlchemy + SQLite | Persistent storage |
| **Frontend** | Streamlit | Interactive visualizations |
| **Charting** | Plotly, Altair | Timeline and bar charts |

---

## Workflow Summary

```
User Login → JWT Token
    ↓
Create/Edit Prompt → PromptVersion record (with parent_version_id)
    ↓
Judge Evaluation → JudgeScore record (linked to version)
    ↓
Temporal Analysis Request
    ↓
Backend: Query versions + scores, compute statistics, detect trends
    ↓
Frontend: Render timeline, version graph, causal hints
    ↓
User Insight: "Structure changes yield +5.2 point improvement"
```

---

**End of Summary**

*This 1-page architecture summary documents the temporal analysis system design for Week 12 of the Self-Learning Prompt Engineering System project.*

