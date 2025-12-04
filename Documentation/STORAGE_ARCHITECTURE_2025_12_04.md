# Storage Architecture: Database-First Pattern
**Date:** December 4, 2025  
**Status:** ✅ COMPLETE - CSV Deprecated, Database Primary

---

## THE SIMPLE RULE

```
ALL DATA GOES TO DATABASE (@db)
CSV FILES ARE EXPORT ONLY (@storage)
```

---

## TWO SYSTEMS EXPLAINED

### ✅ @db - PostgreSQL/SQLite Database (PRIMARY)

**Location:** `packages/db/`

**What Goes Here:**
- ✅ Prompts (with user_id, request_id)
- ✅ Prompt versions
- ✅ Judge scores
- ✅ User feedback (NEW - migrated from CSV)
- ✅ Security scans
- ✅ Temporal analysis data
- ✅ ALL user-specific data

**Models:**
```python
Prompt        - id, user_id, request_id, original_text, created_at
PromptVersion - id, prompt_id, version_no, text, source, parent_version_id
JudgeScore    - id, prompt_version_id, clarity, specificity, ...
UserFeedback  - id, request_id, user_id, prompt_id, user_choice, judge_winner, agent_winner
BestHead      - prompt_id, prompt_version_id, score
SecurityInput - id, user_id, input_text, risk_score, label
```

---

### 📤 @storage - CSV Files (EXPORT ONLY)

**Location:** `storage/`

**What Goes Here:**
- 📤 CSV exports (manual export via API)
- 📤 That's it

**DO NOT:**
- ❌ Save new data to CSV
- ❌ Read CSV as source of truth
- ❌ Use CSV for any writes

**ONLY USE FOR:**
- ✅ Manual export via `/api/storage/export-*` endpoints

---

## DATA FLOW (DATABASE-FIRST)

### Creating Prompts
```python
# Multi-Agent Enhancement
POST /prompts/multi-agent-enhance
    ↓
request_id = str(uuid.uuid4())  # Generate request ID
    ↓
create_prompt_row(
    user_id=current_user.id,
    original_text=prompt_text,
    request_id=request_id  # ← Links feedback to prompt
)
    ↓
create_version_row(...)  # Original version
    ↓
create_version_row(...)  # Enhanced version
    ↓
session.commit()  # All saved to DATABASE
    ↓
Returns: request_id, prompt_id
```

### Submitting Feedback
```python
# User clicks feedback button
POST /prompts/feedback
    ↓
get_prompt_by_request_id(request_id)  # Find prompt in DATABASE
    ↓
Verify: prompt.user_id == current_user.id  # Security check
    ↓
create_feedback_row(
    request_id=request_id,
    user_id=current_user.id,
    prompt_id=prompt.id,
    user_choice="multi",  # User's choice
    judge_winner="syntax",
    agent_winner="syntax"
)
    ↓
session.commit()  # Saved to DATABASE
    ↓
Returns: Success
```

### Querying Agent Effectiveness
```python
# Get agent effectiveness stats
GET /api/storage/agent-effectiveness
    ↓
get_agent_effectiveness_from_feedback(
    user_id=current_user.id  # User-specific
)
    ↓
Queries: user_feedback table (DATABASE)
    ↓
Calculates: Win rates per agent
    ↓
Returns: Effectiveness metrics
```

---

## MIGRATION SUMMARY

### What Changed:

**Before (Broken):**
```
Multi-Agent Enhancement → Database (prompts)
User Feedback → CSV file (multi_agent_log.csv) ← FAILED (file deleted)
```

**After (Fixed):**
```
Multi-Agent Enhancement → Database (prompts + request_id)
User Feedback → Database (user_feedback table)
```

### Files Modified:

1. **`packages/db/models.py`**
   - Added `request_id` field to `Prompt` model
   - Added `UserFeedback` model (complete table)

2. **`packages/db/crud.py`**
   - Updated `create_prompt_row()` to accept `request_id`
   - Added `get_prompt_by_request_id()`
   - Added `create_feedback_row()`
   - Added `get_feedback_by_request_id()`
   - Added `get_feedback_by_user()`
   - Added `get_agent_effectiveness_from_feedback()`

3. **`backend/main.py`**
   - Updated `/prompts/multi-agent-enhance` to save `request_id` with prompt
   - Updated `/prompts/feedback` to save to database (not CSV)
   - Added security check (user can only feedback on their own prompts)

4. **`packages/db/migrations/004_add_request_id_to_prompts.sql`**
   - Adds `request_id` column to prompts table
   - Creates `user_feedback` table
   - Creates indexes for performance

---

## DATABASE SCHEMA

### prompts Table (Updated)
```sql
CREATE TABLE prompts (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    request_id TEXT,  -- NEW: Links to feedback
    original_text TEXT,
    created_at TEXT
);
```

### user_feedback Table (NEW)
```sql
CREATE TABLE user_feedback (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,  -- Links to prompts.request_id
    user_id TEXT NOT NULL,
    prompt_id TEXT NOT NULL REFERENCES prompts(id),
    user_choice TEXT NOT NULL,  -- "original", "single", "multi"
    judge_winner TEXT NOT NULL,  -- "syntax", "structure", "domain"
    agent_winner TEXT NOT NULL,  -- "none", "template", "syntax", etc.
    judge_correct INTEGER NOT NULL,  -- 1=correct, 0=incorrect
    created_at TEXT NOT NULL
);
```

---

## HOW TO USE

### Saving Prompts (With Request Tracking)
```python
from packages.db.crud import create_prompt_row, create_version_row
from packages.db.session import get_session

request_id = str(uuid.uuid4())

with get_session() as session:
    prompt = create_prompt_row(
        session=session,
        user_id=str(current_user.id),
        original_text="Your prompt text",
        request_id=request_id  # NEW: For feedback linkage
    )
    
    version = create_version_row(
        session=session,
        prompt_id=prompt.id,
        version_no=1,
        text="Enhanced text",
        explanation={"source": "multi_agent"},
        source="multi_agent"
    )
    
    session.commit()
```

### Saving Feedback
```python
from packages.db.crud import create_feedback_row, get_prompt_by_request_id
from packages.db.session import get_session

with get_session() as session:
    # Find prompt by request_id
    prompt = get_prompt_by_request_id(session, request_id)
    
    # Save feedback
    feedback = create_feedback_row(
        session=session,
        request_id=request_id,
        user_id=str(current_user.id),
        prompt_id=prompt.id,
        user_choice="multi",
        judge_winner="syntax",
        agent_winner="syntax"
    )
    
    session.commit()
```

### Querying Agent Effectiveness
```python
from packages.db.crud import get_agent_effectiveness_from_feedback
from packages.db.session import get_session

with get_session() as session:
    effectiveness = get_agent_effectiveness_from_feedback(
        session=session,
        user_id=str(current_user.id)  # User-specific
    )
    
# Returns:
{
    "syntax": {"wins": 5, "total": 10, "effectiveness": 0.5},
    "structure": {"wins": 3, "total": 10, "effectiveness": 0.3},
    "domain": {"wins": 2, "total": 10, "effectiveness": 0.2}
}
```

---

## CSV FILES (DEPRECATED)

### What Happened to CSV Files?

**Old System:**
- `storage/multi_agent_log.csv` - Stored prompts + feedback
- `storage/prompt_versions.csv` - Stored version history
- **Problem:** No user isolation, data drift, file corruption

**New System:**
- Database stores everything
- CSV files optional (export only)

### CSV Export (Optional)

**Manual Export Endpoints:**
```python
POST /api/storage/export-multi-agent  # Export prompts to CSV
POST /api/storage/export-temporal     # Export versions to CSV
POST /api/storage/export-all          # Export everything to CSV
```

**Usage:**
- Click "Export Data" button in UI
- Downloads CSV file
- For backup/analysis only

---

## MIGRATION CHECKLIST

### ✅ Completed:
- [x] Created UserFeedback model
- [x] Created database migration (004_add_request_id_to_prompts.sql)
- [x] Added CRUD functions (create_feedback_row, get_feedback_by_request_id, etc.)
- [x] Updated multi-agent endpoint to save request_id
- [x] Updated feedback endpoint to use database
- [x] Ran migration successfully
- [x] Verified tables created

### 🧪 Testing Required:
- [ ] Create new prompt via multi-agent enhance
- [ ] Submit feedback
- [ ] Verify feedback saved to database
- [ ] Verify agent effectiveness queries work

---

## VERIFICATION COMMANDS

```bash
# 1. Check database schema
sqlite3 prompter.db "PRAGMA table_info(prompts);"
sqlite3 prompter.db "PRAGMA table_info(user_feedback);"

# 2. Check indexes
sqlite3 prompter.db "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='user_feedback';"

# 3. Test prompt creation
# Start backend: cd backend && python -m uvicorn main:app --reload --port 8001
# Create prompt via UI
# Check database: sqlite3 prompter.db "SELECT id, user_id, request_id FROM prompts ORDER BY created_at DESC LIMIT 1;"

# 4. Test feedback submission
# Submit feedback via UI
# Check database: sqlite3 prompter.db "SELECT * FROM user_feedback ORDER BY created_at DESC LIMIT 1;"
```

---

## TROUBLESHOOTING

### Error: "Request ID not found"
**Cause:** Prompt not saved with request_id  
**Fix:** Restart backend to pick up new code

### Error: "No such column: request_id"
**Cause:** Migration not run  
**Fix:** Run migration: `sqlite3 prompter.db < packages/db/migrations/004_add_request_id_to_prompts.sql`

### Error: "CSV file not found"
**Cause:** Old code still trying to use CSV  
**Fix:** Restart backend - new code uses database only

---

## STATUS: ✅ COMPLETE

**Migration successful. Feedback system now uses database.**

**Next Steps:**
1. Restart backend: `cd backend && python -m uvicorn main:app --reload --port 8001`
2. Test: Create prompt → Submit feedback → Verify saved
3. Delete old CSV files (they're obsolete now)

