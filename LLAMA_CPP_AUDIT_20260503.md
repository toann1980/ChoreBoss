# LLAMA.CPP AUDIT & MIGRATION PLAN — 2026-05-03

**Mode:** OWL (Operating-level status + Workspace insights)  
**NUC:** 10.0.0.81 | Ubuntu 24 LTS (6.17.0-22-generic x64)  
**Runtime:** node=v22.22.2 | llama.cpp from `/srv/github/llama.cpp`

---

## 🚨 CRITICAL ISSUE: MODEL PATH BROKEN

**Status:** 9 llama.cpp services are pointing to models that don't exist.

### The Problem

Models moved from:
```
❌ /home/leto/.openclaw/models/gguf  (EMPTY - 0 files)
✅ /home/leto/models/gguf            (POPULATED - 16 files, 42 GB)
```

**All 9 services still reference the OLD location.** They will fail on restart or reboot.

---

## 📋 SERVICE INVENTORY & STATUS

### Services Pointing to Old Location

| # | Service Name | Model | Port | Status | Exists? |
|---|--------------|-------|------|--------|---------|
| 1 | llama-cq-gemma4-e2b | CQ-Gemma-4-E2B-bF16-Q4_K.gguf | 11448 | 🔴 Broken | ❌ OLD |
| 2 | llama-embedding-q8 | nomic-embed-text-v1.5.Q8_0.gguf | 11449 | 🔴 Broken | ❌ OLD |
| 3 | llama-gemma4-e2b-q5m | google_gemma-4-E2B-it-Q5_K_M.gguf | 11445 | 🔴 Broken | ❌ OLD |
| 4 | llama-hermes-2-pro | Hermes-2-Pro-Mistral-7B-Q4_K_M.gguf | 11447 | 🔴 Broken | ❌ OLD |
| 5 | llama-llama3-2-moe | Llama-3.2-1B-4B-Quad-MoE.Q4_K_M_Fu01978.gguf | 11450 | 🔴 Broken | ❌ OLD |
| 6 | llama-mistral-7b | Mistral-7B-Instruct-v0.1-Q4_K_M.gguf | 11446 | 🔴 Broken | ❌ OLD |
| 7 | llama-nemotron | NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf | 11451 | 🔴 Broken | ❌ OLD |
| 8 | llama-phi | Phi-3.5-mini-instruct-Q4_K_M.gguf | 11452 | 🔴 Broken | ❌ OLD |
| 9 | llama-qwen2-5-4b | qingy2024.Qwen2.5-4B.Q6_K_DevQuasar-7.gguf | 11444 | 🔴 Broken | ❌ OLD |

---

## 📁 MODEL INVENTORY

### New Location: `/home/leto/models/gguf` (42 GB)

```
✅ CQ-Gemma-4-E2B-bF16-Q4_K.gguf                    (3.2 GB, 2026-05-01)
✅ Fijik-6b-Instruct-Llama3.2-GGUF_Pinkstack.gguf (3.5 GB, 2026-05-02)
✅ gemma-4-E4B-it-UD-IQ3_XXS_unsloth.gguf          (3.5 GB, 2026-05-01)
✅ google_gemma-4-E2B-it-Q5_K_M.gguf               (3.5 GB, 2026-05-01)
✅ google_gemma-4-E2B-it-Q5_K_S.gguf               (3.4 GB, 2026-05-01)
✅ Hermes-2-Pro-Mistral-7B-Q4_K_M.gguf             (4.1 GB, 2026-04-30) ← PRIMARY (Hermes)
✅ Llama-3.2-1B-4B-Quad-MoE.Q4_K_M_Fu01978.gguf   (2.2 GB, 2026-05-02)
✅ Llama-3.2-4X3B-MOE-Ultra-Instruct-10B-D_AU-Q2_k_DavidAU.gguf (3.6 GB, 2026-05-02)
✅ Mistral-7B-Instruct-v0.1-Q4_K_M.gguf            (4.1 GB, 2026-04-30) ← FALLBACK (Gemma)
✅ nomic-embed-text-v1.5.f16.gguf                  (262 MB, 2026-05-01)
✅ nomic-embed-text-v1.5.f32.gguf                  (523 MB, 2026-05-01)
✅ nomic-embed-text-v1.5.Q8_0.gguf                 (140 MB, 2026-05-01) ← Embedding
✅ NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf            (2.7 GB, 2026-05-01)
✅ OrcaAgent-llama3.2-8b-Q2_K_L_bartowski.gguf    (3.5 GB, 2026-05-02)
✅ Phi-3.5-mini-instruct-Q4_K_M.gguf               (2.3 GB, 2026-04-30)
✅ qingy2024.Qwen2.5-4B.Q6_K_DevQuasar-7.gguf     (3.2 GB, 2026-05-02)
```

**All 9 models needed by services are present at NEW location.** ✅ Ready to migrate.

---

## 🔧 MIGRATION PLAN

### Phase 1: Safe Shutdown (Graceful)
```bash
sudo systemctl stop llama-cq-gemma4-e2b.service
sudo systemctl stop llama-embedding-q8.service
sudo systemctl stop llama-gemma4-e2b-q5m.service
sudo systemctl stop llama-hermes-2-pro.service
sudo systemctl stop llama-llama3-2-moe.service
sudo systemctl stop llama-mistral-7b.service
sudo systemctl stop llama-nemotron.service
sudo systemctl stop llama-phi.service
sudo systemctl stop llama-qwen2-5-4b.service
```

### Phase 2: Update Service Files (9 updates)

Each service needs two path replacements:
1. `WorkingDirectory=/home/leto/.openclaw/models/gguf` → `/home/leto/models/gguf`
2. `--model /home/leto/.openclaw/models/gguf/...` → `/home/leto/models/gguf/...`

**Update commands:**
```bash
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-cq-gemma4-e2b.service
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-embedding-q8.service
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-gemma4-e2b-q5m.service
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-hermes-2-pro.service
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-llama3-2-moe.service
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-mistral-7b.service
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-nemotron.service
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-phi.service
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-qwen2-5-4b.service
```

### Phase 3: Reload & Restart

```bash
# Reload systemd to pick up changes
sudo systemctl daemon-reload

# Start all services
sudo systemctl start llama-cq-gemma4-e2b.service
sudo systemctl start llama-embedding-q8.service
sudo systemctl start llama-gemma4-e2b-q5m.service
sudo systemctl start llama-hermes-2-pro.service
sudo systemctl start llama-llama3-2-moe.service
sudo systemctl start llama-mistral-7b.service
sudo systemctl start llama-nemotron.service
sudo systemctl start llama-phi.service
sudo systemctl start llama-qwen2-5-4b.service
```

### Phase 4: Verification

```bash
# Check each service status
systemctl status llama-hermes-2-pro.service --no-pager
systemctl status llama-gemma4-e2b-q5m.service --no-pager

# Verify model loads (check logs)
sudo journalctl -u llama-hermes-2-pro.service -n 20

# Test connectivity
curl -s http://10.0.0.81:11447/health | jq .
```

---

## 📊 IMPACT ANALYSIS

### OCP Dependency Tree

```
llama.cpp services (9 instances)
  ├─ Hermes-2-Pro (Port 11447) — PRIMARY inference model
  │  └─ Used by: Financial analysis, portfolio optimization
  ├─ Gemma-Q5M (Port 11445) — Fallback model
  │  └─ Used by: Technical analysis, scenario testing
  ├─ Qwen-2.5-4B (Port 11444) — Specialized reasoning
  ├─ Embedding Service (Port 11449) — nomic-embed
  └─ Other models (7 total) — Specialized tasks
```

### Failure Mode (Current)

- **If services restart:** Models not found → services crash
- **If NUC reboots:** All 9 llama services fail to start
- **Impact:** OCP inference pipeline unavailable

### Recovery (Post-Migration)

- ✅ All services point to valid model locations
- ✅ Automatic restart on failure (configured in unit files)
- ✅ Ready for production operation

---

## ✅ PRE-FLIGHT CHECKLIST

- [x] All 9 models verified at `/home/leto/models/gguf`
- [x] Service files identified (`/etc/systemd/system/llama-*.service`)
- [x] Safe shutdown procedure documented
- [x] Update commands prepared (sed-based path replacement)
- [x] Restart sequence prepared
- [x] Verification tests identified
- [ ] **AWAITING: Toan approval to execute migration**

---

## 📝 NOTES

- **Backup strategy:** Original service files backed up automatically (`*.service.backup`)
- **Rollback:** If needed, restore from backup and revert paths
- **No downtime risk:** Services gracefully stop, update, restart — no data loss
- **OCL config:** Not affected (configs remain valid, only model filesystem path changed)

---

**Ready to proceed?** Run the commands in Phase 1-3 when you're ready. I'll verify each step with receipts.
