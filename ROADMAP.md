# ChoreBoss — Modernization Roadmap

**Direction:** FastAPI + React + TypeScript  
**Python:** 3.14.4 | **Node:** Latest LTS  
**Status:** Phase 0 complete — ready to refactor

---

## Architecture Target

```
ChoreBoss/
├── api/                          ← FastAPI backend (replaces web/flask_app/)
│   ├── routers/                  ← Route handlers (chores, people, auth)
│   ├── schemas/                  ← Pydantic request/response models
│   ├── dependencies/             ← Auth, DB session injection
│   └── main.py                   ← FastAPI app factory
│
├── choreboss/                    ← KEEP — core domain (models, repos, services)
│   ├── models/                   ← SQLAlchemy 2.x ORM
│   ├── repositories/             ← DB access layer
│   ├── services/                 ← Business logic
│   └── config.py                 ← pydantic_settings.BaseSettings
│
├── frontend/                     ← React + TypeScript (replaces web/)
│   ├── src/
│   │   ├── components/           ← Shared UI components
│   │   ├── pages/                ← Page-level components (Dashboard, Login, etc.)
│   │   ├── hooks/                ← Custom React hooks (useChores, usePeople)
│   │   ├── api/                  ← API client (typed fetch wrappers)
│   │   ├── store/                ← Zustand global state
│   │   └── types/                ← Shared TypeScript types (mirrors API schemas)
│   ├── vite.config.ts
│   └── package.json
│
├── tests/                        ← Extend existing test suite for FastAPI
├── migrations/                   ← Alembic database migrations
├── docker-compose.yml            ← api + frontend + postgres services
├── Dockerfile.api
├── Dockerfile.frontend
└── .env.example
```

### What stays
- `choreboss/models/`, `repositories/`, `services/` — the entire 3-layer core is **reusable as-is**
- `tests/models/`, `tests/services/` — model and service tests **keep working**

### What gets replaced
| Old | New | Why |
|---|---|---|
| `web/flask_app/` | `api/` (FastAPI) | Async, typed, auto-docs |
| `Jinja2 templates` | React + TypeScript | Mobile-first, component-driven |
| SQLite | PostgreSQL | Production-grade, proper constraints |
| `gunicorn` | `uvicorn` | ASGI for async FastAPI |
| Flask test client | `httpx` + `pytest-asyncio` | Native async testing |

---

## Tech Stack

### Backend
| Package | Version | Role |
|---|---|---|
| `fastapi` | latest | ASGI web framework |
| `uvicorn` | latest | ASGI server |
| `sqlalchemy` | 2.x async | ORM (already installed) |
| `asyncpg` | latest | Async PostgreSQL driver |
| `alembic` | latest | DB migrations |
| `pydantic` | v2 | Schema validation (FastAPI native) |
| `pydantic-settings` | latest | Config / env vars |
| `python-jose` | latest | JWT auth tokens |
| `bcrypt` | ≥4.2 | PIN hashing (already installed) |
| `apscheduler` | latest | Chore reminder scheduling |

### Frontend
| Package | Version | Role |
|---|---|---|
| `react` | 18+ | UI framework |
| `typescript` | 5+ | Type safety |
| `vite` | latest | Dev server + bundler |
| `react-router-dom` | 6 | Client-side routing |
| `@tanstack/react-query` | 5 | Server state + caching |
| `zustand` | latest | Client state (auth, UI) |
| `tailwindcss` | 3+ | Utility-first CSS |
| `shadcn/ui` | latest | Accessible component library |
| `axios` | latest | HTTP client |

---

## Phase 0 — Foundation ✅ Complete

- [x] Bug fixes: `validate_id`, `validate_birthday`, `validate_description`
- [x] Python 3.14.4 venv
- [x] All 75 tests passing
- [x] Dockerfile updated to python:3.14-slim
- [x] App running at http://10.0.0.81:8055

---

## Phase 1 — Backend Refactor (FastAPI + PostgreSQL)

**Goal:** Replace Flask with FastAPI. Keep all existing core logic. Add auth + async DB.

### 1.1 Project scaffolding
- [ ] Create `api/` directory structure
- [ ] Add `pyproject.toml` (replace `requirements_linux.txt`)
- [ ] Add Alembic (`migrations/`) with initial migration from existing schema
- [ ] Switch SQLite → PostgreSQL in config + Docker Compose
- [ ] Migrate SQLAlchemy models to async (`AsyncSession`, `async_sessionmaker`)

### 1.2 FastAPI app
- [ ] `api/main.py` — app factory, CORS, lifespan hooks
- [ ] `api/dependencies/db.py` — async DB session dependency
- [ ] `api/dependencies/auth.py` — JWT token dependency
- [ ] `api/schemas/chore.py` — Pydantic schemas (ChoreCreate, ChoreRead, ChoreUpdate)
- [ ] `api/schemas/person.py` — Pydantic schemas (PersonCreate, PersonRead)

### 1.3 Routers
- [ ] `api/routers/auth.py` — `POST /auth/login` (PIN → JWT)
- [ ] `api/routers/chores.py` — CRUD + complete + auto-assign
- [ ] `api/routers/people.py` — CRUD + PIN verify + sequence

### 1.4 Tests
- [ ] Add `pytest-asyncio` + `httpx` test client
- [ ] Port route tests from Flask test client → async httpx
- [ ] Add auth tests (login, protected routes, token expiry)

**Deliverable:** `uvicorn api.main:app` returns JSON API. Swagger docs at `/docs`.

---

## Phase 2 — Frontend (React + TypeScript)

**Goal:** Mobile-first family UI. Replaces all Jinja2 templates.

### 2.1 Scaffold
- [ ] `npm create vite@latest frontend -- --template react-ts`
- [ ] Add Tailwind CSS + shadcn/ui
- [ ] Configure React Query + Zustand
- [ ] Set up API client in `frontend/src/api/`
- [ ] Configure Vite proxy (dev) to forward `/api/*` → FastAPI

### 2.2 Pages
- [ ] **Login** — Enter name → 4-digit PIN pad (touch-friendly)
- [ ] **Dashboard** — All chores, who's assigned, overdue highlight
- [ ] **Chore Detail** — Info, mark complete, assigned person
- [ ] **People** — List all family members
- [ ] **Admin Panel** — Add/edit/delete chores and people (admin only)

### 2.3 TypeScript types
- [ ] Mirror all Pydantic schemas as TypeScript interfaces
- [ ] Strict mode enabled in `tsconfig.json`

**Deliverable:** `npm run dev` shows full family UI, login with PIN, view/complete chores.

---

## Phase 3 — Login System

**Goal:** Proper session management with JWT.

### 3.1 Backend
- [ ] `POST /auth/login` — accepts `{ person_id, pin }`, returns JWT
- [ ] JWT payload: `{ sub: person_id, is_admin: bool, exp: ... }`
- [ ] Protected routes require `Authorization: Bearer <token>`
- [ ] Admin-only routes gated behind `is_admin` check

### 3.2 Frontend
- [ ] Login page with PIN pad component (works on phones)
- [ ] JWT stored in `localStorage` (or `httpOnly` cookie for security)
- [ ] Zustand auth store: `{ person, token, login(), logout() }`
- [ ] Route guards: redirect to login if not authenticated
- [ ] Admin-only nav items hidden from regular users

---

## Phase 4 — Chore Reminders

**Goal:** Notify assigned person when their chore is due or overdue.

### 4.1 Due dates + recurrence
- [ ] Add `due_date` (DateTime) to Chore model + migration
- [ ] Add `recurrence` enum to Chore: `none | daily | weekly | monthly`
- [ ] Add `recurrence_day` (optional) for "every Monday" style
- [ ] Service: `complete_chore()` auto-creates next occurrence on completion
- [ ] API: expose `due_date` and `recurrence` in all Chore schemas

### 4.2 Reminder scheduler
- [ ] Add `apscheduler` background task in FastAPI lifespan
- [ ] Check overdue chores every 15 minutes
- [ ] Strategies (in order of complexity):
  1. **In-app badge** — red dot on assigned chore (frontend polls or WebSocket)
  2. **Browser push notification** (Service Worker, no extra infra)
  3. **Email** (optional, needs SMTP config)

### 4.3 Frontend
- [ ] Overdue chores highlighted in red on Dashboard
- [ ] "Due today" section at top of Dashboard
- [ ] Browser notification permission prompt on first login
- [ ] Toast notifications for new reminders

---

## Phase 5 — Real-Time & History

**Goal:** Live updates + audit trail.

### 5.1 WebSocket
- [ ] FastAPI WebSocket endpoint: `WS /ws`
- [ ] Broadcast events: `chore_completed`, `chore_assigned`, `person_added`
- [ ] React: connect on login, update UI live without polling

### 5.2 Chore history
- [ ] New `ChoreHistory` model: `chore_id`, `person_id`, `completed_at`
- [ ] `GET /chores/{id}/history` endpoint
- [ ] History page / timeline view per chore

### 5.3 Leaderboard
- [ ] `GET /stats/leaderboard` — completions per person this week/month
- [ ] Dashboard widget showing top completers

---

## Phase 6 — Polish & Deployment

### 6.1 Docker Compose (full stack)
```yaml
services:
  postgres:       # PostgreSQL 16
  api:            # FastAPI + uvicorn
  frontend:       # Nginx serving built React app
```

### 6.2 Dev ergonomics
- [ ] `Makefile` with: `make dev`, `make test`, `make build`, `make docker`
- [ ] `.env.example` with all required keys documented
- [ ] pre-commit hooks: `ruff` (Python) + `eslint` (TypeScript)
- [ ] GitHub Actions CI: lint + test on every push

### 6.3 Family access
- [ ] Nginx reverse proxy (serves frontend + proxies `/api/` → FastAPI)
- [ ] Optional: Tailscale for secure remote family access

---

## Feature Backlog (Post-Phase 6)

| Feature | Priority | Notes |
|---|---|---|
| Photo proof | Medium | Attach before/after photo to completion |
| Chore templates | Medium | Pre-built chore packs (kitchen, outdoor, etc.) |
| Allowance tracking | Medium | Points → reward system for kids |
| Mobile app (React Native) | Low | Share 90% of TypeScript logic with web |
| Offline mode | Low | PWA with service worker cache |
| Multi-household | Low | Multiple families on one instance |

---

## TypeScript Primer (Quick Reference for Toan)

Since TypeScript is new — the key things you'll use daily:

```typescript
// Types = Python type annotations
interface Chore {
  id: number;
  name: string;
  description: string;
  person_id: number | null;   // Optional FK
  due_date: string | null;    // ISO date string
}

// Functions — always annotate params + return
const fetchChore = async (id: number): Promise<Chore> => {
  const res = await axios.get<Chore>(`/api/chores/${id}`);
  return res.data;
};

// React component — FC = Function Component
const ChoreCard: React.FC<{ chore: Chore }> = ({ chore }) => {
  return <div>{chore.name}</div>;
};

// useState — TypeScript infers the type from initial value
const [chores, setChores] = useState<Chore[]>([]);
```

**Key insight:** TypeScript is just Python type annotations, but for JavaScript. If you understand Python type hints, you'll understand 80% of TypeScript immediately. The rest is just `interface` instead of `class` and `React.FC` syntax.

---

## Migration Strategy

**The existing Flask app keeps running during the refactor.**

Approach:
1. Build FastAPI in `api/` directory alongside `web/flask_app/`
2. Test FastAPI endpoints with Swagger + httpx
3. Build React frontend pointing at FastAPI
4. When frontend is stable, remove `web/` directory and Flask from requirements
5. One clean commit that drops Flask entirely

This gives us a **working app at all times** — no big-bang cutover.

---

## Definition of Done (per phase)

- Phase 1 done when: `uvicorn api.main:app` serves all existing routes as JSON, tests green
- Phase 2 done when: Family can login and view/complete chores on mobile
- Phase 3 done when: Admin/user roles enforced, tokens expire gracefully
- Phase 4 done when: Assigned person sees their due chores with browser notification
- Phase 5 done when: Completing a chore updates all open browsers in real-time
- Phase 6 done when: `docker compose up` gives a production-grade full-stack app
