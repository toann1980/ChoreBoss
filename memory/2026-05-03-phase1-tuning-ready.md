# Phase 1 Tuning Ready — Next Steps for Toan
**Date:** 2026-05-03 23:25 PDT  
**Status:** Ready to execute

---

## What's Been Done

✅ **Read operating procedure:** MODEL_FINE_TUNING_OPERATING_PROCEDURE_v2.md  
✅ **Identified sweet spot:** DeepSeek-R1-Distill-Qwen-14B-Q5_K_M (10B/Q5 criteria)  
✅ **Created Phase 1 tuning script:** Automates loose tuning (10% increments)  
✅ **Created loading instructions:** How to load models on kids-01  
✅ **Documented hypothesis:** 10B/Q5 should be faster than 6.7B-Q8, better than Q4_K_M  

---

## Your Next Steps (Simple)

### Step 1: Load Model on kids-01
On **kids-01 (Windows machine):**
```
1. Open PowerShell/Command Prompt
2. Navigate to llama.cpp directory
3. Run: llama-server.exe --model "path/to/deepseek-r1-distill-qwen-14b-q5_k_m.gguf" --port 8004 --ngl 99
4. Wait 20-30 seconds
5. Leave running
```

### Step 2: Run Tuning Script
On **NUC (this machine):**
```bash
python3 /srv/openclaw_projects/llama.cpp/kids-01_tuning/phase1_sweetspot_tuning.py
```

**Wait 20-30 minutes for results**

### Step 3: Review Results
Script will:
- Test temperature sweep (0.0-1.0)
- Test 4 scenarios (Simple Python, Blender API, Complex Algorithm, JSON)
- Score each (usability + quality, 1-5 scale)
- Save JSON results
- Print summary with Phase 1 score

### Step 4: For Model 2 (Optional)
On **kids-01:**
1. Stop current model (Ctrl+C)
2. Load Llama-3-8B-Instruct-Q8_0 on port 8006
3. Re-run script

---

## What Gets Tested

Per model:
- Minimum viable tokens (discovers where coherent response starts)
- Temperature sweep: 0.0, 0.1, 0.2, ..., 1.0 (11 values)
- 4 test scenarios per temperature
- 2 iterations per scenario
- Scoring: (Usability + Quality) / 2

Total: ~90 test requests per model

---

## Expected Outcome

**DeepSeek-R1-Distill-Qwen-14B-Q5:**
- Phase 1 Score: ~4.5-4.8/5.0
- Min tokens: ~100
- Best temperature: TBD (will discover)
- Speed: Likely between Q4_K_M and 6.7B-Q8
- Quality: Better than Q4_K_M (Q5 precision)

**Hypothesis validation:**
- If score > 4.5: NEW PRIMARY model (replaces Q4_K_M)
- If score 4.0-4.5: GOOD alternative
- If score < 4.0: Stick with Q4_K_M + 6.7B-Q8

---

## Files Created

All in `/srv/openclaw_projects/llama.cpp/kids-01_tuning/`:

1. `TUNING_SESSION_SWEETSPOT_20260503.md` — Model selection rationale
2. `LOAD_MODELS_INSTRUCTIONS_20260503.md` — How to load on kids-01
3. `phase1_sweetspot_tuning.py` — Automated Phase 1 script (ready to run)
4. `SESSION_READY_PHASE1_20260503.md` — Detailed next steps

---

## You're Ready!

1. Load model on kids-01
2. Run script on NUC
3. Get results in 20-30 minutes

Let me know when you've loaded the model and I'll help monitor the tuning run!

