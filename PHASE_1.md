# Phase 1 — FastAPI Backend Refactor

**Status:** Foundation scaffolded  
**Target:** Working JSON API with auth and CRUD operations

---

## What's Been Created

### Directory Structure
```
api/
├── __init__.py
├── main.py                   ← FastAPI app factory
├── routers/
│   ├── __init__.py
│   ├── auth.py              ← POST /api/auth/login
│   ├── chores.py            ← CRUD chores
│   └── people.py            ← CRUD people
├── schemas/
│   ├── __init__.py
│   ├── auth.py              ← TokenResponse
│   ├── chore.py             ← ChoreCreate, ChoreRead, ChoreUpdate, RecurrenceType
│   └── person.py            ← PersonCreate, PersonRead, PersonLogin
└── dependencies/
    ├── __init__.py
    ├── auth.py              ← JWT validation, admin gating
    └── db.py                ← AsyncSession dependency
```

### New Files
- `pyproject.toml` — Python 3.14, FastAPI, SQLAlchemy 2.x async, pytest config
- `api_run.py` — Entry point for FastAPI dev server
- `.env.example` — All environment variables documented
- `choreboss/config.py` — Updated to use pydantic_settings.BaseSettings
- `PHASE_1.md` — This document

---

## Architecture

### Request Flow
```
HTTP Request
    ↓
FastAPI Router (api/routers/*.py)
    ↓
Dependency Injection (api/dependencies/*.py)
    ├─ get_session() → AsyncSession
    ├─ get_current_person() → JWT validation
    └─ get_admin_person() → Admin check
    ↓
Business Logic (choreboss/services/*.py) ← REUSED from Flask
    ↓
Database (choreboss/repositories/*.py) ← REUSED from Flask
    ↓
Database (PostgreSQL via asyncpg)
    ↓
Response (Pydantic schema)
```

### Core Reuse
- **Models** (`choreboss/models/`) — unchanged SQLAlchemy
- **Repositories** (`choreboss/repositories/`) — unchanged DB access
- **Services** (`choreboss/services/`) — unchanged business logic
- **Tests** (`tests/models/`, `tests/services/`) — keep working

---

## API Endpoints (Implemented)

### Authentication
```
POST /api/auth/login
  Body: { person_id: 1, pin: "1234" }
  Response: { access_token: "...", token_type: "bearer", person_id: 1, is_admin: true }
```

### Chores
```
GET /api/chores/               ← List all (authenticated)
GET /api/chores/{id}           ← Get one (authenticated)
POST /api/chores/              ← Create (admin only)
PUT /api/chores/{id}           ← Update (admin only)
DELETE /api/chores/{id}        ← Delete (admin only)
POST /api/chores/{id}/complete ← Mark complete (authenticated)
```

### People
```
GET /api/people/               ← List all (authenticated)
GET /api/people/{id}           ← Get one (authenticated)
POST /api/people/              ← Create (admin only)
PUT /api/people/{id}           ← Update (admin only)
DELETE /api/people/{id}        ← Delete (admin only)
```

### Health
```
GET /api/health                ← { "status": "ok" }
```

---

## JWT Payload

After login, token contains:
```json
{
  "sub": "1",
  "is_admin": true,
  "exp": 1713650000
}
```

Protected routes require:
```
Authorization: Bearer eyJhbGci...
```

---

## Next Steps

### 1.1 Database Migration (Alembic)
- [ ] Initialize Alembic (`alembic init migrations`)
- [ ] Create migration from existing SQLAlchemy models
- [ ] Test migration: `alembic upgrade head`
- [ ] Update models to use `async_sessionmaker`

### 1.2 Repository Updates (Async)
- [ ] Convert repositories to use `await session.execute(select(...))`
- [ ] Convert repositories to use `session.add()` instead of merge
- [ ] All repositories must be `async def`

### 1.3 Service Updates (Async)
- [ ] All service methods must be `async def`
- [ ] Add type hints to all methods (especially async iterables)
- [ ] Test with pytest-asyncio

### 1.4 Router Completeness
- [ ] Add `GET /api/stats/leaderboard` (week/month totals)
- [ ] Add `GET /api/chores/{id}/history` (completion timeline)
- [ ] Add `PUT /api/people/{id}/pin` (change PIN)

### 1.5 Tests
- [ ] Set up pytest-asyncio with httpx test client
- [ ] Port all route tests from Flask to FastAPI
- [ ] Add auth tests (valid token, expired, invalid)
- [ ] Add admin gating tests

---

## Current Blockers

### 1. Services aren't async yet
Current code:
```python
def get_all_chores(self) -> list[Chore]:
    return self.repository.get_all()
```

Needs to be:
```python
async def get_all_chores(self) -> list[Chore]:
    return await self.repository.get_all()
```

**Fix:** Update all services to use `async def` and `await`.

### 2. Repositories aren't async yet
Current code:
```python
def get_all(self) -> list[Chore]:
    return self.session.query(Chore).all()
```

Needs to be:
```python
async def get_all(self) -> list[Chore]:
    result = await self.session.execute(select(Chore))
    return result.scalars().all()
```

**Fix:** Update all repositories to use SQLAlchemy 2.x async patterns.

### 3. Database is SQLite, not PostgreSQL
Current `.env` points to `sqlite:///choreboss.db`.

**For local dev:** Keep SQLite.  
**For production:** Switch to PostgreSQL in docker-compose.

### 4. Models need `created_at` / `updated_at`
Schemas expect these fields but models don't have them.

**Fix:** Add to models:
```python
from datetime import datetime
from sqlalchemy import func

created_at: Mapped[datetime] = mapped_column(
    DateTime, default=datetime.utcnow
)
updated_at: Mapped[datetime] = mapped_column(
    DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
)
```

---

## Running Phase 1

### Dev server
```bash
cd /srv/github/ChoreBoss
source .venv/bin/activate
pip install -e .  # Install in editable mode with pyproject.toml
python api_run.py
```

Swagger UI: http://localhost:8000/docs

### Test routes
```bash
# Health check
curl http://localhost:8000/api/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"person_id": 1, "pin": "1234"}'
```

---

## Files to Review Next

1. **choreboss/models/** — Add timestamps, make sure constraints align with schemas
2. **choreboss/repositories/** — Convert to async + SQLAlchemy 2.x patterns
3. **choreboss/services/** — Convert to async, update method signatures
4. **tests/** — Prepare for httpx + pytest-asyncio migration

---

## Rough Timeline

- **Blocking issues fix** (repos + services async): 2-3 hours
- **Alembic + migrations**: 1 hour
- **Tests migration**: 2-3 hours
- **Documentation**: 1 hour

**Total Phase 1 estimate:** 6-8 hours of focused work.

Once Phase 1 is done, the API is production-ready and Phase 2 (React frontend) can start in parallel.
