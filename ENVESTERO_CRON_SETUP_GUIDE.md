# Envestero Cron Jobs & llama.cpp Setup Guide

**Status:** ✅ All Envestero crons working | ⚠️ llama-inference requires manual restart

---

## Quick Status Check

```bash
# Check all cron jobs
cron list

# Check embedding service (always running)
systemctl status llama-embedding

# Check inference service
systemctl status llama-inference
```

---

## Envestero Cron Jobs (All Working ✅)

### 1. Daily News Sentiment Collection
- **When:** 2:00 AM PST (9:00 AM UTC)
- **What:** Collects sentiment data from news sources for all watched tickers
- **Status:** ✅ 9 consecutive successful runs
- **Last Run:** 2026-04-29 02:00 PST (13.6 seconds)

### 2. Daily OHLCV Price Data Collection
- **When:** 9:00 PM PST (4:00 AM UTC next day)
- **What:** Fetches daily price bars (OHLCV) after market close
- **Status:** ✅ 9 consecutive successful runs (recently fixed)
- **Last Run:** 2026-04-29 21:00 PST (6.3 seconds)
- **Note:** Previous failures were due to missing dependencies — now resolved

### 3. Memory Promotion (MemoryGraph)
- **When:** 3:00 AM PST (10:00 AM UTC)
- **What:** Promotes short-term memories to long-term MEMORY.md
- **Status:** ✅ Running automatically
- **Last Run:** 2026-04-29 03:00 PST (64.4 seconds)

### 4. Nightly Backup
- **When:** 4:00 AM PST (11:00 AM UTC)
- **What:** Backs up MEMORY.md and identity files to NAS
- **Status:** ✅ Running automatically
- **Last Run:** 2026-04-29 04:00 PST (18.1 seconds)

---

## llama.cpp Models

### Current Status

| Service | Status | Model | Port | GPU | VRAM |
|---------|--------|-------|------|-----|------|
| **llama-embedding** | ✅ RUNNING | nomic-embed-text-v1.5 Q8 | 11434 | Vega M | 20.5M |
| **llama-inference** | ❌ STOPPED | Qwen2.5-7B Q3_K_M | 11435 | Vega M | — |

### llama-embedding ✅ (Embedding Service)

**What it does:**
- Generates 768-dimensional semantic embeddings
- Used by MemoryGraph for lesson clustering
- Used by OpenClaw for chat augmentation
- Running continuously in background

**Verify it's working:**
```bash
curl http://localhost:11434/health
# Should return: {"status":"ok"}

# Test embedding a sentence
curl -X POST http://localhost:11434/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input":"Hello world"}'
```

### llama-inference ⚠️ (Inference Service — Currently Stopped)

**What it does:**
- Runs Qwen2.5-7B model for Envestero AI personas
- Used in backtesting scenarios for trading strategy analysis
- Optional (Envestero has OpenClaw API fallback)

**Why it's stopped:**
- Manually disabled on 2026-04-29 to free VRAM during embedding jobs
- Can be restarted when needed for Envestero backtesting

**To restart (requires elevated permissions):**
```bash
sudo systemctl restart llama-inference

# OR use the provided script:
/home/leto/.openclaw/workspace/restart-llama-inference.sh
```

**Verify it's working:**
```bash
systemctl is-active llama-inference  # Should show "active"

# Test inference endpoint
curl http://localhost:11435/health
```

---

## VRAM Coexistence (Both Models)

Both llama services fit simultaneously in 4GB HBM2:
- **llama-embedding:** 20.5M (batch-size 64)
- **llama-inference:** ~3,800M (batch-size 128 for Envestero)
- **Total:** ~3,820M / 4,096M (93.2% utilization)

If you run both:
1. Embedding starts first (minimal VRAM)
2. Inference starts second (uses remaining VRAM)
3. Both coexist without GTT spillover

---

## Manual Enable llama-inference

If you need the inference service running for Envestero backtesting:

```bash
# Enable auto-start on boot
sudo systemctl enable llama-inference

# Start the service
sudo systemctl start llama-inference

# Verify it started
sudo systemctl status llama-inference

# Check VRAM usage (both services)
watch nvidia-smi  # (if NVIDIA GPU)
# OR
watch -n 1 'ps aux | grep llama'
```

**Note:** Requires `sudo` access. If you don't have it, ask Toan to run the restart command.

---

## Envestero Cron Schedule (PDT)

```
2:00 AM  → Collect daily news sentiment
3:00 AM  → Promote memories to MEMORY.md
4:00 AM  → Backup to NAS
...
9:00 PM  → Collect daily OHLCV price data
```

All jobs have **0 consecutive errors** and are running reliably.

---

## Troubleshooting

### "llama-inference not starting"
1. Check systemd logs: `sudo journalctl -u llama-inference -n 50`
2. Check VRAM: `free -h` and `ps aux | grep llama`
3. Verify model file exists: `ls -lh /srv/github/llama-models/Qwen*.gguf`

### "Envestero cron job failing"
1. Check job status: `cron runs --jobId <id>`
2. View error logs: Check the cron session output
3. Verify dependencies: Test script manually: `python /srv/github/Envestero/envestero/tasks/sentiment_collector.py daily`

### "Embedding slow or not responding"
1. Check if running: `ps aux | grep llama-embedding`
2. Verify port: `netstat -tlnp | grep 11434`
3. Test endpoint: `curl http://localhost:11434/health`

---

## Files Reference

- **Cron jobs config:** OpenClaw cron system (no files, managed via API)
- **llama services:** `/etc/systemd/system/llama-*.service`
- **Models:** `/srv/github/llama-models/`
- **llama.cpp build:** `/srv/github/llama.cpp/build/bin/llama-server`
- **Restart script:** `/home/leto/.openclaw/workspace/restart-llama-inference.sh`
- **Status report:** `/home/leto/.openclaw/workspace/SYSTEM_STATUS_2026_04_30.md`

---

## Summary

✅ **All Envestero cron jobs:** Working perfectly (0 errors)  
✅ **Embedding service:** Live and running  
⚠️ **Inference service:** Stopped (manual restart available)  
🎯 **Recommendation:** Keep embedding active. Restart inference only for Envestero AI personas.

