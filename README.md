# Self-Learning Prompt Engineering System

A comprehensive system that automatically improves prompts through intelligent rewriting, scoring, and learning from feedback.

## Table of Contents
- [Features](#features)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Running the System](#running-the-system)
- [Testing](#testing)
- [File Formats](#file-formats)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

---

## Features

- **Automatic Prompt Improvement**: Uses strategic rewriting to enhance prompt clarity, specificity, and actionability
- **Intelligent Scoring**: Multi-dimensional scoring system evaluating prompts on 5 key criteria
- **Learning Loop**: Adapts improvement strategies based on performance feedback
- **RESTful API**: Complete FastAPI backend with comprehensive endpoints
- **Database Persistence**: PostgreSQL storage for prompts, versions, and scoring history
- **File Storage System**: Organized file storage for prompts and results with metadata support
- **Web Interface**: Streamlit-based UI for easy interaction
- **Deterministic Fallbacks**: Heuristic-based systems ensure reliability

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

**Windows:**
```powershell
docker-compose up --build
```

**Mac/Linux:**
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`  
The web interface will be available at `http://localhost:8501`

### Option 2: Manual Setup (Development)

Follow the [Installation](#installation) section below.

---

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- SQLite (built into Python - no installation needed)

### Step 1: Clone the Repository

**Windows (PowerShell):**
```powershell
git clone https://github.com/yourusername/Self-Learning-Prompt-Engineering-System.git
cd Self-Learning-Prompt-Engineering-System
```

**Mac/Linux:**
```bash
git clone https://github.com/yourusername/Self-Learning-Prompt-Engineering-System.git
cd Self-Learning-Prompt-Engineering-System
```

### Step 2: Create Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

**Backend Dependencies:**

**Windows:**
```powershell
cd backend
python -m pip install -r requirements.txt
cd ..
```

**Mac/Linux:**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

**Web Interface Dependencies:**

**Windows:**
```powershell
cd apps\web
python -m pip install -r requirements.txt
cd ..\..
```

**Mac/Linux:**
```bash
cd apps/web
pip install -r requirements.txt
cd ../..
```

**Test Dependencies (Optional):**

**Windows:**
```powershell
cd tests
python -m pip install -r requirements.txt
cd ..
```

**Mac/Linux:**
```bash
cd tests
pip install -r requirements.txt
cd ..
```

### Step 4: Setup Database

Create the SQLite database (built into Python, no server needed):

**Windows (PowerShell):**
```powershell
python -c "from packages.db.models import Base; from packages.db.session import engine; Base.metadata.create_all(engine)"
```

**Mac/Linux:**
```bash
python -c "from packages.db.models import Base; from packages.db.session import engine; Base.metadata.create_all(engine)"
```

This creates a `prompter.db` file in your project root with all necessary tables.

**Optional: Use a different database location:**

**Windows (PowerShell):**
```powershell
$env:DATABASE_URL = "sqlite:///./my_custom.db"
```

**Mac/Linux:**
```bash
export DATABASE_URL="sqlite:///./my_custom.db"
```

---

## Running the System

### Running the Backend API

**Windows (PowerShell):**
```powershell
cd backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Mac/Linux:**
```bash
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`  
API documentation: `http://localhost:8000/docs`

### Running the Web Interface

**Open a new terminal window/tab, then:**

**Windows (PowerShell):**
```powershell
cd apps\web
streamlit run streamlit_app.py
```

**Mac/Linux:**
```bash
cd apps/web
streamlit run streamlit_app.py
```

The web interface will be available at: `http://localhost:8501`

### Running Both Together

**Windows (PowerShell) - Use two terminal windows:**

Terminal 1:
```powershell
cd backend
python -m uvicorn api:app --reload
```

Terminal 2:
```powershell
cd apps\web
streamlit run streamlit_app.py
```

**Mac/Linux - Use two terminal windows or tmux:**

Terminal 1:
```bash
cd backend && uvicorn api:app --reload
```

Terminal 2:
```bash
cd apps/web && streamlit run streamlit_app.py
```

---

## Testing

### Running Unit Tests

**Windows (PowerShell):**
```powershell
# From project root
python -m pytest tests\unit\test_api.py -v
```

**Mac/Linux:**
```bash
# From project root
pytest tests/unit/test_api.py -v
```

### Running Integration Tests

**Note:** The backend must be running for integration tests.

**Windows (PowerShell):**
```powershell
# Start backend first
cd backend
python -m uvicorn api:app --reload

# In another terminal, run tests
python -m pytest tests\integration\test_integration.py -v
```

**Mac/Linux:**
```bash
# Start backend first
cd backend && uvicorn api:app --reload &

# Run tests
pytest tests/integration/test_integration.py -v
```

### Running All Tests

**Windows:**
```powershell
python -m pytest tests\ -v
```

**Mac/Linux:**
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

**Issue: "Module not found" errors**

**Windows:**
```powershell
# Make sure you're in the virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
python -m pip install -r backend\requirements.txt
python -m pip install -r apps\web\requirements.txt
```

**Mac/Linux:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
pip install -r apps/web/requirements.txt
```

**Issue: "Connection refused" when web app tries to connect to API**

Make sure the backend is running on port 8000:
```
Backend: http://localhost:8000
Web App: http://localhost:8501
```

**Issue: Database connection errors**

Check your `DATABASE_URL` environment variable is set correctly, or the API will fail when trying to save data.

**Issue: Port already in use**

**Windows:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

---

## Support

For questions or issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review component READMEs:
   - [Backend README](backend/README.md)
   - [Web App README](apps/web/README.md)
   - [Storage README](storage/README.md)
   - [Tests README](tests/README.md)
3. Open an issue on GitHub
4. Text or call each other
5. Email prof or sponsor

---

**Built with ❤️ by the Self-Learning Prompt Engineering Team**

