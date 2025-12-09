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

### Core Capabilities
- **Automatic Prompt Improvement**: Uses Groq's LLM API to enhance prompt clarity, specificity, and actionability
- **Multi-Agent Collaboration** ✨: 3 specialized agents (syntax, structure, domain) optimize prompts collaboratively with weighted voting
- **Darwinian Evolution System** 🧬: Self-improving system that learns from user feedback and adapts agent weights over time
- **Intelligent Scoring**: Multi-dimensional scoring system evaluating prompts on 5 key criteria
- **Learning Loop**: Adapts improvement strategies based on performance feedback

### Authentication & Security 🔒
- **JWT Authentication**: Production-ready user authentication with secure login/register system
- **Security Dashboard**: Real-time monitoring of security inputs with risk scoring and configurable blocking thresholds
- **Security Analyzer**: Keyword-based risk assessment system with customizable threat detection
- **Rate Limiting**: API protection with configurable request limits per endpoint
- **Security Headers**: Production-ready HTTP security headers (HSTS, CSP, XSS protection)
- **User Data Isolation**: Database-first architecture ensures users only access their own data

### Analytics & Monitoring 📊
- **Token Cost Tracking**: Real-time token usage and cost analytics across all AI agents
- **Model-Specific Pricing**: Accurate cost calculation for each Groq model (8B, 70B, Gemma, Mixtral)
- **Temporal Analysis**: Time-series analysis of prompt evolution with trend detection and change points
- **Causal Hints**: Statistical correlation detection between prompt changes and score improvements
- **Agent Effectiveness Tracking**: Monitor individual agent performance and contribution over time

### Technical Infrastructure
- **Model Registry**: Centralized configuration for multiple Groq models with cost/speed optimization
- **RESTful API**: Complete FastAPI backend with modular router architecture
- **Database Persistence**: SQLite storage with user-specific data isolation
- **File Storage System**: Organized file storage for prompts and results with metadata support
- **Multi-Page Web Interface**: Streamlit-based UI with dashboard, security monitoring, and analytics
- **Deterministic Fallbacks**: Template-based systems ensure reliability when API is unavailable
- **Full Observability**: Track agent contributions, decisions, and effectiveness over time

---

## Repository Structure

```
Self-Learning-Prompt-Engineering-System/
├── backend/                    # FastAPI backend service
│   ├── main.py                # Main FastAPI app with middleware
│   ├── auth.py                # JWT authentication logic
│   ├── database.py            # User database models
│   ├── temporal_analysis.py   # Time-series analysis
│   ├── routers/               # API route modules
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── prompts.py        # Prompt management
│   │   ├── security.py       # Security monitoring
│   │   ├── temporal.py       # Temporal analysis
│   │   ├── storage.py        # File storage
│   │   └── agents.py         # Multi-agent endpoints
│   ├── requirements.txt       # Backend dependencies
│   └── README.md             # Backend documentation
│
├── frontend/                  # Streamlit web interface
│   ├── app.py                # Main UI entry point
│   ├── auth_client.py        # Authentication client
│   ├── temporal_client.py    # Temporal API client
│   ├── pages/                # Multi-page application
│   │   ├── auth.py          # Login/Register page
│   │   ├── prompt_enhancement.py  # Main enhancement UI
│   │   ├── security_dashboard.py  # Security monitoring
│   │   ├── temporal_analysis.py   # Evolution analytics
│   │   ├── token_analytics.py     # Cost tracking
│   │   └── agent_effectiveness.py # Agent performance
│   ├── components/           # Reusable UI components
│   │   └── feedback.py      # User feedback widgets
│   ├── utils/               # Utility modules
│   │   ├── api_client.py   # API wrapper
│   │   └── session.py      # Session management
│   ├── requirements.txt     # Frontend dependencies
│   └── README.md           # Frontend documentation
│
├── packages/                  # Shared core logic
│   ├── core/                 # Business logic
│   │   ├── engine.py        # Prompt improvement engine
│   │   ├── judge.py         # Scoring system
│   │   ├── learning.py      # Learning loop
│   │   ├── multi_agent.py   # Multi-agent system
│   │   ├── agent_coordinator.py  # Agent orchestration
│   │   ├── agent_registry.py     # Agent factory
│   │   ├── model_config.py  # Groq model registry
│   │   ├── token_tracker.py # Token & cost tracking
│   │   └── security_analyzer.py  # Risk assessment
│   └── db/                   # Database layer
│       ├── models.py        # SQLAlchemy models
│       ├── crud.py          # Database operations
│       ├── session.py       # Database connection
│       └── migrations/      # SQL migration scripts
│           ├── 001_init.sql
│           ├── 002_add_security_inputs.sql
│           ├── 003_add_temporal_fields.sql
│           ├── 004_add_request_id_to_prompts.sql
│           └── 005_add_token_usage.sql
│
├── storage/                   # File storage system
│   ├── file_storage.py       # File operations module
│   ├── prompts/              # Saved prompts
│   ├── results/              # Processing results
│   ├── temporal_data_generator.py  # Test data generation
│   └── README.md            # Storage documentation
│
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── test_auth_system.py  # Authentication tests
│   ├── test_token_tracking.py    # Token tracking tests
│   ├── conftest.py          # Pytest configuration
│   ├── requirements.txt     # Test dependencies
│   └── README.md           # Testing documentation
│
├── Documentation/            # Comprehensive guides
│   ├── SECURITY_GUIDE.md    # Security best practices
│   ├── MULTI_AGENT_SYSTEM.md        # Multi-agent docs
│   ├── DARWINIAN_MULTI_AGENT_SYSTEM.md  # Evolution system
│   ├── TEMPORAL_AUTH_IMPLEMENTATION_2025_12_04.md
│   └── DATABASE_FIRST_STORAGE_PATTERN.md
│
├── auth_system.db           # User authentication database (SQLite)
├── .env                     # Environment variables (GROQ_API_KEY)
└── README.md                # This file
```

**Note:** All databases are SQLite (file-based) - no PostgreSQL, Redis, or Docker containers needed!

---

## Quick Start

The system uses **SQLite** (file-based database) - no Docker or database server installation needed!

### Prerequisites Check
```bash
python --version  # Need Python 3.11+
pip --version     # Need pip
```

### Fast Setup (5 minutes)
```bash
# 1. Clone repository
git clone https://github.com/yourusername/Self-Learning-Prompt-Engineering-System.git
cd Self-Learning-Prompt-Engineering-System

# 2. Create .env file with your Groq API key
echo "GROQ_API_KEY=your-actual-groq-api-key-here" > .env

# 3. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

# 4. Initialize database
python -c "from packages.db.models import Base; from packages.db.session import engine; Base.metadata.create_all(engine)"

# 5. Run backend (Terminal 1)
python -m uvicorn backend.main:app --reload --port 8001

# 6. Run frontend (Terminal 2)
cd frontend && streamlit run app.py
```

**Done!** Visit `http://localhost:8501` to start using the system.

For detailed setup, see [Installation](#installation) section below.

---

## System Architecture

### Multi-Layer Security & Analytics Architecture

```mermaid
graph TB
    User[User] --> Frontend[Streamlit Frontend]
    Frontend --> API[FastAPI Backend]
    
    subgraph "Authentication Layer"
        JWT[JWT Tokens]
        Auth[Auth Middleware]
        RateLimit[Rate Limiting]
    end
    
    subgraph "API Routers"
        AuthRouter[/auth]
        PromptRouter[/prompts]
        SecurityRouter[/security]
        TemporalRouter[/temporal]
        AgentRouter[/agents]
    end
    
    subgraph "Core Services"
        MultiAgent[Multi-Agent System]
        SecurityAnalyzer[Security Analyzer]
        TokenTracker[Token Tracker]
        TemporalEngine[Temporal Analysis]
    end
    
    subgraph "Data Layer"
        UserDB[(User DB)]
        PromptDB[(Prompt DB)]
        SecurityDB[(Security DB)]
        TokenDB[(Token DB)]
    end
    
    API --> Auth --> JWT
    API --> RateLimit
    API --> AuthRouter
    API --> PromptRouter
    API --> SecurityRouter
    API --> TemporalRouter
    API --> AgentRouter
    
    PromptRouter --> MultiAgent
    SecurityRouter --> SecurityAnalyzer
    AgentRouter --> TokenTracker
    TemporalRouter --> TemporalEngine
    
    MultiAgent --> PromptDB
    SecurityAnalyzer --> SecurityDB
    TokenTracker --> TokenDB
    TemporalEngine --> PromptDB
    AuthRouter --> UserDB
```

### Multi-Agent Workflow

```
User Prompt → Security Check → Multi-Agent Enhancement → Token Tracking
                                          ↓
                        ┌─────────────────┼─────────────────┐
                        ↓                 ↓                 ↓
                  SyntaxAgent     StructureAgent     DomainAgent
                    (8B Fast)       (8B Fast)        (70B Powerful)
                        ↓                 ↓                 ↓
                        └─────────────────┼─────────────────┘
                                          ↓
                                  Agent Coordinator
                                  (Weighted Voting)
                                          ↓
                                  Enhanced Prompt
                                          ↓
                              Judge Scoring → Database
                                          ↓
                                  Temporal Analysis
```

---

## JWT Authentication System

### Overview

The system implements production-ready JWT authentication with:
- **Secure Password Hashing**: BCrypt with automatic salt generation
- **Token-Based Auth**: Stateless JWT tokens with configurable expiration (30 min default)
- **Protected Endpoints**: All sensitive routes require authentication
- **User Data Isolation**: Each user only accesses their own prompts, security logs, and analytics

### Authentication Flow

1. **Register**: `POST /auth/register` - Create new user account
2. **Login**: `POST /auth/login` - Get JWT access token
3. **Authenticated Requests**: Include `Authorization: Bearer <token>` header
4. **Token Validation**: Automatic validation on all protected endpoints

### Quick Auth Setup

```bash
# 1. Register a new user
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "email": "user@example.com", "password": "SecurePass123"}'

# 2. Login to get JWT token
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "password": "SecurePass123"}'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 3. Use token for authenticated requests
curl http://localhost:8001/prompts/my-prompts \
  -H "Authorization: Bearer eyJ..."
```

### Frontend Authentication

The Streamlit frontend handles authentication automatically:
1. Navigate to **Authentication** page
2. Register or login
3. Token stored in session state
4. All API calls include authentication header

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

The system uses **SQLite** (no server installation needed). Create the database:

```bash
python -c "from packages.db.models import Base; from packages.db.session import engine; Base.metadata.create_all(engine)"
```

This creates SQLite database files:
- `packages/db/prompter.db` - Main database (prompts, versions, scores, security, tokens)
- `auth_system.db` - User authentication database (created automatically on first register)

**Why SQLite?**
- ✅ No server installation or configuration
- ✅ No Docker containers needed
- ✅ Fast for development and small-to-medium deployments
- ✅ Single file = easy backup and portability

**Optional: Use PostgreSQL for production:**

If you need PostgreSQL for large-scale deployment:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/prompter_db"
```

But for most use cases, SQLite is perfect!

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
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
```

The API will be available at: `http://localhost:8001`  
API documentation (Swagger): `http://localhost:8001/docs`  
Health check: `http://localhost:8001/health`

**Note:** Backend now runs on port **8001** (changed from 8000) to avoid conflicts.

### Running the Web Interface

Open a new terminal window/tab:

```bash
cd /path/to/Self-Learning-Prompt-Engineering-System
source venv/bin/activate
cd frontend
streamlit run app.py
```

The web interface will be available at: `http://localhost:8501`

### Running Both Together

Use two terminal windows:

**Terminal 1 (Backend):**
```bash
cd /path/to/Self-Learning-Prompt-Engineering-System
source venv/bin/activate
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 2 (Frontend):**
```bash
cd /path/to/Self-Learning-Prompt-Engineering-System
source venv/bin/activate
cd frontend
streamlit run app.py
```

**Frontend Pages Available:**
- 🏠 **Dashboard** - Main prompt enhancement interface
- 🔐 **Authentication** - Login/Register page
- 🔒 **Security Dashboard** - Real-time security monitoring
- ⏱️ **Temporal Analysis** - Prompt evolution analytics
- 💰 **Token Analytics** - Cost tracking and usage metrics
- 🤖 **Agent Effectiveness** - Multi-agent performance tracking

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

**Database Files (SQLite):**
- `packages/db/prompter.db` - Main database (prompts, versions, scores, security, tokens)
- `auth_system.db` - User authentication database (users, hashed passwords)
- **No server installation required** - SQLite is file-based
- **Portable** - Copy `.db` files to backup/share data
- **No Docker needed** - Everything runs natively with Python

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

## API Documentation (Updated)

### Base URL
`http://localhost:8001`

### Authentication Endpoints (`/auth`)

#### `POST /auth/register`
Register a new user account.

**Request:**
```json
{
  "username": "myuser",
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "uuid"
}
```

#### `POST /auth/login`
Login and receive JWT access token.

**Request:**
```json
{
  "username": "myuser",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### `GET /auth/me` 🔒
Get current authenticated user info.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "uuid",
  "username": "myuser",
  "email": "user@example.com"
}
```

---

### Prompt Endpoints (`/prompts`)

#### `POST /prompts/enhance` 🔒
Enhance a prompt using multi-agent system.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "text": "Your prompt text",
  "enhancement_type": "general"
}
```

**Response:**
```json
{
  "prompt_id": "uuid",
  "version_id": "uuid",
  "improved": "Enhanced prompt text",
  "explanation": {...},
  "judge_scores": {...},
  "agent_contributions": [...]
}
```

#### `POST /prompts/save` 🔒
Save a prompt to database.

#### `GET /prompts/my-prompts` 🔒
Get all prompts for authenticated user.

#### `GET /v1/prompts/{prompt_id}` 🔒
Get prompt details with version history.

---

### Security Endpoints (`/v1/security`)

#### `POST /v1/security/inputs` 🔒
Log security input with risk assessment.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "inputText": "User prompt",
  "riskScore": 25.5,
  "label": "safe",
  "isBlocked": false,
  "analysisMetadata": {}
}
```

#### `GET /v1/security/inputs` 🔒
Get security inputs with filtering.

**Query Parameters:**
- `limit`: Max results (default: 100)
- `filter_label`: Filter by risk label
- `filter_blocked`: Filter by blocked status
- `filter_high_risk`: Show only high-risk inputs

---

### Temporal Analysis Endpoints (`/api/temporal`)

#### `GET /api/temporal/timeline` 🔒
Get temporal timeline of prompt versions.

**Query Parameters:**
- `prompt_id`: UUID of prompt
- `start`: Start date (ISO 8601)
- `end`: End date (ISO 8601)

#### `GET /api/temporal/statistics` 🔒
Get statistical analysis of prompt evolution.

#### `GET /api/temporal/causal-hints` 🔒
Get causal correlations between changes and improvements.

#### `POST /api/temporal/generate-synthetic` 🔒
Generate synthetic test data for temporal analysis.

---

### Token Tracking Endpoints (`/api/tokens`)

#### `GET /api/tokens` 🔒
Get token usage history.

**Query Parameters:**
- `limit`: Max results (default: 100)

**Response:**
```json
{
  "success": true,
  "data": [...],
  "total_tokens": 15000,
  "total_cost": 0.0105
}
```

---

### Multi-Agent Endpoints (`/v1/agents`)

#### `POST /v1/agents/multi-agent-enhance` 🔒
Enhance prompt using multi-agent collaboration.

#### `GET /v1/agents/agent-effectiveness` 🔒
Get agent performance metrics.

---

### Health & Metrics

#### `GET /health`
Health check endpoint (no auth required).

#### `GET /`
API information and available endpoints.

#### `GET /v1/metrics` 🔒
Get system-wide metrics.

### Interactive API Documentation

Visit `http://localhost:8001/docs` when the API is running for full interactive documentation.

---

## Security Features 🔒

### Security Monitoring Dashboard

The system includes real-time security monitoring with keyword-based risk assessment:

**Features:**
- **Risk Scoring**: Keyword-based analysis (0-100 scale)
- **Configurable Thresholds**: Adjust blocking threshold (default: 80)
- **Real-Time Monitoring**: Track all security inputs with timestamps
- **Filter & Search**: Filter by risk level, blocked status, or label
- **Risk Categories**:
  - **Malicious** (weight: 15): hack, exploit, vulnerability, inject, bypass
  - **Destructive** (weight: 12): delete, destroy, remove, wipe, format
  - **Privacy** (weight: 10): steal, credential, password, private, sensitive
  - **System** (weight: 8): root, admin, sudo, privilege, escalate

**Risk Labels:**
- `safe` (0-30): No security concerns
- `low-risk` (31-50): Minor concerns, monitoring recommended
- `medium-risk` (51-70): Moderate concerns, review recommended
- `high-risk` (71-100): Serious concerns, blocking recommended

### Security Endpoints

```bash
# Log security input (authenticated)
POST /v1/security/inputs
{
  "inputText": "User prompt text",
  "riskScore": 25.5,
  "label": "safe",
  "isBlocked": false,
  "analysisMetadata": {"keywords_found": []}
}

# Get security inputs (authenticated, filtered)
GET /v1/security/inputs?filter_label=high-risk&filter_blocked=true&limit=100
```

### Production Security Features

- **BCrypt Password Hashing**: Secure password storage with automatic salt
- **JWT Token Authentication**: Stateless authentication with 30-minute expiration
- **Rate Limiting**: Configurable per-endpoint request limits (SlowAPI)
- **Security Headers**: HSTS, CSP, X-Frame-Options, X-XSS-Protection
- **CORS Protection**: Configured allowed origins
- **Input Validation**: Pydantic models validate all request data
- **User Data Isolation**: Database-level filtering by user_id

---

## Temporal Analysis ⏱️

### Time-Series Prompt Evolution

Track how prompts improve over time with statistical analysis:

**Features:**
- **Timeline Visualization**: See prompt versions and scores over time
- **Trend Detection**: Identify improving, declining, or stable trends
- **Change Point Detection**: Find significant shifts in performance
- **Velocity Tracking**: Measure rate of improvement over time
- **Causal Hints**: Statistical correlation between changes and score improvements

### Temporal Metrics

1. **Trend Detection**
   - `improving`: Consistent upward trajectory
   - `declining`: Consistent downward trajectory
   - `stable`: No significant change
   - `volatile`: High variance, no clear pattern

2. **Change Points**
   - Significant shifts in performance (>10% deviation from baseline)
   - Statistical anomaly detection
   - Timestamps and magnitude of changes

3. **Statistics**
   - Mean, median, standard deviation of scores
   - Min/max scores and improvement range
   - Trend slope and R² correlation

4. **Causal Correlations**
   - Which edit types (structure, wording, clarity) correlate with improvements
   - Statistical significance of correlations
   - Actionable insights for prompt engineering

### Temporal Endpoints

```bash
# Get timeline (authenticated)
GET /api/temporal/timeline?prompt_id=<uuid>&start=2025-11-01&end=2025-12-07

# Get statistics (authenticated)
GET /api/temporal/statistics?prompt_id=<uuid>&start=2025-11-01&end=2025-12-07

# Get causal hints (authenticated)
GET /api/temporal/causal-hints?prompt_id=<uuid>&start=2025-11-01&end=2025-12-07

# Generate synthetic test data (authenticated)
POST /api/temporal/generate-synthetic
{
  "prompt_id": "<uuid>",
  "days": 30,
  "versions_per_day": 2
}
```

### Synthetic vs Real Data

**Synthetic Data** (for testing):
- Generate 30-day test data instantly
- Marked with `{"synthetic": true}` metadata
- Random scores and version chains
- User-specific (filtered by authenticated user)

**Real Data** (production):
- Natural prompt evolution over time
- Real version chains with parent-child relationships
- Actual judge scores and improvement tracking
- User-specific (filtered by authenticated user)

---

## Token Cost Tracking 💰

### Real-Time Token Analytics

Track token usage and costs across all AI agents with model-specific pricing:

**Features:**
- **Per-Request Tracking**: Individual token counts and costs
- **Aggregate Metrics**: Total tokens, total cost, average cost per request
- **Model Breakdown**: Separate tracking for each Groq model
- **Cost Analysis**: Input vs output token costs
- **Historical Data**: View token history with timestamps

### Groq Model Pricing (Verified 2025-12-03)

| Model | Input (per 1M) | Output (per 1M) | Use Case |
|-------|---------------|-----------------|----------|
| **llama-3.1-8b-instant** | $0.05 | $0.08 | Fast, simple tasks (syntax/structure) |
| **llama-3.3-70b-versatile** | $0.59 | $0.79 | Complex reasoning (default) |
| **gemma2-9b-it** | $0.20 | $0.20 | Balanced performance |
| **mixtral-8x7b-32768** | $0.27 | $0.27 | Long context tasks |

### Token Tracking Workflow

```
User Request → Multi-Agent Processing → Token Tracking
                       ↓
         ┌─────────────┼─────────────┐
         ↓             ↓             ↓
    Syntax (8B)  Structure (8B)  Domain (70B)
         ↓             ↓             ↓
    Track Tokens  Track Tokens  Track Tokens
         └─────────────┼─────────────┘
                       ↓
               Aggregate & Store
                       ↓
               Database Record
                       ↓
           Analytics Dashboard
```

### Token Analytics Endpoints

```bash
# Get token history (authenticated)
GET /api/tokens?limit=100

# Response
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "prompt_tokens": 150,
      "completion_tokens": 200,
      "total_tokens": 350,
      "model": "llama-3.3-70b-versatile",
      "cost_usd": 0.000247,
      "created_at": "2025-12-07T10:30:00Z"
    }
  ],
  "total_tokens": 15000,
  "total_cost": 0.0105
}
```

### Cost Optimization

**Multi-Agent Cost Reduction:**
- Use fast 8B models for simple tasks (syntax, structure)
- Use powerful 70B model only for complex domain reasoning
- **62% cost reduction** vs single 70B model approach

**Example Cost Comparison:**
```
Single Model (70B only):  3 × $0.000247 = $0.000741
Multi-Agent (8B + 70B):   2 × $0.000025 + 1 × $0.000247 = $0.000297
Savings:                  60% cost reduction
```

---

## API Documentation (Updated)

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

**Issue: "Could not import module 'main'" or "No module named 'packages'"**

Run the backend from the project root, not from the backend directory:

```bash
# CORRECT - from project root
cd /path/to/Self-Learning-Prompt-Engineering-System
python -m uvicorn backend.main:app --reload --port 8001

# INCORRECT - don't run from backend/
```

**Issue: "Connection refused" when web app tries to connect to API**

Make sure the backend is running on port 8001 (changed from 8000):
```
Backend: http://localhost:8001
Frontend: http://localhost:8501
```

Check `frontend/utils/api_client.py` and ensure:
```python
API_BASE = "http://localhost:8001"
```

**Issue: Port already in use**

Find and kill the process using the port:

```bash
# Find process using port 8001
lsof -i :8001

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

**Issue: "401 Unauthorized" errors on API calls**

You need to authenticate first:
1. Go to **Authentication** page in frontend
2. Register or login
3. JWT token stored automatically in session
4. Retry the request

Or manually include token in API calls:
```bash
curl http://localhost:8001/prompts/my-prompts \
  -H "Authorization: Bearer <your-token>"
```

**Issue: Security dashboard shows no data**

Security inputs are user-specific. Make sure:
1. You're logged in
2. You've submitted prompts (which triggers security analysis)
3. Check filters - try "All" to see all data

**Issue: Temporal analysis shows empty timeline**

Temporal data requires:
1. Multiple prompt versions over time, OR
2. Generate synthetic test data using "Generate 30-Day Test Data" button
3. Make sure prompt exists and belongs to your user account

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

## Darwinian Evolution System 🧬

**NEW - Self-Improving Multi-Agent System**

The system now features **Darwinian Evolution** - a self-improving mechanism that learns from user feedback and adapts agent weights over time.

### How It Works

```
User Feedback → Weight Learning → Personalized Enhancement → Better Results
```

1. **Phase 1 (Current):** Collect user feedback on which results are best
2. **Phase 2:** Learn personalized agent weights from feedback
3. **Phase 3:** Context-aware intelligence (technical vs creative prompts)
4. **Phase 4:** Self-evolving agent prompts via A/B testing
5. **Phase 5:** Fully autonomous self-improving system

### Key Features

- **Personalized Learning**: System adapts to YOUR preferences
- **Bayesian Weight Updates**: Proven statistical learning method
- **Context Awareness**: Different weights for technical vs creative prompts
- **Full Transparency**: See how the system learns and evolves
- **Continuous Improvement**: Gets better over time without manual tuning

### Current Status

📋 **Phase 1 Ready** - Feedback collection infrastructure  
🔜 **Phase 2-5** - Advanced learning features (coming soon)

### Documentation

**📖 [DARWINIAN_MULTI_AGENT_SYSTEM.md](DARWINIAN_MULTI_AGENT_SYSTEM.md)**

Complete guide including:
- Evolution roadmap (5 phases)
- Learning algorithms explained
- Technical architecture
- API reference
- Implementation timeline
- FAQ and troubleshooting

---

## Support

For questions or issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review documentation:
   - [Multi-Agent System](Documentation/MULTI_AGENT_SYSTEM.md) ⭐
   - [Darwinian Evolution System](Documentation/DARWINIAN_MULTI_AGENT_SYSTEM.md) 🧬
   - [Security Guide](Documentation/SECURITY_GUIDE.md) 🔒
   - [Temporal Auth Implementation](Documentation/TEMPORAL_AUTH_IMPLEMENTATION_2025_12_04.md) ⏱️
   - [Database-First Storage Pattern](Documentation/DATABASE_FIRST_STORAGE_PATTERN.md) 💾
   - [Token Tracking Integration](Documentation/TOKEN_TRACKING_INTEGRATION_SUMMARY.md) 💰
3. Review component READMEs:
   - [Backend README](backend/README.md)
   - [Frontend README](frontend/README.md)
   - [Storage README](storage/README.md)
   - [Tests README](tests/README.md)
4. Open an issue on GitHub
5. Contact team members
6. Email prof or sponsor

---

## System Summary

### What Makes This System Unique?

1. **Multi-Agent Intelligence**: 3 specialized agents collaborate with weighted voting
2. **Darwinian Evolution**: System learns from user feedback and adapts over time
3. **Production Security**: JWT auth, rate limiting, security monitoring, encrypted data
4. **Cost Optimization**: 62% cost reduction through intelligent model selection
5. **Temporal Intelligence**: Track prompt evolution with statistical analysis
6. **Full Observability**: Monitor tokens, costs, security, and agent performance
7. **User Data Isolation**: Each user sees only their own data (database-first architecture)

### Technology Stack

- **Backend**: FastAPI, SQLAlchemy, JWT, BCrypt, SlowAPI
- **Frontend**: Streamlit, Plotly, Pandas
- **AI/LLM**: Groq API (Llama 3.1 8B, Llama 3.3 70B, Gemma2, Mixtral)
- **Database**: SQLite with migrations
- **Security**: JWT tokens, rate limiting, security headers, CORS
- **Analytics**: Token tracking, temporal analysis, agent effectiveness

### Quick Navigation

- **Authentication**: [JWT Authentication System](#jwt-authentication-system)
- **Security**: [Security Features](#security-features-)
- **Analytics**: [Temporal Analysis](#temporal-analysis-️) | [Token Cost Tracking](#token-cost-tracking-)
- **AI System**: [Multi-Agent System](#multi-agent-system) | [Darwinian Evolution](#darwinian-evolution-system-)
- **API Docs**: [API Documentation](#api-documentation-updated)
- **Guides**: [Documentation](Documentation/)

---

**Built with ❤️ by the Self-Learning Prompt Engineering Team**

**Version 2.0** - Now with JWT Authentication, Security Monitoring, Temporal Analysis, and Token Cost Tracking!

