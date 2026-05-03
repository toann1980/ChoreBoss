# Development Best Practices

**Shared by:** Nova & Kira  
**For:** All coding projects & deployments  
**Last Updated:** 2026-04-22

---

## 1. URL Architecture (CRITICAL)

**Problem:** Hard-coded URLs break across environments.  
**Solution:** Nginx reverse proxy + relative API paths.

### Pattern

Use **exactly this pattern** for all new full-stack projects:

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"    # ONLY service exposed
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
      - frontend

  api:
    expose:        # NOT ports: — Docker internal only
      - 8000

  frontend:
    expose:        # NOT ports: — Docker internal only
      - 3000
    environment:
      NEXT_PUBLIC_API_URL: /api  # Relative path, no hardcoding
```

```nginx
# nginx.conf
upstream api_backend {
    server api:8000;
}

upstream frontend_backend {
    server frontend:3000;
}

server {
    listen 80 default_server;
    
    location /api/ {
        proxy_pass http://api_backend/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location / {
        proxy_pass http://frontend_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Frontend API Client

```typescript
// lib/api.ts
function getApiUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  return '/api'  // Relative — Nginx handles routing
}

const api = axios.create({
  baseURL: getApiUrl(),
})
```

### Benefits

✅ Same code works on localhost, 10.0.0.81, production.com  
✅ No environment-specific config needed  
✅ Production-standard pattern (Netflix, Google, AWS)  
✅ Easy SSL termination, load balancing  

### Reference

See: `/srv/github/Envestero/URL_RESOLUTION_ARCHITECTURE.md`

---

## 2. Docker Compose Structure

**Always** use this file organization:

```
project/
├── docker-compose.yml
├── nginx.conf
├── backend/
│   ├── Dockerfile
│   ├── .env                    (DATABASE_URL only, no external URLs)
│   └── main.py
├── frontend/
│   ├── Dockerfile
│   ├── lib/api.ts              (Dynamic URL resolution)
│   └── .env.local              (NEXT_PUBLIC_API_URL=/api)
└── README.md                   (One command: docker compose up)
```

### Checklist

- [ ] Nginx service with `ports: "80:80"`
- [ ] API/Frontend use `expose:` NOT `ports:`
- [ ] Frontend env has `NEXT_PUBLIC_API_URL: /api`
- [ ] Backend env has DATABASE_URL (no external URLs)
- [ ] `nginx.conf` routes `/api/*` and `/*`
- [ ] One `docker-compose.yml` that works everywhere

---

## 3. Testing Deployment

**Before considering a project "done":**

### Local Test
```bash
docker compose up --build
# Access: http://localhost
```

### Cross-network Test
```bash
# From another machine on same network
curl http://[YOUR_IP]:80/api/health
curl http://[YOUR_IP]:80/
```

### Verification Steps

```bash
# 1. All services running
docker compose ps

# 2. API responds through Nginx
curl http://localhost/api/health

# 3. Frontend loads through Nginx
curl -I http://localhost/

# 4. API endpoint accessible
curl http://localhost/api/v1/resource/

# 5. Check Nginx logs for routing
docker logs [nginx-container] | tail -20
```

---

## 4. Code Quality Standards

### Type Safety
- **Python:** Type hints on all functions
  ```python
  async def get_data(symbol: str) -> dict[str, Any]:
      """Fetch ticker data."""
  ```
- **TypeScript:** No `any` types, strict mode enabled
  ```typescript
  interface TickerData {
    symbol: string
    price: number
  }
  ```

### Documentation
- Docstrings on all public functions
- README with clear setup instructions
- Architecture diagrams for complex systems

### Testing
- Unit tests for core logic
- Integration tests for API endpoints
- At minimum: smoke tests for critical paths

### Git Commits
- Atomic commits (one logical change)
- Clear message format:
  ```
  [category]: Short description
  
  - Detailed explanation
  - Why this change
  - Related issues
  ```
- Example:
  ```
  feat: Nginx reverse proxy for URL agnostic deployment
  
  - Add Nginx container as single entry point
  - Remove hardcoded URLs from frontend
  - Works on localhost, NUC, and production
  
  Fixes: #42
  ```

---

## 5. Environment & Secrets

**NEVER commit:**
- `.env` files with actual secrets
- Database passwords
- API keys
- Private credentials

**DO:**
- Provide `.env.example` with placeholders
- Document required variables in README
- Use Docker secrets for production
- Rotate keys regularly

### Example `.env.example`
```bash
# Database
DATABASE_URL=postgresql://user:PASSWORD_HERE@postgres:5432/dbname

# API
API_DEBUG=false
API_LOG_LEVEL=info
```

---

## 6. Deployment Checklist

Before pushing to production:

- [ ] All tests passing (`pytest`, `npm test`)
- [ ] Type checking clean (`mypy`, `tsc`)
- [ ] No hardcoded URLs or IPs
- [ ] Environment variables documented
- [ ] Nginx config tested (routes `/api/*` correctly)
- [ ] Frontend can reach API through Nginx
- [ ] Database migrations applied
- [ ] Logs clean (no warnings/errors)
- [ ] Docker images build without warnings
- [ ] Health check endpoints working
- [ ] CORS configured if needed
- [ ] SSL certificate ready (if HTTPS)

---

## 7. Git Workflow

### Branch Strategy
- `main` — Production-ready code
- `development` — Active development
- `feature/xxx` — Feature branches (from `development`)

### Before Merging
```bash
# Run tests
pytest envestero/tests/
npm test

# Type check
mypy envestero/
tsc --noEmit

# Format code
black envestero/
prettier --write frontend/

# Commit & push
git add .
git commit -m "feat: Clear message"
git push origin feature/xxx
```

### Rebase & Merge (preferred)
```bash
git checkout development
git pull origin development
git rebase development feature/xxx
git checkout development
git merge --ff-only feature/xxx
git push origin development
```

---

## 8. Performance & Monitoring

### Logging
- Backend: Structured logging (JSON)
- Frontend: Console + error tracking
- Nginx: Access logs for routing verification

### Health Checks
Every service should expose `/health` or `/status`:

```python
# FastAPI
@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

```typescript
// Next.js
export async function GET() {
  return Response.json({ status: "ok" })
}
```

### Monitoring Indicators
- API response time (<200ms target)
- Database query time (<50ms target)
- Frontend JS bundle size (<500KB target)
- Error rate (<0.5% target)

---

## 9. Common Pitfalls

### ❌ Don't
- Hard-code URLs or IPs (`http://10.0.0.81:8000`)
- Use `localhost` in environment variables
- Mix relative and absolute API paths
- Expose backend services directly (always use Nginx)
- Forget to change `ports` → `expose` in docker-compose
- Commit `.env` files with real secrets

### ✅ Do
- Use relative paths (`/api/endpoint`)
- Use environment variables for configuration
- Document the deployment process
- Test on multiple machines/networks
- Follow the Nginx reverse proxy pattern
- Keep secrets in `.env.local` (gitignored)

---

## 10. Tools & Versions

### Core Stack
- **Backend:** Python 3.12+, FastAPI
- **Frontend:** Node.js 20+, Next.js 14+, TypeScript
- **Database:** PostgreSQL 15+
- **Container:** Docker 25+, Docker Compose 5+
- **Reverse Proxy:** Nginx (Alpine)

### Dev Tools
- **Python:** pytest, mypy, black, ruff
- **TypeScript:** tsc, prettier, eslint
- **Git:** Conventional commits

---

## Reference Projects

- **Envestero:** `/srv/github/Envestero` — Full implementation
  - ✅ Nginx reverse proxy
  - ✅ Dynamic URL resolution
  - ✅ Docker Compose setup
  - ✅ Type-safe code
  - ✅ Testing infrastructure

---

## Quick Start (Use This Template)

```bash
# Create new project from pattern
mkdir my-project
cd my-project

# Copy structure from Envestero
cp -r /srv/github/Envestero/{docker-compose.yml,nginx.conf} .
mkdir -p backend frontend

# Edit docker-compose.yml with your names
# Edit nginx.conf if needed (usually same)

# Start development
docker compose up --build

# Test
curl http://localhost/api/health
```

---

## Questions?

- Envestero example: `/srv/github/Envestero`
- Architecture docs: `/srv/github/Envestero/URL_RESOLUTION_ARCHITECTURE.md`
- Troubleshooting: Check Nginx logs with `docker logs [nginx-container]`

---

**This is the standard. Follow it for every project.**
