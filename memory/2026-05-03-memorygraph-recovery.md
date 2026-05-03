# 2026-05-03 — MemoryGraph Plugin Installation + Cron Recovery

**Status:** ✅ Plugin installed, 🔴 Cron jobs offline  
**Session:** MemoryGraph OCP verification + installation  

---

## What Happened This Session

### ✅ MemoryGraph Plugin Successfully Installed
- Installed from `/srv/github/MemoryGraph` (compiled version with dist/)
- Version: 0.1.0
- Status: **enabled** and running
- Gateway restarted successfully
- Signal capture ready (not yet tested in real sessions)

### 🔴 Found 4 Missing Cron Jobs
All automation offline since ~2026-04-30:

1. **`memorygraph_extract_and_promote`** (6 AM UTC daily)
   - Pipeline: extract → lint → promote → changelog → build_index
   - Timeout: 600s
   - **Last run:** 2026-04-30 (manual test, 4,577 lessons indexed)
   - Status: NOT CONFIGURED

2. **`memorygraph_scenario_optimization`** (7 AM UTC Mondays)
   - Tests 12 query variants, locks top 3 winners
   - Last run: 2026-04-27 ✅
   - Status: NOT CONFIGURED

3. **`memorygraph_ai_news_ingest`** (8 AM UTC Mondays)
   - Fetches AI articles, scores by relevance
   - First test: 100 articles, 75 above threshold, 1 lesson
   - Status: NOT CONFIGURED

4. **`memorygraph_phase2_promotion_reminder`** (2026-05-06 7 AM UTC, one-time)
   - Triggers Phase 2 decision gate
   - Decision point: Lock HNSW params, ready vector embeddings
   - Status: NOT CONFIGURED (likely past due or waiting)

---

## Key Findings from 2026-04-29 Audit Notes

### Critical Lesson Learned
**Isolated cron agents don't have OpenClaw plugin tools loaded.** The original setup using `systemEvent → main` failed silently for 8 days without alerting.

**Fix pattern discovered:**
- Use `isolated agentTurn` instead of systemEvent
- Call Python CLI directly: `python main.py extract`, `lint`, `promote`, etc.
- Don't try to invoke TypeScript plugin tools from isolated cron jobs

### EM (Entity Memory) Last Known State
- **4,577 lessons** indexed
- **768-dimensional** embeddings (via llama.cpp port 11434)
- **12 clusters** (k-means, cosine similarity)
- **80% baseline** validation success rate
- Query issues: q2 (0 entities), q5 (3278ms timeout)

### Python Index Rebuild Script
- **Script:** `build_index.py` at `/srv/github/MemoryGraph/python/build_index.py`
- **Function:** Loads extraction drafts + memory → deduplicates → embeds via llama.cpp → k-means clusters → writes index
- **Output:** `index-YYYY-MM-DD.json`, `clusters-YYYY-MM-DD.json`, `lessons-YYYY-MM-DD.json`
- **Performance:** ~10min for 4k+ lessons
- **Status:** Need to verify file exists and is functional

---

## Debugging Needed

**Before MemoryGraph is operational:**

1. [ ] Verify `build_index.py` exists and runs
2. [ ] Check llama.cpp port 11434 is responsive
3. [ ] Create + test first cron job (`memorygraph_extract_and_promote`)
4. [ ] Recreate remaining 3 cron jobs
5. [ ] Fix query q2 (0 entities bug)
6. [ ] Monitor for silent failures like 2026-04-21–04-29
7. [ ] Prepare Phase 2 decision for 2026-05-06

---

## Documentation Created

**File:** `/srv/openclaw_projects/MemoryGraph/TODO_RECOVERY_20260503.md` (7.9KB)
- Complete debugging checklist
- Cron job specifications (schedule, timeout, command)
- Phase 2 timeline
- Known issues & workarounds

---

## What's Working vs What's Not

✅ **Working:**
- MemoryGraph plugin installed + enabled
- Gateway running
- Plugin architecture (hooks registered)
- Knowledge graph structure (306 nodes, working)
- Scenario optimization framework (last run 2026-04-27)

🔴 **Offline/Needs Debugging:**
- Daily extraction pipeline (cron job missing)
- EM index rebuild (no longer running)
- Query q2 (returns 0 entities)
- Query q5 (3278ms timeout)
- Signal capture (plugin ready, untested in sessions)
- Phase 2 promotion reminder (one-time job not scheduled)

---

## Next Session Actions

**High priority:**
1. Verify `build_index.py` exists
2. Create first cron job + test run
3. Monitor extraction logs for errors

**Medium priority:**
4. Recreate remaining cron jobs
5. Fix query issues (q2, q5)
6. Prepare Phase 2 decision

**Monitoring:**
- Watch 2026-05-06 Phase 2 gate (in 3 days)
- Track EM index rebuild success
- Log all cron run results

---

**Session time:** 2026-05-03 15:30–16:00 PDT  
**Focus:** MemoryGraph plugin installation, cron recovery planning  
**Outcome:** Plugin running, recovery plan documented
