# MemoryGraph Documentation Index — 2026-05-03 Recovery Session

**Quick links to all documentation created this session**

---

## 📋 Documentation Files Created

### Recovery Planning
1. **`TODO_RECOVERY_20260503.md`** (7.9KB)
   - Location: `/srv/openclaw_projects/MemoryGraph/`
   - Content: Complete debugging checklist, cron job specs, Phase 2 timeline
   - Best for: Technical implementation guide

2. **`MEMORYGRAPH_RECOVERY_CHECKLIST.md`** (6.3KB)
   - Location: `/home/leto/.openclaw/workspace/`
   - Content: Step-by-step checklist with shell commands
   - Best for: Day-to-day tracking, print and check off boxes

3. **`MEMORYGRAPH_SESSION_SUMMARY_20260503.md`** (6.1KB)
   - Location: `/home/leto/.openclaw/workspace/`
   - Content: Executive summary, risk assessment, findings
   - Best for: Understanding what happened & why

### Memory & References
4. **`2026-05-03-memorygraph-recovery.md`** (4.3KB)
   - Location: `/home/leto/.openclaw/workspace/memory/`
   - Content: Session notes, what's working, what's offline
   - Best for: Quick recap, linked from MEMORY.md

5. **Updated MEMORY.md** 
   - Location: `/home/leto/.openclaw/workspace/`
   - Content: Added MemoryGraph section at top with status
   - Best for: Long-term reference point

---

## 🔍 Key Reference Documents (Pre-Existing)

### From 2026-04-29 Cron Audit
- **`2026-04-29-evening-memorygraph-cron-audit.md`** (in workspace/memory/)
- Contains: Root cause analysis, the fix, what was built

### From 2026-05-02 EM Review
- **`2026-05-02-memorygraph-owl-review.md`** (in workspace/memory/)
- Contains: EM status, validation results, Phase 2 timeline

### Project Documentation
- **`/srv/github/MemoryGraph/CURRENT.md`** — Latest project state
- **`/srv/github/MemoryGraph/START_HERE.md`** — Architecture overview
- **`/srv/openclaw_projects/MemoryGraph/CURRENT.md`** — OCP-specific state

---

## 🎯 Where to Start

### If you want a quick overview:
1. Read: `/home/leto/.openclaw/workspace/MEMORYGRAPH_SESSION_SUMMARY_20260503.md`
2. Time: 5 minutes

### If you want to do the recovery:
1. Print: `/home/leto/.openclaw/workspace/MEMORYGRAPH_RECOVERY_CHECKLIST.md`
2. Follow: Step by step
3. Time: 30-45 minutes per job

### If you need technical details:
1. Read: `/srv/openclaw_projects/MemoryGraph/TODO_RECOVERY_20260503.md`
2. Time: 15 minutes to understand, hours to implement

### If you need historical context:
1. Start: `/home/leto/.openclaw/workspace/memory/2026-04-29-evening-memorygraph-cron-audit.md`
2. Then: `/home/leto/.openclaw/workspace/memory/2026-05-02-memorygraph-owl-review.md`
3. Then: `/home/leto/.openclaw/workspace/memory/2026-05-03-memorygraph-recovery.md`

---

## 📊 Status Dashboard

| Component | Status | Last Known | Days Offline |
|-----------|--------|------------|--------------|
| Plugin | ✅ Installed | 2026-05-03 | 0 |
| Gateway | ✅ Running | 2026-05-03 | 0 |
| Extract Job | 🔴 Offline | 2026-04-30 | 3 |
| EM Index | 🔴 Stale | 2026-04-30 | 3 |
| Scenario Opt | 🔴 Offline | 2026-04-27 | 6+ |
| News Ingest | 🔴 Offline | 2026-04-29 test | 3+ |
| Phase 2 Gate | 🔴 Not scheduled | Never | — |

---

## 🔧 Quick Command Reference

```bash
# Start recovery
cd /srv/github/MemoryGraph

# Test build_index.py
python python/build_index.py

# Test CLI
python main.py --help

# List cron jobs
openclaw cron list

# Add extraction job (example)
openclaw cron add --name "memorygraph_extract_and_promote" \
  --schedule "0 6 * * *" --sessionTarget "isolated" \
  --payload.kind "agentTurn" \
  --payload.message "cd /srv/github/MemoryGraph && python main.py extract /srv/openclaw_projects && python main.py lint && python main.py promote && python main.py changelog && python python/build_index.py"
```

---

## 📅 Timeline

| Date | What | Status |
|------|------|--------|
| 2026-04-29 | Cron audit + fix discovered | ✅ Complete |
| 2026-04-30 | Manual test run, 4,577 lessons indexed | ✅ Complete |
| 2026-05-01 | (Offline, cron jobs missing) | 🔴 |
| 2026-05-02 | (Offline, cron jobs missing) | 🔴 |
| 2026-05-03 | Plugin installed, recovery docs created | ✅ This session |
| 2026-05-04 | Expected: First cron job test | ⏳ |
| 2026-05-06 | Phase 2 decision gate | ⏳ |
| 2026-05-07+ | Phase 2 implementation (if ready) | ⏳ |

---

## 🎓 Key Learnings

### The Plugin Tools Problem
- Isolated cron agents don't have TypeScript plugin tools
- Original `systemEvent → main` setup failed silently for 8 days
- Solution: Use Python CLI commands directly with `isolated agentTurn`

### EM Status
- 4,577 lessons indexed with 768-dim embeddings
- 80% validation baseline
- Query bugs need fixing (q2, q5) before Phase 2

### Architecture
- Extraction → Lint → Promote → Changelog → Index Rebuild
- Scenario optimization tests 12 variants weekly
- News ingestion feeds articles into extraction pool
- Phase 2 gate on 2026-05-06 decides vector embedding timeline

---

## ❓ FAQ

**Q: Is MemoryGraph working?**  
A: Plugin is installed and running, but the automation pipeline (cron jobs) is offline.

**Q: How do I fix it?**  
A: Follow the recovery checklist. Verify prerequisites, then create 4 cron jobs.

**Q: How long will this take?**  
A: Prerequisites: 15-20 min. Each cron job: 10-15 min to set up + test. Total: 1-2 hours.

**Q: What if something breaks?**  
A: Disable the job with `openclaw cron update <jobId> --enabled false` and check logs.

**Q: When is Phase 2?**  
A: Decision gate 2026-05-06 7 AM UTC. Implementation starts ~2026-05-07 if EM is stable.

---

## 📞 Need Help?

Check these files in order:
1. `MEMORYGRAPH_RECOVERY_CHECKLIST.md` — Step-by-step
2. `TODO_RECOVERY_20260503.md` — Full technical details
3. `2026-04-29-evening-memorygraph-cron-audit.md` — Historical context

---

**Created:** 2026-05-03 16:05 PDT  
**Next Review:** Before first cron job run (2026-05-04 6 AM UTC)  
**Status:** 🔴 RECOVERY IN PROGRESS
