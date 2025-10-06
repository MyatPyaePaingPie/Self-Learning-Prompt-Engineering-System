# Testing Guide - Week 4 Flow

This guide shows how to test the connections between Backend (Bellul), Storage (Atang), and Frontend (Paing).

## 🎯 What We're Testing

**Complete Flow:**
```
User Input (Streamlit) 
    → Backend API (/v1/prompts) 
    → Engine (improve prompt) 
    → Judge (score it) 
    → Database (save it) 
    → Response back to Streamlit 
    → Display results
```

---

## 🚀 Step-by-Step Testing

### **Step 1: Install Dependencies**

**IMPORTANT: Do this first from the project root!**

**Windows (PowerShell):**
```powershell
# Backend dependencies
python -m pip install -r backend/requirements.txt

# If you get psycopg errors, install this:
python -m pip install psycopg2-binary

# Frontend dependencies
python -m pip install -r apps/web/requirements.txt
```

**Mac/Linux:**
```bash
# Backend dependencies
pip install -r backend/requirements.txt

# If you get psycopg errors:
pip install psycopg2-binary

# Frontend dependencies
pip install -r apps/web/requirements.txt
```

---

### **Step 2: Start the Backend API**

**IMPORTANT: Run from PROJECT ROOT, not from backend/ directory!**

**Windows (PowerShell):**
```powershell
# Make sure you're in the project root
cd C:\Users\myatp\OneDrive\Desktop\Self-Learning-Prompt-Engineering-System

# Run backend (notice backend.api format)
python -m uvicorn backend.api:app --reload
```

**Mac/Linux:**
```bash
# Make sure you're in the project root
cd /path/to/Self-Learning-Prompt-Engineering-System

# Run backend
python -m uvicorn backend.api:app --reload
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\...\\Self-Learning-Prompt-Engineering-System']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Common Errors and Fixes:**

❌ **Error: `ModuleNotFoundError: No module named 'packages'`**
- **Fix:** You're running from the wrong directory. Must run from project root with `python -m uvicorn backend.api:app --reload`

❌ **Error: `ModuleNotFoundError: No module named 'sqlalchemy'`**
- **Fix:** `python -m pip install sqlalchemy`

❌ **Error: `ModuleNotFoundError: No module named 'psycopg2'`**
- **Fix:** `python -m pip install psycopg2-binary` (Note: NOT `psycopg[binary]`)

**Test it:**
Open browser to `http://localhost:8000` - you should see:
```json
{
  "message": "Self-Learning Prompt Engineering System API",
  "version": "1.0.0"
}
```

✅ **Backend is running!**

---

### **Step 3: Test Backend API Directly**

**Option A: Using Browser (Interactive Docs)**

Open: `http://localhost:8000/docs`

You should see the FastAPI interactive documentation with all endpoints.

**Try the `/v1/prompts` endpoint:**
1. Click on `POST /v1/prompts`
2. Click "Try it out"
3. Enter this JSON:
```json
{
  "text": "Write a function to sort numbers"
}
```
4. Click "Execute"

**Expected Response:**
```json
{
  "promptId": "some-uuid-here",
  "versionId": "some-uuid-here",
  "versionNo": 1,
  "improved": "You are a senior Python developer.\nTask: Write a function to sort numbers\nDeliverables:\n- Clear, step-by-step plan\n- Examples and edge-cases\n- Final code ready to use\nConstraints: [time, tools, data sources]\nIf information is missing, list precise clarifying questions first, then proceed with best assumptions.",
  "explanation": {
    "bullets": [
      "Added explicit role for the assistant",
      "Specified deliverables and output artifact",
      "Inserted constraint section",
      "Required clarifying questions before solution"
    ],
    "diffs": [...]
  },
  "judge": {
    "clarity": 5.0,
    "specificity": 5.0,
    "actionability": 5.0,
    "structure": 5.0,
    "context_use": 5.0,
    "total": 25.0,
    "feedback": {
      "pros": ["Clear role and task."],
      "cons": [],
      "summary": "Heuristic scoring v1. Add LLM judge for nuance."
    }
  }
}
```

✅ **Backend API is working!**

**Option B: Using PowerShell**

**Windows (PowerShell):**
```powershell
$body = @{
    text = "Write a function to sort numbers"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/v1/prompts" -Method Post -Body $body -ContentType "application/json"
```

**Mac/Linux:**
```bash
curl -X POST "http://localhost:8000/v1/prompts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Write a function to sort numbers"}'
```

---

### **Step 4: Start the Frontend (Streamlit)**

**IMPORTANT: Run from PROJECT ROOT in a NEW terminal window!**

Keep the backend running in the first terminal, open a NEW terminal for frontend.

**Windows (PowerShell):**
```powershell
# Make sure you're in the project root
cd C:\Users\myatp\OneDrive\Desktop\Self-Learning-Prompt-Engineering-System

# Run Streamlit (notice apps/web/streamlit_app.py path)
python -m streamlit run apps/web/streamlit_app.py
```

**Mac/Linux:**
```bash
# Make sure you're in the project root
cd /path/to/Self-Learning-Prompt-Engineering-System

# Run Streamlit
python -m streamlit run apps/web/streamlit_app.py
```

**Common Errors and Fixes:**

❌ **Error: `streamlit: The term 'streamlit' is not recognized`**
- **Fix:** Use `python -m streamlit run apps/web/streamlit_app.py` instead of just `streamlit run`

❌ **Error: `ModuleNotFoundError: No module named 'streamlit'`**
- **Fix:** `python -m pip install streamlit requests`

**Expected Output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Your browser should automatically open to `http://localhost:8501`**

✅ **Frontend is running!**

---

### **Step 5: Test the Complete Flow**

**In the Streamlit interface:**

1. **Enter a prompt** in the text area:
   ```
   Help me write a Python script to download images
   ```

2. **Click "Improve Prompt"**

3. **You should see:**
   - ✅ Original prompt displayed
   - ✅ Improved prompt with better structure
   - ✅ Explanation bullets showing what was improved
   - ✅ Quality scores (Clarity, Specificity, Actionability, Structure, Context Use)
   - ✅ Total score
   - ✅ Feedback with pros/cons
   - ✅ Prompt ID

4. **Try different prompts:**
   - "Write a story about a cat"
   - "Help me code"
   - "Create a marketing plan"
   - "Build a REST API"

**Each should:**
- Get improved by the engine
- Get scored by the judge
- Display results in the UI

✅ **Complete flow is working!**

---

### **Step 6: Test Storage (File System)**

**Check if files are being created:**

**Windows (PowerShell):**
```powershell
# Check prompts directory
ls storage\prompts\

# Check results directory
ls storage\results\

# Check CSV files
ls storage\*.csv
```

**Mac/Linux:**
```bash
# Check prompts directory
ls storage/prompts/

# Check results directory
ls storage/results/

# Check CSV files
ls storage/*.csv
```

**You should see:**
- `storage/prompts/example_prompt.txt`
- `storage/results/fibonacci_solution.txt`
- `storage/my_learning_log.csv`
- `storage/prompt_learning_log.csv`

**Note:** Storage is currently NOT connected to the backend. It's a separate module.

---

## 🔍 Testing Each Connection

### **Connection 1: Frontend → Backend** ✅

**Test:** Enter prompt in Streamlit → Click button

**What happens:**
- Streamlit sends POST request to `http://localhost:8000/v1/prompts`
- Request body: `{"text": "your prompt"}`

**Check in Backend Terminal:**
You should see:
```
INFO:     127.0.0.1:xxxxx - "POST /v1/prompts HTTP/1.1" 200 OK
```

**Code Location:**
- `apps/web/streamlit_app.py` lines 15-18

✅ **Frontend can talk to Backend**

### **Connection 2: Backend → Engine** ✅

**Test:** Backend receives request → Calls engine

**What happens:**
- `backend/api.py` line 50: `improved = improve_prompt(payload.text, strategy="v1")`
- Calls `packages/core/engine.py` function
- Engine uses template to improve prompt

**Check:** Look at the improved prompt - it should have:
- "You are a senior {domain} expert."
- "Task: {task}"
- "Deliverables:"
- "Constraints:"

**Code Location:**
- `backend/api.py` line 4 (import)
- `backend/api.py` line 50 (usage)
- `packages/core/engine.py` (implementation)

✅ **Backend can use Engine**

### **Connection 3: Backend → Judge** ✅

**Test:** Backend gets improved prompt → Calls judge

**What happens:**
- `backend/api.py` line 54: `score = judge_prompt(improved.text, rubric=None)`
- Calls `packages/core/judge.py` function
- Judge scores on 5 criteria

**Check:** Look at judge scores in the response - should have:
- clarity: 0-10
- specificity: 0-10
- actionability: 0-10
- structure: 0-10
- context_use: 0-10

**Code Location:**
- `backend/api.py` line 5 (import)
- `backend/api.py` line 54 (usage)
- `packages/core/judge.py` (implementation)

✅ **Backend can use Judge**

### **Connection 4: Backend → Database** ⚠️

**Test:** Backend saves to database

**What happens:**
- `backend/api.py` line 45: `prompt = create_prompt_row(s, payload.userId, payload.text)`
- Calls `packages/db/crud.py` functions
- Saves to PostgreSQL

**Check:** Run this query (if you have PostgreSQL set up):
```sql
SELECT * FROM prompts ORDER BY created_at DESC LIMIT 5;
```

**If NO database:** The system will fail here. That's okay for Week 4 testing.

**Code Location:**
- `backend/api.py` line 7 (import)
- `backend/api.py` lines 45-58 (usage)
- `packages/db/crud.py` (implementation)

⚠️ **Database connection (optional for Week 4)**

### **Connection 5: Backend → Storage** ❌

**Status:** NOT CONNECTED

The backend does NOT currently use the file storage system. They are independent:
- Backend saves to database
- Storage saves to files

**To connect them (future work):** Add file storage calls to backend API after database saves.

❌ **Storage is standalone**

---

## 🐛 Troubleshooting

### **Issue: "Connection refused" in Streamlit**

**Problem:** Frontend can't reach backend

**Solution:**
1. Make sure backend is running on port 8000
2. Check: `http://localhost:8000` in browser
3. Make sure you're running both in separate terminals
4. Both must be run from project root

### **Issue: "Module not found 'packages'" in Backend**

**Problem:** Running from wrong directory

**Solution:**
```powershell
# DON'T run from backend/ directory
# DO run from project root with:
python -m uvicorn backend.api:app --reload
```

### **Issue: "Module not found 'sqlalchemy'" or "psycopg2"**

**Problem:** Missing dependencies

**Solution:**
```powershell
python -m pip install sqlalchemy psycopg2-binary
```

### **Issue: "streamlit is not recognized"**

**Problem:** Streamlit not in PATH or not installed

**Solution:**
```powershell
# Install if needed
python -m pip install streamlit requests

# Always run with python -m
python -m streamlit run apps/web/streamlit_app.py
```

### **Issue: Database errors in backend**

**Problem:** Database not set up

**Solution (Quick Fix - Disable Database):**

Edit `backend/api.py` temporarily to skip database:

```python
# Around line 40, comment out database code:
@app.post("/v1/prompts", response_model=CreatePromptResponse)
def create_prompt(payload: CreatePromptIn):
    """Create a new prompt and automatically generate first improvement"""
    try:
        # Generate improvement (v1)
        improved = improve_prompt(payload.text, strategy="v1")
        
        # Judge the improvement
        score = judge_prompt(improved.text, rubric=None)
        
        # Return without database
        return CreatePromptResponse(
            promptId="test-id",
            versionId="test-version",
            versionNo=1,
            improved=improved.text,
            explanation=improved.explanation,
            judge=score.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## ✅ Success Checklist

- [ ] Installed backend dependencies
- [ ] Installed frontend dependencies
- [ ] Backend runs on port 8000 (from project root)
- [ ] Can access `http://localhost:8000/docs`
- [ ] API returns improved prompt via /docs
- [ ] Streamlit runs on port 8501 (from project root)
- [ ] Can enter prompt in Streamlit
- [ ] Improved prompt displays in Streamlit
- [ ] Judge scores display in Streamlit
- [ ] Can see request logs in backend terminal
- [ ] File storage exists (even if not connected)

---

## 📊 Quick Command Reference

**From Project Root:**

```powershell
# Terminal 1 - Backend
python -m uvicorn backend.api:app --reload

# Terminal 2 - Frontend  
python -m streamlit run apps/web/streamlit_app.py

# Install dependencies (if needed)
python -m pip install -r backend/requirements.txt
python -m pip install -r apps/web/requirements.txt
python -m pip install psycopg2-binary

# Test backend
# Open: http://localhost:8000
# Open: http://localhost:8000/docs

# Test frontend
# Open: http://localhost:8501
```

---

## 🎯 Week 4 Demo Script

**For your presentation:**

**Setup (Before Demo):**
1. Open 2 terminals
2. Terminal 1: Start backend
3. Terminal 2: Start frontend
4. Open browser to http://localhost:8501

**Demo Steps (5 minutes):**

1. **Show Backend API (1 min):**
   - Open new tab: `http://localhost:8000/docs`
   - Point out the endpoints
   - Show POST /v1/prompts endpoint

2. **Show Frontend (3 min):**
   - Switch to Streamlit tab (http://localhost:8501)
   - Enter a prompt: "Write a Python function to calculate fibonacci"
   - Click "Improve Prompt"
   - Point out:
     - Original prompt
     - Improved prompt (with role, deliverables, constraints)
     - Explanation bullets
     - Judge scores (5 metrics)
     - Total score

3. **Show Backend Logs (30 sec):**
   - Switch to backend terminal
   - Show the POST request log
   - Explain the flow

4. **Explain Architecture (30 sec):**
   ```
   User → Streamlit (port 8501) 
        → HTTP POST request 
        → FastAPI Backend (port 8000)
        → Engine (improve prompt)
        → Judge (score it)
        → Return JSON
        → Display in Streamlit
   ```

**Talking Points:**
- "We have 3 components: Frontend, Backend, and Storage"
- "Frontend and Backend are connected via HTTP"
- "Backend uses Engine to improve prompts"
- "Backend uses Judge to score improvements"
- "Storage is separate for now (Week 4)"

---

## 📝 Testing Report Template

Use this to document your testing:

```
## Testing Report - [Date]

### Setup
- Team members present: Paing, Atang, Bellul
- Location: [Where you tested]
- Duration: [How long]

### Backend Test
- Status: ✅ / ❌
- Port: 8000
- Endpoints tested: GET /, POST /v1/prompts
- Dependencies installed: ✅ / ❌
- Running from project root: ✅ / ❌
- Notes: 

### Frontend Test
- Status: ✅ / ❌
- Port: 8501
- Features tested: Input form, Display results, Scores
- Dependencies installed: ✅ / ❌
- Running from project root: ✅ / ❌
- Notes:

### Integration Test
- Status: ✅ / ❌
- Flow: Frontend → Backend → Engine → Judge → Frontend
- Sample prompt tested: "Write a Python function"
- Response received: ✅ / ❌
- Response time: [seconds]
- Notes:

### Storage Test
- Status: ✅ / ❌ / Not Connected
- Files exist: ✅ / ❌
- Connected to backend: ❌ (not required for Week 4)
- Notes:

### Issues Found
1. [Issue description]
2. [Issue description]
3. [Issue description]

### Solutions Applied
1. [Solution description]
2. [Solution description]

### Screenshots/Evidence
- [ ] Backend running in terminal
- [ ] Frontend in browser
- [ ] API docs page
- [ ] Improved prompt result

### Next Steps for Week 5
- [ ] Add LLM integration (replace template with real API)
- [ ] Connect storage to backend
- [ ] Set up PostgreSQL database
```

---

**Good luck with your demo! 🚀**

**Remember:**
- Both must run from project root
- Use `python -m` for both commands
- Backend first, then frontend
- Check http://localhost:8000 and http://localhost:8501
