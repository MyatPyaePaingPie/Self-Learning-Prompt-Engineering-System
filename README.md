# Self-Learning Prompt Engineering System

A comprehensive system that automatically improves prompts through intelligent rewriting, scoring, and learning from feedback.

> **🚀 New here?** Check out the [Quick Setup Guide](SETUP_GUIDE.md) for step-by-step instructions!

## Table of Contents
- [Features](#features)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Installation](#installation)
- [Running the System](#running-the-system)
- [Testing](#testing)
- [File Formats](#file-formats)
- [API Documentation](#api-documentation)
- [Multi-Agent System](#multi-agent-system)
- [Contributing](#contributing)

---

## Features

- **Automatic Prompt Improvement**: Uses Groq's LLM API to enhance prompt clarity, specificity, and actionability
- **Multi-Agent Collaboration** ✨ NEW: 3 specialized agents (syntax, structure, domain) optimize prompts collaboratively with weighted voting
- **Intelligent Scoring**: Multi-dimensional scoring system evaluating prompts on 5 key criteria
- **Learning Loop**: Adapts improvement strategies based on performance feedback
- **Model Registry**: Centralized configuration for multiple Groq models with cost/speed optimization
- **RESTful API**: Complete FastAPI backend with comprehensive endpoints
- **Database Persistence**: SQLite storage for prompts, versions, and scoring history
- **File Storage System**: Organized file storage for prompts and results with metadata support
- **Web Interface**: Streamlit-based UI for easy interaction
- **Deterministic Fallbacks**: Template-based systems ensure reliability when API is unavailable
- **Full Observability**: Track agent contributions, decisions, and effectiveness over time

---

## Repository Structure

```
Self-Learning-Prompt-Engineering-System/
├── backend/                    # FastAPI backend service
│   ├── api.py                 # Main API with all endpoints
│   ├── requirements.txt       # Backend dependencies
│   └── README.md             # Backend documentation
│
├── apps/web/                  # Streamlit web interface
│   ├── streamlit_app.py      # UI application
│   ├── requirements.txt      # Web dependencies
│   └── README.md            # Web app documentation
│
├── packages/                  # Shared core logic
│   ├── core/                 # Business logic
│   │   ├── engine.py        # Prompt improvement engine
│   │   ├── judge.py         # Scoring system
│   │   └── learning.py      # Learning loop
│   └── db/                   # Database layer
│       ├── models.py        # SQLAlchemy models
│       ├── crud.py          # Database operations
│       ├── session.py       # Database connection
│       └── migrations/      # SQL migration scripts
│           └── 001_init.sql
│
├── storage/                   # File storage system
│   ├── file_storage.py       # File operations module
│   ├── prompts/              # Saved prompts
│   ├── results/              # Processing results
│   └── README.md            # Storage documentation
│
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   │   └── test_api.py      # API endpoint tests
│   ├── integration/          # Integration tests
│   │   └── test_integration.py
│   ├── conftest.py          # Pytest configuration
│   ├── requirements.txt     # Test dependencies
│   └── README.md           # Testing documentation
│
├── docker-compose.yml        # Docker orchestration
└── README.md                # This file
```

---

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`  
The web interface will be available at `http://localhost:8501`

### Option 2: Manual Setup (Development)

Follow the [Installation](#installation) section below.

---

## Environment Setup

### ⚠️ IMPORTANT: Groq API Key Required

This system uses **Groq's LLM API** to improve prompts. You **must** set up your API key before running the system.

### Step 1: Get Your Groq API Key

1. Go to https://console.groq.com/
2. Sign up or log in (it's free!)
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you'll need it in the next step)

### Step 2: Create `.env` File

Create a file named `.env` in the project root directory:

```bash
cd /path/to/Self-Learning-Prompt-Engineering-System
touch .env
```

Add your API key to the `.env` file:

```bash
GROQ_API_KEY=your-actual-groq-api-key-here
```

**Example `.env` file:**
```
GROQ_API_KEY=gsk_abc123xyz456def789
```

### Step 3: Install python-dotenv

The system needs this package to load environment variables:

```bash
pip install python-dotenv
```

---

## Installation

### Prerequisites

- **Python 3.11 or higher**
- **pip** (Python package manager)
- **Groq API Key** (see [Environment Setup](#environment-setup))
- SQLite (built into Python - no installation needed)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Self-Learning-Prompt-Engineering-System.git
cd Self-Learning-Prompt-Engineering-System
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Set Up Environment Variables

**Create your `.env` file** (see [Environment Setup](#environment-setup) for details):

```bash
echo "GROQ_API_KEY=your-actual-api-key-here" > .env
```

### Step 4: Install Dependencies

```bash
# Install python-dotenv first
pip install python-dotenv

# Backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Web interface dependencies
cd apps/web
pip install -r requirements.txt
cd ../..

# Test dependencies (optional)
cd tests
pip install -r requirements.txt
cd ..
```

### Step 5: Setup Database

Create the SQLite database:

```bash
python -c "from packages.db.models import Base; from packages.db.session import engine; Base.metadata.create_all(engine)"
```

This creates a `prompter.db` file in your project root with all necessary tables.

**Optional: Use a different database location:**

```bash
export DATABASE_URL="sqlite:///./my_custom.db"
```

---

## Running the System

### ⚠️ Before Running

Make sure you have:
1. ✅ Created your `.env` file with `GROQ_API_KEY`
2. ✅ Activated your virtual environment: `source venv/bin/activate`
3. ✅ Installed all dependencies

### Running the Backend API

From the **project root directory**:

```bash
cd /path/to/Self-Learning-Prompt-Engineering-System
source venv/bin/activate
python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`  
API documentation: `http://localhost:8000/docs`

### Running the Web Interface

Open a new terminal window/tab:

```bash
cd /path/to/Self-Learning-Prompt-Engineering-System
source venv/bin/activate
cd apps/web
streamlit run streamlit_app.py
```

The web interface will be available at: `http://localhost:8501`

### Running Both Together

Use two terminal windows:

**Terminal 1 (Backend):**
```bash
cd /path/to/Self-Learning-Prompt-Engineering-System
source venv/bin/activate
python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd /path/to/Self-Learning-Prompt-Engineering-System
source venv/bin/activate
cd apps/web
streamlit run streamlit_app.py
```

---

## Testing

### Running Unit Tests

```bash
# From project root
pytest tests/unit/test_api.py -v
```

### Running Integration Tests

**Note:** The backend must be running for integration tests.

```bash
# Start backend first (in one terminal)
python -m uvicorn backend.api:app --reload &

# Run tests (in another terminal)
pytest tests/integration/test_integration.py -v
```

### Running All Tests

```bash
pytest tests/ -v
```

---

## File Formats

### 1. Database Schema (SQLite)

The system uses four main tables:

- **`prompts`**: Original prompt submissions
  - `id` (UUID, Primary Key)
  - `user_id` (TEXT, Optional)
  - `original_text` (TEXT)
  - `created_at` (TIMESTAMPTZ)

- **`prompt_versions`**: All variations and improvements
  - `id` (UUID, Primary Key)
  - `prompt_id` (UUID, Foreign Key)
  - `version_no` (INT) - 0 for original, 1+ for improvements
  - `text` (TEXT)
  - `explanation` (JSONB) - Improvement explanation
  - `source` (TEXT) - 'original' or 'engine/v1'
  - `created_at` (TIMESTAMPTZ)

- **`judge_scores`**: Multi-dimensional scoring results
  - `id` (UUID, Primary Key)
  - `prompt_version_id` (UUID, Foreign Key)
  - `clarity` (NUMERIC 0-10)
  - `specificity` (NUMERIC 0-10)
  - `actionability` (NUMERIC 0-10)
  - `structure` (NUMERIC 0-10)
  - `context_use` (NUMERIC 0-10)
  - `total` (NUMERIC, Generated)
  - `feedback` (JSONB) - Detailed feedback
  - `created_at` (TIMESTAMPTZ)

- **`best_heads`**: Tracks best-performing version for each prompt
  - `prompt_id` (UUID, Primary Key)
  - `prompt_version_id` (UUID, Foreign Key)
  - `score` (NUMERIC)
  - `updated_at` (TIMESTAMPTZ)

**Database File:**
- SQLite database stored in `prompter.db` at project root
- No server installation required
- Portable - can copy the .db file to backup/share data

### 2. File Storage Format

**Prompts Directory** (`storage/prompts/`):
- Plain text files
- Format: `{prompt_id}.txt`
- Example: `factorial_prompt.txt`

**Results Directory** (`storage/results/`):
- Plain text files
- Format: `{result_id}.txt`
- Example: `factorial_solution.txt`

**CSV Learning Logs** (`storage/*.csv`):
- Sequential ID system (001, 002, 001.1 for rewrites)
- Columns: `prompt_id`, `llm_name`, `prompt`, `original_response`, `rewritten_prompt`, `rewritten_response`, `learning_memory`, `timestamp`

### 3. API Request/Response Formats

**Create Prompt Request:**
```json
{
  "userId": "optional-user-id",
  "text": "Your prompt text here"
}
```

**Create Prompt Response:**
```json
{
  "promptId": "uuid",
  "versionId": "uuid",
  "versionNo": 1,
  "improved": "Improved prompt text",
  "explanation": {
    "bullets": ["Point 1", "Point 2"],
    "diffs": [{"from": "original", "to": "improved"}]
  },
  "judge": {
    "clarity": 8.0,
    "specificity": 8.0,
    "actionability": 8.0,
    "structure": 8.0,
    "context_use": 8.0,
    "total": 40.0,
    "feedback": {
      "pros": ["Pro 1", "Pro 2"],
      "cons": ["Con 1"],
      "summary": "Overall assessment"
    }
  }
}
```

---

## API Documentation

### Base URL
`http://localhost:8000`

### Endpoints

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "message": "Self-Learning Prompt Engineering System API",
  "version": "1.0.0"
}
```

#### `POST /v1/prompts`
Create a new prompt and generate first improvement.

**Request Body:**
```json
{
  "text": "Your prompt text"
}
```

#### `GET /v1/prompts/{prompt_id}`
Get prompt details with history.

#### `POST /v1/prompts/{prompt_id}/improve`
Generate additional improvement for existing prompt.

**Request Body:**
```json
{
  "strategy": "v1"
}
```

#### `POST /v1/versions/{version_id}/judge`
Re-judge a specific prompt version.

#### `POST /v1/prompts/{prompt_id}/learn`
Update learning rules based on prompt history.

#### `GET /v1/metrics`
Get system metrics.

### Interactive API Documentation

Visit `http://localhost:8000/docs` when the API is running for full interactive documentation.

---

## Contributing

### Team Members

- **Paing**
- **Atang**
- **Bellul**

### Development Workflow

1. Create a feature branch from `main`
2. Make your changes with tests
3. Run tests locally
4. Submit a pull request
5. Code review and merge

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions small and focused

---

## Troubleshooting

### Common Issues

**Issue: "The api_key client option must be set" or GROQ_API_KEY error**

This means your `.env` file is not set up correctly:

1. Make sure you have a `.env` file in the project root
2. Verify it contains: `GROQ_API_KEY=your-actual-key`
3. Make sure `python-dotenv` is installed: `pip install python-dotenv`
4. Restart the backend after creating/editing the `.env` file

**Issue: "Module not found" errors**

Make sure you're in the virtual environment:

```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
pip install -r apps/web/requirements.txt
```

**Issue: "Could not import module 'api'" or "No module named 'packages'"**

Run the backend from the project root, not from the backend directory:

```bash
# CORRECT - from project root
cd /path/to/Self-Learning-Prompt-Engineering-System
python -m uvicorn backend.api:app --reload

# INCORRECT - don't run from backend/
```

**Issue: "Connection refused" when web app tries to connect to API**

Make sure the backend is running on port 8000:
```
Backend: http://localhost:8000
Web App: http://localhost:8501
```

**Issue: Port already in use**

Find and kill the process using the port:

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

---

## Multi-Agent System

**Week 11 Assignment - Collaborative Prompt Optimization**

The system now includes a multi-agent architecture where specialized AI agents collaborate to optimize prompts:

### Key Features

- **3 Specialized Agents**: Each focuses on one aspect (syntax, structure, domain)
- **Multiple Groq Models**: Fast models for simple tasks, powerful models for complex reasoning
- **Weighted Voting**: Coordinator selects best improvement based on scores
- **Full Observability**: Track agent contributions, decisions, and effectiveness
- **Cost Optimized**: 62% cost reduction vs single-model approach

### Quick Start

```bash
# Use multi-agent enhancement
curl -X POST http://localhost:8001/prompts/multi-agent-enhance \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your prompt here", "enhancement_type": "general"}'

# View agent effectiveness
curl -X GET http://localhost:8001/prompts/agent-effectiveness \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Architecture

```
SyntaxAgent (8B) ──┐
                   ├──> AgentCoordinator (Weighted Voting) ──> Final Prompt
StructureAgent(8B) ─┤
                    │
DomainAgent (70B) ──┘
```

### Components

- **Model Registry**: Centralized Groq model configuration (`packages/core/model_config.py`)
- **Agent Registry**: Factory pattern for agent creation (`packages/core/agent_registry.py`)
- **Agents**: Specialized analyzers (`packages/core/multi_agent.py`)
- **Coordinator**: Weighted voting system (`packages/core/agent_coordinator.py`)
- **Storage**: CSV tracking of contributions (`storage/file_storage.py`)

### Documentation

For complete documentation, API reference, usage examples, and testing guide, see:

**📖 [MULTI_AGENT_SYSTEM.md](MULTI_AGENT_SYSTEM.md)**

Includes:
- Detailed architecture and component reference
- API endpoint documentation with examples
- Adding new agents guide
- Cost & performance analysis
- Configuration options
- Troubleshooting guide

---

## Support

For questions or issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review component READMEs:
   - [Backend README](backend/README.md)
   - [Web App README](apps/web/README.md)
   - [Storage README](storage/README.md)
   - [Tests README](tests/README.md)
   - [Multi-Agent System](MULTI_AGENT_SYSTEM.md) ⭐ NEW
3. Open an issue on GitHub
4. Text or call each other
5. Email prof or sponsor

---

**Built with ❤️ by the Self-Learning Prompt Engineering Team**

