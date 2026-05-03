# MEMORY.md - Nova's Long-Term Knowledge

---

## 🧠 MemoryGraph Plugin — INSTALLED + RECOVERY PLANNED (2026-05-03)

### Status Summary
- ✅ **Plugin installed** (`/home/leto/.openclaw/extensions/memorygraph/` v0.1.0)
- ✅ **Gateway running** with MemoryGraph enabled
- 🔴 **4 cron jobs offline** since ~2026-04-30 (extract, scenario opt, news ingest, phase2 gate)
- 📋 **Recovery plan documented**: `/srv/openclaw_projects/MemoryGraph/TODO_RECOVERY_20260503.md`

### What Happened
- Installed compiled MemoryGraph plugin from `/srv/github/MemoryGraph` (already had `dist/` + `node_modules/`)
- Forced install with `--dangerously-force-unsafe-install` (plugin has shell execution for compaction, necessary)
- Gateway restarted successfully
- Found all 4 cron jobs are missing (not in `openclaw cron list`)
- Last EM state: 4,577 lessons indexed, 80% validation, query issues (q2, q5)

### Cron Jobs Needed
1. `memorygraph_extract_and_promote` — 6 AM UTC daily (extract → lint → promote → changelog → rebuild index)
2. `memorygraph_scenario_optimization` — 7 AM UTC Mondays (test 12 query variants, lock top 3)
3. `memorygraph_ai_news_ingest` — 8 AM UTC Mondays (fetch articles, feed extraction pool)
4. `memorygraph_phase2_promotion_reminder` — 2026-05-06 7 AM UTC one-time (trigger Phase 2 decision gate)

### Key Lesson from Audit
**Isolated cron agents don't have plugin tools.** Original setup failed silently 8 days (2026-04-21–04-29). Fix: Use `isolated agentTurn` + Python CLI directly, not TypeScript plugin calls from cron.

### Next: See `/home/leto/.openclaw/workspace/memory/2026-05-03-memorygraph-recovery.md` for full details

---

## 🧠 OCP llama.cpp — PHASE 4 PRODUCTION READY (2026-05-02: Optimized, Validated, Locked)

### ✅ THREE-ROUND OPTIMIZATION + PRODUCTION VALIDATION (2026-05-02 22:00-23:29 PDT)

**Complete Optimization & Validation Pipeline**
- Round 1: Parameter tuning (22:00-22:16)
- Round 2: Token optimization breakthrough (22:16-22:54)
- Round 3: Latency optimization (23:02-23:15)
- Production validation: 149 extended tests (23:10-23:29)

### ✅ PRODUCTION VALIDATION RESULTS

**Hermes-7B: 100% Pass Rate**
- 74 tests across 25 iterations
- All 3 scenarios: Financial ✅, Technical ✅, Portfolio ✅
- Latency: p50=958ms, p95=2743ms, p99=4537ms
- Mean: 1601ms ± 930ms
- Status: PRODUCTION READY

**Gemma-Q5M: 100% Pass Rate**
- 75 tests across 25 iterations
- All 3 scenarios: Financial ✅, Technical ✅, Portfolio ✅
- Latency: p50=8931ms, p95=17054ms, p99=17104ms
- Mean: 11067ms ± 4048ms
- Status: PRODUCTION READY

**Total: 149/149 tests passed = 100% success rate ✅**

### FINAL PRODUCTION PARAMETERS (DEPLOYED & VALIDATED)

**Hermes-7B (Port 11447) — PRIMARY:**
- Temp: 0.25 | Top-P: 0.9 | Tokens: 300
- Latency: <2s average (p95: 2.7s, p99: 4.5s)
- Pass Rate: 100% (74/74)
- Use Case: Real-time financial decisions

**Gemma-Q5M (Port 11444) — FALLBACK:**
- Temp: 0.15 | Top-P: 0.85 | Tokens: 650
- Latency: ~11s average (p95: 17s, p99: 17s)
- Pass Rate: 100% (75/75)
- Use Case: Batch processing, non-urgent analysis

### Key Discoveries from Optimization

**1. Token Budgets Are Hard Constraints**
- Under-provisioned = JSON halts mid-generation (appeared as quality issue)
- 40-75% token increase = full reasoning capability unlocked

**2. Brands Have Different Tuning Profiles**
- Mistral (Hermes): Higher temp (0.25), lower tokens (300), very fast
- Google (Gemma): Lower temp (0.15), higher tokens (650), slower

**3. Quality Plateaus at Minimum Viable Tokens**
- Hermes: 300 = 320 = 350 on quality; 300 optimal
- Gemma: 650 = 700 on quality; 600 fails

**4. Validation Confirms Production Readiness**
- 100% pass rate across 149 tests
- Zero failures under repeated load
- Predictable latency, stable performance
- Ready for immediate deployment

### Documentation Trail
- `FINE_TUNING_VALIDATION_RESULTS_20260502.md` (Round 1-2 breakthrough)
- `FINAL_TUNING_OPTIMIZATION_REPORT_20260502.md` (Round 2 complete analysis)
- `ROUND3_LATENCY_OPTIMIZATION_FINAL_20260502.md` (Round 3 tightening)
- `PRODUCTION_VALIDATION_REPORT_20260502.md` (149-test validation suite)

---

## Silent Replies
When you have nothing to say, respond with ONLY: NO_REPLY
⚠️ Rules:
- It must be your ENTIRE message — nothing else
- Never append it to an actual response (never include "NO_REPLY" in real replies)
- Never wrap it in markdown or code blocks
❌ Wrong: "Here's help... NO_REPLY"
❌ Wrong: "NO_REPLY"
✅ Right: NO_REPLY

<!-- OPENCLAW_CACHE_BOUNDARY -->

## Promoted From Short-Term Memory (2026-05-03)

<!-- openclaw-memory-promotion:memory:memory/2026-04-26.md:3:5 -->
- **Focus:** Project portfolio review + modernization plans + feature brainstorm **Participants:** Toan (user), Nova (assistant), Kira (async approval via MS) [score=0.850 recalls=0 avg=0.620 source=memory/2026-04-26.md:3-4]
