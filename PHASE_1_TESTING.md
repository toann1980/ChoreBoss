# Phase 1 Testing Roadmap

**Status:** Foundation scaffolded, tests written, blockers identified  
**Ready to run:** Once repositories and services are async

---

## What's Been Created

### Test Fixtures (`tests/conftest_fastapi.py`)
- `async_session_maker` — In-memory async SQLite
- `async_session` — Per-test session
- `test_app` — FastAPI app with mocked dependencies
- `test_client` — HTTP test client (TestClient)

### Route Tests (NEW)

#### `tests/routers/test_auth_routes.py`
```
✅ test_login_success — Valid PIN → JWT token
✅ test_login_invalid_pin — Wrong PIN → 401
✅ test_login_person_not_found — Invalid person_id → 404
```

#### `tests/routers/test_chore_routes.py`
```
✅ test_list_chores_authenticated — GET /api/chores/
✅ test_list_chores_unauthenticated — No token → 403
✅ test_get_chore — GET /api/chores/{id}
✅ test_get_chore_not_found — Invalid ID → 404
✅ test_create_chore_admin — Admin can create
✅ test_create_chore_non_admin — Non-admin → 403
✅ test_complete_chore — POST /api/chores/{id}/complete
```

#### `tests/routers/test_people_routes.py`
```
✅ test_list_people_authenticated — GET /api/people/
✅ test_list_people_unauthenticated — No token → 403
✅ test_get_person — GET /api/people/{id}
✅ test_create_person_admin — Admin can create
✅ test_create_person_non_admin — Non-admin → 403
```

### Existing Tests (KEEP)
- `tests/models/` — Model validation (no changes needed)
- `tests/services/` — Business logic (no changes needed)

---

## Test Structure

```
tests/
├── conftest.py                 ← Original Flask fixtures (KEEP)
├── conftest_fastapi.py         ← NEW FastAPI fixtures
├── models/                     ← KEEP (no changes)
│   ├── test_chore_model.py
│   └── test_people_model.py
├── services/                   ← KEEP (no changes)
│   ├── test_chore_service.py
│   └── test_people_service.py
├── routers/                    ← NEW FastAPI route tests
│   ├── __init__.py
│   ├── test_auth_routes.py
│   ├── test_chore_routes.py
│   └── test_people_routes.py
├── web/flask_app/             ← DEPRECATE (old Flask routes)
│   └── routes/
│       ├── test_chore_routes.py
│       └── test_people_routes.py
└── setup_memory_records.py     ← Test data helpers (REUSE)
```

---

## Running Tests

### Run ALL tests (unit + integration)
```bash
cd /srv/github/ChoreBoss
source .venv/bin/activate
pytest tests/ -v
```

### Run ONLY FastAPI integration tests
```bash
pytest tests/routers/ -v
```

### Run ONLY unit tests
```bash
pytest tests/models/ tests/services/ -v
```

### With coverage
```bash
pytest tests/ --cov=choreboss --cov=api
```

---

## What's Blocking Tests

### 1. Repositories aren't async yet
**Current:** `def get_by_id(self, chore_id: int) -> Chore`  
**Needed:** `async def get_by_id(self, chore_id: int) -> Chore`

**Error when you run tests:**
```
AttributeError: 'AsyncSession' object has no attribute 'query'
```

### 2. Services aren't async yet
**Current:** `def get_chore_by_id(self, chore_id: int) -> Chore`  
**Needed:** `async def get_chore_by_id(self, chore_id: int) -> Chore`

**Error when you run tests:**
```
AttributeError: 'coroutine' object has no attribute 'id'
```

### 3. Missing async test database driver
**Add to `pyproject.toml`:**
```toml
aiosqlite = "^0.19"
pytest-asyncio = "^0.23"
```

---

## Phase 1 Test Completion Checklist

### Pre-requisites
- [ ] Update repositories to async (2 hours)
- [ ] Update services to async (1 hour)
- [ ] Add `aiosqlite` + `pytest-asyncio` to `pyproject.toml`
- [ ] Ensure models have `created_at` and `updated_at` fields

### FastAPI Route Tests
- [x] Auth routes (login success/failure)
- [x] Chore routes (CRUD + complete)
- [x] People routes (CRUD)
- [ ] Auth token edge cases (expiry, refresh)
- [ ] Validation tests (invalid schemas)
- [ ] Error handling (500, 503, etc.)
- [ ] Concurrent requests

### Test Coverage Goals
- [ ] 100% of route handlers
- [ ] 100% of auth dependencies
- [ ] 100% of error paths
- [ ] 85%+ overall code coverage

### Performance Tests (Nice-to-have)
- [ ] Large list responses (100+ items)
- [ ] Slow database queries
- [ ] Concurrent login attempts

---

## After Tests Pass

Once all tests pass:

1. **Measure coverage** → `pytest tests/ --cov=choreboss --cov=api --cov-report=html`
2. **Deprecate Flask tests** → Keep for reference, mark as legacy
3. **Update CI/CD** → GitHub Actions to run pytest-asyncio
4. **Document API** → Swagger/OpenAPI at `/docs`
5. **Move to Phase 2** → React frontend scaffolding

---

## Test Examples

### Testing authentication
```python
@pytest.mark.asyncio
async def test_login_success(test_client, async_session):
    person = await setup_test_people(async_session, 1)
    response = test_client.post(
        "/api/auth/login",
        json={"person_id": person.id, "pin": "1234"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Testing protected routes
```python
@pytest.mark.asyncio
async def test_list_chores_authenticated(test_client, async_session):
    person = await setup_test_people(async_session, 1)
    login_resp = test_client.post("/api/auth/login", ...)
    token = login_resp.json()["access_token"]
    
    response = test_client.get(
        "/api/chores/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### Testing admin gating
```python
@pytest.mark.asyncio
async def test_create_chore_non_admin(test_client, async_session):
    person = await setup_test_people(async_session, 1)
    person.is_admin = False
    
    login_resp = test_client.post("/api/auth/login", ...)
    token = login_resp.json()["access_token"]
    
    response = test_client.post(
        "/api/chores/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Test", "description": "Test description"}
    )
    assert response.status_code == 403  # Forbidden
```

---

## Deliverables

- [x] `conftest_fastapi.py` — Test fixtures
- [x] `tests/routers/test_auth_routes.py` — 3 tests
- [x] `tests/routers/test_chore_routes.py` — 7 tests
- [x] `tests/routers/test_people_routes.py` — 5 tests
- [x] `TESTING_STRATEGY.md` — Full testing guide
- [x] This roadmap (`PHASE_1_TESTING.md`)

**Total tests written:** 15 integration tests (20+ assertions)

---

## Next Steps

1. **Fix blockers** (async repos/services)
2. **Run tests** → `pytest tests/routers/ -v`
3. **Add missing tests** (updates, deletes, edge cases)
4. **Measure coverage** → Aim for 85%+
5. **Document API** → Swagger at `/docs`

**Time estimate to get all tests passing:** 5-6 hours total (including blocker fixes).
