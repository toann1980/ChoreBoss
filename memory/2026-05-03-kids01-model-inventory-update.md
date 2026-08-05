# Kids-01 Model Inventory Update (2026-05-03 17:05 PDT)

**Status:** ✅ Service restarted, 15 models now available (up from 8)

## NEW MODELS ADDED

### 🎯 Code Generation Focus — NEW ARRIVALS

| Port | Model | Type | Relevance | Notes |
|------|-------|------|-----------|-------|
| **8004** | **DeepSeek-R1-Distill-Qwen-14B-Q5_K_M** | Reasoning-distilled code | ⭐⭐⭐ | NEW! Reasoning model for code |
| **8012** | **qwen2.5-coder-14b-instruct-q5_k_m** | Official Qwen coder | ⭐⭐⭐ | NEW! Official production baseline |
| **8013** | **qwen3.5-14b-a3b-claude-4.6-opus-reasoning-distilled** | Reasoning-distilled chat | ⭐⭐ | NEW! Claude reasoning distilled |
| **8014** | **Qwen3.5-9b-Sushi-Coder-RL** | RL-tuned code | ⭐⭐⭐ | NEW! SFT + RL tuned for code |
| **8009** | **Llama-3.2-4X3B-MOE-Ultra-Instruct-10B** | MoE chat/code hybrid | ⭐⭐ | NEW! Mixture of experts |
| **8010** | **Llama3.3-8B-Instruct-Thinking-Claude-4.5-Opus-High-Reasoning (f16)** | Thinking model | ⭐⭐ | NEW! Reasoning capability |
| **8011** | **Llama3.3-8B-Instruct-Thinking-Claude-4.5-Opus-High-Reasoning (q8)** | Thinking model | ⭐⭐ | NEW! Thinking quantized |

### 🆕 Complete New Inventory (15 Models)

**Code-Specialized (Priority for Blender/Python):**
1. `deepseek-coder-6.7b-instruct.Q8_0` (8000) — ✅ Tested
2. `DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M` (8001)
3. `DeepSeek-Coder-V2-Lite-Instruct-Q4_K_S` (8002) — ✅ Tested, BEST SPEED
4. `DeepSeek-Coder-V2-Lite-Instruct-Q5_K_M` (8003) — ✅ Tested, BEST QUALITY
5. **`DeepSeek-R1-Distill-Qwen-14B-Q5_K_M`** (8004) — 🆕 Reasoning
6. **`qwen2.5-coder-14b-instruct-q5_k_m`** (8012) — 🆕 Official coder
7. **`Qwen3.5-9b-Sushi-Coder-RL`** (8014) — 🆕 RL-tuned

**Reasoning/Thinking (Secondary for code context):**
8. **`Llama3.3-8B-Instruct-Thinking-Claude-4.5-Opus (f16)`** (8010) — 🆕 Thinking
9. **`Llama3.3-8B-Instruct-Thinking-Claude-4.5-Opus (q8)`** (8011) — 🆕 Thinking quant
10. **`Llama-3.2-4X3B-MOE-Ultra-Instruct`** (8009) — 🆕 MoE hybrid

**General Chat (Fallback):**
11. `Llama-3.1-13B-Instruct.Q6_K` (8008)
12. `Llama-3.1-13B-abliterated.i1-Q6_K` (8007)
13. `Llama-3-13B-Instruct.Q6_K` (8005)
14. `Llama-3-8B-Instruct-Q8_0` (8006)
15. **`qwen3.5-14b-a3b-claude-4.6-opus-reasoning-distilled`** (8013) — 🆕 Reasoning distilled

---

## RECOMMENDED TEST ORDER FOR CODE GENERATION

### Phase 1: Safe-Order Smoke Test (Code Specialists First)

**Tier 1 — Code-Optimized (TEST FIRST):**
1. `DeepSeek-Coder-V2-Lite-Q4_K_S` (port 8002) — ✅ Fastest code model
2. `DeepSeek-Coder-V2-Lite-Q5_K_M` (port 8003) — ✅ Best code quality
3. **`qwen2.5-coder-14b-instruct`** (port 8012) — 🆕 NEW official coder
4. **`Qwen3.5-9b-Sushi-Coder-RL`** (port 8014) — 🆕 NEW RL-tuned code

**Tier 2 — Reasoning-Distilled (Code Context):**
5. **`DeepSeek-R1-Distill-Qwen-14B`** (port 8004) — 🆕 Reasoning for code
6. **`Llama3.3-8B-Thinking`** (port 8010 or 8011) — 🆕 Thinking capability

**Tier 3 — Fallback (If needed):**
7. `deepseek-coder-6.7b-Q8_0` (port 8000) — Older, has token leak

Skip Llama-3.x unless testing reasoning.

---

## CALIBRATION SETTINGS (v3 Procedure)

### DeepSeek-Coder Models
- **Temperature:** 0.25-0.35 (Mistral-based)
- **Top-P:** 0.9
- **Min Tokens (Phase 1 start):** 200
- **Optimal Tokens (expected):** 300-350
- **Use Case:** Fast, reliable code generation

### Qwen2.5-Coder & Qwen3.5 Models
- **Temperature:** 0.2-0.3 (conservative for code)
- **Top-P:** 0.9
- **Min Tokens:** 250-300
- **Optimal Tokens (expected):** 400-500
- **Use Case:** Production code, better reasoning

### DeepSeek-R1-Distill & Llama3.3-Thinking
- **Temperature:** 0.2-0.3 (reasoning models are deterministic)
- **Top-P:** 0.95 (may help reasoning paths)
- **Min Tokens:** 400 (reasoning = longer)
- **Optimal Tokens (expected):** 600-800
- **Use Case:** Code reasoning, algorithm explanation

### CRITICAL: Gemma Temperature Fix
If testing any Gemma models:
- **OLD (incorrect):** 0.15
- **NEW (registry-corrected):** 0.5
- **Reason:** Registry baseline is 1.0, compromise to 0.5

---

## KEY INSIGHTS FROM REGISTRY

### ⭐ Best Speed Model (Production Primary)
- **Phi-3.5:** 0.29s latency, 98% JSON compliance
- Not on kids-01, but reference for speed comparisons

### ⭐ Best for Code Generation
- **DeepSeek-Coder-V2-Lite-Q4_K_S:** 0.124s (from earlier G01 test)
- 96.9 tok/s
- Recommended for real-time code suggestions

### ⭐ Best for Code Quality (with reasoning)
- **Qwen2.5-Coder-14B:** Official production baseline
- Higher token budget (400-500) for complex algorithms
- Better for Blender API reasoning

### ⚠️ Known Issues
- `deepseek-coder-6.7b-Q8_0` leaks chat template tokens — needs stop token
- `Llama-3.1-abliterated` has verbose personality (expected)
- MoE models need source config files + llama_HF

---

## NEXT STEPS

1. **Phase 1 — Parameter Tuning (Today)**
   - Test Tier 1 models: DeepSeek-V2 Q4_K_S, Q5_K_M
   - Add Qwen2.5-Coder (NEW)
   - Record temperature sweep, find optimal tokens
   - Expected: 1-2 hours

2. **Phase 2 — Token Optimization (Today)**
   - Binary search for quality plateau
   - Expected: 30-45 min per model

3. **Phase 3 — Production Validation**
   - 25+ iterations with Blender/Python prompts
   - Expected: 20-30 min per model

4. **Create Code-Generation Test Suite (C01-C04)**
   - Simple Python function (baseline)
   - Blender API usage (structure)
   - Complex algorithm (tokens)
   - JSON extraction (metadata)

---

## VRAM NOTES

- Kids-01: 12GB RTX 4070 Ti
- Per model: ~3.5GB (Qwen/Llama 14B models)
- Smaller models (Qwen 9B): ~2.5GB
- Rule: ONE model at a time

---

**Status:** ✅ Ready to execute Phase 1 tuning on code models
**Recommended Start:** DeepSeek-Coder-V2-Lite-Q4_K_S (port 8002)
**Estimated Duration:** 3-4 hours for Tier 1 (3 models × ~1.2 hours each)
