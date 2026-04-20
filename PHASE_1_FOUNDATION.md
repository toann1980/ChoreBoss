# 2026-04-20 ChoreBoss Phase 1 — FastAPI Backend Foundation

## Completed
- [x] Directory structure: `api/` with routers, schemas, dependencies
- [x] FastAPI app factory (`api/main.py`)
  - CORS configured for localhost:5173 (React dev) and localhost:3000
  - Lifespan hooks for startup/shutdown
  - Health check endpoint
- [x] Authentication system
  - JWT token creation (`create_access_token`)
  - Token validation (`get_current_person` dependency)
  - Admin gating (`get_admin_person` dependency)
  - `POST /api/auth/login` route
- [x] Pydantic schemas (Chore, Person, Auth)
  - ChoreCreate, ChoreRead, ChoreUpdate with RecurrenceType enum
  - PersonCreate, PersonRead, PersonUpdate, PersonLogin
  - TokenResponse
- [x] CRUD routers
  - `/api/chores/*` (list, get, create, update, delete, complete)
  - `/api/people/*` (list, get, create, update, delete)
  - `/api/auth/login`
- [x] Database dependency injection (`api/dependencies/db.py`)
  - AsyncSession factory for PostgreSQL+asyncpg
  - get_session() dependency
- [x] Config update (`choreboss/config.py`)
  - pydantic_settings.BaseSettings for env vars
  - JWT secret key, algorithm, expiration
  - Backwards compat with legacy TestingConfig
- [x] Entry point (`api_run.py`)
  - `uvicorn api_run:app --reload`
- [x] Project metadata (`pyproject.toml`)
  - Poetry-compatible build system
  - FastAPI, uvicorn, sqlalchemy, asyncpg, alembic
  - pytest + pytest-asyncio + httpx for testing
  - Ruff linter config
- [x] Documentation (`PHASE_1.md`)
  - Architecture diagram
  - API endpoint reference
  - Blockers and next steps
  - Estimated timeline

## What's NOT Changed Yet
- `choreboss/models/` — still SQLAlchemy 2.x but no async
- `choreboss/repositories/` — still sync (need async conversion)
- `choreboss/services/` — still sync (need async conversion)
- `tests/` — still using Flask test client (needs httpx + pytest-asyncio)
- Database is SQLite in local dev (migrations plan for phase 1.1)

## Blockers to Fix (Phase 1.1)
1. **Repositories not async** — need `async def` + SQLAlchemy 2.x async patterns
2. **Services not async** — need to wrap repo calls with `await`
3. **Models missing timestamps** — schemas expect `created_at`, `updated_at`
4. **No Alembic migrations** — need initial migration from models

## Test Commands (When Ready)
```bash
# Dev server
python api_run.py

# Swagger UI
http://localhost:8000/docs

# Health check
curl http://localhost:8000/api/health

# Login (when DB is ready)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"person_id": 1, "pin": "1234"}'
```

## Dependencies Added to requirements/pyproject.toml
- fastapi, uvicorn
- sqlalchemy 2.0.35 (async support)
- asyncpg (PostgreSQL driver)
- alembic (migrations)
- python-jose, cryptography (JWT)
- pytest-asyncio, httpx (testing)
- ruff (linting)

## Notes
- Entry point is `api_run.py` (not `run.py` which still runs Flask)
- JWT tokens expire in 7 days by default
- All protected routes require `Authorization: Bearer <token>` header
- Admin-only routes check `is_admin` flag in token
- CORS allows React dev server at localhost:5173 (Vite default)

## Next: Phase 1.1
Make repositories and services async, then Phase 1 is production-ready.
