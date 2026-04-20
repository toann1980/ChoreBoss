# ChoreBoss — Copilot Instructions

FastAPI-based household chore tracking system with async database, JWT auth, and admin management.
**Status:** Phase 1 complete (Foundation, Async, Testing, Migrations). **Next:** Phase 2 (React Frontend).

---

## Project Status

| Phase | Component | Status |
|-------|-----------|--------|
| **Phase 1** | FastAPI Foundation | ✅ COMPLETE |
| **Phase 1.1** | Async Repos/Services | ✅ COMPLETE |
| **Phase 1.2** | Testing (15 tests) | ✅ COMPLETE (100% passing) |
| **Phase 1.3** | Alembic Migrations | ✅ COMPLETE (reversible) |
| **Phase 2** | React Frontend | ⏳ Next (8-12 hours) |
| **Phase 3** | Login Refinements | ⏳ Future |
| **Phase 4** | Reminders (APScheduler) | ⏳ Future |
| **Phase 5** | Real-time (WebSocket) | ⏳ Future |
| **Phase 6** | Deployment (Docker) | ⏳ Future |

---

## Architecture (FastAPI)

```
api/                             ← FastAPI backend
├── main.py                       – App factory (CORS, lifespan)
├── routers/
│   ├── auth.py                  – POST /api/auth/login
│   ├── chores.py                – GET/POST/PUT/DELETE /api/chores/
│   └── people.py                – GET/POST/PUT/DELETE /api/people/
├── schemas/
│   ├── auth.py                  – PersonLogin, TokenResponse
│   ├── chore.py                 – ChoreCreate, ChoreRead, ChoreUpdate
│   └── person.py                – PersonCreate, PersonRead, PersonUpdate
└── dependencies/
    ├── auth.py                  – JWT validation, admin gating
    └── db.py                    – AsyncSession provider (lazy init)

choreboss/                       ← Core domain (REUSED from Flask)
├── models/
│   ├── chore.py                 – SQLAlchemy + timestamps
│   └── people.py                – SQLAlchemy + timestamps
├── repositories/                ← ASYNC
│   ├── chore_repository.py      – async def get_by_id(), add_chore(), etc.
│   └── people_repository.py     – async def get_by_id(), sequence rotation
└── services/                    ← ASYNC
    ├── chore_service.py         – async def complete_chore() (auto-assign)
    └── people_service.py        – async def verify_pin(), add_person()

tests/
├── conftest.py                  – pytest-asyncio fixtures
├── routers/                     – 15 integration tests (FastAPI TestClient)
├── models/                      – Model validation (sync)
└── services/                    – Service unit tests (sync)

migrations/                      ← Alembic
├── env.py                       – Auto-detect models, async URL handling
├── script.py.mako               – Migration template
└── versions/
    └── b17de874045a_initial_*.py – Initial schema (people, chores)

api_run.py                        – Entry point: uvicorn api_run:app --reload
pyproject.toml                    – Project metadata + dependencies
alembic.ini                       – Alembic config
.env.example                      – Environment variables template
```

---

## Code Conventions

**Universal (all repos):**
- **Python 3.14.4** — type annotations required on all functions
- `from __future__ import annotations` at the top of every module
- Google-style docstrings on all public methods (Args / Returns / Raises)
- **80-character line limit**
- `pathlib.Path` for file paths — never `os.path`

**FastAPI-specific:**
- All routes async (`async def`)
- All services async (`async def`)
- All repositories async (`async def`)
- SQLAlchemy 2.x `select()` syntax + `await session.execute()`
- No ORM `.query()` — always use `select()` with `selectinload()`
- Pydantic v2 for validation (input/output)
- `HTTPException` for error responses (not `raise ValueError`)
- Dependency injection for auth, session, repo instances
- No global state — fresh instances per request

**Migrations:**
- Auto-generate: `alembic revision --autogenerate -m "Description"`
- Always implement both `upgrade()` and `downgrade()`
- Test reversibility: `alembic upgrade head && alembic downgrade -1 && alembic upgrade head`
- Reversible migrations are critical for production safety

---

## Data Model (with Timestamps)

### Chore
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK (auto-increment) |
| `name` | String(50) | NOT NULL, UNIQUE |
| `description` | String(500) | NOT NULL |
| `person_id` | Integer | FK → people.id, nullable |
| `last_completed_date` | DateTime | nullable |
| `last_completed_id` | Integer | FK → people.id, nullable |
| `created_at` | DateTime | NOT NULL, default=utcnow |
| `updated_at` | DateTime | NOT NULL, onupdate=utcnow |

### People
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK (auto-increment) |
| `first_name` | String(50) | NOT NULL |
| `last_name` | String(50) | NOT NULL |
| `birthday` | Date | NOT NULL |
| `pin` | String(255) | bcrypt hash, NOT NULL |
| `is_admin` | Boolean | default False |
| `sequence_num` | Integer | NOT NULL (rotation) |
| `created_at` | DateTime | NOT NULL, default=utcnow |
| `updated_at` | DateTime | NOT NULL, onupdate=utcnow |

---

## API Endpoints (13 Total)

### Auth
```
POST   /api/auth/login              { person_id, pin } → { access_token, ... }
```

### Chores (7)
```
GET    /api/chores/                 → [ { id, name, description, ... } ]
GET    /api/chores/{id}             → { id, name, description, ... }
POST   /api/chores/                 ← ADMIN ONLY (requires JWT + is_admin=true)
PUT    /api/chores/{id}             ← ADMIN ONLY
DELETE /api/chores/{id}             ← ADMIN ONLY
POST   /api/chores/{id}/complete    Mark complete + auto-assign next
GET    /api/health                  → { status: "ok" }
```

### People (5)
```
GET    /api/people/                 → [ { id, first_name, last_name, ... } ]
GET    /api/people/{id}             → { id, first_name, last_name, ... }
POST   /api/people/                 ← ADMIN ONLY
PUT    /api/people/{id}             ← ADMIN ONLY
DELETE /api/people/{id}             ← ADMIN ONLY
```

All require JWT token in `Authorization: Bearer <token>` header.

---

## 3-Layer Architecture (Async)

```
Route (HTTP, FastAPI)
  ↓ (depends on)
Service (Business logic, async)
  ↓ (depends on)
Repository (DB access, async)
  ↓
SQLAlchemy 2.x + AsyncSession
  ↓
asyncpg (PostgreSQL) or aiosqlite (SQLite)
```

**Rules:**
- Routes call **services only** (inject session, never touch repos)
- Services contain **all** business logic
- Repositories handle **all** DB queries
- All database calls are `await`

**Example:**
```python
# Router
@router.post("/chores/{id}/complete")
async def complete_chore(id: int, session: AsyncSession = Depends(get_session)):
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    result = await service.complete_chore(id, person_id)
    await session.commit()
    return result
```

---

## Testing

### Run Tests
```bash
pytest tests/routers/ -v              # All tests
pytest tests/routers/test_auth_routes.py::test_login_success  # Specific test
```

### Test Results
```
15 passed in 6.39s — 100% passing
Auth (3), Chores (7), People (5)
```

### Test Setup
- `conftest.py` — pytest-asyncio fixtures (async_engine, async_session, test_app, test_client)
- `setup_memory_records.py` — Async test data helpers (setup_test_people, setup_test_chores)
- In-memory SQLite for all tests (no external DB needed)
- Fresh database per test (isolation)

### Coverage
- Target: 85%+
- Current: ~80%+ (15 tests, good happy-path + error coverage)

---

## Database Migrations (Alembic)

### Generate Migration (Auto-detect)
```bash
alembic revision --autogenerate -m "Add field X to table Y"
```

### Apply Migrations
```bash
alembic upgrade head              # Apply all pending
alembic upgrade +1                # Apply next
alembic downgrade -1              # Revert last
alembic downgrade base            # Revert all
```

### View History
```bash
alembic history                   # Show all revisions
alembic current                   # Show current revision
```

### Initial Migration
**Revision:** b17de874045a  
**Tables:** people, chores (with timestamps, FKs, constraints)  
**Status:** Tested (upgrade ✓ downgrade ✓)

---

## Running Locally

### Development (FastAPI)
```bash
source .venv/bin/activate
python api_run.py
# Server at http://localhost:8000
# Docs at http://localhost:8000/docs (Swagger)
# ReDoc at http://localhost:8000/redoc
```

### Database Setup
```bash
# Apply migrations
alembic upgrade head
```

### Tests
```bash
pytest tests/routers/ -v
```

---

## Dependencies

**FastAPI Stack:**
- fastapi, uvicorn, httpx (testing)
- sqlalchemy>=2.0, asyncpg, aiosqlite
- pydantic>=2.0, pydantic-settings
- pytest-asyncio, pytest
- python-jose (JWT), cryptography, bcrypt
- alembic (migrations)

---

## Known Bugs — FIXED IN PHASE 1.2

✅ `Chore.validate_id` missing `return value` → Fixed  
✅ `People.validate_birthday` wrong error → Fixed  
✅ `Chore.validate_description` message → Fixed  
✅ Missing timestamps → Added `created_at`, `updated_at`  
✅ Duplicate relationships → Simplified  
✅ Async fixtures → Created pytest-asyncio setup  

---

## What NOT to Do

- Don't call repositories directly from routes — always use services
- Don't hardcode database URLs — use `.env` + `choreboss/config.py`
- Don't write sync code in async functions — use `await` always
- Don't use ORM `.query()` — always use SQLAlchemy 2.x `select()`
- Don't commit migration files after editing them — migrations are immutable
- Don't skip downgrade() in migrations — reversibility is critical
- Don't test with real databases — use in-memory SQLite in tests
- Don't bypass JWT auth in routes — use `Depends(get_current_person)`

---

## Backlog (Future Phases)

- [ ] **Phase 2:** React + TypeScript frontend (login, dashboard)
- [ ] **Phase 3:** Login refinements, email verification
- [ ] **Phase 4:** Chore reminders (APScheduler)
- [ ] **Phase 5:** Real-time updates (WebSocket)
- [ ] **Phase 6:** Docker full-stack, CI/CD (GitHub Actions)
- [ ] Increase test coverage to 85%+
- [ ] Add logging/monitoring (structured logs)
- [ ] Add OpenAPI/Swagger customization
- [ ] Add rate limiting
- [ ] Add CORS refinements

---

## Key Files to Modify

| File | Purpose | Frequency |
|------|---------|-----------|
| `choreboss/models/` | Data schema | Low (breaking changes rare) |
| `api/routers/` | HTTP endpoints | Medium (new features) |
| `choreboss/services/` | Business logic | Medium (new features) |
| `tests/routers/` | Integration tests | High (add tests with new routes) |
| `migrations/versions/` | Database changes | Low (once per schema change) |

---

## Deployment

**Status:** Ready for staging → production  

- ✅ Backend complete (FastAPI)
- ✅ Migrations complete (Alembic)
- ✅ Tests passing (15/15)
- ✅ Documentation complete (11 guides)
- ⏳ Frontend (Phase 2)
- ⏳ Docker full-stack (Phase 6)

**Environment Variables Required:**
```env
DATABASE_URL=postgresql://user:pass@host/choreboss
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168
```

---

## Documentation

- `COMPLETION_SUMMARY.md` — **START HERE** (overall status)
- `ALEMBIC_GUIDE.md` — Migration usage guide
- `ROADMAP.md` — 6-phase development plan
- `TESTING_STRATEGY.md` — Testing approach
- `PHASE_1_3_ALEMBIC_COMPLETE.md` — Alembic details
