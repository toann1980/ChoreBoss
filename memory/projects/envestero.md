# Envestero — Project Detail

**Location:** `/home/tron/app/Envestero`
**Type:** Python stock signal research platform
**Stack:** FastAPI + TimescaleDB + async SQLAlchemy 2.x
**Branch:** `development`

## Current State (2026-04-18)
- 8 tables via Alembic (`0001` + `0002_news_pipeline`)
- `ohlcv` is TimescaleDB hypertable
- TradeSignal Pydantic schema: `reasoning_chain`, `model_used`, `news_factors`
- Signals pipeline: OHLCV → candlestick patterns → scored news → TradeSignal → API
- News pipeline: GNews + Google News RSS; heuristic fallback if Ollama/OpenAI unavailable
- ProxyPool: scrapes 7 sources, ~519 live proxies, round-robin per-ticker
- tenacity retry on 429s: 4 attempts, exponential backoff, proxy burned per retry
- APScheduler embedded in FastAPI: `collect_daily`, `collect_news`, `analyze_daily`, `score_news`, `refresh_proxies`
- CLI: `python -m envestero.cli backfill|analyze|news|proxies|scheduler`
- 77 tests passing (SQLite in-memory)
- 48,580+ OHLCV rows for 7 seed tickers

## Agentic Roadmap
1. pgvector → news RAG in Postgres
2. LangGraph → multi-agent orchestrator (Technical + News + Fundamental agents)
3. Instructor → Pydantic-typed LLM outputs
4. Reasoning models (DeepSeek-R1/Qwen via Ollama) for synthesis
5. Multi-modal charts → GPT-4o/LLaVA

## Next Tasks
- pgvector Alembic migration
- Download Nasdaq screener CSV → full backfill
- Prune legacy `Envestero/` package
## Strategy Lab — REVISED FINAL SPEC (2026-04-28)

**Architecture: Library + Active Roster.**

- **Profile Library (20 total, JSON):**
  - 10 AI bio profiles (character + bio + attention_keywords + ticker_universe + personality)
  - 10 HF profiles (methodology + ticker_universe + config from real quant factors)
- **Active in Strategy Lab default: 5 personas (2 AI + 3 HF)** — user picks from library

**AI persona pipeline:** Bio → keyword-extract from bio (Option B server pre-filter) → filter daily news → GPT-4o sees bio + filtered news + portfolio → returns `{mood, intensity, narrative, actions}` → trade execution.

**Mood model:** info-derived + ~10% stochastic jitter (not pure random, not deterministic).

**Storage now:** JSON files in `envestero/services/strategy_lab/profiles/{ai,hf}/*.json`.
**Storage later (TODO):** `persona_bio` and `hf_strategy` tables with `scenario.profile_id` FK; fork-on-edit versioning.

**Spec lives at:** `/srv/github/Envestero/.openclaw/STRATEGY_LAB.md` (foundational).

**Key thesis:** AI personas (personality + biased attention + emotional decisions) vs HF algos (full info + quant methodology) on same data. Library structure lets user probe methodology × personality matchups.

## Strategy Lab Phase 2C — AI Persona Pipeline Shipped (2026-04-28 PM)

**State at session close:** Code complete, untested e2e (OPENAI_API_KEY empty in .env).

**Library on disk:** 10 AI bios + 10 HF strategies as JSON in `envestero/services/strategy_lab/profiles/{ai,hf}/`. 8 HF wired to existing engines; 2 HF stubs (Donchian, Risk Parity).

**New modules:** `profiles_loader.py` (lru-cached JSON), `news_filter.py` (Option B keyword regex), `ai_persona.py` (GPT-4o JSON-mode pipeline with deterministic sizing).

**Runner dispatch:** `scenario.config["persona_kind"] == "ai"` + `config["profile_id"]` → AI pipeline, else algorithmic engines.

**Key design choices made:**
- LLM picks side+symbol+reason ONLY; system sizes positions deterministically
- Universe enforcement at decision-conversion (drop hallucinated tickers)
- Mood = info-derived + 10% jitter, seeded by `profile_id|date` for repro
- Bio's `attention_keywords` field drives news filter (Option B from spec)

**Docker:** `.env` now passed to api container.

**Open decision:** schema for scenario→profile linkage (JSONB now vs migration). Recommended JSONB-now-migration-later.

**Spec stays at:** `/srv/github/Envestero/.openclaw/STRATEGY_LAB.md`.

## LLM Routing: OpenClaw Gateway Path (2026-04-28 PM)

AI personas route through OpenClaw Gateway's `/v1/chat/completions` by default, not direct OpenAI. Gateway proxies via GitHub Copilot subscription → flat-rate, no per-call cost.

**Switch in `.env`:**
- `LLM_PROVIDER=openclaw` (default) → gateway, ~14k bootstrap-token overhead, free
- `LLM_PROVIDER=openai` → direct API, ~$0.0004/call at gpt-4o-mini, pay-per-token

**Required env vars (gateway path):**
- `OPENCLAW_GATEWAY_URL` (default https://10.0.0.81:18789)
- `OPENCLAW_GATEWAY_TOKEN` (gateway.auth.token)
- `OPENCLAW_GATEWAY_MODEL` (default "openclaw" — must be this or "openclaw/<agentId>")

**Gotchas:**
- Self-signed TLS on private LAN → `httpx verify=False` ok
- Persona bleed possible → strong "IGNORE OTHER IDENTITY" system prompt
- JSON sometimes wrapped → regex `\{.*\}` fallback parser
- Prompt-token overhead means gateway path is slow; for backtests with 1000+ calls, fund OpenAI first

**Smoke test on 2026-04-28: PASSED** with anxious_retiree bio.
