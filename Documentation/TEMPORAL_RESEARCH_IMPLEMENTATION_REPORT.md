# Temporal Prompt Learning & Causal Analysis: Implementation Research Report

**Author:** Paing 
**Course:** Self-Learning Prompt Engineering System  
**Week:** 12 (Nov 28 – Dec 4, 2025)  
**Topic:** Time-Aware Analysis of Prompt Evolution and Causal Relationships

---

## Executive Summary

This report documents the implementation of a temporal analysis system for tracking prompt evolution over time. The system enables detection of trends, change-points, and causal relationships between prompt modifications and performance metrics. Our implementation uses a database-first architecture with version chains, implements statistical trend detection using linear regression, and provides causal hints through correlation analysis of edit types and score deltas.

**Key Contributions:**
- Parent-child version chain data structure for temporal reconstruction
- Linear regression-based trend detection with classification thresholds
- Threshold-based change-point detection for identifying significant transitions
- Correlation-based causal hint extraction grouping change types with score deltas
- User-authenticated temporal data isolation for multi-user environments

**Research Hypothesis:**
We hypothesize that structural changes (major rewrites) will yield higher score improvements than superficial edits (wording tweaks), and that the magnitude of change will positively correlate with score delta, with diminishing returns beyond a threshold.

---

## Table of Contents

1. [Temporal Modeling](#1-temporal-modeling)
2. [Version Tracking Architecture](#2-version-tracking-architecture)
3. [Correlation Analysis & Causal Hints](#3-correlation-analysis--causal-hints)
4. [Visualization and Interpretation](#4-visualization-and-interpretation)
5. [API Architecture](#5-api-architecture)
6. [Implementation Statistics](#6-implementation-statistics)
7. [Research Background & Literature Review](#7-research-background--literature-review)
8. [Hypothesis Testing Framework](#8-hypothesis-testing-framework)
9. [Limitations and Future Work](#9-limitations-and-future-work)
10. [Conclusion](#10-conclusion)

---

## 1. Temporal Modeling

### 1.1 Core Concepts

**Temporal modeling** treats prompt history as a time series where each version represents a data point with associated performance metrics. Our system captures three fundamental temporal patterns:

1. **Trend Detection:** Identifying long-term directional movement (improving, degrading, stable)
2. **Change-Point Detection:** Locating significant transitions in score sequences
3. **Temporal Statistics:** Computing descriptive statistics over time windows

### 1.2 Mathematical Formulation: Linear Regression Trend Detection

We model prompt score evolution as a linear function of time:

```
score(t) = β₀ + β₁·t + ε
```

Where:
- `t` = timestamp (seconds since epoch)
- `score(t)` = judge score at time t (0-100 scale)
- `β₀` = intercept (baseline score)
- `β₁` = slope (rate of change per second)
- `ε` = noise/residual error

**Implementation:**

```python
def detect_trend(scores: List[float], timestamps: List[datetime]) -> str:
    """Linear regression-based trend detection"""
    time_numeric = [ts.timestamp() for ts in timestamps]
    slope, intercept, r_value, p_value, std_err = stats.linregress(time_numeric, scores)
    
    # Classification thresholds
    if slope > 0.05:
        return "improving"
    elif slope < -0.05:
        return "degrading"
    else:
        return "stable"
```

**Design Rationale:**
- **Linear regression** provides statistical rigor (R² value, p-value for significance testing)
- **Slope threshold (±0.05)** balances sensitivity vs. noise resilience
- **Classification** simplifies interpretation for end users

**Limitations:**
- Assumes linear trends (misses sinusoidal/exponential patterns)
- Sensitive to outliers (could use robust regression)
- No significance testing implemented (could filter by p-value)

### 1.3 Change-Point Detection: Threshold-Based Method

**Algorithm:**

```
For each consecutive pair (score[i-1], score[i]):
    delta = |score[i] - score[i-1]|
    if delta > threshold × 100:
        mark i as change-point
```

**Implementation:**

```python
def detect_change_points(scores: List[float], threshold: float = 0.2) -> List[int]:
    """Threshold-based change-point detection"""
    change_points = []
    threshold_scaled = threshold * 100  # Scale to 0-100 range
    
    for i in range(1, len(scores)):
        delta = abs(scores[i] - scores[i-1])
        if delta > threshold_scaled:
            change_points.append(i)
    
    return change_points
```

**Parameters:**
- **Threshold = 0.2 (20 points):** Empirically chosen to balance false positives vs. false negatives
- **Consecutive comparison:** Simple O(n) algorithm, real-time capable

**Alternative Approaches (Not Implemented):**
- **CUSUM (Cumulative Sum):** Detects subtle shifts in mean
- **Bayesian change-point detection:** Probabilistic model
- **Pruned exact linear time (PELT):** Optimal segmentation

**Why threshold-based?**
- Simplicity: Easy to understand and debug
- Speed: O(n) vs. O(n²) for dynamic programming methods
- Interpretability: Threshold has clear semantic meaning

### 1.4 Temporal Statistics

**Computed Metrics:**

| Metric | Formula | Purpose |
|--------|---------|---------|
| Average | `Σ scores / n` | Central tendency |
| Std Dev | `√(Σ(score - avg)² / (n-1))` | Variability measure |
| Min/Max | `min(scores), max(scores)` | Range bounds |
| Velocity | `(score[n] - score[0]) / Δt_days` | Rate of change (points/day) |

**Velocity Calculation:**

```python
def compute_score_velocity(scores: List[float], timestamps: List[datetime]) -> float:
    """Average rate of score change (points per day)"""
    total_change = scores[-1] - scores[0]
    time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 86400.0
    return total_change / time_span if time_span > 0 else 0.0
```

**Use Case:** Velocity provides intuitive metric for progress rate (e.g., "improving by 2.5 points/day")

---

## 2. Version Tracking Architecture

### 2.1 Database Schema

**Entity-Relationship Model:**

```
┌─────────────────┐
│    Prompt       │
│─────────────────│
│ id (UUID)       │◄──┐
│ user_id (str)   │   │
│ original_text   │   │
│ created_at      │   │
└─────────────────┘   │
                      │
                      │ 1:N
┌──────────────────────┼──────────────┐
│   PromptVersion      │              │
│──────────────────────┼──────────────│
│ id (UUID)            │              │
│ prompt_id (FK)       ├──────────────┘
│ version_no (int)     │
│ text (str)           │
│ source (str)         │
│ created_at (datetime)│
│ ↓ TEMPORAL FIELDS    │
│ parent_version_id ───┼──┐ Self-referential
│ change_type (enum)   │  │ (version chain)
│ change_magnitude (0-1)│ │
└──────────────────────┘  │
         ▲                │
         └────────────────┘
```

**Key Design Decisions:**

1. **Self-Referential Foreign Key (`parent_version_id`)**
   - Creates directed acyclic graph (DAG) of version history
   - Enables branching (multiple children per parent)
   - Nullable for root versions (version 0)

2. **Metadata Fields:**
   - `change_type`: Categorical classification ("structure", "wording", "length", "other")
   - `change_magnitude`: Normalized edit distance (0 = identical, 1 = completely different)
   - `created_at`: High-precision timestamp for temporal ordering

3. **User Isolation:**
   - `Prompt.user_id` ensures data isolation in multi-user environment
   - All temporal queries filter by authenticated user

### 2.2 Version Chain Reconstruction

**Algorithm:**

```
1. Query all versions for prompt_id, ordered by created_at
2. Build adjacency list: parent_id → [child_ids]
3. Traverse from root (parent_id = null) in breadth-first order
4. Validate acyclicity (no version can be ancestor of itself)
```

**Timeline API Response Format:**

```json
[
  {
    "timestamp": "2025-11-28T10:30:00Z",
    "score": 65.0,
    "version_id": "uuid-v1",
    "change_type": "structure"
  },
  {
    "timestamp": "2025-11-28T14:15:00Z",
    "score": 72.5,
    "version_id": "uuid-v2",
    "change_type": "wording"
  }
]
```

### 2.3 Change Type Classification

**Algorithm (difflib-based):**

```python
def compute_change_type(old_text: str, new_text: str) -> str:
    ratio = difflib.SequenceMatcher(None, old_text, new_text).ratio()
    
    if ratio < 0.5:
        return "structure"  # Major rewrite
    
    length_ratio = len(new_text) / max(len(old_text), 1)
    if length_ratio > 1.5 or length_ratio < 0.5:
        return "length"  # Significant length change
    
    return "wording"  # Minor edits
```

**Thresholds:**
- **Structure:** `similarity < 0.5` (less than 50% matching subsequences)
- **Length:** `length_ratio > 1.5 or < 0.5` (50% increase/decrease)
- **Wording:** Default (minor textual changes)

**Change Magnitude:**

```python
def compute_change_magnitude(old_text: str, new_text: str) -> float:
    ratio = difflib.SequenceMatcher(None, old_text, new_text).ratio()
    return 1.0 - ratio  # 0 = identical, 1 = completely different
```

---

## 3. Correlation Analysis & Causal Hints

### 3.1 Problem Statement

**Goal:** Determine which types of edits correlate with score improvements.

**Formal Problem:**
```
Given: Set of edges E = {(change_type, score_delta)}
Find: For each change_type, average score_delta
Output: Ranked list of change types by effectiveness
```

### 3.2 Implementation

```python
def compute_causal_hints(edges: List[Tuple[str, float]]) -> List[Dict[str, any]]:
    """Compute causal hints by grouping edges by change_type"""
    
    # Group by change_type
    groups: Dict[str, List[float]] = {}
    for change_type, score_delta in edges:
        if change_type not in groups:
            groups[change_type] = []
        groups[change_type].append(score_delta)
    
    # Compute averages
    results = []
    for change_type, deltas in groups.items():
        results.append({
            "change_type": change_type,
            "avg_score_delta": statistics.mean(deltas),
            "occurrence_count": len(deltas)
        })
    
    # Sort by avg_score_delta descending
    results.sort(key=lambda x: x["avg_score_delta"], reverse=True)
    
    return results
```

**Example Output:**

```json
[
  {"change_type": "structure", "avg_score_delta": +5.2, "occurrence_count": 12},
  {"change_type": "length", "avg_score_delta": +2.8, "occurrence_count": 8},
  {"change_type": "wording", "avg_score_delta": +1.3, "occurrence_count": 25},
  {"change_type": "other", "avg_score_delta": -0.5, "occurrence_count": 5}
]
```

**Interpretation:** Structure changes yield highest average improvement (+5.2 points), suggesting substantial rewrites are more effective than minor wording tweaks.

### 3.3 Causal vs. Correlation

**Important Distinction:**

| Correlation | Causation |
|-------------|-----------|
| ✅ We compute | ❌ We do NOT establish |
| Association between change_type and score_delta | Change_type CAUSES score_delta |
| Statistical relationship | Mechanistic relationship |

**Why not causal inference?**
1. **Confounding variables:** User skill, prompt complexity, judge variability
2. **Selection bias:** Users may apply different edit types to different prompts
3. **Temporal dependencies:** Earlier edits affect viability of later edits

**What we provide:**
- **"Causal hints"** = suggestive correlations requiring human interpretation
- **Exploratory analysis** for hypothesis generation, not hypothesis testing

**Future Work (Rigorous Causal Inference):**
- Instrumental variables (randomized edit suggestions)
- Difference-in-differences (compare prompts with/without edit type)
- Propensity score matching (control for confounders)

---

## 4. Visualization and Interpretation

### 4.1 Timeline Visualization (Conceptual)

**Components:**

```
Score
  100 ┤                                    ●
      │                               ●
   75 ┤                          ●
      │                     ●
   50 ┤   ●────●
      │
      └────┬────┬────┬────┬────┬────┬────▶ Time
         Day 0  5   10   15   20   25   30

Legend:
  ● = Version data point
  ▲ = Change-point (significant jump)
  Line = Trend (linear regression fit)
```

**Annotations:**
- **Versions:** Hoverable markers showing version_id, change_type, score
- **Change-points:** Highlighted with vertical lines and annotations
- **Trend line:** Overlaid linear regression with slope label

### 4.2 Version Graph (Directed Acyclic Graph)

**Structure:**

```
         v0 (original)
         │
         ├───────┬───────┐
         │       │       │
         v1      v2      v3
      (struct) (word) (length)
         │               │
         v4              v5
```

**Node Attributes:**
- **Color:** Gradient based on score (red = low, green = high)
- **Size:** Proportional to change_magnitude
- **Label:** Version number + score

**Edge Attributes:**
- **Color:** Green if score_delta > 0, red if < 0
- **Width:** Proportional to |score_delta|
- **Label:** change_type

### 4.3 Interpretation Guidelines

**Trend Classification:**

| Pattern | Interpretation | Action |
|---------|----------------|--------|
| Improving | Edits are effective | Continue current approach |
| Degrading | Edits are harmful | Revert to earlier version |
| Stable | Edits have no effect | Try different edit types |
| Oscillating | Inconsistent quality | Stabilize editing process |

**Causal Hint Interpretation:**

1. **High avg_score_delta + high occurrence:** Reliable improvement strategy
2. **High avg_score_delta + low occurrence:** Promising but needs validation
3. **Low/negative avg_score_delta:** Avoid this edit type

---

## 5. API Architecture

### 5.1 Endpoint Design

**RESTful Endpoints:**

| Endpoint | Method | Purpose | Query Params |
|----------|--------|---------|--------------|
| `/api/temporal/timeline` | GET | Get version sequence | prompt_id, start, end |
| `/api/temporal/statistics` | GET | Get trend & stats | prompt_id |
| `/api/temporal/causal-hints` | GET | Get correlation analysis | prompt_id |
| `/api/temporal/generate-synthetic` | POST | Create test data | prompt_id, days, versions_per_day |

### 5.2 Authentication Flow

```
1. User logs in → JWT token (contains user_id)
2. Client includes token: Authorization: Bearer <token>
3. Backend extracts user_id from token
4. All queries filter by: WHERE prompt.user_id = <authenticated_user_id>
5. Returns 404 if prompt doesn't belong to user
```

**Security Benefits:**
- Data isolation between users
- No access to other users' prompt histories
- Audit trail via user_id in database logs

### 5.3 Synthetic Data Generation (Testing)

**Purpose:** Generate 30+ days of history for testing without waiting.

**Algorithm:**

```
For each day in [1..30]:
    For each version in [1..versions_per_day]:
        1. Calculate timestamp (spread evenly across day)
        2. Generate version text (progressive modification)
        3. Compute score based on trend_type:
           - "improving": previous_score + random(0.5, 2.0) + noise
           - "degrading": previous_score - random(0.5, 2.0) + noise
           - "oscillating": 70 + 10*sin(version_count/4) + noise
        4. Create PromptVersion and JudgeScore records
        5. Link to parent via parent_version_id
```

**Key Features:**
- **User-specific:** Tied to authenticated user
- **Controllable trends:** Can generate all three patterns
- **Realistic noise:** ±5 point random variation
- **Metadata tagged:** `{"synthetic": True}` for filtering

---

## 6. Implementation Statistics

**Code Metrics:**

| Component | Lines of Code | Files |
|-----------|---------------|-------|
| Temporal Analysis Engine | 175 | `backend/temporal_analysis.py` |
| API Endpoints | 355 | `backend/routers/temporal.py` |
| Data Generator | 232 | `storage/temporal_data_generator.py` |
| Database Models | 28 | `packages/db/models.py` (temporal fields) |
| **Total** | **790** | **4** |

**Dependencies:**
- `scipy.stats` (linear regression)
- `numpy` (numerical operations)
- `difflib` (text similarity)
- `sqlalchemy` (ORM)
- `fastapi` (REST API)

**Test Coverage:** (Not yet implemented for temporal module)

---

## 7. Research Background & Literature Review

### 7.1 Temporal Modeling in Software Evolution

**Related Work:**

**Time Series Analysis in Software Engineering:**
- Software metrics evolution (code complexity over commits)
- Bug density trends over release cycles
- Developer productivity analysis over time

**Key Concepts Applied:**

1. **Trend Detection:**
   - **Moving Averages:** Smooth noisy data by averaging over sliding windows
   - **Exponential Smoothing:** Weight recent observations more heavily (α parameter)
   - **Linear Regression:** Our chosen method for computational simplicity
   - **LOESS (Locally Weighted Scatterplot Smoothing):** Non-parametric regression for non-linear trends

2. **Drift Detection:**
   - **Concept Drift:** When underlying data distribution changes over time
   - **Application:** Prompt effectiveness may drift as user skill improves or task complexity changes
   - **Detection:** Statistical tests (Kolmogorov-Smirnov, Mann-Kendall)

3. **Change-Point Detection Methods:**
   
   | Method | Complexity | Pros | Cons |
   |--------|------------|------|------|
   | **Threshold-based** (ours) | O(n) | Fast, interpretable | Fixed threshold, no significance test |
   | **CUSUM** | O(n) | Detects small shifts | Requires parameter tuning |
   | **Bayesian** | O(n²) | Probabilistic, uncertainty quantification | Computationally expensive |
   | **PELT** | O(n log n) | Optimal segmentation | Complex implementation |

4. **Temporal Smoothing:**
   - **Purpose:** Reduce noise in score sequences
   - **Methods:** 
     - Simple moving average (SMA): `score_smooth[i] = mean(scores[i-k:i+k])`
     - Exponential moving average (EMA): `score_smooth[i] = α·score[i] + (1-α)·score_smooth[i-1]`
     - Savitzky-Golay filter: Polynomial smoothing preserving peaks
   - **Not Implemented:** Could improve trend detection reliability

### 7.2 Version Control & Evolution Analysis

**Version Chain Concepts:**

1. **Parent-Child Relationships:**
   - DAG (Directed Acyclic Graph) structure
   - Each version has ≤1 parent, ≥0 children
   - Enables branching (experimental edits without affecting main line)

2. **Timeline Reconstruction:**
   - **Topological Sort:** Order versions respecting parent-child constraints
   - **Timestamps:** Resolve ambiguity when multiple valid orderings exist
   - **Breadth-First Traversal:** Reconstruct evolution chronologically

3. **Delta Encoding:**
   - **Full Text Storage (our approach):** Each version stores complete text
   - **Delta Storage (alternative):** Store only differences (diffs) from parent
   - **Trade-off:** Storage space vs. reconstruction speed

**Historical Metadata Tracking:**

| Field | Purpose | Example Values |
|-------|---------|----------------|
| `parent_version_id` | Chain linking | UUID or null (root) |
| `change_type` | Edit classification | "structure", "wording", "length", "other" |
| `change_magnitude` | Edit intensity | 0.0 (no change) to 1.0 (total rewrite) |
| `created_at` | Temporal ordering | ISO 8601 timestamp |
| `source` | Provenance tracking | "user_edit", "agent_enhancement", "synthetic" |

### 7.3 Causal Inference in Observational Data

**Correlation vs. Causation:**

```
Correlation: P(Score↑ | Edit=Structure) > P(Score↑ | Edit=Wording)
Causation:   Edit=Structure → Score↑ (mechanistic relationship)
```

**Threats to Causal Validity:**

1. **Confounding:** 
   - User skill level affects both edit choice and score improvement
   - Prompt complexity influences which edit types are viable

2. **Selection Bias:**
   - Users may apply structural changes only to low-scoring prompts
   - Creates spurious correlation

3. **Reverse Causality:**
   - High scores may discourage major edits (ceiling effect)
   - Low scores may trigger structural rewrites

**Methods for Causal Inference (Not Implemented):**

| Method | Approach | Requirements |
|--------|----------|--------------|
| **Randomized Controlled Trial (RCT)** | Random edit assignment | Experimental control (difficult for prompts) |
| **Instrumental Variables (IV)** | Find variable affecting edit but not score | Valid instrument (hard to find) |
| **Regression Discontinuity** | Exploit threshold effects | Sharp cutoff in treatment assignment |
| **Difference-in-Differences** | Compare treatment/control over time | Parallel trends assumption |
| **Propensity Score Matching** | Match similar prompts with different edits | Rich covariate data |

**Our Approach: Causal Hints**
- Acknowledge limitations (correlation ≠ causation)
- Provide suggestive evidence for hypothesis generation
- Label output as "hints" not "causal effects"

### 7.4 Edit-Type Correlation Analysis

**Performance Delta Calculation:**

```
Δ_score = score(version_child) - score(version_parent)
```

**Temporal Alignment:**
- Ensure parent-child pairs are consecutive (no skipped versions)
- Filter out branches (only follow main timeline)
- Weight by recency (recent edits more relevant than historical)

**Statistical Tests (Future Work):**

1. **t-test:** Compare mean Δ_score between edit types
   ```
   H₀: μ_structure = μ_wording
   H₁: μ_structure ≠ μ_wording
   ```

2. **ANOVA:** Compare means across all edit types simultaneously
   ```
   H₀: μ_structure = μ_wording = μ_length = μ_other
   ```

3. **Effect Size:** Cohen's d for practical significance
   ```
   d = (μ₁ - μ₂) / σ_pooled
   ```

**Correlation Coefficients:**

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **Pearson r** | `cov(X,Y) / (σ_X · σ_Y)` | Linear correlation (-1 to +1) |
| **Spearman ρ** | Rank-based correlation | Monotonic relationships |
| **Kendall τ** | Concordance measure | Robust to outliers |

---

## 8. Hypothesis Testing Framework

### 8.1 Primary Research Hypotheses

**H1: Edit Type Effectiveness**
- **Hypothesis:** Structural changes yield higher score improvements than wording changes
- **Prediction:** `avg_Δ_score(structure) > avg_Δ_score(wording) > avg_Δ_score(other)`
- **Rationale:** Major rewrites address fundamental issues; minor tweaks have limited impact
- **Test:** One-way ANOVA on Δ_score grouped by change_type

**H2: Change Magnitude Correlation**
- **Hypothesis:** Larger changes correlate with larger score deltas (positive or negative)
- **Prediction:** `|Δ_score| ∝ change_magnitude` (positive correlation)
- **Rationale:** Small edits have small effects; large edits have large effects
- **Test:** Pearson correlation between change_magnitude and |Δ_score|

**H3: Diminishing Returns**
- **Hypothesis:** Incremental edits yield smaller improvements over time
- **Prediction:** `Δ_score[i] > Δ_score[i+1]` (decreasing returns)
- **Rationale:** Early edits fix obvious issues; later edits yield marginal gains
- **Test:** Regression of Δ_score on version_no (expect negative slope)

**H4: Learning Effect**
- **Hypothesis:** Users improve at prompt engineering over time
- **Prediction:** Later prompts (by created_at) have higher baseline scores
- **Rationale:** Experience accumulates; users internalize best practices
- **Test:** Linear regression of score on timestamp (across different prompts)

### 8.2 Feature Correlation Predictions

**Predicted Correlates of Score Improvement:**

| Feature | Expected Correlation | Strength | Mechanism |
|---------|---------------------|----------|-----------|
| **change_type=structure** | Positive (+++) | Strong | Addresses core prompt design issues |
| **change_magnitude** | Positive (++) | Moderate | Larger changes → more opportunity for improvement |
| **prompt_length** | Positive (+) | Weak | More context → better AI responses |
| **edit_frequency** | Negative (-) | Weak | Too many edits → lack of clear vision |
| **time_since_last_edit** | Neutral (0) | None | No inherent relationship |

**Interaction Effects:**

1. **Structure × Magnitude:** Structural changes with high magnitude → highest gains
2. **Wording × Frequency:** Frequent wording changes → no cumulative benefit
3. **Length × Structure:** Structural changes that expand length → synergistic effect

### 8.3 Temporal Pattern Hypotheses

**Pattern 1: Progressive Improvement**
```
Score trajectory: Low → Medium → High (monotonic increase)
Edit pattern: Structure → Wording → Polish
Expected frequency: 60% of prompts
```

**Pattern 2: Exploration Phase**
```
Score trajectory: Low → High → Low → High (oscillation)
Edit pattern: Experiment → Fail → Learn → Succeed
Expected frequency: 25% of prompts
```

**Pattern 3: Plateau Effect**
```
Score trajectory: Low → High → Stable
Edit pattern: Major rewrite → Diminishing returns
Expected frequency: 10% of prompts
```

**Pattern 4: Degradation**
```
Score trajectory: High → Medium → Low (decrease)
Edit pattern: Over-optimization → Complexity creep
Expected frequency: 5% of prompts
```

### 8.4 Validation Methodology

**Dataset Requirements:**
- Minimum 30 days of history (natural or synthetic)
- Minimum 50 version transitions per edit type
- Balanced distribution of edit types
- Multiple users (to control for individual variation)

**Evaluation Metrics:**

1. **Prediction Accuracy:** Can we predict Δ_score from change_type?
   ```
   R² = 1 - (SS_residual / SS_total)
   ```

2. **Classification Accuracy:** Can we classify high/low impact edits?
   ```
   Accuracy = (TP + TN) / (TP + TN + FP + FN)
   ```

3. **Trend Detection Precision/Recall:**
   ```
   Precision = True_positives / (True_positives + False_positives)
   Recall = True_positives / (True_positives + False_negatives)
   ```

**Validation Protocol:**
1. Generate synthetic data with known patterns (ground truth)
2. Run temporal analysis algorithms
3. Compare detected patterns vs. ground truth
4. Measure precision, recall, F1 score
5. Tune thresholds to maximize F1

---

## 9. Limitations and Future Work

### 7.1 Current Limitations

1. **Linear Trend Assumption:**
   - Misses non-linear patterns (exponential, logarithmic, sinusoidal)
   - Solution: Implement polynomial regression or time series decomposition

2. **Simple Change-Point Detection:**
   - Sensitive to noise (short-term fluctuations)
   - No statistical significance testing
   - Solution: Use CUSUM or Bayesian methods with confidence intervals

3. **Correlation ≠ Causation:**
   - No confounding variable control
   - No randomization or experimental design
   - Solution: Implement propensity score matching or instrumental variables

4. **No Seasonal Decomposition:**
   - Can't separate trend, seasonality, noise
   - Solution: Use STL decomposition or ARIMA models

5. **Fixed Time Windows:**
   - No adaptive windowing based on data density
   - Solution: Implement sliding window with variable size

### 7.2 Future Enhancements

**Advanced Temporal Modeling:**
- ARIMA/SARIMA for time series forecasting
- Hidden Markov Models for state transitions
- Recurrent Neural Networks for pattern recognition

**Rigorous Causal Inference:**
- A/B testing framework (randomized edit suggestions)
- Difference-in-differences analysis
- Granger causality tests
- Mediation analysis (direct vs. indirect effects)

**Visualization:**
- Interactive timeline with zoom/pan
- Real-time updates (WebSocket)
- Comparison view (multiple prompts side-by-side)
- Heatmaps for change_type × time period

**Performance Optimization:**
- Materialized views for pre-computed statistics
- Caching layer (Redis) for frequently accessed timelines
- Batch processing for large histories
- Incremental updates (don't recompute entire timeline)

---

## 10. Conclusion

We implemented a comprehensive temporal analysis system for prompt engineering that:

1. **Models prompts as time series** using linear regression for trend detection
2. **Tracks version chains** via self-referential database schema with parent-child links
3. **Detects significant transitions** using threshold-based change-point detection
4. **Provides causal hints** through correlation analysis of edit types and score deltas
5. **Ensures data security** via user-authenticated API endpoints with JWT tokens

**Key Innovations:**
- Database-first architecture (not file-based)
- Real-time temporal queries with O(n) algorithms
- Synthetic data generation for rapid testing
- Multi-user isolation with authentication

**Research Contributions:**
- Documented mathematical formulations for trend detection
- Designed version chain data structure for prompt evolution
- Established correlation analysis methodology for edit effectiveness
- Created interpretable visualization specifications

**Impact:**
This system enables prompt engineers to:
- Understand long-term evolution of their prompts
- Identify which edit types are most effective
- Detect when edits start degrading performance
- Make data-driven decisions about prompt refinement strategies

**Limitations:**
Our approach provides exploratory correlation analysis, not rigorous causal inference. Future work should implement experimental designs (A/B testing) and advanced statistical methods (propensity score matching) to establish causation.

---

## References

1. **Linear Regression for Trend Detection:**
   - `scipy.stats.linregress` documentation
   - Montgomery, D.C., Peck, E.A., Vining, G.G. (2012). *Introduction to Linear Regression Analysis*

2. **Change-Point Detection:**
   - Killick, R., Fearnhead, P., Eckley, I.A. (2012). *Optimal Detection of Changepoints With a Linear Computational Cost*
   - Page, E.S. (1954). *Continuous Inspection Schemes*

3. **Time Series Analysis:**
   - Box, G.E.P., Jenkins, G.M., Reinsel, G.C., Ljung, G.M. (2015). *Time Series Analysis: Forecasting and Control*
   - Hyndman, R.J., Athanasopoulos, G. (2021). *Forecasting: Principles and Practice*

4. **Causal Inference:**
   - Pearl, J., Mackenzie, D. (2018). *The Book of Why: The New Science of Cause and Effect*
   - Imbens, G.W., Rubin, D.B. (2015). *Causal Inference in Statistics, Social, and Biomedical Sciences*

5. **Version Control & DAGs:**
   - Spinellis, D. (2005). *Version Control Systems*
   - Directed Acyclic Graphs in database schema design

---

**End of Report**

*This research report documents the implementation of Week 12's temporal analysis system as part of the Self-Learning Prompt Engineering System course project.*

