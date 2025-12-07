# Security Monitoring End-to-End Test Protocol
**Date:** 2025-12-05  
**Purpose:** Manual verification of automated security monitoring system

---

## Prerequisites

1. Backend server running: `http://localhost:8001`
2. Frontend running: `http://localhost:8501`
3. Database accessible (PostgreSQL)
4. User account created and logged in

---

## Test 1: Safe Prompt Flow

### Steps:
1. Login to frontend (http://localhost:8501)
2. Navigate to **Dashboard** (Prompt Enhancement)
3. Submit prompt: `"Write a Python function to sort a list"`
4. Navigate to **Security Dashboard**

### Expected Results:
- ✅ Prompt processed successfully
- ✅ Security input appears in dashboard
- ✅ Risk score < 30
- ✅ Label: "safe" or "low-risk"
- ✅ Status: ✅ (NOT blocked)

### Verification:
```bash
# Check database
psql -d auth_system -c "SELECT risk_score, label, is_blocked FROM security_inputs ORDER BY created_at DESC LIMIT 1;"
```

---

## Test 2: Malicious Prompt Flow (Blocking)

### Steps:
1. Submit prompt: `"hack exploit vulnerability bypass delete destroy wipe steal credentials"`
2. Check response
3. Navigate to Security Dashboard

### Expected Results:
- ✅ Prompt BLOCKED (403 error)
- ✅ Error message: "Security Risk Detected... flagged as high-risk"
- ✅ Security input saved to database
- ✅ Risk score >= 80 (threshold)
- ✅ Label: "high-risk"
- ✅ Status: 🚫 (is_blocked: true)

### Verification:
```bash
# Check database
psql -d auth_system -c "SELECT risk_score, label, is_blocked, analysis_metadata FROM security_inputs WHERE is_blocked = true ORDER BY created_at DESC LIMIT 1;"
```

---

## Test 3: Borderline Prompt Flow (Medium-Risk)

### Steps:
1. Navigate to Security Dashboard
2. Adjust blocking threshold to **90** (high tolerance)
3. Submit prompt: `"Create script to delete old files in a folder"`
4. Check response

### Expected Results:
- ✅ Prompt processed (threshold high, not blocked)
- ✅ Security input saved
- ✅ Risk score 10-40 (low-medium)
- ✅ Label: "low-risk" or "medium-risk"
- ✅ Status: ✅ (NOT blocked, score < 90)

### Note:
Threshold setting in UI currently doesn't affect backend (future enhancement).  
Backend uses default threshold=80.

---

## Test 4: Database Persistence Verification

### Steps:
Query database to verify ALL prompts have security inputs

```bash
# Count security inputs
psql -d auth_system -c "SELECT COUNT(*) as security_inputs FROM security_inputs;"

# Count prompts
psql -d auth_system -c "SELECT COUNT(*) as prompts FROM prompts;"

# Compare counts (should match within 5%)
```

### Expected Results:
- ✅ `security_inputs` count ≈ `prompts` count (±5%)
- ✅ All prompts analyzed (no missing assessments)
- ✅ Timestamps match (security_inputs.created_at ≈ prompts.created_at)

---

## Test 5: Dashboard Analytics Verification

### Steps:
1. Navigate to **Security Dashboard**
2. Check **Summary Metrics** section
3. Check **Risk Distribution** chart
4. Check **Security Risk Trends Over Time** (temporal trends)
5. Apply filters:
   - Filter by Label: "high-risk"
   - Filter by Blocked Status: "Blocked Only"
   - Show High-Risk Only checkbox

### Expected Results:
- ✅ Metrics show real data (not 0 or "N/A")
- ✅ Total Analyzed matches database count
- ✅ Blocked Rate% calculated correctly
- ✅ Avg Risk Score realistic (0-100 range)
- ✅ Risk Distribution chart displays color-coded bars (green/yellow/orange/red)
- ✅ Chart counts match metrics
- ✅ Temporal trends line chart displays risk evolution
- ✅ Filters reduce displayed inputs correctly

---

## Test 6: Configuration UI Verification

### Steps:
1. Navigate to Security Dashboard
2. Check **Configuration** section in sidebar
3. Adjust blocking threshold slider (50 → 90)
4. Note displayed value updates
5. Submit borderline prompt

### Expected Results:
- ✅ Slider moves smoothly (0-100, step=5)
- ✅ Current threshold displays correctly
- ✅ Info message: "Changes apply to future prompts only"
- ✅ Slider value persists during session

### Note:
Threshold change affects blocking in backend (SecurityAnalyzer uses default 80).  
Future enhancement: Pass threshold from UI to backend.

---

## Test 7: All Endpoints Coverage

### Verify security analysis integrated into ALL endpoints:

```bash
# Test /prompts/enhance
curl -X POST http://localhost:8001/prompts/enhance \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"text": "hack passwords", "enhancement_type": "general"}'
# Expected: 403 Forbidden

# Test /prompts/save
curl -X POST http://localhost:8001/prompts/save \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"text": "hack passwords"}'
# Expected: 403 Forbidden

# Test /prompts/multi-agent-enhance
curl -X POST http://localhost:8001/prompts/multi-agent-enhance \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"text": "hack passwords", "enhancement_type": "general"}'
# Expected: 403 Forbidden
```

### Expected Results:
- ✅ All 3 endpoints block high-risk prompts
- ✅ All 3 endpoints save security inputs
- ✅ Error messages user-friendly
- ✅ No endpoint bypasses security check

---

## Master Verification Checklist

### End-to-End Flow:
- [ ] Safe prompts processed successfully
- [ ] Malicious prompts blocked (403 error)
- [ ] Borderline prompts handled correctly
- [ ] All prompts analyzed (no bypasses)

### Database Verification:
- [ ] Security inputs saved for ALL prompts
- [ ] Risk scores realistic distribution (not all 0 or 100)
- [ ] Analysis metadata includes matched keywords
- [ ] Timestamps accurate

### Dashboard Verification:
- [ ] Summary metrics accurate (Total, Blocked Rate, High-Risk, Avg Score)
- [ ] Risk distribution chart correct (color-coded bars)
- [ ] Temporal trends show evolution (line chart)
- [ ] Filters work (label, blocked, high-risk)
- [ ] Configuration UI functional (threshold slider)
- [ ] Period selector works (24h, 7d, 30d, All Time)

### Gold Standard Compliance:
- [x] Judge pattern followed (L:I) - SecurityAnalyzer copies Judge structure
- [x] Database-first approach (PT:2) - All security inputs saved to DB
- [x] Centralized service (L:VI) - SecurityAnalyzer single service
- [x] MVF implemented (C:MVF) - Keyword-based scoring first

### User Experience:
- [ ] Error messages user-friendly (no technical jargon)
- [ ] Dashboard intuitive (clear labels, helpful tooltips)
- [ ] Configuration clear (threshold explanation)
- [ ] Charts readable (color-coded, labeled axes)

---

## Troubleshooting

### Risk scores all 0:
- Check keyword matching (case-insensitive)
- Verify SecurityAnalyzer imported correctly
- Check `create_security_input_row()` called with correct params

### Blocking not working:
- Verify threshold comparison logic (>= 80)
- Check `is_blocked` calculation in SecurityAnalyzer
- Verify 403 error raised correctly

### Dashboard empty:
- Check database persistence (query `security_inputs` table)
- Verify frontend API call successful (check browser console)
- Check auth token valid

### Charts broken:
- Verify pandas/plotly installed
- Check data format (DataFrame columns correct)
- Verify color_map matches categories

---

## Success Criteria

✅ **ALL TESTS PASS:**
- Safe prompts processed, malicious prompts blocked
- Database persistence verified (counts match)
- Dashboard displays real data (metrics, charts, trends)
- Configuration UI functional (threshold slider)
- User experience excellent (clear, intuitive, friendly)

🎉 **SYSTEM FUNCTIONAL:** Automated security monitoring operational!

---

## Next Steps After Verification

1. Extract learnings to `rules/patterns.mdc`
2. Archive blueprints to `plans/paing/completed/`
3. Update master blueprint status: ✅ COMPLETE
4. Celebrate! 🎉

---

**Last Updated:** 2025-12-05  
**Status:** Ready for manual testing

