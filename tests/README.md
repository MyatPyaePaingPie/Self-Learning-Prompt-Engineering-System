# Testing & Documentation

## How to run tests

### Prerequisites

1. **Install test dependencies:**
   ```bash
   pip install -r tests/requirements.txt
   ```

2. **Set up `.env` file** with your Groq API key (required for integration tests)

3. **Make sure your backend is running** (for integration tests):
   ```bash
   cd /path/to/Self-Learning-Prompt-Engineering-System
   source venv/bin/activate
   python -m uvicorn backend.api:app --reload
   ```

### Running Tests

#### Run all tests:
```bash
pytest tests/ -v
```

#### Run only unit tests:
```bash
pytest tests/unit/ -v
```

#### Run only integration tests:
```bash
pytest tests/integration/ -v
```

#### Run specific test file:
```bash
pytest tests/unit/test_api.py -v
pytest tests/unit/test_streamlit_app.py -v
```

#### Run with coverage:
```bash
pytest tests/ --cov=backend --cov=apps/web
```

## Test Structure

- `tests/unit/` - Individual component tests
  - `test_api.py` - FastAPI backend tests
  - `test_streamlit_app.py` - Streamlit UI tests
- `tests/integration/` - End-to-end tests
  - `test_integration.py` - Full system flow tests

## What Each Test Does

### API Tests (`test_api.py`)
- ✅ Home endpoint returns correct message
- ✅ Improve endpoint processes prompts correctly
- ✅ Handles empty prompts
- ✅ Validates input format
- ✅ Handles invalid JSON
- ✅ Processes long prompts

### Streamlit Tests (`test_streamlit_app.py`)
- ✅ App title is correct
- ✅ Text input component exists
- ✅ Output display logic works
- ✅ Handles empty input
- ✅ Handles special characters
- ✅ Handles long input

### Integration Tests (`test_integration.py`)
- ✅ API server is available
- ✅ End-to-end prompt improvement flow
- ✅ API documentation is accessible

## Notes

- Integration tests require the FastAPI server to be running
- Streamlit tests are basic logic tests (full UI testing requires special setup)
- All tests follow the Week 3 requirements for basic functionality testing
