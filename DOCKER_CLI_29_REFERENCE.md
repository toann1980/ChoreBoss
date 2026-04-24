# Docker CLI 29.x Reference & Common Issues

**Latest Stable:** Docker Engine 29.4.1 (released 2026-04-20)  
**Documentation:** https://docs.docker.com/engine/release-notes/29/

## Installation

### Ubuntu 24.04
```bash
VERSION_STRING=5:29.4.1-1~ubuntu.24.04~noble
sudo apt install docker-ce=$VERSION_STRING docker-ce-cli=$VERSION_STRING containerd.io docker-buildx-plugin docker-compose-plugin
```

### macOS / Windows
Docker Desktop includes the latest CLI. Check: `docker --version`

---

## Common Docker Compose Issues & Solutions

### Issue: Commands Not Found Inside Container
**Symptom:** `exec: "kill": executable file not found in $PATH`  
**Cause:** Alpine/minimal containers don't have standard Unix utilities  
**Solution:** Use `docker compose restart <service>` to cleanly restart instead of killing processes

### Issue: Docker Compose `-d` (Detach) Behavior
**What `-d` does:** Runs container in background, returns immediately  
**What it doesn't do:** Doesn't keep a shell parent process alive  
**Best practice:** Use `-d` for long-running tasks; don't chain with `&` in bash

**Correct:**
```bash
docker compose exec -d api python long_task.py
# Process runs inside container, detached
```

**Avoid:**
```bash
docker compose exec api python long_task.py &  # Parent shell exits, kills child
```

### Issue: Containers Block on Async Tasks
**Symptom:** Container starts, process runs, but nothing logs  
**Cause:** Process is waiting on an async task (e.g., `await pool.ensure_ready()`)  
**Solution:** 
1. Check if async task is necessary (proxy pool warming during direct-connection backfill = unnecessary)
2. Skip the await if not needed
3. Add logging before/after await to debug

### Issue: Docker Network Permissions in exec
**Symptom:** `OCI runtime exec failed: exec failed: unable to start container process`  
**Cause:** Command doesn't exist in container image OR permission denied  
**Debug:** Check if binary exists: `docker compose exec <service> which <binary>`

---

## Docker Compose Exec Flags

| Flag | Purpose | Example |
|------|---------|---------|
| `-d` | Detach (run in background) | `docker compose exec -d api python task.py` |
| `-T` | Disable pseudo-TTY (for piping) | `docker compose exec -T api python -c "..."` |
| `-e VAR=val` | Set environment variable | `docker compose exec -e DEBUG=1 api bash` |
| `--user user` | Run as specific user | `docker compose exec --user root api apt update` |

---

## Clean Container Restart Pattern

Instead of trying to kill processes:
```bash
# Kill a specific container
docker compose restart api

# Wait for it to be ready
sleep 5

# Verify it's running
docker compose ps

# Check logs
docker compose logs api --tail=50
```

---

## Useful Debugging Commands

```bash
# Top processes in container
docker compose top api

# Check if process exists
docker compose top api | grep backfill

# Clean restart (kills + restarts)
docker compose restart api

# View last N lines of logs
docker compose logs api -n 50

# Follow logs in real-time
docker compose logs api -f --tail=20

# Logs since a specific time
docker compose logs api --since 5m

# Full container rebuild + restart
docker compose down
docker compose up --build -d api postgres
```

---

## Docker 29 Highlights

- **HTTP Keep-Alive:** Improved image pull/push performance (fewer TCP/TLS handshakes)
- **Networking:** Single-stack endpoints now preferred as default gateway when they have higher priority
- **Bug fixes:** Container removal, AppArmor profiles, Swarm reliability
- **Updated dependencies:** Go 1.26.2, BuildKit v0.29.0, containerd v2.2.3

---

## Key Learning for NUC Setup

**Our issues today:**
1. Proxy pool warming (`await pool.ensure_ready()`) was blocking backfill start unnecessarily
2. Docker containers don't have standard shell commands (kill, pkill, etc.)
3. `-d` flag works, but don't assume the parent shell stays alive
4. Network restrictions on NUC gateway mean some operations need to happen inside Docker

**Best pattern for long-running tasks:**
```bash
docker compose exec -d api python -m envestero.cli backfill ...
sleep 5
docker compose logs api | grep "Starting\|Upserted"
# Let it run; check progress periodically with logs
```

No polling, no parent shell needed, clean logs.

---

**Source:** Official Docker documentation v29.4.1 (2026-04-20)  
**Checked:** 2026-04-23 02:16 UTC
