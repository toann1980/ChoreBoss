# Docker Configuration Audit & Fixes

## Envestero ✅ GOOD

**Current State:**
- ✅ All 4 services have `restart: always`
- ✅ Health checks on postgres (pg_isready) and nginx (wget)
- ✅ Proper depends_on with health conditions
- ✅ Environment variables set correctly
- ✅ Volumes configured for persistence (postgres_data)

**Recommendation:** No changes needed. This is production-ready.

---

## ChoreBoss ❌ NEEDS FIXES

**Current Issues:**
1. ❌ No `restart` policy (will NOT restart after shutdown/crash)
2. ❌ No `container_name` (harder to reference)
3. ❌ No healthcheck (can't verify service is actually working)
4. ❌ Port 8055 exposed but no validation
5. ❌ No explicit `depends_on` (if it has dependencies)

**Recommended Fix:**
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: choreboss-app
    restart: unless-stopped
    ports:
      - "8055:8055"
    env_file:
      - .env
    volumes:
      - .:/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8055/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**What this adds:**
- `restart: unless-stopped` — Auto-restart after crash/reboot, but respects manual stops
- `container_name` — Easy reference (choreboss-app)
- `healthcheck` — Every 30s, curl /health endpoint; fail after 3 misses
- `start_period: 40s` — Grace period before health checks start (app startup time)

---

## Docker Restart Policies (Best Practices)

| Policy | Auto-restart? | On reboot? | On manual stop? | Use case |
|--------|---------------|-----------|-----------------|----------|
| `no` | ❌ Never | ❌ No | ❌ No | Dev, testing |
| `always` | ✅ Yes | ✅ Yes | ❌ No (override) | Production critical services |
| `unless-stopped` | ✅ Yes | ✅ Yes | ✅ Yes (respects stop) | Most services |
| `on-failure` | ✅ If exit code ≠ 0 | ❌ No | ❌ No | Batch jobs, cron tasks |
| `on-failure:5` | ✅ Up to 5 retries | ❌ No | ❌ No | Reliable batch with max retries |

**Recommendation for Envestero & ChoreBoss:** `unless-stopped`
- Auto-restarts after crashes
- Survives reboots
- Respects manual `docker compose stop` (dev-friendly)

---

## Healthcheck Best Practices

**Every container should have:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:PORT/health"]
  interval: 30s           # Check every 30 seconds
  timeout: 10s            # Wait max 10s for response
  retries: 3              # Fail after 3 consecutive failures
  start_period: 40s       # Wait 40s before first check (app startup)
```

**Or for databases:**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U user"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Why it matters:**
- `docker compose up` waits for dependencies with `depends_on: condition: service_healthy`
- Orchestration tools (Kubernetes, Swarm) use health status for scheduling
- Prevents cascading failures (if a service isn't ready, don't send traffic to it)

---

## Summary of Findings

| Service | Restart | Health | Status |
|---------|---------|--------|--------|
| Envestero nginx | ✅ always | ✅ wget | Good |
| Envestero postgres | ✅ always | ✅ pg_isready | Good |
| Envestero api | ✅ always | ❌ None | Missing health |
| Envestero frontend | ✅ always | ❌ None | Missing health |
| ChoreBoss app | ❌ None | ❌ None | **CRITICAL** |

---

## Action Items

1. **Immediate (critical):** Add restart + healthcheck to ChoreBoss
2. **Soon:** Add healthchecks to Envestero api & frontend
3. **Nice-to-have:** Add dependency conditions for healthchecks in Envestero

---

**Documented:** 2026-04-23 02:28 UTC
