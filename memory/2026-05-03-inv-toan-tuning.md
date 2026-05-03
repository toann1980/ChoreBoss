# Session: inv-toan Tuning — 2026-05-03

## Key Decision: Qwen3-30B Excluded from inv-toan

**Model 5 (Qwen3-30B-A3B-Q4_K_M, Port 8024) is TOO LARGE for inv-toan.**

- Requires 20-24GB VRAM (at absolute ceiling of 24GB system)
- Consistently returns 503 Service Unavailable errors
- Extended warmup (40s) and sequential loading don't resolve issues
- **Verdict:** EXCLUDE from future tuning on inv-toan

**Alternative:** Use **Qwen3.6-27B-Claude-Opus-Reasoning-Distilled-Q5_K_M** (Port 8027)
- VRAM: 18-19GB (safe margin)
- Similar reasoning capability
- Documented in OCP registry

---

## Anchor Set Testing Results (2026-05-03)

**Original Run (5 models):**
1. ✅ DeepSeek-Coder-V2-Lite-Q4_K_S (Port 8002) — 100/100, 1.27s
2. ✅ Llama-3.2-MoE-Quad (Port 8011) — 100/100, 933ms (needs brand tuning)
3. ✅ qwen2.5-coder-14b (Port 8022) — 93.3/100, 12.3s (JSON extraction)
4. ⚠️ DeepSeek-R1-Distill (Port 8005) — 20/100 (wrong field parsed)
5. ❌ Qwen3-30B (Port 8024) — 0/100 (503 errors, VRAM exhaustion)

**Corrected Parameters Identified:**

From MODEL_INVENTORY.md:
- Model 2: Should use temp **0.1** (math/logic) and **0.8** (creative), not 0.25
- Model 4: Should parse **`reasoning_content`** field, not `content` (explains 1/5 scores)
- Model 5: Needs **40s warmup + sequential load** (but still won't fit)

**Re-test Planned:**
- Replace Model 5 with Qwen3.6-27B (Port 8027)
- Run Models 1-4 with corrected parameters
- Dual temperature pass for Model 2 (0.1 and 0.8)
- Parse reasoning_content for Model 4

---

## Next Actions

1. Re-run anchor set with corrected parameters
2. Add Qwen3.6-27B to test suite (replaces Qwen3-30B)
3. Phase 2: Token optimization on passing models
4. Create inv-toan performance tiers based on results
