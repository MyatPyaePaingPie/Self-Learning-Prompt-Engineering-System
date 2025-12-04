# Temporal Analysis User Authentication Implementation
**Date:** December 4, 2025  
**Status:** ✅ COMPLETE  
**Purpose:** Tie temporal analysis data to authenticated users

---

## Overview

Updated the temporal analysis system to filter all data by authenticated user, ensuring each user only sees their own prompt evolution data.

## Changes Implemented

### 1. Temporal Timeline Endpoint (`GET /api/temporal/timeline`)
**File:** `backend/main.py` (lines 849-913)

**Added Security Check:**
```python
# SECURITY: Verify prompt belongs to current user
prompt = session.query(Prompt).filter(
    Prompt.id == uuid.UUID(prompt_id),
    Prompt.user_id == str(current_user.id)
).first()

if not prompt:
    raise HTTPException(status_code=404, detail="Prompt not found or access denied")
```

**Impact:** Users can only view timeline data for their own prompts.

---

### 2. Temporal Statistics Endpoint (`GET /api/temporal/statistics`)
**File:** `backend/main.py` (lines 914-976)

**Added Security Check:**
```python
# SECURITY: Verify prompt belongs to current user
prompt = session.query(Prompt).filter(
    Prompt.id == uuid.UUID(prompt_id),
    Prompt.user_id == str(current_user.id)
).first()

if not prompt:
    raise HTTPException(status_code=404, detail="Prompt not found or access denied")
```

**Impact:** Users can only view statistics for their own prompts.

---

### 3. Causal Hints Endpoint (`GET /api/temporal/causal-hints`)
**File:** `backend/main.py` (lines 977-1067)

**Added Security Check:**
```python
# SECURITY: Verify prompt belongs to current user
prompt = session.query(Prompt).filter(
    Prompt.id == uuid.UUID(prompt_id),
    Prompt.user_id == str(current_user.id)
).first()

if not prompt:
    raise HTTPException(status_code=404, detail="Prompt not found or access denied")
```

**Impact:** Users can only view causal correlations for their own prompts.

---

### 4. Synthetic Data Generation (`POST /api/temporal/generate-synthetic`)
**File:** `backend/main.py` (lines 1068-1167)

**Added Security Check:**
```python
# SECURITY: Verify prompt exists and belongs to current user
prompt = session.query(Prompt).filter(
    Prompt.id == uuid.UUID(request.prompt_id),
    Prompt.user_id == str(current_user.id)
).first()

if not prompt:
    raise HTTPException(status_code=404, detail="Prompt not found or access denied")
```

**Impact:** Users can only generate test data for their own prompts.

---

## Authentication Architecture

### Database Layer
**File:** `packages/db/models.py`

```python
class Prompt(Base):
    __tablename__ = "prompts"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str | None]  # ← User authentication field
    original_text: Mapped[str]
    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.utcnow)
```

**CRUD Layer:** `packages/db/crud.py`
```python
def create_prompt_row(session: Session, user_id: str | None, original_text: str) -> Prompt:
    """Create a new prompt record"""
    prompt = Prompt(user_id=user_id, original_text=original_text)
    session.add(prompt)
    session.flush()
    return prompt
```

### API Layer
All temporal endpoints now use:
```python
async def endpoint(
    prompt_id: str,
    current_user: User = Depends(get_current_user)  # ← JWT authentication
):
```

### Frontend Layer
**File:** `frontend/temporal_client.py`

```python
headers = {
    'Authorization': f'Bearer {self.token}'  # ← JWT token passed to backend
}
```

---

## How Real Data Works

### Data Flow (User-Specific):

1. **User logs in** → JWT token generated with `user_id`
2. **User creates prompt** → `Prompt` record saved with `user_id` field
3. **User edits prompt** → New `PromptVersion` created with `parent_version_id` (version chain)
4. **Judge evaluates** → `JudgeScore` record created for version
5. **Temporal analysis** → Queries filtered by `user_id` (shows only user's data)

### Real Data Example:

```python
# User creates prompt (database saves user_id)
prompt = create_prompt_row(
    session=session,
    user_id="123",  # From authenticated JWT token
    original_text="Write a Python function..."
)

# User edits prompt (version chain created)
version1 = create_version_row(
    session=session,
    prompt_id=prompt.id,
    version_no=1,
    text="Write a Python function to sort...",
    parent_version_id=None,  # First version
    change_type="structure"
)

version2 = create_version_row(
    session=session,
    prompt_id=prompt.id,
    version_no=2,
    text="Write a Python function to efficiently sort...",
    parent_version_id=version1.id,  # Parent → child chain
    change_type="wording"
)

# Judge scores each version
score1 = create_judge_score_row(
    session=session,
    version_id=version1.id,
    scorecard=Scorecard(clarity=70, specificity=65, ...)
)

score2 = create_judge_score_row(
    session=session,
    version_id=version2.id,
    scorecard=Scorecard(clarity=85, specificity=80, ...)
)

# Temporal analysis (automatically filtered by user_id)
timeline = await get_temporal_timeline(
    prompt_id=prompt.id,
    start="2025-11-01",
    end="2025-12-04",
    current_user=authenticated_user  # Only shows user's versions
)
```

---

## Synthetic vs. Real Data

### Synthetic Data (Test Mode)
- **Purpose:** Testing temporal analysis without waiting 30+ days
- **Generation:** Click "Generate 30-Day Test Data" button
- **Data:** Fake version history with random scores
- **User-specific:** ✅ Now filtered by authenticated user
- **Indicator:** Versions marked with `{"synthetic": True}` in metadata

### Real Data (Production Mode)
- **Purpose:** Actual prompt evolution over time
- **Generation:** Natural usage - edit prompts, get judge evaluations
- **Data:** Real version chains with actual judge scores
- **User-specific:** ✅ Filtered by authenticated user
- **Indicator:** Versions marked with actual `source` (e.g., "user_edit", "agent_enhancement")

---

## Security Benefits

1. **Data Isolation:** Users only see their own prompts and versions
2. **Access Control:** 404 error if user tries to access another user's prompt
3. **JWT Authentication:** All endpoints require valid authentication token
4. **User Verification:** `user_id` validated on every temporal API call

---

## Verification

### Test User Authentication:

```bash
# 1. Register user
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "Test123"}'

# 2. Login to get JWT token
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "Test123"}'
# Returns: {"access_token": "eyJ...", "token_type": "bearer"}

# 3. Access temporal endpoint with token
curl http://localhost:8001/api/temporal/timeline?prompt_id=... \
  -H "Authorization: Bearer eyJ..."

# 4. Try accessing another user's prompt (should fail with 404)
curl http://localhost:8001/api/temporal/timeline?prompt_id=<other_user_prompt> \
  -H "Authorization: Bearer eyJ..."
# Returns: 404 "Prompt not found or access denied"
```

---

## Next Steps

### For Development:
1. ✅ Temporal endpoints filter by user_id (DONE)
2. ✅ Synthetic data generation user-specific (DONE)
3. ✅ Database CRUD layer supports user_id (ALREADY WORKING)
4. ⏳ Frontend: Ensure prompts are saved to database when created
5. ⏳ Frontend: Display real vs. synthetic data indicator

### For Production:
1. Add rate limiting per user (not just global)
2. Add audit logging for temporal data access
3. Add data export feature (user downloads their temporal data)
4. Add data deletion feature (GDPR compliance)

---

## Files Modified

- `backend/main.py` (4 endpoints updated with user_id filtering)
- No database schema changes (user_id field already exists)
- No frontend changes (JWT authentication already in place)

---

## Status: ✅ COMPLETE

All temporal analysis endpoints now filter data by authenticated user. Users can only access their own prompt evolution data.

