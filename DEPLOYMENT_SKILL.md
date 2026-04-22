# Deployment Architecture Skill

**Shared by:** Nova & Kira  
**Purpose:** Production-standard Docker + Nginx setup for all projects  
**Status:** Battle-tested in Envestero  

## Overview

This skill documents the **permanent solution** for multi-container deployments that work across all environments without code changes.

## Key Principle

> **Frontend doesn't know backend's IP/port. Nginx handles it.**

This means:
- Same code runs on localhost, 10.0.0.81, production.com
- Zero environment-specific configuration
- Production-standard pattern (Netflix, Google, AWS)

## The Pattern

### 1. docker-compose.yml

```yaml
version: '3.8'

services:
  # ONLY service exposed to host
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
      - frontend

  # Internal only
  api:
    build: ./backend
    expose:      # Note: expose, not ports
      - 8000
    environment:
      DATABASE_URL: postgresql://...

  # Internal only
  frontend:
    build: ./frontend
    expose:      # Note: expose, not ports
      - 3000
    environment:
      NEXT_PUBLIC_API_URL: /api  # Relative path

  # Database (if needed)
  postgres:
    image: postgres:15-alpine
    expose:
      - 5432
```

**Critical:** Services use `expose:` NOT `ports:` (except Nginx).

### 2. nginx.conf

```nginx
upstream api_backend {
    server api:8000;
}

upstream frontend_backend {
    server frontend:3000;
}

server {
    listen 80 default_server;
    
    # API routes
    location /api/ {
        proxy_pass http://api_backend/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Frontend
    location / {
        proxy_pass http://frontend_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 3. Frontend API Resolution

```typescript
// lib/api.ts
function getApiUrl(): string {
  // Use env if set, otherwise relative path
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  return '/api'
}

const api = axios.create({
  baseURL: getApiUrl(),
})
```

## How It Works

```
User (any host: localhost, 10.0.0.81, production.com)
  ↓
Nginx (port 80)
  ├─ /api/* → FastAPI (internal)
  └─ /* → Next.js (internal)
```

Same Nginx config, same frontend code, works everywhere.

## Deployment Examples

### localhost
```bash
docker compose up --build
# Access: http://localhost
```

### NUC (10.0.0.81)
```bash
docker compose up --build
# Access: http://10.0.0.81
# Same setup, no code changes
```

### Production
```bash
docker compose up --build
# Access: https://production.com (SSL at Nginx)
# Same setup, no code changes
```

## Testing

```bash
# Is Nginx running?
docker ps | grep nginx

# Does API respond?
curl http://localhost/api/health

# Does frontend load?
curl -I http://localhost/

# Check Nginx logs
docker logs [nginx-container]
```

## Common Issues

### "API not found" (404)
- Check: Is API service running? (`docker ps`)
- Check: Is `api:8000` correct in nginx.conf?
- Check: Nginx logs show routing?

### "CORS errors"
- Add to nginx.conf or FastAPI:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_methods=["*"],
  )
  ```

### "Works on localhost, not on 10.0.0.81"
- Check: Nginx config has `server_name _` (catch-all)
- Check: Nginx listening on `0.0.0.0:80`
- Check: Firewall allows port 80

## Copy This Structure

For every new project:

```
project/
├── docker-compose.yml        ← Copy from Envestero
├── nginx.conf                ← Copy from Envestero
├── backend/
│   └── Dockerfile
└── frontend/
    └── Dockerfile
```

With this pattern, you're guaranteed to work across all environments.

## Reference

- **Full docs:** `/srv/github/Envestero/URL_RESOLUTION_ARCHITECTURE.md`
- **Example:** `/srv/github/Envestero/`
- **Best practices:** `/home/leto/.openclaw/workspace/DEVELOPMENT_BEST_PRACTICES.md`

---

## Summary

**Old way (broken):**
```typescript
const API_URL = "http://10.0.0.81:8000"  // Hard-coded, breaks in production
```

**New way (production):**
```typescript
const API_URL = "/api"  // Relative, Nginx handles routing
```

Use Nginx reverse proxy for every full-stack project. No hardcoded URLs. Problem solved.
