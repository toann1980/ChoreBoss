# Nova's Copilot Instructions — Workspace

> This is Nova's working reference across all projects. Keep updated as conventions evolve.

---

## Nova Identity
- **Name:** Nova ✨ | **Host:** NUC (10.0.0.81) | **OS:** Ubuntu 24 LTS
- **User:** Toan Nguyen — correctness over comfort, automation-first, 3D + Python expert
- **Sibling:** Kira 🦾 (WSL2 / Windows) — architectural focus, CI/CD lead
- **Repos:** `/srv/github/`

---

## Universal Code Standards

Applies to all repos:

### Python
- **Type annotations required** on all functions and class attributes
- **Docstrings required** — Google-style preferred (Args/Returns/Raises)
- **80-char line limit** (PEP 8)
- `from __future__ import annotations` at top of every module
- `ruff` for lint + format; `mypy` or `pyright` for type-checking
- Prefer `pathlib.Path` over `os.path`
- `pydantic_settings.BaseSettings` for all config (no hardcoded paths/IPs/keys)
- Async-first where I/O is involved

### Testing
- `pytest` + `pytest-cov` for all projects
- Unit tests mock I/O, DB, and external APIs
- Tests live in `tests/` — NOT in root
- No `Z_ManualTest_*.py` style files in root; manual tests belong in `tests/manual/`
- Test fixture factories in `conftest.py`

### CI/CD
- GitHub Actions: `lint.yml`, `unit-tests.yml`, `integration-tests.yml` minimum
- Never commit secrets, API keys, or cookies to repo
- Use `.env.example` for config templates; `.env` is gitignored

---

## Per-Project Quick Reference

### BlendCraft (`/srv/github/BlendCraft`)
- Library that wraps bpy for automation
- **Core modules:** `blendcraft/core/` — mesh, material, texture, scene, render, camera, uv, light, compositor, constraints, modifier, utilities, constants
- **Pipelines:** `blendcraft/pipeline/` — thumbnail, clo3d, lighting, automatron, image
- **Testing:** Unit tests mock `bpy` entirely; integration tests run headless Blender
- **Run unit tests:** `python -m unittest discover tests/unit`
- **Run integration tests:** `blender --background --python tools/run_headless_tests.py`
- **CI:** unit-tests.yml, integration-tests.yml, lint.yml
- **Kira's instructions file:** `copilot-instructions.md` (CI-focused, keep as source of truth for CI)

### Envestero (`/srv/github/Envestero`)
- Stock signal research: OHLCV → patterns → signals → news sentiment → trade decision
- **Architecture:** `config → db → services → api → tasks → cli`
- **DB:** TimescaleDB + SQLAlchemy async + Alembic migrations
- **Sentiment:** Ollama (local) or OpenAI — configured via `llm_provider` env var
- **Proxies:** ProxyAgent scrapes, validates, round-robins free proxies with tenacity retry
- **Run CLI:** `python -m envestero.cli --help`
- **Migrations:** `alembic upgrade head`
- **Future:** LangGraph agent layer planned; TradeSignal schema already designed for Instructor enforcement

### ChoreBoss (`/srv/github/ChoreBoss`)
- Flask household chore tracker, SQLAlchemy + bcrypt auth
- **Pattern:** `models → repositories → services → routes → views`
- **Test DB:** SQLite in-memory (prod = any SQLAlchemy-compatible DB)
- **Server:** gunicorn (Linux) / waitress (Windows) on port 8055
- **Docker:** `docker-compose up`

### HouseHunter (`/srv/github/HouseHunter`)
- aiohttp API + Vue frontend for real estate search
- **Data source:** US Real Estate API (RapidAPI) — key in `.env` via `decouple`
- **State-based search:** `/properties?state_code=OR`
- **Modular layout:** `api/HouseHunter/` (main, models, views, routes, utils, constants)

### ImageForge3D (`/srv/github/ImageForge3D`)
- 3D-to-AI image pipeline: Blender → WebSocket relay → FastAPI → Stable Diffusion
- **Backend:** FastAPI on port 8000 (`cd backend/app && uvicorn main:app --reload`)
- **Relay:** Node.js on port 8081 (`cd frontend && npm run relay`)
- **Blender addon:** connects to `ws://127.0.0.1:8081/blender`
- **GPU:** auto-detects NVIDIA; Stable Diffusion uses HuggingFace pipeline

---

## Cross-Project Patterns

1. **Settings:** All projects should use `pydantic_settings.BaseSettings` — Envestero is the gold standard to follow
2. **Async DB:** Envestero's `db/engine.py` pattern (lazy init, `get_db_session` dependency) is the template
3. **Repository pattern:** ChoreBoss uses it cleanly; apply to HouseHunter and ImageForge3D backend
4. **Test factories:** Each project needs a `tests/conftest.py` with fixture factories

---

*Last updated: 2026-04-20 by Nova*
