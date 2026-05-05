# Session: 2026-05-04 22:32:17 PDT

- **Session Key**: agent:main:dashboard:b6073054-481b-42ea-96cd-6d1f0400c359
- **Session ID**: 553f4c6d-4422-467f-9f57-69b0d7f6e02c
- **Source**: webchat

## Conversation Summary

user: [Mon 2026-05-04 22:27 PDT] OWL Mode read OCP llama.cpp inv-toan_tuning. CURRENT. We have some models to test.
assistant: **OWL Mode Summary — OCP CURRENT.md (as of 2026-04-29 23:18 PDT)**

The CURRENT.md snapshot shows the main OCP focus is the **3D production ecosystem** (Helix, ImageForge, MEGA DAM design complete). MemoryGraph is noted as "✅ M1-M6 + Phase 1 Extended live on NUC."

But this doesn't directly reference **inv-toan_tuning** or tuning/model testing work.

---

**Question for clarity:** When you say "models to test" — are you referring to:

1. **LLM model variants** for BenchModel (tuning framework from my memory — Phase 3 complete, 102 tests passing)?
2. **MemoryGraph inference models** (llama.cpp on port 11447 — all 4 cron jobs validated as of 2026-05-04)?
3. **New models** in a different inv-toan_tuning project context?

Is there a separate `inv-toan_tuning/CURRENT.md` or a `.openclaw/CURRENT.md` in that project directory I should read instead? Or should I pull my BenchModel context from memory?

What's the testing goal tonight?
user: [Mon 2026-05-04 22:28 PDT] OCP llama.cpp inv-toan_tuning subfolder CURRENT
assistant: Directory doesn't exist at `/srv/openclaw_projects/inv-toan_tuning`. Let me search for it:
assistant: 🎯 **inv-toan_tuning Current State (2026-05-04 21:52 PDT)**

**Status:** ✅ **Phase 1-4 COMPLETE** — All 5 models production-ready, audit verified (14 corrections applied)

---

## What We Have (Ready to Test)

| Model | Role | Port | Latency | Quality | Status |
|---|---|---|---:|---|---|
| **1: DeepSeek-Coder** | Real-time | 8002 | 344ms (p95: 627ms) | 5/5 ✅ | Production |
| **2: Llama-MoE** | Fallback | 8011 | 615ms | 5/5 ✅ | Dual-temp (0.1/0.8) |
| **3: Qwen-Coder** | JSON spec | 8022 | 2,839ms | 4/5 ✅ | Batch mode |
| **4: DeepSeek-R1** | Deep reasoning | 8005 | 10,570ms | 4-5/5 ✅ | Parse `reasoning_content` |
| **5: Qwen3.6-27B** | Overnight batch | 8027 | 45,128ms | 4-5/5 ✅ | Sequential load only |

---

## Key Things to Know Before Testing

🔴 **Model 4 Critical:** Parse `reasoning_content` field, NOT `content` (content will be empty on reasoning models)  
🔴 **Model 5 Critical:** Load sequentially only (no parallel), 40s warmup (not 20s)  
🔴 **Port 8027:** Not 8024 (old model replaced)  
🟢 **Token budgets:** Model 1 = 150, Models 2-5 = 200 (Phase 2 optimization applied)

---

## Pending Work (Engineering Sprint)

**Pre-Integration:**
- [ ] Review `COMPLETE_MODEL_COMPARISON_TABLE_20260504.md` (corrected, production spec)
- [ ] Verify port assignments (8002, 8011, 8022, 8005, 8027)

**Week 1-3 Implementation:**
- [ ] Routing service (task → model selection)
- [ ] Model 4 reasoning_content extraction
- [ ] Model 2 dual-temperature routing
- [ ] Configuration files (JSON routing tables)
- [ ] Unit + integration tests
- [ ] SLA verification (p50/p95/p99 latencies)
- [ ] Canary → Staging → Production rollout

**New Model Evaluation (Windows folder scan — 2026-05-04):**
- [ ] Gemma-4 E4B research (4B, 10GB VRAM, thinking mode)
- [ ] Qwen3.6-35B-A3B feasibility (MoE efficiency vs 27B)
- [ ] Benchmark against current suite, decide if warranted

---

**Question:** Are you ready to test these 5 models live, or do you want to evaluate the new candidates first (Gemma-4 E4B, Qwen3.6-35B-A3B)?
user: [Mon 2026-05-04 22:30 PDT] Read GEMMA4_AND_MODELS_FINAL_STATUS_20260504.md

Let's test Gemma-4A4B and Qwen3.6-27B
assistant: Perfect. **Status:** ✅ Research complete — Gemma-4 E4B & Qwen3.6-27B ready for Phase 1 testing.

---

## Test Plan: Gemma-4 E4B + Qwen3.6-27B

**What we're testing:**
- **Gemma-4 E4B** (10GB VRAM, multimodal + thinking mode) vs Model 2 (Llama-3.2-MoE, 615ms)
- **Qwen3.6-27B** (18GB VRAM, multimodal + thinking mode) — as shown in CURRENT.md Phase 2-4 tested

**Why:**
- Both fit RTX 4090 safely
- Both have thinking mode (reasoning capability)
- Both multimodal (text + vision + audio)
- Gemma-4 E4B is ultra-lightweight (good fallback candidate)
- Qwen3.6-27B already partially validated in CURRENT.md

---

## Download & Load

**Gemma-4 E4B (Community GGUF — recommended):**
```
https://huggingface.co/ManniX-ITA/gemma-4-A4B-109e-v3-it-GGUF
```
**Alternative (if A4B unavailable):**
```
https://huggingface.co/unsloth/gemma-4-E4B-it
```

**Qwen3.6-27B (Official GGUF):**
```
https://huggingface.co/unsloth/Qwen3.6-27B-GGUF/resolve/main/Qwen3.6-27B-UD-Q4_K_XL.gguf
```

---

## Action: Load Both Models Now?

Should I:
1. **Download** both models to `/srv/openclaw_projects/llama.cpp/models/`
2. **Load** them via llama.cpp on inv-toan (ports 8030 & 8031?)
3. **Run Phase 1 smoke tests** (latency, quality, parsing, thinking mode activation)
4. **Benchmark** against your Suite 2 prompts?

**Or do you want to handle the downloads separately?** (They're large — Gemma-4 E4B ~8GB, Qwen3.6-27B ~18GB)

What's your preference for port assignment, test prompts, and timing?
user: [Mon 2026-05-04 22:31 PDT] Look in D:\Applications\llama.cpp\models. Some models are downloaded alrady
assistant: Let me check if Windows drive is mounted:
assistant: NUC is running Linux. The D: drive is a Windows machine. Let me check if there's a mounted Windows share or if models are accessible via the NAS:
assistant: Let me check if D: is accessible via SMB or if there's a Windows mount point:
assistant: **Clarification needed:** The NUC (Linux 10.0.0.81) doesn't have direct access to the Windows D: drive yet. 

**Questions:**

1. **Is D: on the Windows machine at 10.0.0.4** (the NAS/OpenClaw gateway)?
2. **Should I mount D: as a network share** (SMB/NFS) on the NUC?
3. **Or are the models already copied** to `/srv/openclaw_projects/llama.cpp/models/` on the NUC?

Let me check what's already on the NUC:
assistant: No actual model files (*.gguf) in `/srv/openclaw_projects/llama.cpp/models/`. Let me check if they're in the llama.cpp working directory:
assistant: Those are just vocab files. Let me check the actual inv-toan_tuning models directory:
assistant: Still no actual .gguf model files. **Clarification:**

Are the Gemma-4 E4B and Qwen3.6-27B model files physically located on the Windows D: drive at `D:\Applications\llama.cpp\models\`?

If so, I need either:

1. **SMB share access** to the Windows machine (to mount D: as a network drive on the NUC)
2. **Windows machine IP** to set up a direct connection
3. **Or you copy them manually** from D: to the NUC at `/srv/openclaw_projects/llama.cpp/inv-toan_tuning/` or similar

**Quick check:** What's on D: that we need? Can you paste what you see in that folder, or should I mount it directly?
