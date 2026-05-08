OCP — ChoreBoss Current (OWL Mode update)

Timestamp: 2026-05-07 17:55 PDT
Scope: ChoreBoss (Flask UI bridge + FastAPI backend)

Summary
-------
Short: The running ChoreBoss stack is healthy. Key fixes for PIN handling, UI numpad ergonomics, sequence updates, and header layout were implemented and pushed to origin/main. Runtime services (FastAPI on :8055, Flask bridge on :8056) are running and responding to health checks.

Status (live)
-------------
- FastAPI backend: running (http://127.0.0.1:8055/api/health → 200)
- Flask bridge/UI: running (http://127.0.0.1:8056/api/health → 200)
- Git: changes merged to origin/main and pushed.

What I changed (high-level)
---------------------------
- Auth / PIN
  - Normalized login_name at API boundary (case-insensitive lookup) and normalized database login_name values.
  - Verified bcrypt hashing/verification; no PINs are stored in plaintext.
  - Promoted user `dad` to admin on request (DB flag updated).
- UI / UX
  - Increased numpad touch targets & spacing in CSS for mobile ergonomics.
  - Rewrote pin modal JS: uses modal-local storage for PIN, defensive checks, and clearer error messaging.
  - Centralized Back control in header: Back (upper-left) / Home + Logout (upper-right). Removed per-page Back buttons.
  - Fixed Complete Chore flow to redirect/render friendly pages rather than showing raw JSON.
- Backend / Bridge
  - Added POST /people/sequence on FastAPI (admin-only) for bulk sequence updates.
  - Updated Flask bridge to proxy update_sequence and to return consistent JSON shapes.
  - Added logging for auth attempts (non-sensitive) to aid debugging.
- Repo & CI
  - Added scripts/check-back-buttons.sh and a GitHub Actions workflow to prevent reintroduction of page-level Back buttons.
  - Legacy back_home_buttons.html partial is still present and is now explicitly tracked for removal in the baton pass checklist.

Backups
-------
- I created a DB backup before the normalization step (named choreboss.db.bak.*) during the session. If you want it preserved, say so; I can move it to a secure backup location or remove it on request.

Health/Smoke commands
---------------------
- Backend health: curl -s http://127.0.0.1:8055/api/health
- Bridge health: curl -s http://127.0.0.1:8056/api/health
- Restart backend: (in project root) .venv/bin/python run.py  or manage via uvicorn/run:app process
- Restart bridge: FLASK_PORT=8056 API_BASE_URL=http://127.0.0.1:8055/api .venv/bin/python -u flask_bridge.py

Open / Outstanding
------------------
- User reported intermittent "Invalid PIN" earlier: root causes were (a) case-sensitive login lookups (fixed), (b) stale cached JS/CSS and sessions (restart + hard refresh fixed), (c) dad was not an admin originally (promoted on request).
- WebAuthn (FIDO2) biometric auth: TODO — add to backlog. Estimate 2–5 days for an MVP (server endpoints + frontend navigator.credentials flows, HTTPS requirement).
- UX improvements: replace alert() with toast + inline DOM updates for a smoother UX on sequence/complete flows.
- Audit & observability: add event logging for sequence changes, chore completions, and failed auth attempts (do not log sensitive PINs).
- Tests: add unit/integration tests for /people/sequence endpoint and bridge proxy paths; add UI tests for the numpad modal.
- Baton pass: FastAPI-only app shell migration plan is now captured in OCP/ChoreBoss/FASTAPI_BATON_PASS_CHECKLIST.md.

Risks & Mitigations
-------------------
- Risk: accidental reintroduction of page-level Back buttons. Mitigation: CI check added (scripts/check-back-buttons.sh).
- Risk: DB backup exposures. Mitigation: backup files are kept local and not committed; we removed temporary backups/ directory after sweep.
- Risk: unaddressed security advisories on GitHub (Dependabot). Mitigation: separate task to triage dependencies and update vulnerable packages.

Owners & Next Actions
---------------------
- Owner: Toan (primary) — confirm whether to enable WebAuthn next or prioritize audit logs and toasts.
- Next immediate actions (pick from below):
  1. Implement toast-based UX for PIN flows and inline DOM updates (recommended UX chore).
  2. Add audit logging and retention policy for admin actions.
  3. Triage GitHub Dependabot advisories and create PRs to bump deps.
  4. Add automated UI test that asserts header Back/Home/Logout presence and absence of page-level Back.

If you want, I will:
- Start (1) and push a small UX PR replacing alert() with a Bootstrap toast and update the Change Sequence flow to update the list inline, or
- Start (2) and sketch the audit schema + quick logging endpoints.

Log pointers & evidence
-----------------------
- Bridge log: /home/leto/.openclaw/workspace/choreboss-bridge.log
- Backend run: uvicorn run:app (process managed in this environment)
- DB backup (created during session): choreboss.db.bak.* (ask if you want me to locate/remove it)

-- Nova (on behalf of Toan)
