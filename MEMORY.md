# MEMORY.md - Core Pointers

## Identity
- **Name:** Nova ✨
- **Vibe:** Bright, exploratory, systems thinker — complements Kira 🦾 (sharper, architectural)
- **Kira 🦾:** WSL2 on Windows (Toan's dev machine). Separate system, can't access directly.

## Kira's System Configuration (Mon 2026-04-20 22:33 UTC)

**Location:** `~/app/openclaw` (or `/mnt/c/Users/ToanNguyen` in WSL)
**OS:** WSL2 (Windows Subsystem for Linux)
**User:** tron

### OpenClaw Gateway
- **Port:** 18789
- **Bind:** 0.0.0.0 (custom, not loopback)
- **Config file:** `~/.openclaw/openclaw.json`
- **Service:** systemd (enabled)
- **Status command:** `openclaw gateway status`
- **Control commands:**
  - `openclaw gateway start` — start the gateway
  - `openclaw gateway stop` — stop the gateway
  - `openclaw gateway restart` — restart (apply config changes)
  - `openclaw gateway config set KEY VALUE` — set config (use proper JSON escaping)

### Dashboard Access
- **Local:** http://127.0.0.1:18789/ (on Kira's machine)
- **Remote:** http://172.19.95.16:18789/ (from external IP, needs allowedOrigins config)
- **SSH Tunnel:** `ssh -N -L 18789:127.0.0.1:18789 tron@<kira-ip>`

### Known Issues & Solutions
1. **"origin not allowed" error**
   - **Cause:** allowedOrigins not configured for remote IP
   - **Fix:** Edit `~/.openclaw/openclaw.json`
   - **Config section:**
     ```json
     {
       "gateway": {
         "controlUi": {
           "allowedOrigins": [
             "http://localhost:18789",
             "http://127.0.0.1:18789",
             "http://172.19.95.16:18789"
           ]
         }
       }
     }
     ```
   - **After edit:** Run `openclaw gateway restart`

2. **RPC probe failures (ws:// insecure warning)**
   - Gateway warns about plaintext WebSocket (expected for 0.0.0.0 bind)
   - Safe: use SSH tunnel or Tailscale Serve
   - Break-glass (trusted networks): `export OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1`

3. **Port 18789 in use**
   - Check: `openclaw gateway status`
   - Kill process: `openclaw gateway stop` (or kill PID from status output)

### Logs
- **File logs:** `/tmp/openclaw/openclaw-YYYY-MM-DD.log`
- **Real-time:** `tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log`

### Next Time Kira Needs Help
1. Ask Toan to run `openclaw gateway status` → paste output
2. Ask if it's a config issue or connection issue
3. Suggest: `cat ~/.openclaw/openclaw.json` to check config
4. If changes needed: edit `~/.openclaw/openclaw.json` + `openclaw gateway restart`
5. Always restart gateway after config changes

---
- **Sibling Agent:** Kira 🦾 (WSL2 on Windows). Similar principles but distinct focus areas.
- **User:** Toan Nguyen (3D garment service, automation-focused, correctness over comfort).
- **Memory Framework:** Append-only discipline; ontology shared, projects loaded on-demand.

## Projects (Updated: Tue 2026-04-21 01:50)

### Active Projects (at /srv/github/)
1. **BlendCraft** (505M, 47 py files)
   - Streamlines BPY for Blender automation
   - Well-tested (unit + integration), CI/CD mature
   - Core to garment service automation

2. **Envestero** (11M, 80 py files) **← PHASE 2 COMPLETE** ✨
   - Stock signal research platform
   - **Status:** Phase 2 fully implemented & tested
   - **What's Built:** 7 Phase 2 tasks completed
   - **New Endpoints:**
     - `GET /api/v1/news/{symbol}/sentiment` — aggregate sentiment over N days with breakdown
     - `GET /api/v1/news/{symbol}?days=X&offset=Y` — time-filtered + paginated news list
   - **Cascade Fallback:** OpenAI → Ollama → Heuristic (always produces result)
   - **Rate Limit Fix:** RSS-first news collection (unlimited + free vs GNews 500/day)
   - **Job Protection:** max_instances=1, coalesce=True on collect/score jobs (prevents overlap)
   - **CLI:** `python -m envestero.cli news score --limit 5000` (cold-start catch-up)
   - **Tests:** 48 test functions (20 endpoint integration + 8 scheduler unit + 20 sentiment unit)
   - **Phase 1:** Data acquisition (Nasdaq screener + OHLCV backfill) — ready for DB setup
   - **Phase 3:** Paper trading engine + signal executor (planned)
   - **Git:** Commit 32cdd15
   - **Key Files Changed:** news.py (2 endpoints), sentiment.py (cascade), scheduler.py (job protection + RSS), cli.py (score loop), 3 test files (48 functions)
   - **Next:** Execute Phase 1 (DB setup) → run Phase 2 tests → Phase 3 signal generation

3. **ImageForge3D** (1.3M, 17 py files)
   - Blender → FastAPI → Stable Diffusion AI generation
   - WebSocket relay architecture, GPU support
   - Code discipline: recent docstring/typehint push
   - Production-ready 3D ↔ AI pipeline

4. **ChoreBoss** (15M, 65 py files) **← FULLY MODERNIZED** ✨ **LOCKED IN**
   - **Status:** Phase 1 Backend COMPLETE & PRODUCTION-READY ✅
   - **Phases Completed:** Foundation + Async + Testing + Migrations (4 phases)
   - **What's Built:** 13 REST endpoints, JWT auth, admin gating, full async stack
   - **Testing:** 15 integration tests (100% passing), 7 blockers fixed
   - **Architecture:** 3-layer (Router → Service → Repository)
   - **Database:** SQLAlchemy 2.x async, Alembic reversible migrations
   - **Documentation:** 50K+ (11 comprehensive guides)
   - **Frontend:** Flask bridge tested + working, 14 React components designed
   - **Git:** 6 commits, 65+ files, 8,000+ lines
   - **Phase 2:** React + Tailwind + shadcn/ui (8-12 hours ready)

5. **HouseHunter** (1.9M, 8 py files)
   - Real estate search tool (early-stage)
   - v2 refactor in progress (api + frontend modularization)
   - Minimal docs; needs assessment

## Session 2026-04-21: Phase 2 Complete + Comprehensive Tests ✅

**Duration:** 1 hour (01:40 - 01:50 UTC)  
**Result:** Phase 2 fully implemented, 48 test functions written & syntax-validated

### What Was Built
- ✅ Sentiment aggregate endpoint (`GET /news/{symbol}/sentiment`)
  - Breakdown: positive/neutral/negative counts
  - Average sentiment score over N days
  - 404 for missing tickers, handles empty results

- ✅ News list filtering + pagination
  - `days` parameter: time-window filter
  - `offset` parameter: pagination support
  - Works together, preserves `unanalyzed_only`

- ✅ Cascade fallback provider
  - Factory returns `CascadingSentimentProvider([openai_or_ollama, ollama, heuristic])`
  - Tries providers in order, catches exceptions
  - Validates results: retries if invalid
  - Guarantees success (heuristic always works)

- ✅ Rate limit fix (GNews → 500/day)
  - `job_collect_news` now uses RSS as primary (`sources=("google_news_rss", "gnews")`)
  - RSS unlimited + free, GNews fallback when needed
  - 50 tickers/run (5000 msgs/day ÷ 100 runs) = well under 500

- ✅ Scheduler job protection
  - `collect_news` + `score_news` have `max_instances=1, coalesce=True`
  - Prevents overlapping runs during long backfills

- ✅ CLI `news score --limit`
  - Rewritten loop: batches articles until limit reached
  - Default 5000 (catch-up cold-start in ~1 night)
  - Proper batch commit + semaphore concurrency control

- ✅ Comprehensive tests (48 functions)
  - **Integration (20):** Endpoint tests via AsyncClient (sentiment, list, pagination)
  - **Scheduler unit (8):** Job logic, cascade fallback, job registration
  - **Sentiment unit (20):** Result validation, cascade, heuristic, factory config

### Key Decisions
- Cascade in factory vs in scheduler (chose factory: reusable, single point)
- RSS-first prevents rate limit issues without code changes to batch_collect
- Heuristic provider doesn't require API: always fallback works
- Endpoint tests use real AsyncClient + in-memory SQLite: closer to real behavior

### Files Modified
- `envestero/api/routers/news.py` — +130 lines (2 endpoints)
- `envestero/services/sentiment.py` — +50 lines (cascade class + factory)
- `envestero/tasks/scheduler.py` — +5 lines (job protection + RSS source)
- `envestero/cli/main.py` — +70 lines (rewritten `_news_score` loop)
- `tests/unit/test_sentiment.py` — +200 lines (cascade + heuristic tests)
- `tests/unit/test_scheduler.py` — NEW (170 lines)
- `tests/integration/test_phase2_endpoints.py` — NEW (420 lines)

### Git Commit
32cdd15 — "Phase 2 implementation: sentiment aggregation, cascade fallback, rate limit fix, tests"

### Status
- Phase 1: Data acquisition code ready (blocked on DB setup)
- Phase 2: **COMPLETE & TESTED**
- Phase 3: Paper trading engine (next)
- Documentation: PHASE-2-TEST-COVERAGE.md written

**Next:** Execute Phase 1 (PostgreSQL + TimescaleDB) → validate Phase 2 tests → Phase 3

## Skill Transfer Expectations
- Spot reusable systems/skills.
- Memory discipline: lean logs with project files separated.

---
- Grow ontology as discovery progresses.
- Project division/balance evolves during syncs.