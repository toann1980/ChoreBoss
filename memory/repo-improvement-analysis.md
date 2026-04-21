# Repo Improvement Analysis
*Nova — 2026-04-20*

---

## Summary Table

| Repo | Health | Priority Issues | Quick Wins |
|---|---|---|---|
| BlendCraft | ✅ Good | Docs, 505M size, no facade | README, `.gitignore` audit |
| Envestero | ✅ Strong | `.google-cookie` in repo, no README | Delete secret, add README |
| ChoreBoss | ⚠️ Good-ish | Bug: validate_id returns None, hardcoded paths | 2-line bug fix |
| HouseHunter | ⚠️ Early | Hardcoded IP, platform path hacks, no tests | Env-driven config |
| ImageForge3D | ✅ Good | No backend tests, relay overhead | Add pytest skeleton |

---

## 1. BlendCraft

### Strengths
- Clean `core/` + `pipeline/` module split
- Unit tests mock `bpy` properly (no real Blender needed)
- CI/CD in place (unit + integration + lint workflows)
- garment-specific pipelines already exist: `clo3d.py`, `thumbnail.py`
- Eval scripts (`blendcraft_eval.py`, `automatron_eval.py`) for rapid iteration

### Issues & Improvements

#### 🔴 High — Repo Size (505MB)
The repo is huge. This is almost certainly due to committed binary assets (Blender builds, `.blend` files, rendered images).
- **Action:** Audit with `git lfs ls-files` and `du -sh *`; migrate assets to Git LFS or an external store
- Large repo = slow clones, CI bloat

#### 🟡 Medium — README is a one-liner
`README.md` only says "Streamline BPY for Blender." No install, no usage, no module overview.
- **Action:** Add setup instructions, import examples, module overview, link to `copilot-instructions.md`

#### 🟡 Medium — No unified public API / facade
There's no `BlendCraft` class or `__init__.py` export that exposes a clean top-level API.
- **Action:** Add `blendcraft/__init__.py` exports for core functions; define what the public surface is
- Prevents breaking changes from cascading into consuming code

#### 🟡 Medium — `z_legacy/` has no deprecation policy
No comments, no `DeprecationWarning`, no timeline for removal.
- **Action:** Add docstring to each legacy file: what it replaces and when it'll be removed

#### 🟢 Low — Type annotations consistency
Some modules have type annotations, others may not. `mypy` or `pyright` should be enforced in `lint.yml`.

#### 🟢 Low — copilot-instructions.md is CI-only
Kira wrote it well for CI/CD, but it doesn't describe module conventions, docstring standards, or garment-specific pipeline expectations.
- **Action:** Add a "Module Conventions" section (already captured in Nova's workspace `copilot-instructions.md`)

---

## 2. Envestero

### Strengths
- Modern Python 3.13, fully async throughout
- Pydantic v2 settings with no hardcoded config — gold standard
- Clean layered architecture: `config → db → services → api → tasks → cli`
- Proxy rotation + tenacity retry strategy is production-grade
- LLM-provider abstraction (Ollama / OpenAI) is well-designed
- v2 copilot-instructions already present and comprehensive

### Issues & Improvements

#### 🔴 CRITICAL — `.google-cookie` is committed to the repo
```
-rwxrwxr-x  1 leto leto  1348 Apr 20 17:47 .google-cookie
```
This is a security risk — authentication credentials in version history.
- **Action (immediate):**
  1. `git rm --cached .google-cookie`
  2. Add `.google-cookie` to `.gitignore`
  3. Rotate/invalidate the cookie
  4. Consider `git filter-repo` to purge from history

#### 🔴 High — `Z_ManualTest_*.py` files in root (5 files)
Manual test files in the project root are unprofessional and untidy. They won't be auto-discovered by pytest and create confusion.
- **Action:** Move to `tests/manual/` and document how to run them; or convert to proper `pytest` tests

#### 🔴 High — No README
No `README.md` at all. For a project of this complexity, this is a gap.
- **Action:** Add README with: purpose, architecture diagram (ASCII is fine), setup/install, CLI usage examples, `.env.example`

#### 🟡 Medium — `.bat` files in project root
`Envestero_daily.bat`, `Envestero_daily_custom.bat`, `Envestero_test.bat` are Windows batch scripts in the root. They suggest Windows-era remnants.
- **Action:** Move to `scripts/` folder; add Linux equivalents (`.sh`); consider Makefile targets

#### 🟡 Medium — `EXCLUDED_SITES` hardcoded in `newser.py`
The list of news sites to exclude is hardcoded in the service.
- **Action:** Move to config (env var or JSON file) so it can be updated without code changes

#### 🟡 Medium — No visible pytest config
`pyproject.toml` exists but unclear if `[tool.pytest.ini_options]` is configured. `smoke_test.py` in root suggests ad-hoc testing.
- **Action:** Add `[tool.pytest.ini_options]` to pyproject.toml; configure `testpaths`, `asyncio_mode = "auto"`

#### 🟢 Low — LangGraph roadmap not documented
`signals.py` comments mention future LangGraph agent layer. This intent should be in a design doc or `ROADMAP.md`.

---

## 3. ChoreBoss

### Strengths
- Clean repository/service/model separation
- `@validates` on all model fields — good defensive programming
- bcrypt for PIN hashing (correct approach)
- Test suite covers models, services, and routes
- Docker support (Dockerfile + docker-compose)

### Issues & Improvements

#### 🔴 CRITICAL BUG — `Chore.validate_id` returns `None`
```python
@validates('id')
def validate_id(self, key, value):
    if not isinstance(value, int):
        raise AttributeError(f'{key} must be an integer')
    # ← MISSING: return value
```
SQLAlchemy `@validates` must return the value. When a valid `id` is set, this returns `None`, silently setting `id = None`. This will cause insert failures or corrupt data.
- **Action:** Add `return value` as the final line — 1-line fix

#### 🔴 High BUG — `People.validate_birthday` wrong error message
```python
@validates('birthday')
def validate_birthday(self, key, value):
    if not isinstance(value, datetime.date):
        raise AttributeError(f'{key} must be a string')  # ← Says "string" but checks date
```
- **Action:** Fix to `f'{key} must be a datetime.date object'`

#### 🟡 Medium — `setup_memory_records` description mismatch
`validate_description` error says "between 20 and 500 characters" but code checks 10–500.
- **Action:** Align error message with actual constraint

#### 🟡 Medium — Tests use SQLite, production uses (presumably) Postgres
SQLite dialect differences (e.g., no `ON CONFLICT`, limited JSON, type coercion) can mask real issues.
- **Action:** Add a `pytest-postgresql` fixture for integration tests; keep SQLite only for model unit tests

#### 🟡 Medium — No type annotations on models
Models use SQLAlchemy columns but have no Python type annotations on class attributes.
- **Action:** Adopt SQLAlchemy 2.x `Mapped[]` syntax with `mapped_column()` for type-safe models

#### 🟢 Low — `validate_id` probably shouldn't exist
Auto-increment PKs shouldn't need validation — SQLAlchemy sets them after INSERT. The validator is both buggy and unnecessary.
- **Action:** Remove `validate_id` entirely

---

## 4. HouseHunter

### Strengths
- aiohttp async architecture — right choice for I/O-heavy property fetching
- API key managed via `decouple` (not hardcoded)
- Good docstrings on existing functions
- Frontend/API separation in place

### Issues & Improvements

#### 🔴 High — Hardcoded IP in `main.py`
```python
web.run_app(app, host='10.0.0.8', port=5950)
```
This is a local network IP hardcoded in the source — breaks on any other machine.
- **Action:** Read from env: `host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 5950))`
- Better: adopt `pydantic_settings.BaseSettings` (same pattern as Envestero)

#### 🔴 High — Platform-specific hardcoded `sys.path` hacks in standalone
```python
if sys.platform == "linux":
    sys.path.append("/var/git/library")
else:
    sys.path.append(r"D:\Git\library")
```
This references paths that only exist on Toan's local machines.
- **Action:** This file is v1 legacy. Either remove or convert to proper package imports after packaging

#### 🟡 Medium — No tests at all
8 Python files, 0 tests. Even a minimal smoke test would help.
- **Action:** Add `tests/` with at least: route tests (aiohttp `TestClient`), mock of RapidAPI calls

#### 🟡 Medium — Frontend/API integration unclear
Frontend (`src/`) and API (`api/`) exist but no docs describe how they talk to each other (CORS config, base URL, build steps).
- **Action:** Add `README.md` with setup steps, dev workflow, and architecture note

#### 🟡 Medium — No Docker support
Unlike ChoreBoss, no Dockerfile or docker-compose.
- **Action:** Add Dockerfile for the aiohttp API; add docker-compose with optional frontend build step

#### 🟢 Low — Only 2 API routes
`/` and `/properties?state_code=XX` is thin. Likely early stage.
- **Action:** Define route roadmap: property detail, saved searches, filters, comparison

---

## 5. ImageForge3D

### Strengths
- Excellent architecture documentation (`ARCHITECTURE.md`, `IMPLEMENTATION_SUMMARY.md`)
- WebSocket relay cleanly decouples Blender from backend
- Code quality push (docstrings + type hints + 80-char limit) — recent and disciplined
- GPU auto-detection
- Vue 3 frontend is modern

### Issues & Improvements

#### 🟡 Medium — No backend tests
17 Python files, 0 visible pytest tests for the FastAPI backend.
- **Action:** Add `backend/tests/` with: WebSocket endpoint tests (using `httpx.AsyncClient`), AI service mocks, Blender message parsing tests

#### 🟡 Medium — Node.js relay is an unnecessary dependency
The relay server is Node.js + `ws` package. This adds a runtime dependency for what's essentially a WebSocket proxy.
- **Action (optional):** Consider replacing with a pure Python asyncio WebSocket proxy in FastAPI — same functionality, one fewer runtime. Only worth doing if Node.js maintenance becomes a burden.

#### 🟡 Medium — CORS not configured on relay
The relay forwards raw messages but CORS isn't mentioned. If browser clients connect directly to port 8081, this will fail.
- **Action:** Add `Access-Control-Allow-Origin` headers to relay server for dev; tighten in production

#### 🟡 Medium — Stable Diffusion not containerized
GPU passthrough for Docker is complex, but no Dockerfile for the full stack including the AI model worker.
- **Action:** Add a `docker-compose.yml` with `backend` + `frontend` services; document GPU passthrough requirements for NVIDIA (nvidia-container-toolkit)

#### 🟢 Low — No ESLint config for Vue frontend
`.prettierrc` is present for formatting, but no `eslint.config.js`.
- **Action:** Add ESLint with `plugin:vue/vue3-recommended` + `@typescript-eslint` if TypeScript is used

#### 🟢 Low — `Notes.md` is empty
Empty file committed to root.
- **Action:** Either use it (sprint notes, known issues) or delete it

---

## Cross-Cutting Recommendations

### 1. Shared `.env.example` convention
Every repo should have `.env.example` with all required keys documented and blank. Makes onboarding instant.

### 2. `Makefile` as a universal entry point
All projects benefit from a `Makefile` with standard targets:
```makefile
make test      # run unit tests
make lint      # run ruff/mypy
make dev       # start dev server
make migrate   # run alembic/schema migrations
make docker    # build + run docker-compose
```

### 3. Pre-commit hooks
Add `.pre-commit-config.yaml` to each repo:
- `ruff` for lint/format
- `mypy` for type checking
- `detect-secrets` or `gitleaks` to prevent secret commits (would have caught `.google-cookie`)

### 4. README templates
BlendCraft and Envestero need proper READMEs. HouseHunter needs one. Template:
```markdown
# Project Name
One-sentence description.

## Setup
## Usage  
## Architecture
## Contributing / Dev Notes
```

---

*Analysis by Nova — /srv/github/ as of 2026-04-20*
