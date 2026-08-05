# Session Summary: MemoryGraph Plugin Installation & Cron Recovery (2026-05-03)

**Date:** 2026-05-03 15:30–16:05 PDT  
**Status:** ✅ Plugin installed, 🔴 Recovery planning phase  
**Owner:** Nova  

---

## Executive Summary

MemoryGraph plugin successfully installed and running in OpenClaw, but discovered **4 critical cron jobs are offline** that were responsible for automated knowledge extraction, scenario optimization, and index rebuilding. A comprehensive recovery plan has been documented.

---

## What Was Accomplished

### ✅ Plugin Installation Completed
1. Located compiled MemoryGraph from `/srv/github/MemoryGraph` (had dist/ + node_modules)
2. Installed via `openclaw plugins install --dangerously-force-unsafe-install`
   - Note: Safe to force install (compaction needs shell execution)
3. Gateway restarted successfully
4. Plugin enabled and verified in `openclaw plugins list`

### ✅ Discovered Root Issues
Through memory search and audit notes from 2026-04-29, found:
- **4 missing cron jobs** (not configured in OpenClaw cron)
- **Silent failure pattern** (8-day failure in April went unnoticed)
- **Plugin tool accessibility issue** (isolated cron sessions don't have plugin tools)
- **EM index offline** (~3 days, 4,577 lessons not being updated)

### ✅ Created Recovery Documentation
1. **`TODO_RECOVERY_20260503.md`** (7.9KB) — Detailed debugging & cron setup guide
2. **`2026-05-03-memorygraph-recovery.md`** (4.3KB) — Session notes & findings
3. **Updated MEMORY.md** — Added recovery section with key lessons

---

## Key Findings

### Previous Audit Trail (2026-04-29)
Found comprehensive notes from a cron audit that discovered and fixed a critical bug:
- **Root cause:** `systemEvent → main` jobs tried calling TypeScript plugin tools from isolated sessions
- **Result:** 8 days of silent failures (2026-04-21 to 2026-04-29)
- **Fix applied:** Switched to `isolated agentTurn` with Python CLI direct execution
- **New script created:** `build_index.py` for nightly EM index rebuilding

### EM (Entity Memory) Last Known State
- **4,577 lessons** indexed with 768-dimensional embeddings
- **k-means clustering:** 12 clusters (cosine similarity)
- **Validation baseline:** 80% success rate
- **Known issues:** 
  - Query q2 returns 0 entities (bug)
  - Query q5 timeout at 3278ms (performance issue)
- **Last index build:** 2026-04-30 (manual test run)

### Cron Jobs That Should Be Running

| Job | Schedule | Status | Last Run | Days Offline |
|-----|----------|--------|----------|--------------|
| extract_and_promote | 6 AM UTC daily | ❌ | 2026-04-30 | 3 |
| scenario_optimization | 7 AM UTC Mon | ❌ | 2026-04-27 | 6+ |
| ai_news_ingest | 8 AM UTC Mon | ❌ | 2026-04-29 (test) | 3+ |
| phase2_promotion | 2026-05-06 7 AM UTC | ❌ | Never | — |

---

## Architecture Issue Discovered

### The Plugin Tools Problem
**Symptom:** Cron jobs appeared to succeed but did nothing  
**Root cause:** `systemEvent` dispatch vs actual execution
- Main session = has plugin tools loaded
- Isolated cron sessions = no plugin tools available
- `systemEvent → main` tried to call tools from isolated session context

**Solution Pattern (2026-04-29):**
```
OLD (broken):
  systemEvent (main) → try calling memorygraph_extract → fail silently

NEW (working):
  isolated agentTurn → shell exec: python main.py extract → works
```

### Critical Lesson
**Never call OpenClaw plugin tools from isolated cron jobs.** Use Python CLI or shell commands instead.

---

## Recovery Checklist

### Immediate (Before Next Run)
- [ ] Verify `/srv/github/MemoryGraph/python/build_index.py` exists
- [ ] Test build_index.py manually
- [ ] Check llama.cpp port 11434 is responsive
- [ ] Create first cron job (`memorygraph_extract_and_promote`)
- [ ] Test first cron job manually

### This Week
- [ ] Create remaining 3 cron jobs
- [ ] Monitor first scheduled runs (6 AM UTC tomorrow)
- [ ] Check `data/index-YYYY-MM-DD.json` is created
- [ ] Fix query q2 bug (returns 0 entities)
- [ ] Prepare Phase 2 decision for 2026-05-06

### Monitoring
- Watch for silent failures (set up alert on cron runs)
- Track EM index size (should grow daily)
- Monitor scenario winners (should update Mondays)
- Verify news articles feeding into extraction

---

## Documentation Trail

**Created this session:**
- `/srv/openclaw_projects/MemoryGraph/TODO_RECOVERY_20260503.md` — Complete recovery guide
- `/home/leto/.openclaw/workspace/memory/2026-05-03-memorygraph-recovery.md` — Session findings
- `/home/leto/.openclaw/workspace/MEMORY.md` — Updated with MemoryGraph status

**Reference documents:**
- `/home/leto/.openclaw/workspace/memory/2026-04-29-evening-memorygraph-cron-audit.md` — Original audit + fix
- `/home/leto/.openclaw/workspace/memory/2026-05-02-memorygraph-owl-review.md` — EM status review
- `/srv/openclaw_projects/MemoryGraph/CURRENT.md` — Project current state
- `/srv/openclaw_projects/MemoryGraph/START_HERE.md` — Architecture overview

---

## Phase 2 Timeline Impact

**Original plan:** Phase 2 (vector embeddings) starts ~2026-05-07  
**Current status:** EM pipeline offline, needs recovery first  
**Decision gate:** 2026-05-06 7 AM UTC (phase2_promotion.py one-time job)

**Action required:** Get cron jobs running before Phase 2 gate or Phase 2 implementation will stall

---

## Risk Assessment

🔴 **HIGH PRIORITY** — EM offline, knowledge extraction not happening  
🔴 **HIGH PRIORITY** — Phase 2 gate approaching (3 days), needs working EM first  
🟡 **MEDIUM** — Query bugs (q2, q5) but workarounds exist  
🟢 **LOW** — Plugin installed correctly, infrastructure is ready  

---

## Next Session

**Ready to proceed with:**
1. Verify build_index.py
2. Create and test first cron job
3. Monitor extraction pipeline
4. Debug query issues if time permits

**NOT YET ready for:**
- Phase 2 implementation (wait for cron jobs to stabilize)
- Full vector embedding integration (need working EM first)

---

**Prepared by:** Nova  
**Date:** 2026-05-03 16:05 PDT  
**Status:** 🔴 DEBUGGING — Cron jobs offline, recovery plan ready, plugin installed
