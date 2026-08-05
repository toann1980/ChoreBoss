# ChoreBoss FastAPI Baton Pass — Route Inventory

Status: Historical migration inventory, retained as a receipt for the baton pass
Last updated: 2026-05-07 21:10 PDT
Owner: Nova / Toan

Goal
- Inventory every browser-facing route that previously lived in `flask_bridge.py`.
- Mark whether the route was a page render, form submit, or API proxy.
- Mark whether FastAPI already owned the backing API behavior.
- Use this as the porting order for the baton pass.

## Current architecture

- FastAPI now owns the browser shell and the JSON API under `/api/*`.
- Flask bridge has been retired from the runtime path.
- This document is preserved as the route-inventory receipt for the migration.

## Flask bridge route inventory

| Route | Type | Current job | FastAPI backing already exists? | Notes |
|---|---|---|---|---|
| `/` | page render | Dashboard shell; loads chores + people | Yes (`GET /api/chores/`, `GET /api/people/`) | Core landing page to port first |
| `/login` | page render + POST | Login screen and login submit | Yes (`POST /api/auth/login`) | Needs FastAPI session/cookie handling |
| `/logout` | redirect | Clear session | Yes (auth/session layer needed) | Replace with FastAPI logout route |
| `/chores` | page render | Chores list | Yes (`GET /api/chores/`) | Straightforward port |
| `/chores/<id>` | page render | Chore detail page | Yes (`GET /api/chores/{id}`, `GET /api/people/{id}`) | Uses related people hydration |
| `/chores/add` | page render + POST | Add chore form | Yes (`POST /api/chores/`) | Admin-only behavior |
| `/chores/<id>/edit` | page render + POST | Edit chore form | Yes (`PUT /api/chores/{id}`) | Admin-only behavior |
| `/chores/<id>/complete` | POST | Complete chore action | Yes (`POST /api/chores/{id}/complete`) | UI currently submits form/AJAX |
| `/chores/<id>/delete` | POST | Delete chore action | Yes (`DELETE /api/chores/{id}`) | Admin-only behavior |
| `/verify_pin` | POST | Bridge-only PIN verification helper | Partially (login API exists) | Likely collapses into FastAPI login/session flow |
| `/people` | page render | People list | Yes (`GET /api/people/`) | Straightforward port |
| `/people/<id>` | page render + POST | Person detail/edit shell | Yes (`GET /api/people/{id}`, `PUT /api/people/{id}`) | Needs careful inspection of UI usage |
| `/people/add` | page render + POST | Add person form | Yes (`POST /api/people/`) | Admin-only behavior |
| `/people/<id>/delete` | POST | Delete person action | Yes (`DELETE /api/people/{id}`) | Admin-only behavior |
| `/people/<id>/edit_pin` | page render + POST | Edit PIN form | Backend support likely in people service/model | Need verify if a dedicated API route exists or must be added |
| `/change_sequence` | page render + POST | Sequence editor page | Yes (`POST /api/people/sequence`) | This is now a supported API path |
| `/update_sequence` | POST | Bridge proxy for sequence update | Yes (`POST /api/people/sequence`) | Can be removed after FastAPI shell cutover |
| `/api/health` | JSON | Bridge health proxy | Yes (`GET /api/health`) | Not needed once bridge is retired |

## FastAPI API inventory already in place

| API route | Status | Notes |
|---|---|---|
| `POST /api/auth/login` | Present | Returns JWT access token and person info |
| `GET /api/chores/` | Present | Auth required |
| `GET /api/chores/{id}` | Present | Auth required |
| `POST /api/chores/` | Present | Admin required |
| `PUT /api/chores/{id}` | Present | Admin required |
| `DELETE /api/chores/{id}` | Present | Admin required |
| `POST /api/chores/{id}/complete` | Present | Auth required |
| `GET /api/people/` | Present | Auth required |
| `GET /api/people/{id}` | Present | Auth required |
| `POST /api/people/` | Present | Admin gating exists in router logic |
| `PUT /api/people/{id}` | Present | Admin required |
| `DELETE /api/people/{id}` | Present | Admin required |
| `POST /api/people/sequence` | Present | Admin required |
| `GET /api/health` | Present | Health check |

## Porting order recommendation

1. `/login` and session handling
2. `/` dashboard shell
3. `/chores` and `/chores/<id>`
4. `/people` and `/people/<id>`
5. chore/person create-edit actions
6. `/change_sequence` and `/update_sequence`
7. `/verify_pin` cleanup and bridge-specific action removal
8. delete `flask_bridge.py` only after parity is proven

## Risks to watch

- Session behavior must be equivalent or better than Flask.
- Any route that currently depends on bridge-side response shaping needs to be re-tested.
- The legacy `/people/<id>/edit_pin` path may need an explicit FastAPI API endpoint if the current UI depends on it.
- Keep the current templates first; do not rewrite the UI into an SPA during this pass.

## Exit criteria

- Browser can hit FastAPI directly for page rendering and actions.
- No browser traffic depends on Flask bridge routes.
- Health, login, dashboard, chore detail, edit, create, sequence, and complete flows all work.
- `flask_bridge.py` is no longer required to run the app.
