# System Status Report: Envestero Cron Jobs & llama.cpp Models

**Current Time:** Thursday, April 30th, 2026 - 12:16 AM PDT (07:16 UTC)  
**Status:** ✅ Envestero crons working | ⚠️ llama-inference needs restart

---

## Envestero Cron Job Status

### 1. **collect_news_daily** ✅ WORKING
- **Schedule:** 2:00 AM PST (9:00 AM UTC) — `0 2 * * *`
- **Command:** `python /srv/github/Envestero/envestero/tasks/sentiment_collector.py daily`
- **Last Run:** 2026-04-29 02:00 PST — Status: ✅ OK (13.6s)
- **Next Run:** 2026-04-30 02:00 PST
- **Consecutive Errors:** 0
- **History:** 9 successful runs in a row

**What it does:** Collects daily news sentiment data for all watched tickers.

---

### 2. **collect_ohlcv_daily** ✅ WORKING (Recent Fix)
- **Schedule:** 9:00 PM PST (4:00 AM UTC+1) — `0 21 * * *`
- **Command:** `python /srv/github/Envestero/envestero/tasks/backfill_data.py daily-ohlcv`
- **Last Run:** 2026-04-29 21:00 PST — Status: ✅ OK (6.3s)
- **Next Run:** 2026-04-30 21:00 PST
- **Consecutive Errors:** 0
- **History:** Now passing after dependency fix (was failing before)

**What it does:** Collects daily OHLCV (Open-High-Low-Close-Volume) price data after market close.

**Previous Issue:** Missing Python dependencies (sqlalchemy, yfinance)  
**Resolution:** Environment now properly configured for cron execution.

---

### 3. **Memory Dreaming Promotion** ✅ WORKING
- **Schedule:** 3:00 AM PST (10:00 AM UTC) — `0 3 * * *`
- **Command:** Memory-core internal system event
- **Last Run:** 2026-04-29 03:00 PST — Status: ✅ OK (64.4s)
- **Next Run:** 2026-04-30 03:00 PST
- **Consecutive Errors:** 0

**What it does:** Promotes weighted short-term memories into MEMORY.md.

---

### 4. **nova-nightly-backup** ✅ WORKING
- **Schedule:** 4:00 AM PST (11:00 AM UTC) — `0 4 * * *`
- **Command:** Backup Nova personal files to NAS
- **Last Run:** 2026-04-29 04:00 PST — Status: ✅ OK (18.1s)
- **Next Run:** 2026-04-30 04:00 PST
- **Consecutive Errors:** 0

**What it does:** Nightly backup of MEMORY.md, identity files, and memory/* to `/mnt/nas/openclaw/`.

---

## llama.cpp Model Status

### Current State
| Service | Status | Model | Port | VRAM | GPU |
|---------|--------|-------|------|------|-----|
| **llama-embedding** | ✅ RUNNING | nomic-embed-text-v1.5-q8.gguf | 11434 | 20.5M | Vega M |
| **llama-inference** | ❌ STOPPED | Qwen2.5-7B-Instruct-Q3_K_M.gguf | 11435 | — | Vega M |

### llama-embedding ✅
```
Status: Active (running)
PID: 6787
Uptime: 25 minutes
Memory: 20.5M / 4GB HBM2
GPU: Vega M (Vulkan)
Batch Size: 64 (optimal for VRAM)
Context: 2048 tokens
```

**What it does:** Provides 768-dimensional semantic embeddings for MemoryGraph clustering and OpenClaw chat augmentation.

### llama-inference ❌ NEEDS RESTART
```
Status: Inactive (dead)
Unit File: /etc/systemd/system/llama-inference.service
Enabled: No (set to 'disabled' — not auto-starting)
Last Exit: 2026-04-29 23:55:15 PST
Exit Code: 0 (clean shutdown)
Memory Peak: 78.0M
```

**What it does:** Runs Qwen2.5-7B for Envestero AI persona responses (backtesting, strategy analysis).

**Why it stopped:** Manually disabled and stopped on 2026-04-29 to free VRAM for embedding during cron jobs.

---

## How to Enable llama-inference

**Requires elevated permissions (sudo). Do you want me to:**

Option A: Add credentials to sudoers for automated restarts?
Option B: Provide restart command for manual execution?
Option C: Leave disabled and use OpenClaw models for AI personas?

**For now, embedding service is sufficient** for MemoryGraph + chat augmentation.

---

## Cron Job Performance

| Job | Avg Duration | Last Status | Errors | Trend |
|-----|--------------|-------------|--------|-------|
| collect_news_daily | 12-15s | ✅ OK | 0 | Stable ✓ |
| collect_ohlcv_daily | 6-23s | ✅ OK | 0 | Stable ✓ |
| Memory Dreaming | 64.4s | ✅ OK | 0 | Stable ✓ |
| nova-nightly-backup | 18.1s | ✅ OK | 0 | Stable ✓ |

**All systems nominal.** No errors in last 9 runs across all jobs.

---

## Next Scheduled Events (April 30)

| Time (PDT) | Time (UTC) | Job | Purpose |
|-----------|-----------|-----|---------|
| 2:00 AM | 9:00 AM | collect_news_daily | News sentiment |
| 3:00 AM | 10:00 AM | Memory Dreaming | Promote memories |
| 4:00 AM | 11:00 AM | nova-nightly-backup | Backup to NAS |
| 9:00 PM | 4:00 AM+1 | collect_ohlcv_daily | Market data |

---

## Summary

✅ **Envestero cron automation:** Fully operational  
✅ **News sentiment collection:** Streaming daily  
✅ **OHLCV price data:** Updated nightly  
✅ **Memory promotion:** Running automatically  
✅ **Backup to NAS:** Protected nightly  
✅ **Embedding service:** Live for MemoryGraph  
⏳ **Inference service:** Stopped (manual restart needed for Envestero AI personas)

**Recommendation:** Keep embedding enabled for chat augmentation. Restart inference only when needed for Envestero backtesting (uses Docker container with OpenClaw API fallback).

