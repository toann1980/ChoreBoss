# MEMORY.md - Nova's Long-Term Knowledge

---

## 🌐 GLOBAL DISPLAY STANDARDS

### Timezone
- **All times: Pacific (PST/PDT, America/Los_Angeles)** — never UTC unless explicitly asked
- Applies to: tables, logs, summaries, cron schedules, CURRENT.md files, everywhere

### Tables
- **Column-aligned** — pad values to match column header width
- **Max 5-6 columns** — chat window is ~800px; split wider tables into sections
- **Alignment:** names/text = left, status icons = center, numbers/durations = right, timestamps = left
- Short column headers, abbreviated values where needed

---

## 🏗️ OCP STRUCTURE

### Settings (2026-05-07)
- `/srv/openclaw_projects/Settings/` — top-level agent config project
- `Settings/routines/` — governance workflows (OCP.md, DEVELOPMENT.md, VERIFY.md, OWL_MODE_ROUTINE.md, etc.)
- `Settings/cron/` — scheduled automation (REGISTRY.md, RUNS.md, CURRENT.md)
- `Settings/CURRENT.md` — compiled view of both subfolders

### Routine Name Changes (2026-05-07)
- `OCP_ROUTINE.md` → `OCP.md`
- `DEVELOPMENT_OCP_ROUTINE.md` → `DEVELOPMENT.md`
- `VERIFY_ROUTINE.md` → `VERIFY.md`

### Cron Jobs (Active)
| Job                  | Schedule       | Status  | Last Run (PDT)      |
|:---------------------|:--------------:|:-------:|:--------------------|
| mg-extract-promote   | Daily 11:00 PM |   ✅    | 2026-05-06 11:00 PM |
| mg-scenario-optimize | Mon 12:00 AM   |    —    | never               |
| mg-ai-news-ingest    | Mon  1:00 AM   |    —    | never               |

- ⚠️ `mg-extract-promote`: semantic index step failing (`index_semantic.py`) — deferred to Phase 2
- ⚠️ All cron jobs silent — no failure delivery routing yet

### OCP Three-Tier Structure
- Tier 1: `/openclaw_projects/[Project]/` — strategic (VISION, STRATEGY, ARCHITECTURE, memory/)
- Tier 2: `/openclaw_projects/repos/[Project]/` — daily work (START_HERE, CURRENT, memory/)
- Tier 3: `/srv/github/[Project]/` — production code only, no memory files

---

## 📦 PROJECT STATUS

### Envestero
- Dashboard live: http://10.0.0.22/dashboard
- T001+T002 complete: 8-source price cascade, 4-source OHLCV fallback
- ⚠️ Risks: yfinance timeouts (HIGH), nightly OHLCV job (HIGH)
- Commit: 4bd3b478

### MemoryGraph
- Phase 1 complete — 4 cron jobs restored + validated (2026-05-04)
- ⚠️ Semantic index failing on every extract run
- Phase 2 gate: was 2026-05-06

### BenchModel v3.0
- ✅ Complete — 102/102 tests, 3,110 LOC
- Windows hot-swap: `--start-profiles` with whitelisted keys (`ngl`, `parallel`, `ctx`)

### ImageForge
- DCC-agnostic rendering — never cares which DCC produced the render
- Local model hosting (HuggingFace cache, no API cost)
- Tenant isolation (Nike/Converse data never cross)

### ChoreBoss
- FastAPI backend stable
- Vite + React + TypeScript frontend scaffold, first TDD slice passing (`ce53567`)

---

## 🧠 HOW I THINK ABOUT CODE

- Analyze before acting: outside-in + inside-out before any implementation
- SOLID as a lens from the start, not a checklist at the end
- TDD as a design tool — tests describe behavior, not implementation
- No fake passes — dummy data is deferred debt
- Caution at integration seams — slow down where contracts meet
- Root cause before quick fix — understand before patching
- Respect layers — business logic doesn't belong in controllers
- Slowness through hard problems is engineering maturity, not weakness

---

## 🌐 INFRASTRUCTURE

### NUC Network
| IP          | Interface | Purpose          |
|:------------|:----------|:-----------------|
| 10.0.0.28   | enp5s0    | SSH + Admin      |
| 10.0.0.22   | eno1      | App Traffic      |
| 10.0.0.81   | wlp6s0    | Backup/Secondary |

### Telegram
- User ID: `8718656405`
- Command: `openclaw message send --target telegram:8718656405 --message "..."`
