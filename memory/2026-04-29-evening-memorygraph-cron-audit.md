# 2026-04-29 Evening — Cron Audit + MemoryGraph Index Rebuild

## Session Context
Audit of all MemoryGraph cron jobs. Found a critical bug that had been silently failing for 8 days. Fixed, tested, and shipped a missing script that was on the open items list.

---

## What Was Found

### `memorygraph_extract_and_promote` — Silent Failure (8 days)
- **Root cause:** Job was configured as `systemEvent → main` then as `systemEvent → main` but the isolated sessions that ran it don't have the TypeScript plugin tools (`memorygraph_extract`, `memorygraph_lint`, etc.)
- Every run reported `status: ok` but summary = "tool not found, want help?" — false positive
- The 184ms "successful" run was the event dispatching + model erroring out immediately
- **Fix:** Rewrote as `isolated agentTurn` using Python CLI directly (`python main.py extract`, `lint`, `promote`, `changelog`)
- Added Step 5: `build_index.py` (see below)

### `memorygraph_scenario_optimization` — Clean ✅
- Last run 2026-04-27 (Monday), all 12 scenarios passed
- Top 3: `qf_expanded_q2`, `qf_baseline`, `fs_recency_filter` (~97.5 score each)
- Next run: Monday 2026-05-06 7 AM UTC

### `memorygraph_ai_news_ingest` — First Test Run ✅
- Never run before (new job). Test triggered manually.
- 100 articles fetched, 75 above threshold, 1 lesson extracted
- Job is wired correctly for Monday

---

## What Was Built

### `build_index.py` — New Script
- Resolves yesterday's open item: "Add Python index rebuild step to nightly cron"
- Location: `/srv/github/MemoryGraph/python/build_index.py`
- Flow: load extraction drafts + memory/*.md → deduplicate → embed via llama.cpp (port 11434, batches of 20, 120ms delay) → k-means cluster (k=12, cosine sim, numpy) → write index files
- Output format: `{id, content, clusterID, clusterLabel, confidence, embedding[768]}`
- Outputs: `data/index-YYYY-MM-DD.json`, `clusters-YYYY-MM-DD.json`, `lessons-YYYY-MM-DD.json`, `latest.json`
- Test run: 4,577 lessons embedded, 12 clusters, `index-2026-04-30.json` (96MB) written ✅

### Nightly Cron Updated
- `memorygraph_extract_and_promote` now runs full Python CLI pipeline:
  1. `python main.py extract /srv/openclaw_projects`
  2. `python main.py lint`
  3. Auto-approve decisions JSON + `python main.py promote`
  4. `python main.py changelog`
  5. `python build_index.py` (new — rebuilds experience model index)
- Timeout: 600s (needed for embedding 4k+ lessons)

---

## Tonight's Pipeline Run (Manual)
- 5 OCP files scanned
- 4 lessons extracted (OCP principles from OCP_STANDARDS.md + INDEX.md)
- 0 duplicates
- 4 lessons promoted to `memory/2026-04-30.md`
- Changelog updated
- Experience model index rebuilt: 4,577 lessons, 768-dim, k=12

---

## Key Lesson
**Isolated cron agents don't have OpenClaw plugin tools.** Only the main session has plugin tools loaded. If a job needs to call `memorygraph_*` tools, it either needs to:
- Run in the main session (systemEvent), OR
- Use the Python CLI / shell commands (isolated agentTurn with exec)

The main session systemEvent approach also broke because the 184ms "run" was just event dispatch — the actual tool calls never happened. Isolated agentTurn + Python CLI is the right pattern for this.

---

## Open Items (Updated)
- ✅ ~~Add Python index rebuild to nightly cron~~ — Done, `build_index.py` shipped
- 🔲 Monitor tomorrow's 4:30 AM PDT run — should be first clean run
- 🔲 Phase 2 trigger: 2026-05-06 7 AM UTC — `phase2_promotion.py` auto-fires
- 🔲 Remove old venv `/srv/openclaw_projects/MemoryGraph/venv/` after 2026-05-15
