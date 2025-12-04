# Database Cleanup Guide - Database-First Pattern

**Date:** December 4, 2025  
**Pattern:** Single Source of Truth (Database-First)

---

## Current State

### Databases Found:

1. **`prompter.db` (204 KB)** ← **PRIMARY DATABASE (KEEP)**
   - Contains: All prompt versions, judge scores, agent effectiveness data
   - Status: ACTIVE (single source of truth)
   - Last Modified: Dec 3, 2025
   - **What's in it:** 15 prompts + 45 versions + scores (from test data generator)

2. **`auth_system.db` (20 KB)** ← **AUTHENTICATION DATABASE (KEEP)**
   - Contains: User accounts, sessions, authentication data
   - Status: ACTIVE (used by backend auth)
   - Location: Project root

3. **`backend/auth_system.db` (20 KB)** ← **DUPLICATE (DELETE)**
   - Contains: Same auth data as above
   - Status: STALE (duplicate copy)
   - Action: DELETE (not used)

### CSV Files Found:

1. **`storage/multi_agent_log.csv` (6.8 KB)** ← **STALE (DELETE)**
   - Contains: 5 old multi-agent requests
   - Created: Before database-first migration
   - Status: STALE (not synced with database)
   - Action: DELETE (will regenerate from database)

2. **`storage/prompt_versions.csv` (127 KB)** ← **STALE (DELETE)**
   - Contains: Old temporal version data
   - Created: Before database-first migration
   - Status: STALE (not synced with database)
   - Action: DELETE (will regenerate from database)

3. **`storage/my_learning_log.csv` (797 B)** ← **DEMO DATA (DELETE)**
   - Contains: Demo/test learning log entries
   - Status: Demo data (not production)
   - Action: DELETE (demo only)

4. **`storage/prompt_learning_log.csv` (941 B)** ← **DEMO DATA (DELETE)**
   - Contains: Demo/test prompt learning entries
   - Status: Demo data (not production)
   - Action: DELETE (demo only)

---

## What to Keep

### ✅ KEEP THESE (Single Source of Truth):

1. **`prompter.db`** (204 KB)
   - **Why:** PRIMARY DATABASE - All production data lives here
   - **Contains:** 
     - 15 prompts
     - 45 prompt versions (syntax, structure, domain agents)
     - 45 judge scores
     - 15 best head selections
     - User data
   - **Status:** ACTIVE

2. **`auth_system.db`** (20 KB)
   - **Why:** Authentication database (users, sessions)
   - **Contains:** User accounts, access tokens, session data
   - **Status:** ACTIVE

---

## What to Delete

### ❌ DELETE THESE (Stale/Duplicate):

1. **`backend/auth_system.db`** (20 KB)
   - **Reason:** Duplicate of auth_system.db in root
   - **Impact:** None (not used)

2. **`storage/multi_agent_log.csv`** (6.8 KB)
   - **Reason:** Stale (created before database-first migration)
   - **Impact:** None (will regenerate from database when needed)

3. **`storage/prompt_versions.csv`** (127 KB)
   - **Reason:** Stale (not synced with database)
   - **Impact:** None (will regenerate from database when needed)

4. **`storage/my_learning_log.csv`** (797 B)
   - **Reason:** Demo/test data
   - **Impact:** None (demo only)

5. **`storage/prompt_learning_log.csv`** (941 B)
   - **Reason:** Demo/test data
   - **Impact:** None (demo only)

---

## Cleanup Commands

### Safe Cleanup (Recommended):

```bash
cd /Users/ariahan/Documents/persistos/Self-Learning-Prompt-Engineering-System

# Backup stale files first (just in case)
mkdir -p backup_old_csvs
cp storage/*.csv backup_old_csvs/
cp backend/auth_system.db backup_old_csvs/

# Delete stale CSV files
rm storage/multi_agent_log.csv
rm storage/prompt_versions.csv
rm storage/my_learning_log.csv
rm storage/prompt_learning_log.csv

# Delete duplicate auth database
rm backend/auth_system.db

echo "✅ Cleanup complete!"
```

### Regenerate Fresh CSV Files (From Database):

```bash
# After cleanup, regenerate CSV from database using the export page:
# 1. Go to frontend: http://localhost:8501
# 2. Navigate to "📊 Export Data (CSV)"
# 3. Click "Export Multi-Agent Data"
# 4. Click "Export Temporal Data"
```

---

## Verification

### After Cleanup, You Should Have:

```
Self-Learning-Prompt-Engineering-System/
├── prompter.db               ← PRIMARY DATABASE (204 KB)
├── auth_system.db            ← AUTH DATABASE (20 KB)
└── storage/
    ├── prompts/              ← Empty (or generated exports)
    └── results/              ← Empty (or generated exports)
```

### Verify Database Content:

```bash
# Check prompter.db has data
sqlite3 prompter.db "SELECT COUNT(*) FROM prompts;"
# Should return: 15

sqlite3 prompter.db "SELECT COUNT(*) FROM prompt_versions;"
# Should return: 45

sqlite3 prompter.db "SELECT source, COUNT(*) FROM prompt_versions GROUP BY source;"
# Should return:
#   syntax|15
#   structure|15
#   domain|15
```

---

## Database-First Pattern (Reminder)

### ✅ DO (Going Forward):

1. **Write to Database:**
   ```python
   # Write data
   version = create_prompt_version(db, ...)
   db.commit()
   ```

2. **Read from Database:**
   ```python
   # Query data
   effectiveness = get_agent_effectiveness_stats(db)
   ```

3. **Export CSV Manually (When Needed):**
   ```python
   # Export for analysis
   storage = FileStorage(db_session=db)
   storage.export_multi_agent_results_to_csv()
   ```

### ❌ DON'T (Never):

1. **Never Write to CSV Directly:**
   ```python
   # ❌ WRONG (data drift risk)
   storage.save_to_csv(...)
   ```

2. **Never Query CSV in Production:**
   ```python
   # ❌ WRONG (stale data)
   data = storage.read_from_csv('data.csv')
   ```

---

## Summary

**Single Source of Truth:**
- PostgreSQL (`prompter.db`) = PRIMARY
- CSV files = EXPORT ONLY (generated from database)

**Action Items:**
1. ✅ Delete 5 files (4 CSV + 1 duplicate DB)
2. ✅ Keep 2 databases (prompter.db + auth_system.db)
3. ✅ Regenerate CSV from database when needed (via export page)

**Space Saved:** ~155 KB (mostly stale CSV files)

---

## FAQ

**Q: What if I need the old CSV data?**
A: It's backed up in `backup_old_csvs/`. But the database (`prompter.db`) now has fresh test data that's better.

**Q: Will deleting CSV files break anything?**
A: No! The database-first pattern means CSV files are export-only. They'll be regenerated when you click "Export" in the UI.

**Q: How do I get CSV files back?**
A: Just use the export page in the UI or run:
```bash
curl -X POST http://localhost:8001/api/storage/export-all \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Q: What about auth_system.db vs backend/auth_system.db?**
A: Keep the one in root (`auth_system.db`), delete the duplicate in `backend/`.

---

**Next Steps:**
1. Run the cleanup commands above
2. Verify database content
3. Use the export page to regenerate fresh CSV when needed


