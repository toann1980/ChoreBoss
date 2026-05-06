# DEVELOPMENT_OCP_ROUTINE - Testing & Project Work (2026-05-01)

**Purpose:** Systematic workflow for testing in development and working with OCP projects
**Status:** Shared draft (available to everyone)
**Audience:** Everyone doing dev/OCP work
**Frequency:** Every session when doing dev/OCP work

---

## The Routine (5 Steps)

### Step 1: Check Documentation First
**Before any action, read project documentation in this order:**
1. Project's `/CURRENT.md` (status, recent changes)
2. Project's `/START_HERE.md` (quick reference, methodology)
3. Project's `.openclaw/` folder (local notes, decisions, operating procedures)
4. Workspace `TOOLS.md` (infrastructure IPs, SSH hosts, configurations)
5. Workspace `MEMORY.md` (key decisions, lessons learned)

**Why:** Prevents duplicating work, uses documented methodology, respects prior decisions

### Step 2: Identify Model/Component Information
**For each model or component being tested:**
- [ ] Track exact name (from registry, not variations)
- [ ] Track source path (where file lives)
- [ ] Track destination path (where it gets deployed)
- [ ] Track port/endpoint (documented in project)
- [ ] Track test methodology (from project standards)

**Document in:** Project's CURRENT.md or dedicated tracking file

### Step 3: Use Documented Testing Protocol
**Never invent test methodology:**
- [ ] Use exact protocol from project (e.g., `/v1/chat/completions`, not raw endpoints)
- [ ] Use exact load times documented (e.g., 3s for NUC, 15s for inv-toan)
- [ ] Use exact metrics tracked (e.g., actual `completion_tokens`, not word count)
- [ ] Use same test format across all models (consistency)

**Source:** Project's MASTER.md, CONSOLIDATED_DEPLOYMENT.md, or START_HERE.md

### Step 4: Document Plan Before Executing
**Write down the plan first:**
- [ ] What are we testing? (models, components)
- [ ] Why are we testing it? (decision needed, verification)
- [ ] How will we test it? (protocol, methodology)
- [ ] What are we measuring? (metrics, success criteria)
- [ ] Where will results go? (file, database, OCP project)

**File location:** Project's `.openclaw/TESTING_PLAN_YYYYMMDD.md` or dedicated tracking file

### Step 5: Execute Systematically, Track Results
**During testing:**
- [ ] Run tests following exact documented protocol
- [ ] Track ALL results (even partial, even failures)
- [ ] Record exact model names, times, conditions
- [ ] Use consistent naming/formatting across all results
- [ ] Log unexpected issues or deviations

**File location:** Project's `CURRENT.md` + `.openclaw/RESULTS_YYYYMMDD.md`

---

## Decision Framework

### When to Check Documentation
- **Always before:** Starting any new model test
- **Always before:** Using a port, IP, or endpoint
- **Always before:** Changing testing methodology
- **Always before:** Acting on previous assumptions

### When to Create a Plan
- **Always before:** Multi-step testing (>1 model)
- **Always before:** Testing across multiple machines
- **Always before:** Any work affecting deployment decisions

### When to Track Information
- **Always:** Model names (exact from registry)
- **Always:** Port numbers and endpoints
- **Always:** File paths (source → destination)
- **Always:** Test methodology used
- **Always:** Raw results (before analysis)

---

## Red Flags (Stop & Recheck Documentation)

🚩 **Using different IP addresses without noting why**
→ Check TOOLS.md for documented network configuration

🚩 **Changing test methodology between models**
→ Check project MASTER.md for standard protocol

🚩 **Getting different results each run with same setup**
→ Check if methodology drifted; re-read documentation

🚩 **Making assumptions about model names/ports**
→ Check project registry files for exact names

🚩 **Testing without a written plan**
→ Create `.openclaw/TESTING_PLAN.md` first

---

## Workflow Example

**Scenario:** Testing 2 new models on NUC

### Step 1: Check Docs
- Read `/srv/openclaw_projects/llama.cpp/CURRENT.md`
- Read `/srv/openclaw_projects/llama.cpp/START_HERE.md`
- Read `/home/leto/.openclaw/workspace/TOOLS.md` (NUC network config)

### Step 2: Identify Components
- Model 1: `NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf` (documented in llama.cpp CURRENT.md)
- Model 2: `Opus4.7-GODs.Ghost.Codex.Distill.4B-Q8_0_WithinUsAI.gguf` (documented)
- Destination: `/home/leto/.openclaw/models/gguf/` (documented)
- Ports: 11439, 11440 (from planned systemd services)
- Endpoint: `/v1/chat/completions` (from START_HERE.md)

### Step 3: Document Protocol
- Load time: 3 seconds (per NUC documentation)
- Warmup: 3 requests (discard)
- Measurement: 5 requests (record)
- Metric: `completion_tokens` from API response
- Prompt: "What is 2+2?" (consistent)

### Step 4: Write Plan
```markdown
# Testing Plan - NUC New Models (2026-05-01)

**Models:** Nemotron-4B, Opus4.7-Distill
**Goal:** Baseline performance measurement
**Protocol:** llama.cpp START_HERE.md standard
**Success:** All 2 models respond with valid JSON
```

### Step 5: Execute & Track
- Install systemd services (with sudo)
- Test Model 1: Record latency, tokens, tok/s
- Test Model 2: Record latency, tokens, tok/s
- Update CURRENT.md with results
- Update BenchModel/CURRENT.md with comparison

---

## Integration with OCP Workflow

**When working in OCP projects:**

1. Every project has: `CURRENT.md` (always read first)
2. Every project has: `START_HERE.md` (quick reference)
3. Every project may have: `.openclaw/` (local notes, decisions)
4. Never invent methodology → always check project docs first
5. Always update `CURRENT.md` when work completes

**Before leaving a session:**
- Update project's `CURRENT.md` with status
- Update `.openclaw/` with session notes
- Commit to OCP if significant work done

---

## Related Shared Routines

- `OCP_ROUTINES.md` — central routine index
- `DOCUMENTATION_VERIFICATION_ROUTINE.md` — notify only after docs are complete

## Benefits of This Routine

✅ **Consistency** - Same methodology every test
✅ **Traceability** - Know exactly what was tested, how, when
✅ **Reproducibility** - Results can be verified by others
✅ **Efficiency** - No duplicated work, uses documented decisions
✅ **Correctness** - Follows established protocols, not ad-hoc guessing
✅ **Learning** - Mistakes are documented and learned from

---

## Enacting This Routine

**Status:** PROPOSAL

**To activate:**
- [ ] You approve the routine
- [ ] I move this file into the shared OCP routine set
- [ ] I reference this routine in every OCP/dev session going forward
- [ ] Everyone follows this pattern for consistency

**Questions for approval:**
1. Does this match your workflow expectations?
2. Should we adjust any steps?
3. Should we add this to MS-CONVENTIONS.md?
4. Ready to enable?

