# ChoreBoss Deployment Persistence TDD

**Status:** Prep doc
**Purpose:** Define the first tests and implementation targets for a deployment that survives restarts and keeps the latest version explicit.
**Date:** 2026-05-20

## What "persistent webapp" means here

For ChoreBoss, deployment persistence should mean:

1. **Data survives restarts**
   - chores, people, auth data, and migrations remain intact after container restart or recreate

2. **Session behavior is stable**
   - signed auth sessions keep working across app restarts when the secret stays the same
   - sessions intentionally invalidate if the secret changes

3. **Release identity is explicit**
   - the running build reports its version/commit
   - the deployed image is immutable and traceable

4. **Production config is externalized**
   - no hardcoded production URLs or secrets in code
   - runtime config comes from env/secrets

## Current facts

- FastAPI app runs on port `8055`.
- App config already reads `DATABASE_URL` and `SECRET_KEY` from env.
- Session auth already uses `SessionMiddleware`.
- `docker-compose.yml` currently bind-mounts the repo into the app container.
- The DB service already uses a named volume.
- `docker-compose.prod.yml` now exists for image-based production deploys.
- `/api/version` now exposes build identity.

## Recommended deployment shape

### Development
- bind mount the repo
- keep hot reload or local iteration if needed
- okay to use SQLite for quick tests

### Production
- build an immutable image from a commit/tag
- run the image without a repo bind mount
- use `docker-compose.prod.yml` (or equivalent) so the running service is image-based, not source-mounted
- keep only durable volumes for the database and any other intended state
- inject secrets and config from env or secret storage

## TDD checklist

### 1) Restart-safe database state

**Failing test to write first:**
- create a person and a chore
- restart only the app container
- confirm the rows still exist
- restart the DB container with its volume intact
- confirm the rows still exist again

**Acceptance:**
- data survives app restarts
- data survives DB container recreation when the named volume is preserved

### 2) Session continuity contract

**Failing test to write first:**
- log in with a valid person/PIN
- capture the signed session cookie
- restart the app container
- confirm protected routes still work with the cookie

**Acceptance:**
- the same `SECRET_KEY` preserves existing sessions across app restarts
- changing the secret invalidates old sessions as expected

### 3) Config is external, not baked in

**Failing test to write first:**
- start the app with a test env file
- assert `DATABASE_URL`, `SECRET_KEY`, `HOST`, and `PORT` are read from env
- assert no production path depends on the default dev fallback values

**Acceptance:**
- runtime config is controlled externally
- production does not rely on insecure defaults

### 4) Version/build identity is visible

**Failing test to write first:**
- add an endpoint like `/api/version` or `/api/build-info`
- assert it returns the version, commit SHA, or image tag
- assert the value changes when the build changes

**Acceptance:**
- the running app can tell us which release is live
- we can distinguish the latest deployed build from previous ones

### 5) Deployment restart smoke test

**Failing test to write first:**
- bring the stack up
- create or read a known record
- restart the app service
- confirm the health check returns ok
- confirm the record still exists
- confirm login still works

**Acceptance:**
- one clean restart does not break the app
- health, auth, and data all survive

### 6) Migration-on-start safety

**Failing test to write first:**
- start the app against an older schema snapshot
- run migrations
- verify the app comes up and reads the data

**Acceptance:**
- schema upgrades are repeatable
- deployment updates do not require manual DB surgery

## Small implementation sequence

1. Keep the version/build endpoint and wire build metadata through Docker.
2. Add build metadata injection in Docker.
3. Split dev/prod compose behavior if needed.
4. Add restart-persistence tests.
5. Keep a production compose file with immutable image + named DB volume.
6. Update docs so the live deployment recipe is obvious.

## Recommended file targets

- `api/main.py` — version/build route
- `Dockerfile` — build labels or build args
- `docker-compose.yml` — dev behavior
- `docker-compose.prod.yml` — production behavior, if we split it
- `tests/` — restart/session/version smoke tests
- `OCP/ChoreBoss/CURRENT.md` — live state summary

## Exit criteria

- App survives restart without losing data.
- App can identify the running release.
- Production does not rely on bind-mounted source.
- Tests prove the deployment is durable, not just the code.
