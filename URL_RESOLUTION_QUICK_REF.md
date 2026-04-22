# Quick Reference: URL Resolution Pattern

## What Changed (Commit 7df41742)

| Component | Before | After | Why |
|-----------|--------|-------|-----|
| **Frontend Port** | 3000 (exposed) | 3000 (internal) | Nginx is the only entry point |
| **API Port** | 8000 (exposed) | 8000 (internal) | Nginx is the only entry point |
| **Nginx Port** | None | 80 (exposed) | Single gateway for all traffic |
| **API URL in Frontend** | `http://10.0.0.81:8000` | `/api` | Relative path works everywhere |

## How to Use

### Deploy
```bash
cd /srv/github/Envestero
docker-compose up --build
```

### Access
- **Local:** http://localhost
- **NUC:** http://10.0.0.81
- **Anywhere:** Same URL pattern, works without changes

### Verify
```bash
# Check Nginx is routing
curl http://10.0.0.81/api/health

# Check frontend loads
curl http://10.0.0.81/
```

## Files to Understand

1. **docker-compose.yml** — Service definitions (Nginx + API + Frontend)
2. **nginx.conf** — Routing rules (main magic)
3. **frontend/lib/api.ts** — Dynamic URL resolution (the key)

## For New Projects

Copy this pattern:
1. `docker-compose.yml` with Nginx service (port 80 only)
2. `nginx.conf` with upstream servers
3. Frontend: `NEXT_PUBLIC_API_URL=/api` (relative path)
4. Backend: No knowledge of external URLs

See `DOCKER_FULLSTACK_TEMPLATE.md` for ready-to-use boilerplate.

## Key Principle

**Frontend doesn't know backend's IP/port. Nginx handles it.**

This solves:
- ✅ Different machines (localhost, 10.0.0.81, production.com)
- ✅ Different environments (dev, staging, prod)
- ✅ Easy SSL termination (Nginx only)
- ✅ Load balancing (add more API instances)

---

**Production-ready. No more hardcoded URLs.**
