# ChoreBoss FastAPI Baton Pass Checklist

Status: Draft
Owner: Nova / Toan
Last updated: 2026-05-07 21:08 PDT

Goal
- Remove the Flask bridge as the app shell.
- Serve the HTML UI directly from FastAPI.
- Keep the existing Jinja templates where possible.
- Preserve the current user flows, but make FastAPI the only runtime that matters.

Current reality
- FastAPI already owns the API under `/api/*`.
- Flask bridge currently serves the HTML pages and proxies browser actions to FastAPI.
- The bridge still contains some app-shell behavior that should not survive the baton pass.

Recommended target architecture
- FastAPI serves:
  - API routes under `/api/*`
  - HTML pages using Jinja2Templates
  - static assets via StaticFiles
  - auth/session state via FastAPI-compatible session handling
- Flask bridge is retired after parity is verified.

Phase 0 — Verify the current contract
- [x] List every route currently served by `flask_bridge.py`.
- [x] Group routes into:
  - [x] page render routes
  - [x] form submit / AJAX proxy routes
  - [x] auth/session routes
  - [x] pure API passthrough routes
- [x] Identify which routes are still required by the UI.
- [x] Record any Flask-specific behavior that the UI accidentally depends on.
- [x] Confirm the backend API endpoints already exist or note the missing ones.
- [x] Capture the exact inventory in `OCP/ChoreBoss/FASTAPI_ROUTE_INVENTORY.md`.

Phase 1 — Move the app shell into FastAPI
- [x] Add Jinja2Templates to the FastAPI app.
- [x] Mount static files in FastAPI.
- [x] Create HTML routes in FastAPI for the current dashboard and chore/person flows.
- [x] Port the login/logout flow into FastAPI.
- [x] Port the current page rendering helpers from the bridge.
- [x] Keep the existing templates initially; do not rewrite the UI yet unless necessary.
- [x] Start with: `/login`, `/`, `/chores`, `/chores/<id>`, `/people`, `/people/<id>`.
- [x] Smoke-tested page rendering after switching to FastAPI.

Phase 2 — Replace Flask session behavior
- [x] Pick the FastAPI session strategy.
  - [x] Preferred: signed session cookie via Starlette SessionMiddleware.
  - [ ] Optional later: separate secure token cookie or server-backed session store.
- [x] Make login set the session state in FastAPI.
- [x] Make protected page routes read the FastAPI session state.
- [x] Make the UI no longer depend on Flask session semantics.
- [x] Confirm auth still works after a hard refresh and a new browser session.
- [x] Verified login + session cookie with curl smoke test.

Phase 3 — Port bridge-only actions
- [x] Move the sequence update flow into FastAPI.
- [x] Move chore complete / update / assign flows into FastAPI handlers if they still go through the bridge.
- [x] Preserve the current response shapes until the frontend is fully aligned.
- [x] Normalize any remaining response-shape mismatches.
- [x] Remove any bridge-only form translation logic.
- [x] Verified `verify_pin`, `update_sequence`, and page renders against the FastAPI shell.

Phase 4 — Verify parity before cutover
- [x] Login flow works.
- [x] Dashboard loads chores and people.
- [x] Chore detail page works.
- [x] Change sequence works.
- [x] Add/edit chore works.
- [x] Add/edit person works.
- [x] PIN modal flows work.
- [x] Auth failures are clear and do not expose secrets.
- [x] Health endpoints remain green.
- [x] Confirmed with live curl smoke tests against port 8055.

Phase 5 — Remove the Flask bridge
- [x] Stop routing browser traffic through Flask.
- [x] Update start scripts to launch FastAPI only.
- [x] Delete or archive `flask_bridge.py` once no longer needed.
- [x] Remove or rewrite any bridge-specific docs.
- [x] Update `CURRENT.md` to reflect the new single-runtime architecture.
- [x] Update memory notes with the migration outcome.

Verification gates
- [ ] Run a manual smoke test on a fresh browser session.
- [ ] Run at least one full chore flow end-to-end.
- [ ] Verify the network tab shows FastAPI responses directly, not bridge proxies.
- [ ] Confirm `/api/health` is still OK.
- [ ] Confirm no pages depend on Flask-only behaviors.

Stop conditions
- [ ] Do not remove the bridge until parity is proven.
- [ ] Do not rewrite the frontend into a SPA during this pass.
- [ ] Do not introduce Redis unless a real need appears.

Notes
- This is a baton pass, not a rewrite.
- Keep the templates first; simplify the runtime first.
- After the cutover, we can decide whether the UI should stay Jinja-based or become a SPA later.
