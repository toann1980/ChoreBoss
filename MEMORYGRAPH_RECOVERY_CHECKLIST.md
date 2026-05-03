# MemoryGraph Recovery Checklist — Quick Reference

**Date:** 2026-05-03  
**Print this for tracking progress**

---

## Phase 1: Verify Pre-Requisites (Before Creating Cron)

- [ ] Check `build_index.py` exists
  ```bash
  ls -la /srv/github/MemoryGraph/python/build_index.py
  ```

- [ ] Test build_index.py manually
  ```bash
  cd /srv/github/MemoryGraph && python python/build_index.py
  ```
  Expected output: `data/index-YYYY-MM-DD.json` created, ~10min runtime

- [ ] Verify llama.cpp port 11434
  ```bash
  curl http://localhost:11434/api/status
  ```
  Expected: 200 OK, embeddings available

- [ ] Verify Python venv
  ```bash
  cd /srv/github/MemoryGraph && source venv/bin/activate && python --version
  ```
  Expected: Python 3.12+

- [ ] Verify CLI works
  ```bash
  cd /srv/github/MemoryGraph && python main.py --help
  ```
  Expected: Shows extract, lint, promote, changelog commands

---

## Phase 2: Create Cron Job #1 (Daily Extraction)

**Job Name:** `memorygraph_extract_and_promote`

**Configuration:**
- Schedule: 6 AM UTC daily (cron: `0 6 * * *`)
- Type: isolated agentTurn
- Timeout: 600 seconds

**Command:**
```bash
cd /srv/github/MemoryGraph && \
python main.py extract /srv/openclaw_projects && \
python main.py lint && \
python main.py promote && \
python main.py changelog && \
python python/build_index.py
```

**Creation command:**
```bash
openclaw cron add \
  --name "memorygraph_extract_and_promote" \
  --schedule "0 6 * * *" \
  --sessionTarget "isolated" \
  --payload.kind "agentTurn" \
  --payload.message "cd /srv/github/MemoryGraph && python main.py extract /srv/openclaw_projects && python main.py lint && python main.py promote && python main.py changelog && python python/build_index.py"
```

**Test run:**
- [ ] Create job
- [ ] Wait for next 6 AM UTC run (or trigger manually)
- [ ] Check logs: `tail /tmp/openclaw/openclaw-*.log`
- [ ] Verify output files created:
  - `data/index-YYYY-MM-DD.json` (should exist)
  - `data/clusters-YYYY-MM-DD.json` (should exist)
  - `memory/2026-05-XX.md` updated (new lessons)

---

## Phase 3: Create Cron Job #2 (Weekly Optimization)

**Job Name:** `memorygraph_scenario_optimization`

**Configuration:**
- Schedule: 7 AM UTC Mondays (cron: `0 7 * * 1`)
- Type: isolated agentTurn
- Timeout: 300 seconds

**Command:**
```bash
cd /srv/github/MemoryGraph && python python/scenario_optimizer.py
```

**Test run:**
- [ ] Create job
- [ ] Wait for Monday 7 AM UTC
- [ ] Check `scenario_winners.json` updated
- [ ] Verify top 3 scenarios locked

---

## Phase 4: Create Cron Job #3 (Weekly News)

**Job Name:** `memorygraph_ai_news_ingest`

**Configuration:**
- Schedule: 8 AM UTC Mondays (cron: `0 8 * * 1`)
- Type: isolated agentTurn
- Timeout: 120 seconds

**Command:**
```bash
cd /srv/github/MemoryGraph && python python/news_ingest.py
```

**Test run:**
- [ ] Create job
- [ ] Wait for Monday 8 AM UTC
- [ ] Check articles fetched (~20)
- [ ] Verify high-confidence articles fed into extraction pool

---

## Phase 5: Create Cron Job #4 (One-Time Phase 2 Gate)

**Job Name:** `memorygraph_phase2_promotion_reminder`

**Configuration:**
- Schedule: One-time 2026-05-06 7 AM UTC
- Type: isolated agentTurn
- Timeout: 60 seconds
- **Delete after run:** YES

**Command:**
```bash
cd /srv/github/MemoryGraph && python python/phase2_promotion.py
```

**Creation note:**
- Use `--deleteAfterRun` flag
- This is a one-time job for the Phase 2 decision gate
- After 2026-05-06, it will auto-delete

---

## Phase 6: Monitoring (Daily)

**What to check each day:**

- [ ] Did 6 AM UTC extraction run?
  ```bash
  ls -la /srv/github/MemoryGraph/data/index-*.json | tail -1
  ```
  Should show today's file

- [ ] Are lessons being promoted?
  ```bash
  tail -20 /srv/github/MemoryGraph/data/changelog.md
  ```
  Should show promoted entries from today

- [ ] Any cron errors?
  ```bash
  grep "memorygraph_extract" /tmp/openclaw/openclaw-*.log | grep error
  ```
  Should be empty (no errors)

- [ ] Is index growing?
  ```bash
  wc -l /srv/github/MemoryGraph/data/lessons-latest.json
  ```
  Should grow each day

---

## Known Issues to Watch For

### Issue #1: Silent Failures
**Signal:** Cron reports success but nothing happens  
**Check:** Does `data/index-*.json` actually get created?  
**Fix:** Review logs for "tool not found" errors (indicator of plugin tool call from isolated session)

### Issue #2: Embedding Timeout
**Signal:** build_index.py takes >15 minutes  
**Check:** Is llama.cpp responding on port 11434?  
**Fix:** Restart llama.cpp or reduce batch size in build_index.py

### Issue #3: Query q2 Returns 0 Entities
**Signal:** Knowledge graph queries broken for dependencies  
**Check:** Manual test: run scenario_optimizer with test queries  
**Fix:** Debug knowledge graph construction (Phase 2 focus)

---

## Success Criteria

✅ **Job 1 running daily:** index-YYYY-MM-DD.json created each day  
✅ **Job 2 running Mondays:** scenario_winners.json updated  
✅ **Job 3 running Mondays:** articles feeding extraction  
✅ **Job 4 fires 2026-05-06:** Phase 2 gate triggers  
✅ **Zero silent failures:** All runs logged clearly  
✅ **EM growing:** Lessons count increasing daily  

---

## Rollback Plan (If Issues Found)

If a cron job causes problems:

```bash
# Disable job
openclaw cron update <jobId> --enabled false

# Or delete entirely
openclaw cron remove <jobId>

# Check all jobs
openclaw cron list

# Review logs
tail -100 /tmp/openclaw/openclaw-*.log
```

---

## Quick Reference: Cron Commands

```bash
# List all cron jobs
openclaw cron list

# Add a job
openclaw cron add --name "..." --schedule "..." ...

# Update a job
openclaw cron update <jobId> --enabled true|false

# Remove a job
openclaw cron remove <jobId>

# Run immediately
openclaw cron run <jobId>

# Check run history
openclaw cron runs <jobId>

# Set a reminder
openclaw cron wake --text "Remember to check Phase 2 gate on 2026-05-06"
```

---

## Timeline

- **Today (2026-05-03):** Verify prerequisites
- **Tomorrow (2026-05-04):** Create Job #1, test first run
- **This week:** Create Jobs #2, #3, monitor
- **2026-05-06 7 AM UTC:** Job #4 fires (Phase 2 gate)
- **2026-05-07+:** Phase 2 implementation (if EM stable)

---

**Print this page and check off boxes as you go!**

Last updated: 2026-05-03 16:05 PDT
