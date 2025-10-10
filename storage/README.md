# Self-Learning Prompt Engineering System

A comprehensive system that automatically improves prompts through intelligent rewriting, scoring, and learning from feedback.

## Features

- **Automatic Prompt Improvement**: Uses strategic rewriting to enhance prompt clarity, specificity, and actionability
- **Intelligent Scoring**: Multi-dimensional scoring system evaluating prompts on 5 key criteria
- **Learning Loop**: Adapts improvement strategies based on performance feedback
- **RESTful API**: Complete FastAPI backend with comprehensive endpoints
- **Database Persistence**: PostgreSQL storage for prompts, versions, and scoring history
- **File Storage System**: Organized file storage for prompts and results with metadata support
- **Deterministic Fallbacks**: Heuristic-based systems ensure reliability when external services fail

## Quick Start

### Using Docker Compose (Recommended)

```bash
cd self-learning-prompter
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### Manual Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Setup Database**
```bash
# Create PostgreSQL database and run migrations
psql -U user -d prompter_db -f packages/db/migrations/001_init.sql
```

3. **Run API**
```bash
uvicorn apps.api.main:app --reload
```

## File Storage System

The enhanced file storage system provides organized storage for prompts, results, and **CSV learning data** with sequential ID tracking.

### Directory Structure
- `prompts/` - Stores original and improved prompts
- `results/` - Stores processing results and outputs
- **NEW**: CSV files with learning data using sequential ID system (001, 002, 001.1, etc.)

### Basic File Storage

```python
from file_storage import FileStorage

# Initialize storage
storage = FileStorage()

# Save a prompt
prompt_file = storage.save_prompt(
    text="Write a Python function to calculate factorial",
    prompt_id="factorial_prompt"
)

# Save a result
result_file = storage.save_result(
    text="def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
    result_id="factorial_solution"
)

# List files
prompts = storage.list_prompts()
results = storage.list_results()
```

### NEW: CSV Learning System with Sequential IDs

**Sequential ID System:**
- **New prompts**: 001, 002, 003, ...
- **Rewritten prompts**: 001.1, 002.1, 003.1, ...
- **Auto-generated** based on existing entries

**CSV Usage:**
```python
# Save new prompt (gets ID: 001)
prompt_data = {
    'llm_name': 'GPT-4',
    'prompt': 'Write a sorting algorithm',
    'original_response': 'Here is bubble sort...',
    'learning_memory': 'Basic request yielded simple solution'
}
storage.save_to_csv('learning_log', prompt_data)

# Save rewrite (gets ID: 001.1)
rewrite_data = {
    'llm_name': 'GPT-4',
    'prompt': 'Write efficient merge sort with complexity analysis',
    'original_response': 'Here is optimized merge sort...',
    'learning_memory': 'Specific requirements improve response quality'
}
storage.save_to_csv('learning_log', rewrite_data, is_rewrite=True, base_prompt_id='001')

# Read and search CSV data
entries = storage.read_from_csv('learning_log')
matches = storage.search_csv_entries('learning_log', 'sorting')
```

**Interactive Data Collection:**
```python
# Guided prompts for user input
data = storage.collect_prompt_data_interactive()
storage.save_to_csv('my_prompts', data)  # Gets next sequential ID
```

**With Metadata:**
```python
# Save with metadata
storage.save_prompt(
    text="Create a web scraper for news articles",
    prompt_id="webscraper_prompt",
    metadata={"author": "Atang", "type": "coding", "difficulty": "intermediate"}
)
```

### Running the File Storage Script

**Demo the enhanced system with CSV Sequential IDs:**
```bash
cd self-learning-prompter
python file_storage.py
```

Expected output with sequential IDs:
```
📊 CSV Functionality Demo (Sequential ID System)
--------------------------------------------------
Entry 1: ID 001 - GPT-4
Entry 2: ID 001.1 - GPT-4
Entry 3: ID 002 - Claude-3
```

**Try the CSV usage example:**
```bash
python csv_usage_example.py
```

**Run tests:**
```bash
# Run specific file storage tests (includes CSV tests)
pytest tests/unit/test_file_storage.py -v

# Quick integration test
python tests/unit/test_file_storage.py
```

### File Storage API

**Basic File Storage:**
- `save_prompt(text, prompt_id=None, metadata=None)` - Save prompt to `prompts/`
- `save_result(text, result_id=None, metadata=None)` - Save result to `results/`
- `load_prompt(filename)` - Load prompt from file
- `load_result(filename)` - Load result from file
- `list_prompts()` - List all prompt files
- `list_results()` - List all result files

**NEW: CSV Learning API:**
- `save_to_csv(filename, data, is_rewrite=False, base_prompt_id=None)` - Save with sequential ID
- `read_from_csv(filename)` - Read all CSV entries
- `search_csv_entries(filename, search_term, field=None)` - Search CSV data
- `collect_prompt_data_interactive()` - Interactive data collection

## API Usage

### Create and Improve a Prompt

```bash
curl -X POST "http://localhost:8000/v1/prompts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Help me code"}'
```

**Response:**
```json
{
  "promptId": "uuid",
  "versionId": "uuid", 
  "versionNo": 1,
  "improved": "You are a senior Python developer.\nTask: Help me design and implement clean, well-commented Python code for [task].\nDeliverables:\n- Step-by-step plan with rationale\n- Working code examples with docstrings and tests\n- Edge cases and performance notes\nConstraints: [Python version], [libraries allowed], [time], [I/O limits]\nIf information is missing, list 3–5 clarifying questions first, then proceed with reasonable assumptions.",
  "explanation": {
    "bullets": [
      "Added explicit role for the assistant",
      "Specified deliverables and output artifact", 
      "Inserted constraint section",
      "Required clarifying questions before solution"
    ],
    "diffs": [{"from": "Help me code", "to": "..."}]
  },
  "judge": {
    "clarity": 8.0,
    "specificity": 8.0,
    "actionability": 8.0,
    "structure": 8.0,
    "context_use": 8.0,
    "total": 40.0,
    "feedback": {...}
  }
}
```

### Get Prompt Details

```bash
curl "http://localhost:8000/v1/prompts/{promptId}"
```

### Generate Additional Improvements

```bash
curl -X POST "http://localhost:8000/v1/prompts/{promptId}/improve" \
  -H "Content-Type: application/json" \
  -d '{"strategy": "v1"}'
```

## Architecture

```
self-learning-prompter/
├── apps/
│   ├── api/                # FastAPI service (Prompt Engineer, Judge, Memory)
│   └── web/                # Next.js (or simple React) UI
├── packages/
│   ├── core/               # Shared Python lib: rewrite strategies, judge rubric, learning
│   └── db/                 # SQL migrations + DB access layer
├── infra/
│   ├── docker/             # Dockerfiles
│   └── github/             # GitHub Actions
├── tests/
│   ├── unit/
│   └── e2e/
└── README.md
```

## Core Components

### 1. Prompt Engine (`packages/core/engine.py`)
- **Strategy V1**: Template-based improvement with role assignment, deliverables specification, and constraint handling
- **Domain Detection**: Automatically identifies context (Python development, marketing, etc.)
- **Extensible**: Ready for ensemble strategies and LLM-powered improvements

### 2. Judge System (`packages/core/judge.py`)
- **Multi-dimensional Scoring**: Evaluates clarity, specificity, actionability, structure, and context use
- **Heuristic Baseline**: Deterministic scoring for reliability
- **Feedback Generation**: Structured pros/cons analysis

### 3. Learning Loop (`packages/core/learning.py`)
- **Performance Tracking**: Monitors which improvements perform best
- **Rule Adaptation**: Adjusts improvement strategies based on historical success
- **Best Head Management**: Maintains the highest-scoring version of each prompt

## Database Schema

The system uses four main tables:
- `prompts`: Original prompt submissions
- `prompt_versions`: All variations and improvements
- `judge_scores`: Multi-dimensional scoring results  
- `best_heads`: Tracks the best-performing version for each prompt

## Testing

```bash
# Run unit tests
pytest tests/unit/ -v

# Run e2e tests
pytest tests/e2e/ -v

# Run all tests
pytest -v
```

## Development Workflow

1. Create `develop` from `main`
2. Work in `feature/<short-name>` branches
3. Small, frequent commits
4. Open PR to `develop` weekly; squash-merge after review
5. Promote `develop` → `main` after green tests

## Deployment

### Production Environment Variables

```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

### Docker Production Build

```bash
docker build -f infra/docker/api/Dockerfile -t prompter-api .
docker run -p 8000:8000 -e DATABASE_URL="..." prompter-api
```

## Future Enhancements

- **LLM Integration**: Replace heuristic engine and judge with LLM-powered versions
- **Ensemble Strategies**: Generate and compare multiple improvement approaches
- **Advanced Analytics**: Detailed performance metrics and trend analysis
- **Web Interface**: User-friendly frontend for prompt improvement
- **API Rate Limiting**: Production-ready request throttling
- **Caching Layer**: Performance optimization for frequent operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details