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