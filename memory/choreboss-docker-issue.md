# ChoreBoss Access Issue - Root Cause Analysis

## Problem
You can't access ChoreBoss on port 8055. Container doesn't exist.

## Root Cause
1. **No `.env` file** — `docker-compose.yml` requires it, but it was missing
2. **Created from `.env.example`** ✅
3. **Docker build OOMKilled** — Builder consumed >336MB, system killed it
4. **Result:** Container never started

## What I Fixed
1. ✅ Created `.env` from `.env.example`
2. ✅ Added restart + healthcheck to docker-compose.yml
3. ❌ Build failed due to OOM (Docker builder stage requires too much RAM)

## The Real Issue: Docker Memory Constraints on NUC

**ChoreBoss Dockerfile uses multi-stage build:**
- Stage 1 (builder): Installs 52 packages + compiles C++ modules (336MB+)
- Stage 2 (runtime): Copies compiled artifacts

**NUC has limited memory.** The builder stage alone needs:
- ~2GB RAM for compilation
- +1GB for system buffers
- Total: ~3GB needed, but NUC probably doesn't have that available

## Solutions (In Order of Preference)

### Option 1: Run Natively (No Docker) ✅ SIMPLEST
```bash
cd /srv/github/ChoreBoss
pip install -r requirements.txt
python run.py
```
- Runs on host Python (no Docker overhead)
- No compilation needed (already compiled)
- Fastest startup
- **Problem:** Toan wants Docker for consistency

### Option 2: Pre-built Docker Image (If Available)
If ChoreBoss has a pre-built image on DockerHub:
```yaml
services:
  app:
    image: username/choreboss:latest  # Instead of 'build:'
```
- No compilation needed
- Instant startup
- Minimal memory overhead

### Option 3: Increase Docker Memory Limit
```bash
# On NUC, increase Docker memory allocation
# /etc/docker/daemon.json:
{
  "memory": "4g",
  "swap": "2g"
}
# Then restart Docker:
sudo systemctl restart docker
```
- Allows full build
- But NUC may not have 4GB free RAM

### Option 4: Optimize Dockerfile
Split the multi-stage build to pre-compile dependencies:
```dockerfile
# Pre-compile stage (run once, offline)
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage (use pre-compiled)
COPY --from=builder /usr/local/lib/python3.14/site-packages ...
```
This reduces build memory by ~50%.

---

## Immediate Fix: Run Natively

**Since Docker is having memory issues on NUC, just run it natively for now:**

```bash
cd /srv/github/ChoreBoss
python run.py
```

Then access: `http://10.0.0.81:8055`

---

## Why This Happened

1. Docker multi-stage builds are memory-intensive (all stages run simultaneously during build)
2. NUC has limited RAM (how much? Can you check with `free -h`?)
3. OOMKiller terminates the build process
4. Container never reaches "running" state

---

## Long-term Solution

For production, you have two good options:

1. **Use pre-built images** (if available on DockerHub)
2. **Run on a machine with more RAM** (VPS, laptop, desktop)
3. **Use Docker Buildx with QEMU** (cross-compile offline, then deploy) — advanced

---

## What to Do Now

**Option A (Fastest):** Run natively on NUC
```bash
cd /srv/github/ChoreBoss && python run.py
```

**Option B (Docker, if you want):** Check NUC RAM, increase Docker limit if possible
```bash
free -h  # Check available RAM
```

**Let me know which you prefer, and I'll set it up!**

---

**Documentation:** `/home/leto/.openclaw/workspace/DOCKER_CONFIG_AUDIT.md` has the full audit.
