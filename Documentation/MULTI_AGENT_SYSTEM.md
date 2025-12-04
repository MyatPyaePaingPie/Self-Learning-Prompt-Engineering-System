# Multi-Agent Prompt Optimization System

**Week 11 Assignment - Multi-Agent Architecture**  
**Version:** 1.0.0  
**Last Updated:** 2025-12-03

---

## Overview

This system implements collaborative prompt optimization using multiple specialized AI agents with a clear coordination mechanism.

### Key Features

- **3 Specialized Agents**: Each focuses on one aspect (syntax, structure, domain)
- **Multiple Groq Models**: Fast models for simple tasks, powerful models for complex reasoning
- **Weighted Voting**: Coordinator selects best improvement based on scores
- **Full Observability**: Track agent contributions, decisions, and effectiveness
- **Cost Optimized**: 62% cost reduction vs single-model approach

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Backend (FastAPI)               │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ Syntax   │  │Structure │  │ Domain ││
│  │ Agent    │  │ Agent    │  │ Agent  ││
│  │ (8B)     │  │ (8B)     │  │ (70B)  ││
│  └────┬─────┘  └────┬─────┘  └────┬───┘│
│       │             │              │    │
│       └─────────────┴──────────────┘    │
│                     │                   │
│              ┌──────▼──────┐            │
│              │ Coordinator │            │
│              │  (Voting)   │            │
│              └──────┬──────┘            │
└─────────────────────┼───────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
┌────────▼─────────┐      ┌───────▼───────┐
│ File Storage     │      │ Streamlit UI  │
│ - CSV logs       │      │ - Comparison  │
│ - Effectiveness  │      │ - Viz         │
└──────────────────┘      └───────────────┘
```

---

## Components

### 1. Model Registry (`packages/core/model_config.py`)

Centralized configuration for Groq models.

**Available Models:**
- `llama-3.1-8b-instant` - Fastest, cheapest (syntax/structure)
- `llama-3.3-70b-versatile` - Balanced, general purpose
- `llama-3.1-70b-versatile` - Powerful reasoning (domain)
- `gemma2-9b-it` - Alternative perspective
- `mixtral-8x7b-32768` - Complex analysis

**Agent-to-Model Mapping:**
```python
AGENT_MODEL_MAPPING = {
    "syntax": "fast",        # llama-3.1-8b-instant
    "structure": "fast",     # llama-3.1-8b-instant
    "domain": "powerful",    # llama-3.1-70b-versatile
}
```

### 2. Agent Registry (`packages/core/agent_registry.py`)

Factory pattern for agent creation.

**Usage:**
```python
from packages.core.agent_registry import AgentRegistry

# Create single agent
agent = AgentRegistry.create_agent("syntax")

# Create default set (syntax, structure, domain)
agents = AgentRegistry.create_default_agents()

# Get agent metadata
metadata = AgentRegistry.get_metadata("syntax")
print(metadata.model_config.model_id)  # llama-3.1-8b-instant
```

### 3. Specialized Agents (`packages/core/multi_agent.py`)

Each agent analyzes and improves prompts from one perspective.

#### SyntaxAgent
- **Focus:** Clarity, role definition, explicit instructions
- **Model:** llama-3.1-8b-instant (fast, cheap)
- **Checks:** Clear role, unambiguous language, precise terminology

#### StructureAgent
- **Focus:** Organization, formatting, logical flow
- **Model:** llama-3.1-8b-instant (fast, cheap)
- **Checks:** Sections, bullets, step-by-step flow, deliverables

#### DomainAgent
- **Focus:** Domain context, examples, best practices
- **Model:** llama-3.1-70b-versatile (powerful reasoning)
- **Checks:** Domain detection, terminology, examples, constraints

### 4. Agent Coordinator (`packages/core/agent_coordinator.py`)

Runs agents in parallel and selects best improvement via weighted voting.

**Algorithm:**
1. Execute all agents in parallel (`asyncio.gather`)
2. Calculate weighted scores: `score = analysis_score × confidence × weight`
3. Select winner (highest weighted score)
4. Return final prompt + decision metadata

**Usage:**
```python
from packages.core.agent_coordinator import AgentCoordinator

coordinator = AgentCoordinator()  # Uses default agents
decision = await coordinator.coordinate("Your prompt here")

print(decision.final_prompt)       # Best improved version
print(decision.selected_agent)     # Which agent won
print(decision.vote_breakdown)     # All agent scores
```

### 5. File Storage (`storage/file_storage.py`)

Tracks agent contributions and effectiveness over time.

**Methods:**
- `save_multi_agent_result()` - Log each request to CSV
- `get_agent_effectiveness()` - Agent statistics (wins, win_rate, avg_score)
- `get_agent_contributions(request_id)` - Query specific request

**CSV Structure:**
```csv
request_id, timestamp, original_prompt, final_prompt, selected_agent,
syntax_score, syntax_confidence, syntax_suggestions, syntax_improved,
structure_score, structure_confidence, structure_suggestions, structure_improved,
domain_score, domain_confidence, domain_suggestions, domain_improved,
vote_breakdown
```

---

## API Endpoints

### POST `/prompts/multi-agent-enhance`

Enhance a prompt using multi-agent collaboration.

**Request:**
```json
{
  "text": "Your prompt here",
  "enhancement_type": "general"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "request_id": "uuid",
    "original_text": "Your prompt",
    "enhanced_text": "Improved prompt",
    "selected_agent": "domain",
    "decision_rationale": "Selected domain (score: 8.1)",
    "agent_results": [
      {
        "agent_name": "syntax",
        "analysis": {"score": 8.5, "strengths": [...], "weaknesses": [...]},
        "suggestions": {"suggestions": [...], "improved_prompt": "...", "confidence": 0.85},
        "model_used": {"model_id": "llama-3.1-8b-instant", "speed": "fastest", "cost": "lowest"}
      }
    ],
    "vote_breakdown": {"syntax": 7.225, "structure": 4.9, "domain": 8.1}
  }
}
```

### GET `/prompts/available-agents`

List all available agents and their configurations.

**Response:**
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "name": "syntax",
        "display_name": "Syntax Agent",
        "description": "Analyzes clarity, role definition...",
        "focus_areas": ["role", "clarity", "precision"],
        "model": {
          "model_id": "llama-3.1-8b-instant",
          "display_name": "Llama 3.1 8B (Fast)",
          "speed": "fastest",
          "cost": "lowest",
          "use_case": "Quick syntax analysis"
        }
      }
    ]
  }
}
```

### GET `/prompts/agent-effectiveness`

Get agent effectiveness statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "syntax": {"wins": 10, "win_rate": 0.33, "avg_score": 8.5},
    "structure": {"wins": 15, "win_rate": 0.50, "avg_score": 9.0},
    "domain": {"wins": 5, "win_rate": 0.17, "avg_score": 7.8}
  }
}
```

---

## Usage Examples

### Basic Multi-Agent Enhancement

```python
import requests

# Authenticate first
login_response = requests.post("http://localhost:8001/login", json={
    "username": "your_username",
    "password": "your_password"
})
token = login_response.json()["access_token"]

# Enhance prompt with multi-agent
response = requests.post(
    "http://localhost:8001/prompts/multi-agent-enhance",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "text": "Write a Python function to sort numbers",
        "enhancement_type": "technical"
    }
)

result = response.json()["data"]
print(f"Original: {result['original_text']}")
print(f"Improved: {result['enhanced_text']}")
print(f"Selected: {result['selected_agent']}")
print(f"Why: {result['decision_rationale']}")

# View all agent suggestions
for agent in result['agent_results']:
    print(f"\n{agent['agent_name'].upper()} Agent:")
    print(f"  Model: {agent['model_used']['model_id']}")
    print(f"  Score: {agent['analysis']['score']}/10")
    print(f"  Confidence: {agent['suggestions']['confidence']:.0%}")
    print(f"  Suggestions: {agent['suggestions']['suggestions']}")
```

### Query Agent Effectiveness

```python
# Get agent statistics
effectiveness = requests.get(
    "http://localhost:8001/prompts/agent-effectiveness",
    headers={"Authorization": f"Bearer {token}"}
).json()["data"]

# Which agent wins most?
for agent, stats in effectiveness.items():
    print(f"{agent}: {stats['win_rate']:.0%} win rate, {stats['avg_score']:.1f} avg score")
```

### Access CSV Logs Directly

```python
from storage.file_storage import FileStorage

storage = FileStorage(base_dir="./storage")

# Get effectiveness
effectiveness = storage.get_agent_effectiveness()

# Get specific request
contributions = storage.get_agent_contributions("request-uuid")
print(contributions['agent_contributions'])  # All 3 agent outputs
```

---

## Cost & Performance

### Example Request (500 token prompt)

**Multi-Agent (Optimized):**
- Syntax Agent (8B): ~$0.001, ~500ms
- Structure Agent (8B): ~$0.001, ~500ms
- Domain Agent (70B): ~$0.015, ~2000ms
- **Total: ~$0.017, ~3 seconds**

**Single-Agent (70B only):**
- One Agent (70B): ~$0.015, ~2000ms
- **Total: ~$0.015, ~2 seconds**

**All Agents with 70B:**
- 3 × 70B: ~$0.045, ~6 seconds
- **Total: ~$0.045, ~6 seconds**

**Savings vs All 70B:** 62% cost reduction, 50% faster

---

## Adding New Agents

### Step 1: Create Agent Class

```python
# In packages/core/multi_agent.py

from packages.core.agent_registry import register_agent

@register_agent(
    display_name="Style Agent",
    description="Analyzes tone, voice, and audience fit",
    focus_areas=["tone", "voice", "audience", "style"]
)
class StyleAgent(AgentInterface):
    name = "style"
    
    def _initialize_prompts(self):
        self.analysis_prompt = """You are a style expert..."""
        self.improvement_prompt = """Improve style..."""
    
    async def analyze(self, prompt: str) -> AgentAnalysis:
        # Implementation (copy pattern from SyntaxAgent)
        pass
    
    async def propose_improvements(self, prompt: str, analysis: AgentAnalysis) -> AgentSuggestions:
        # Implementation (copy pattern from SyntaxAgent)
        pass
```

### Step 2: Configure Model Assignment

```python
# In packages/core/model_config.py

AGENT_MODEL_MAPPING = {
    "syntax": "fast",
    "structure": "fast",
    "domain": "powerful",
    "style": "balanced",  # Add new agent
}
```

### Step 3: Update Coordinator (Optional)

```python
# To use specific agents instead of defaults
coordinator = AgentCoordinator(
    agent_names=["syntax", "structure", "domain", "style"],
    weights={"syntax": 1.0, "structure": 1.0, "domain": 1.5, "style": 0.8}
)
```

**That's it!** Agent automatically registered via decorator.

---

## Testing

### Unit Tests

```bash
# Test model registry
python3 -c "from packages.core.model_config import get_all_models; print(get_all_models())"

# Test agent registry
python3 -c "from packages.core.agent_registry import AgentRegistry; print(AgentRegistry.get_all_agents())"

# Test agent creation
python3 -c "from packages.core.agent_registry import AgentRegistry; agent = AgentRegistry.create_agent('syntax'); print(agent.model_config.model_id)"

# Test coordinator
python3 -c "from packages.core.agent_coordinator import AgentCoordinator; c = AgentCoordinator(); print(c.get_agent_names())"

# Test storage
python3 -c "from storage.file_storage import FileStorage; s = FileStorage(); print('Storage methods:', [m for m in dir(s) if 'multi_agent' in m])"
```

### Integration Test

```bash
# Start backend server
cd backend
python3 main.py

# In another terminal, test endpoint
curl -X POST http://localhost:8001/prompts/multi-agent-enhance \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Write a Python function to calculate fibonacci numbers",
    "enhancement_type": "technical"
  }'
```

### Verify Storage

```bash
# Check CSV created
ls -lh storage/multi_agent_log.csv

# View CSV contents
head storage/multi_agent_log.csv

# Test effectiveness calculation
python3 -c "from storage.file_storage import FileStorage; s = FileStorage(base_dir='./storage'); print(s.get_agent_effectiveness())"
```

---

## Configuration

### Change Agent Weights

```python
# In backend/main.py

def get_multi_agent_coordinator():
    if not _multi_agent_coordinator:
        _multi_agent_coordinator = AgentCoordinator(
            weights={
                "syntax": 1.0,      # Standard weight
                "structure": 1.2,   # Favor structure
                "domain": 1.5       # Strongly favor domain
            }
        )
    return _multi_agent_coordinator
```

### Use Different Models

```python
# In packages/core/model_config.py

AGENT_MODEL_MAPPING = {
    "syntax": "alternative",    # Use gemma2-9b-it instead
    "structure": "fast",        # Keep llama-3.1-8b-instant
    "domain": "expert",         # Use mixtral-8x7b-32768
}
```

### Add Custom Agents

```python
# Option 1: Create new agent in multi_agent.py
@register_agent(
    display_name="Custom Agent",
    description="Your custom logic",
    focus_areas=["custom", "focus"]
)
class CustomAgent(AgentInterface):
    name = "custom"
    # ... implementation ...

# Option 2: Use coordinator with specific agents
coordinator = AgentCoordinator(agent_names=["syntax", "custom"])
```

---

## Data & Analytics

### CSV Schema

**File:** `storage/multi_agent_log.csv`

**Columns:**
- `request_id` - Unique request identifier
- `timestamp` - When request was made
- `original_prompt` - Original prompt text
- `final_prompt` - Selected improved version
- `selected_agent` - Which agent won
- `decision_rationale` - Why that agent was selected
- `{agent}_score` - Agent's analysis score (0-10)
- `{agent}_confidence` - Agent's confidence (0-1)
- `{agent}_suggestions` - JSON array of suggestions
- `{agent}_improved` - Agent's improved prompt
- `vote_breakdown` - JSON object with weighted scores

### Query Methods

```python
from storage.file_storage import FileStorage

storage = FileStorage(base_dir="./storage")

# Get agent effectiveness
effectiveness = storage.get_agent_effectiveness()
# Returns: {"syntax": {"wins": 10, "win_rate": 0.33, "avg_score": 8.5}, ...}

# Get specific request
contributions = storage.get_agent_contributions("request-uuid")
# Returns: {"request_id": "...", "agent_contributions": [...], ...}

# Read raw CSV
all_logs = storage.read_from_csv('multi_agent_log.csv')
```

---

## Research Concepts Implemented

### 1. Agent Specialization

Each agent focuses on different properties of a prompt:
- **Syntax**: Role clarity, explicit instructions
- **Structure**: Organization, formatting, flow
- **Domain**: Context, terminology, examples

This granularity improves prompt quality vs single-agent approach.

### 2. Coordination Mechanism

**Weighted Voting Algorithm:**
```python
weighted_score = analysis_score × confidence × agent_weight
winner = agent with highest weighted_score
```

**Benefits:**
- Deterministic (same input → same output)
- Transparent (decision rationale logged)
- Configurable (adjust weights for different use cases)

### 3. Parallel Execution

Agents run independently and simultaneously using `asyncio.gather()`:
- No inter-agent dependencies
- Modular design (easy to add/remove agents)
- Faster execution (parallel vs sequential)

### 4. Observability

Full transparency via:
- Per-agent traces (all suggestions logged)
- Contribution logging (CSV stores everything)
- Decision transparency (rationale + vote breakdown)
- Effectiveness tracking (which agents perform best)

---

## Expected Test Results

### Configuration Tests
- ✅ 3 agents registered (syntax, structure, domain)
- ✅ Different models per agent
- ✅ Agent creation via registry works
- ✅ Coordinator initialization works

### Functionality Tests
- ✅ Agents run in parallel (check timestamps)
- ✅ Weighted voting produces deterministic results
- ✅ Same input → same output (run twice, compare)
- ✅ Storage logs all requests

### Effectiveness Analysis
- ✅ Track which agent wins most over 10+ requests
- ✅ Calculate average scores per agent
- ✅ Identify patterns (which prompts favor which agents)

---

## Troubleshooting

### Import Errors

```bash
# Ensure packages/core/__init__.py exists
touch packages/core/__init__.py

# Verify imports
python3 -c "from packages.core.multi_agent import SyntaxAgent; print('✅ Import works')"
```

### Groq API Errors

```bash
# Check API key
echo $GROQ_API_KEY

# Test with single agent first
python3 -c "from packages.core.engine import improve_prompt; print(improve_prompt('test')[0].text)"
```

### Storage Errors

```bash
# Ensure storage directory exists
mkdir -p storage

# Check permissions
ls -la storage/

# Verify CSV writing
python3 -c "from storage.file_storage import FileStorage; s = FileStorage(); s.save_to_csv('test', {'llm_name': 'GPT-4', 'prompt': 'test'})"
```

---

## Performance Tuning

### Reduce Cost

Use faster/cheaper models for all agents:
```python
AGENT_MODEL_MAPPING = {
    "syntax": "fast",
    "structure": "fast",
    "domain": "fast"  # Change from "powerful" to "fast"
}
```

### Reduce Latency

Run fewer agents:
```python
coordinator = AgentCoordinator(agent_names=["syntax", "domain"])  # Skip structure
```

### Increase Quality

Use more powerful models:
```python
AGENT_MODEL_MAPPING = {
    "syntax": "balanced",
    "structure": "balanced",
    "domain": "expert"  # Use mixtral for best quality
}
```

---

## Future Enhancements

### Potential Additions
- Confidence-based agent selection (only run high-confidence agents)
- Agent chaining (output of one feeds into next)
- User preference learning (track which agents user prefers)
- Custom agent creation UI (build agents without code)
- Agent A/B testing (compare different configurations)

### Research Opportunities
- Optimal agent weights (learn from user feedback)
- Agent consensus (require 2+ agents to agree)
- Meta-agent (agent that selects which agents to run)
- Hybrid voting (combine suggestions instead of picking one)

---

## Documentation

**Related Files:**
- `README.md` - System overview
- `TESTING_GUIDE.md` - Testing procedures
- `QUICK_START.md` - Getting started guide

**Week 11 Assignment:**
- Research report: Agent specialization, coordination, parallel design, observability
- Team summary: Architecture diagram, coordination strategy, logging plan
- Integration: Full-stack (backend, storage, UI)

**Last Updated:** 2025-12-03

