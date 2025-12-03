# Backend API

FastAPI backend service for the Self-Learning Prompt Engineering System.

## Prerequisites

1. **Groq API Key** - Get yours at https://console.groq.com/
2. **Python 3.11+** with virtual environment activated
3. **python-dotenv** installed

## Setup

### 1. Set Up Environment Variables

Create a `.env` file in the **project root** (not in backend/):

```bash
cd /path/to/Self-Learning-Prompt-Engineering-System
echo "GROQ_API_KEY=your-actual-api-key-here" > .env
```

### 2. Install Dependencies

```bash
cd backend
pip install python-dotenv  # Required for loading .env
pip install -r requirements.txt
```

## Running the Backend

**⚠️ IMPORTANT:** Run from the **project root**, not from the backend directory!

```bash
cd /path/to/Self-Learning-Prompt-Engineering-System
source venv/bin/activate
python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

## API Documentation

Interactive API docs: http://localhost:8000/docs

### Endpoints

- `GET /` - Health check
- `POST /v1/prompts` - Create and improve a prompt
- `GET /v1/prompts/{prompt_id}` - Get prompt details and history
- `POST /v1/prompts/{prompt_id}/improve` - Generate additional improvements
- `POST /v1/versions/{version_id}/judge` - Re-judge a prompt version
- `POST /v1/prompts/{prompt_id}/learn` - Update learning rules
- `GET /v1/metrics` - Get system metrics

## Troubleshooting

**Error: "The api_key client option must be set"**
- Make sure your `.env` file exists in the project root
- Verify it contains: `GROQ_API_KEY=your-key`
- Install python-dotenv: `pip install python-dotenv`

**Error: "No module named 'packages'"**
- You must run from the project root
- Use: `python -m uvicorn backend.api:app --reload`

**Error: "Module not found"**
- Activate your virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`