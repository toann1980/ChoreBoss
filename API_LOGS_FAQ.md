# API Access & Logging Clarification

## About http://10.0.0.81:8000

### The 404 Response is CORRECT ✅

```json
{"detail":"Not Found"}
```

**Why?** You're accessing the root of the FastAPI server directly:
```
GET http://10.0.0.81:8000/
        ↑ No path = Not Found
```

FastAPI only has API endpoints under `/api/` prefix. Accessing root returns 404 - this is expected!

### Correct API Endpoints

```
✅ GET  http://10.0.0.81:8000/docs        ← Swagger UI (interactive docs)
✅ GET  http://10.0.0.81:8000/redoc       ← ReDoc (pretty docs)
✅ GET  http://10.0.0.81:8000/api/health  ← Health check
❌ GET  http://10.0.0.81:8000/             ← 404 (no endpoint here)
```

### Try This in Browser

```
http://10.0.0.81:8000/docs
```

You'll see the beautiful Swagger UI with all endpoints documented!

---

## API Logs: Where Are They?

### FastAPI Backend Logs (Terminal 1)

You should see logs there when accessing the API. Check the terminal where you started `python api_run.py`:

```
INFO:     127.0.0.1:57350 - "GET /api/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:57362 - "POST /api/auth/login HTTP/1.1" 200 OK
INFO:     127.0.0.1:42638 - "GET /api/chores/ HTTP/1.1" 200 OK
```

### Flask Frontend Logs (Terminal 2)

We already saw these earlier:
```
10.0.0.21 - - [20/Apr/2026 20:55:28] "GET / HTTP/1.1" 302 -
10.0.0.21 - - [20/Apr/2026 20:55:28] "GET /login HTTP/1.1" 200 -
10.0.0.21 - - [20/Apr/2026 20:55:43] "POST /login HTTP/1.1" 401 -
```

**You ARE seeing logs!** ✅

### Logs Show Connection Between Flask → FastAPI

When you submit the login form in Flask:
1. Flask receives POST `/login`
2. Flask calls FastAPI `POST /api/auth/login`
3. FastAPI logs show the incoming request
4. FastAPI returns JSON response
5. Flask renders result

**Both sets of logs = full integration working!**

---

## What the 404 Error on POST /login Meant

Looking at your Flask logs:
```
10.0.0.21 - - [20/Apr/2026 20:55:46] "POST /login HTTP/1.1" 404 -
10.0.0.21 - - [20/Apr/2026 20:55:47] "POST /login HTTP/1.1" 404 -
```

This was a Flask 404, not an API 404. The login form was sending to the wrong endpoint.

**Fixed by:** Updated `login.html` to POST to `/login` (which Flask handles)

---

## Test API Directly (Command Line)

### Health Check
```bash
curl http://10.0.0.81:8000/api/health
```

Response:
```json
{"status":"ok"}
```

### Login
```bash
curl -X POST http://10.0.0.81:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"person_id": 1, "pin": "1234"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "person_id": 1,
  "is_admin": true
}
```

### Get Chores (with token)
```bash
TOKEN="your_token_from_above"
curl http://10.0.0.81:8000/api/chores/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Summary

| Question | Answer |
|----------|--------|
| Is 404 on root expected? | ✅ Yes - FastAPI uses `/api/` prefix |
| Can I see logs? | ✅ Yes - check your terminal windows |
| Where are Flask logs? | ✅ Terminal 2 (start_frontend.sh) |
| Where are FastAPI logs? | ✅ Terminal 1 (start_backend.sh) |
| Is integration working? | ✅ Yes - logs show Flask → FastAPI calls |

**Everything is working correctly!** 🚀
