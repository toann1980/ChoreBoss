# Testing Strategy for Phase 1

**Goal:** 100% coverage of new FastAPI routes + auth + async DB operations

---

## Test Architecture

### Layer 1: Unit Tests (Existing)
- Location: `tests/models/`, `tests/services/`
- Tool: `pytest`
- Database: SQLite in-memory
- **No changes needed** — these test business logic, not HTTP

### Layer 2: Integration Tests (New FastAPI)
- Location: `tests/routers/`
- Tool: `pytest` + `pytest-asyncio` + `TestClient`
- Database: SQLite in-memory with async driver (`aiosqlite`)
- **New:** FastAPI routes with full stack (auth, DB, schemas)

### Layer 3: End-to-End (Future)
- Location: `tests/e2e/`
- Tool: Playwright or Selenium (for React frontend)
- Database: Real PostgreSQL or Docker container
- **Phase 2+:** Integration with React frontend

---

## Test Files Created

### `tests/conftest_fastapi.py`
Fixtures for FastAPI testing:
- `async_session_maker` — Create async session factory with in-memory SQLite
- `async_session` — Session for a single test
- `test_app` — FastAPI app with mocked session dependency
- `test_client` — TestClient for making HTTP requests

### `tests/routers/test_auth_routes.py`
- ✅ Login with valid PIN
- ✅ Login with invalid PIN (should fail)
- ✅ Login with non-existent person (should 404)
- 🔲 Token expiry (needs `freezegun`)
- 🔲 Token refresh (if implemented)

### `tests/routers/test_chore_routes.py`
- ✅ List chores (authenticated)
- ✅ List chores (unauthenticated, should 403)
- ✅ Get single chore
- ✅ Get non-existent chore (should 404)
- ✅ Create chore (admin only)
- ✅ Create chore (non-admin, should 403)
- ✅ Complete chore
- 🔲 Update chore (admin only)
- 🔲 Delete chore (admin only)
- 🔲 Chore auto-assignment on complete

### `tests/routers/test_people_routes.py`
- ✅ List people (authenticated)
- ✅ List people (unauthenticated, should 403)
- ✅ Get single person
- ✅ Create person (admin only)
- ✅ Create person (non-admin, should 403)
- 🔲 Update person (admin only)
- 🔲 Delete person (admin only)
- 🔲 Change PIN

---

## Test Coverage Goals

| Area | Unit | Integration | Target |
|---|---|---|---|
| Models | ✅ 100% | — | Keep |
| Services | ✅ 100% | — | Keep |
| Auth Dependency | — | ✅ In progress | 100% |
| Chore Routes | — | ✅ In progress | 100% |
| People Routes | — | ✅ In progress | 100% |
| DB Dependency | — | ✅ In progress | 100% |
| JWT Token | — | 🔲 TODO | 100% |
| Admin Gating | — | ✅ In progress | 100% |
| Error Handling | — | 🔲 Partial | 100% |

---

## Running Tests

### All tests (unit + integration)
```bash
pytest tests/ -v
```

### Only FastAPI integration tests
```bash
pytest tests/routers/ -v
```

### Only unit tests (models + services)
```bash
pytest tests/models/ tests/services/ -v
```

### With coverage report
```bash
pytest tests/ --cov=choreboss --cov=api --cov-report=html
```

### Watch mode (auto-rerun on file changes)
```bash
pytest-watch tests/routers/
```

---

## Blockers Before Tests Run

### 1. Services must be async
Current error:
```
AttributeError: 'coroutine' object has no attribute 'id'
```

**Reason:** Routes call `await chore_service.get_chore_by_id()` but services are still sync.

**Fix:** Convert all services to `async def`:
```python
# Before
def get_chore_by_id(self, chore_id: int) -> Chore:
    return self.repository.get_by_id(chore_id)

# After
async def get_chore_by_id(self, chore_id: int) -> Chore:
    return await self.repository.get_by_id(chore_id)
```

### 2. Repositories must be async
Current error:
```
AttributeError: 'AsyncSession' object has no attribute 'query'
```

**Reason:** Session is async, but repos use sync SQLAlchemy patterns.

**Fix:** Convert to async patterns:
```python
# Before
def get_by_id(self, chore_id: int) -> Chore:
    return self.session.query(Chore).filter(Chore.id == chore_id).first()

# After
async def get_by_id(self, chore_id: int) -> Chore:
    result = await self.session.execute(select(Chore).where(Chore.id == chore_id))
    return result.scalar_one_or_none()
```

### 3. Test database requires aiosqlite
Add to `pyproject.toml`:
```toml
pytest-asyncio = "^0.23"
aiosqlite = "^0.19"
```

---

## Test Pattern (for reference)

```python
@pytest.mark.asyncio
async def test_create_chore_admin(
    test_client, async_session: AsyncSession
) -> None:
    """Test creating chore as admin.

    Args:
        test_client: FastAPI test client.
        async_session: Database session.
    """
    # 1. Setup: Create test data
    person = await setup_test_people(async_session, 1)

    # 2. Action: Login to get token
    login_response = test_client.post(
        "/api/auth/login",
        json={"person_id": person.id, "pin": "1234"},
    )
    token = login_response.json()["access_token"]

    # 3. Action: Make request with auth
    response = test_client.post(
        "/api/chores/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Test", "description": "Test chore content"},
    )

    # 4. Assert: Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test"
```

---

## Next Steps

1. **Fix blockers** (repos/services async) — ~2 hours
2. **Run tests** — should see failures on the lines above
3. **Add missing tests** (updates, deletes, auth edge cases) — ~2 hours
4. **Coverage report** — aim for 85%+ across all layers

---

## Tips for Writing More Tests

### Test both success AND failure
```python
def test_create_chore_success(...): ...
def test_create_chore_invalid_description(...): ...  # Too short
def test_create_chore_unauthenticated(...): ...      # Missing token
def test_create_chore_non_admin(...): ...            # 403 forbidden
```

### Use parameterize for variants
```python
@pytest.mark.parametrize("pin", ["1234", "9999", "0000"])
def test_login_pins(test_client, async_session, pin):
    ...
```

### Test edge cases
- Empty strings
- Null values
- Very long strings (>255 chars)
- Special characters
- Unicode
- Concurrent requests (load test)

---

## Mocking Strategy

**Don't mock the database.** Test against in-memory SQLite, just like Flask tests.

**Do mock external services** (if added later):
- Email sending
- SMS notifications
- Third-party APIs

```python
from unittest.mock import patch

@patch("api.services.send_email")
def test_complete_chore_sends_email(mock_email, test_client, async_session):
    ...
    mock_email.assert_called_once()
```

---

## Timeline

- **Phase 1.1 (blockers):** 2 hours
- **Phase 1.2 (running tests):** 1 hour
- **Phase 1.3 (full coverage):** 2-3 hours

**Total:** ~5-6 hours to get Phase 1 to 100% test coverage.
