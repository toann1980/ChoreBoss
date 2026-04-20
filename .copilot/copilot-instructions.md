# ChoreBoss — Copilot Instructions

Flask web app for tracking and managing household chores between members.
Read this fully before generating code, tests, or migrations.

---

## Architecture

```
choreboss/
├── models/
│   ├── __init__.py          – SQLAlchemy Base
│   ├── chore.py             – Chore model (name, description, person_id, last_completed)
│   └── people.py            – People model (name, birthday, PIN hash, is_admin)
│
├── repositories/
│   ├── chore_repository.py  – DB read/write for Chore
│   └── people_repository.py – DB read/write for People
│
├── services/
│   ├── chore_service.py     – Business logic for chores
│   └── people_service.py    – Business logic for people, PIN verify
│
├── config.py                – App config (testing / production)
└── setup_services.py        – Wire repositories → services

web/
└── flask_app/               – Flask app factory, Jinja2 templates, static assets

tests/
├── conftest.py / setup_memory_records.py
├── models/                  – Model unit tests (SQLite in-memory)
├── services/                – Service unit tests (SQLite in-memory)
└── web/flask_app/
    ├── test_main.py
    └── routes/              – Route integration tests (Flask test client)

Dockerfile + docker-compose.yml
requirements_linux.txt / requirements_windows.txt
run.py                       – Entry point
```

---

## Code Conventions

- **Python 3.14.4** — type annotations required on all functions
- `from __future__ import annotations` at the top of every module
- Google-style docstrings on all public methods (Args / Returns / Raises)
- **80-character line limit**
- `pathlib.Path` for file paths — never `os.path`
- `pydantic_settings.BaseSettings` for all config — no hardcoded values
- SQLAlchemy 2.x `Mapped[]` + `mapped_column()` syntax preferred for new models

---

## Data Model

### Chore
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK (auto-increment) |
| `name` | String(50) | NOT NULL, UNIQUE |
| `description` | String(500) | NOT NULL |
| `person_id` | Integer | FK → people.id, nullable |
| `last_completed_date` | DateTime | nullable |
| `last_completed_id` | Integer | FK → people.id, nullable |

### People
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK (auto-increment) |
| `first_name` | String(50) | NOT NULL |
| `last_name` | String(50) | NOT NULL |
| `birthday` | Date | NOT NULL |
| `pin` | String(255) | bcrypt hash |
| `is_admin` | Boolean | default False |
| `sequence_num` | Integer | NOT NULL |

---

## Known Bugs — Fix Before Extending

### 🔴 `Chore.validate_id` missing `return value`
```python
@validates('id')
def validate_id(self, key, value):
    if not isinstance(value, int):
        raise AttributeError(f'{key} must be an integer')
    return value   # ← THIS LINE IS MISSING — silently sets id=None on every valid insert
```
**Fix:** Add `return value`. This is a data-corruption bug.

> Note: `validate_id` is arguably unnecessary since `id` is an auto-increment PK
> set by SQLAlchemy after INSERT. Consider removing the validator entirely.

### 🔴 `People.validate_birthday` wrong error message
```python
raise AttributeError(f'{key} must be a string')  # ← wrong
raise AttributeError(f'{key} must be a datetime.date object')  # ← correct
```

### 🟡 `Chore.validate_description` error message mismatch
Code checks `10 <= len(value) <= 500` but error says "between 20 and 500 characters".
Align message with actual constraint.

---

## Repository Pattern

Follow the existing 3-layer pattern strictly:

```
Model (SQLAlchemy) → Repository (DB access) → Service (business logic) → Route (HTTP)
```

- Routes call **services only** — never repositories directly
- Services contain **all** business logic — routes stay thin
- Repositories handle **all** DB queries — services never write raw SQL

---

## Testing

### Run all tests
```bash
python -m pytest tests/ -q
```

### Test DB
- Unit and integration tests use **SQLite in-memory** (`sqlite:///:memory:`)
- **Never** connect to a real database in tests
- Use `tests/setup_memory_records.py` for fixture data

### Test structure
- `tests/models/` — model validation tests (field constraints, `@validates` logic)
- `tests/services/` — service layer tests (business logic, dependency injection)
- `tests/web/flask_app/routes/` — route tests (Flask test client, JSON responses)

### Known gap
- Tests use SQLite, production likely uses PostgreSQL
- SQLite dialect differences (type coercion, ON CONFLICT) can mask real bugs
- Add `pytest-postgresql` fixtures for integration tests; keep SQLite for model unit tests

---

## Running Locally

```bash
# Development
flask --app run.py run

# Linux production
gunicorn --bind 0.0.0.0:8055 run:app

# Windows production
waitress-serve --host=0.0.0.0 --port=8055 run:app

# Docker
docker-compose up
```

Port: **8055**

---

## Active Work / Backlog

- [ ] Fix `validate_id` missing `return value` bug (data corruption)
- [ ] Fix `validate_birthday` wrong error message
- [ ] Fix `validate_description` message mismatch
- [ ] Add `pytest-postgresql` for integration test parity with production DB
- [ ] Migrate models to SQLAlchemy 2.x `Mapped[]` syntax
- [ ] Add `Makefile` with `make test`, `make lint`, `make dev`, `make docker`
- [ ] Add `.env.example` with all required config keys
- [ ] Add pre-commit hooks (ruff + gitleaks)

---

## What NOT to Do

- Don't call repositories from routes — always go through services
- Don't hardcode database URLs — use `config.py` / environment variables
- Don't connect to a real DB in tests
- Don't add validators on auto-increment PKs — SQLAlchemy manages them
- Don't bypass the Flask test client for route tests
