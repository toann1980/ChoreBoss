# Docker + TypeScript/Python Stack Template

This is a production-ready template for new projects. It solves the URL/environment problem **from day one**.

## Key Features

✅ Nginx reverse proxy (single entry point)  
✅ Dynamic URL resolution (works on localhost, staging, production)  
✅ FastAPI backend + Next.js frontend  
✅ PostgreSQL database  
✅ Docker Compose (one command: `docker-compose up --build`)  
✅ No hardcoded URLs  

## File Structure

```
project/
├── docker-compose.yml              # Services: Nginx + API + Frontend + DB
├── nginx.conf                      # Reverse proxy config
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                     # FastAPI app
│   └── .env                        # DB connection (no external URLs)
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── lib/api.ts                  # getApiUrl() helper
│   ├── .env.local                  # (optional) overrides
│   └── app/page.tsx                # Main app
└── README.md
```

## Critical Pattern

### 1. docker-compose.yml

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"  # ONLY service exposed to host
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
      - frontend

  api:
    build: ./backend
    expose:      # NOT ports: — exposed only to Docker network
      - 8000
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/dbname

  frontend:
    build: ./frontend
    expose:      # NOT ports: — exposed only to Docker network
      - 3000
    environment:
      NEXT_PUBLIC_API_URL: /api  # Relative path
```

### 2. nginx.conf

```nginx
upstream api_backend {
    server api:8000;
}

upstream frontend_backend {
    server frontend:3000;
}

server {
    listen 80;

    location /api/ {
        proxy_pass http://api_backend/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://frontend_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. frontend/lib/api.ts

```typescript
function getApiUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  return '/api'
}

const api = axios.create({
  baseURL: getApiUrl(),
})
```

### 4. .env

```bash
# frontend/.env.local (optional overrides)
NEXT_PUBLIC_API_URL=/api

# backend/.env
DATABASE_URL=postgresql://user:password@postgres:5432/dbname
```

## How It Works

1. **User accesses:** `http://localhost` (or `http://10.0.0.81`, `https://production.com`)
2. **Nginx listens on port 80** (single entry point)
3. **Routes based on URL path:**
   - `/api/*` → proxies to FastAPI
   - `/*` → proxies to Next.js
4. **Frontend uses relative paths:** `fetch('/api/data')`
5. **No code changes needed** for different environments

## Deployment Scenarios

### Local
```bash
docker-compose up --build
# Access: http://localhost
```

### Staging (10.0.0.81)
```bash
docker-compose up --build
# Access: http://10.0.0.81
# Same code, same setup, no changes needed
```

### Production (AWS, Heroku, etc.)
```bash
docker-compose up --build
# Access: https://production.com (SSL termination at Nginx)
# Same code, same setup, no changes needed
```

## Why This Pattern?

**Old way (broken):**
```typescript
const API_URL = "http://10.0.0.81:8000"  // ❌ Hard-coded
```

**New way (production):**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "/api"  // ✅ Works everywhere
```

Nginx handles routing. Your code doesn't need to know about backend IPs/ports.

## Getting Started

1. Copy this template to your project directory
2. Replace backend logic (FastAPI endpoints)
3. Replace frontend logic (Next.js pages)
4. Run: `docker-compose up --build`
5. Access: `http://localhost`

That's it. Works on any machine, any environment, no config changes.

---

See `/srv/github/Envestero/URL_RESOLUTION_ARCHITECTURE.md` for the full rationale and examples.
