# OPERATIONAL GUIDELINES - 2026-04-21

## 1. PORT MANAGEMENT

**Current Allocation:**
- 3000 → Envestero Frontend (Next.js)
- 5432 → Envestero Database (PostgreSQL)
- 8000 → Envestero Backend (FastAPI)
- 18789 → OpenClaw Gateway
- 18791 → OpenClaw Internal

**Registry Location:** `/srv/github/PORT_REGISTRY.md`

**Before deploying new service:**
1. Check PORT_REGISTRY.md
2. Reserve ports in new project range
3. Update registry immediately
4. Test for conflicts: `lsof -i :PORT`

**Port Ranges by Project:**
- Envestero: 3000-5999 ✅ (3000, 5432, 8000 in use)
- ChoreBoss: 6000-6999
- BlendCraft: 7000-7999
- ImageForge3D: 8100-8199 (avoid 8000-8099)
- HouseHunter: 9000-9999

---

## 2. DOCKER DNS & SECURITY

**Current Status:**
- DNS: Added to docker-compose.yml (8.8.8.8, 8.8.4.4)
- Security: Default (functional, not hardened)
- Access: Ports 3000, 8000 open; 5432 open (consider restricting)

**Recommended Changes (Optional):**

Option A: Restrict Database Port
```yaml
# docker-compose.yml
postgres:
  ports:
    - "127.0.0.1:5432:5432"  # Only localhost access
```

Option B: Network Isolation
```yaml
networks:
  backend:    # API ↔ Database only
  frontend:   # Frontend ↔ API only
```

**Documentation:** `/srv/github/DOCKER_DNS_SECURITY.md`

---

## 3. LEARNING METHODOLOGY

**Four Issues Fixed & Patterns:**

1. **DNS Timeout (Network Isolation)**
   - Container sandboxing blocks external DNS by default
   - Solution: Explicit DNS config or build locally
   - Applies to: Any Docker build needing npm/pip/git

2. **Missing tsconfig.json (Config Discovery)**
   - Path aliases need explicit configuration
   - Solution: Add tsconfig with baseUrl + paths
   - Applies to: TypeScript, Next.js, Webpack builds

3. **SWC Binary Mismatch (OS Compatibility)**
   - Native binaries are glibc/musl specific
   - Solution: Pre-compile on host or use pure JS
   - Applies to: Node.js native modules, Python extensions

4. **Command Override (Precedence)**
   - docker-compose.yml commands override Dockerfile
   - Solution: Document overrides, use Dockerfile defaults
   - Applies to: Any multi-layer build system

**Pattern Recognition Checklist:**
- [ ] Can reproduce locally?
- [ ] Isolate build vs runtime issue
- [ ] Check configuration hierarchy
- [ ] Document why this approach
- [ ] Test doesn't break other things

**Documentation:** `/srv/github/LEARNING_FROM_FIXES.md`

---

## 4. NUC SYSTEM SPECS (For Future Troubleshooting)

**Hardware:**
- CPU: Intel x86_64, 8 cores
- RAM: 31 GB available
- Storage: 421 GB free (NVMe)
- IP: 10.0.0.81/24 (WiFi)

**Tools Available:**
- Python 3.11-3.14 (3.12 in venv)
- Node.js v22.22.2, npm 10.9.7
- Docker 29.4.1, Compose v5.1.3
- Git, gcc, make, curl, wget

**Full Inventory:** `/srv/memory-sync/NUC_SPECS.md`

---

## 5. DEPLOYMENT CHECKLIST

Before deploying new service:

- [ ] Port allocated and added to PORT_REGISTRY.md
- [ ] Dockerfile doesn't rely on external network (or DNS added)
- [ ] tsconfig.json exists for TypeScript projects
- [ ] docker-compose overrides documented
- [ ] Security implications reviewed
- [ ] Logs configured (max-size, max-file)
- [ ] Health checks defined
- [ ] Tested on host first, then container

---

## 6. QUICK REFERENCE

**Check running services:**
```bash
docker compose ps
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

**Check ports:**
```bash
lsof -i :8000
netstat -tlnp | grep LISTEN
```

**Test DNS:**
```bash
docker run --rm alpine:latest nslookup registry.npmjs.org
```

**View logs:**
```bash
docker logs -f envestero-api
docker compose logs -f frontend
```

**Restart services:**
```bash
docker compose down && docker compose up -d
docker compose restart api
```

**Remove old images:**
```bash
docker image prune -a
docker system prune -a
```

---

**Last Updated:** 2026-04-21 16:10 UTC  
**By:** Nova ✨  
**Status:** Operational, documented, ready for future projects
