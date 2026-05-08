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
- [ ] List every route currently served by `flask_bridge.py`.
- [ ] Group routes into:
  - [ ] page render routes
  - [ ] form submit / AJAX proxy routes
  - [ ] auth/session routes
  - [ ] pure API passthrough routes
- [ ] Identify which routes are still required by the UI.
- [ ] Record any Flask-specific behavior that the UI accidentally depends on.
- [ ] Confirm the backend API endpoints already exist or note the missing ones.

Phase 1 — Move the app shell into FastAPI
- [ ] Add Jinja2Templates to the FastAPI app.
- [ ] Mount static files in FastAPI.
- [ ] Create HTML routes in FastAPI for the current dashboard and chore/person flows.
- [ ] Port the login/logout flow into FastAPI.
- [ ] Port the current page rendering helpers from the bridge.
- [ ] Keep the existing templates initially; do not rewrite the UI yet unless necessary.

Phase 2 — Replace Flask session behavior
- [ ] Pick the FastAPI session strategy.
  - [ ] Preferred: signed session cookie via Starlette SessionMiddleware.
  - [ ] Optional later: separate secure token cookie or server-backed session store.
- [ ] Make login set the session state in FastAPI.
- [ ] Make protected page routes read the FastAPI session state.
- [ ] Make the UI no longer depend on Flask session semantics.
- [ ] Confirm auth still works after a hard refresh and a new browser session.

Phase 3 — Port bridge-only actions
- [ ] Move the sequence update flow into FastAPI.
- [ ] Move chore complete / update / assign flows into FastAPI handlers if they still go through the bridge.
- [ ] Preserve the current response shapes until the frontend is fully aligned.
- [ ] Normalize any remaining response-shape mismatches.
- [ ] Remove any bridge-only form translation logic.

Phase 4 — Verify parity before cutover
- [ ] Login flow works.
- [ ] Dashboard loads chores and people.
- [ ] Chore detail page works.
- [ ] Change sequence works.
- [ ] Add/edit chore works.
- [ ] Add/edit person works.
- [ ] PIN modal flows work.
- [ ] Auth failures are clear and do not expose secrets.
- [ ] Health endpoints remain green.

Phase 5 — Remove the Flask bridge
- [ ] Stop routing browser traffic through Flask.
- [ ] Update start scripts to launch FastAPI only.
- [ ] Delete or archive `flask_bridge.py` once no longer needed.
- [ ] Remove or rewrite any bridge-specific docs.
- [ ] Update `CURRENT.md` to reflect the new single-runtime architecture.
- [ ] Update memory notes with the migration outcome.

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
