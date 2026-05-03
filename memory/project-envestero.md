# Envestero - Project Baseline

**Status:** Active | **Size:** 11M | **Files:** 76 Python files

## Overview
Python stock signal research platform. Investment analysis and signal generation engine with news ingestion, sentiment analysis, proxy cycling, and trade signal pipelines.

## Structure
```
Envestero/
├── envestero/           # Core package
├── Envestero/           # Additional subfolder
├── newser/              # News ingestion module
├── Lib/                 # Custom libraries
├── alembic/             # Database migrations
├── Documentation/       # Project docs
├── Examples/            # Example scripts
├── tests/               # Test suite
├── test/                # Additional tests
├── utilities/           # Utility scripts
├── .github/             # CI/CD
├── alembic.ini
├── app.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements_py313.txt
├── MIGRATION_PY313.md
├── smoke_test.py
├── Z_ManualTest_*.py    # Manual test suites (5+ files)
└── .gitignore
```

## Recent Commits (Latest 5)
1. `8e66526` - feat: implement news ingestion, sentiment, and news-aware signals
2. `6a68029` - docs: full rewrite of copilot-instructions for v2
3. `9b46172` - feat: ProxyAgent — scrape, validate, cycle free proxies
4. `1f75554` - feat: scheduler + CLI backfill + batch upsert
5. `e34a263` - feat: TradeSignal schema + signals pipeline

## Tech Stack
- **Language:** Python 3.13+ (recent migration documented)
- **Database:** SQLAlchemy with Alembic migrations
- **Deployment:** Docker (Dockerfile + docker-compose.yml)
- **APIs:** News ingestion (e.g., newsapi), Hugging Face (sentiment), multiple data sources
- **Features:** Proxy cycling, sentiment analysis, trade signal generation

## Key Modules & Features
- **ProxyAgent:** Free proxy scraping, validation, cycling
- **News Ingestion:** Real-time news with sentiment scoring
- **Trade Signals:** Multi-factor signal pipeline (news-aware)
- **Scheduler:** CLI backfill + batch upsert capabilities
- **Database:** Alembic migrations for schema evolution

## Recent Changes Highlights
- News + sentiment integration (news-aware signals)
- Full v2 documentation rewrite for copilot integration
- Proxy agent for free proxy sourcing
- Scheduler + CLI infrastructure
- Python 3.13 migration guidance included

## Key Insights
- **Complex:** 76 Python files — largest codebase reviewed
- **Production-ready:** Full migration path, Docker, test suites
- **Active development:** Multi-feature rollout across recent commits
- **Manual testing:** Heavy reliance on manual test scripts (Z_ManualTest_*.py)
- **v2 in flight:** Copilot instructions rewritten; v2 architecture evolving

## Toan's Role
Primary research/investment analysis platform. Core project for signal research.

## Next Steps
- [ ] Review Python 3.13 migration status (MIGRATION_PY313.md)
- [ ] Understand news-aware signal architecture
- [ ] Check manual test coverage scope
- [ ] Validate proxy agent resilience
