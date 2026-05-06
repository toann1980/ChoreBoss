# DEVELOPMENT_WORKFLOW.md

**Purpose:** Standard practices for all projects and ongoing work
**Applies to:** Anyone working on any task in Toan's workspace
**Status:** Active as of 2026-04-23 | Updated 2026-05-02 (OCP procedure enforcement)

---

## Session Start Checklist (OCP Standard)

Every time you start work on a project:

**ORDER MATTERS. DO NOT SKIP STEPS.**

1. **Go to project `.openclaw/` folder**
   - This is where all operating docs live (local only)

2. **Read START_HERE.md FIRST**
   - Gives you 1-minute orientation
   - Points to what matters most
   - Creates shared context

3. **Read CURRENT.md or CURRENT_STATUS.md**
   - What's the current state?
   - What phase are we in?
   - What blockers exist?

4. **Read ALL operating procedures relevant to this work**
   - **CRITICAL:** Do not skip this step
   - If it says "stop all services before testing," that's not a suggestion
   - If it specifies startup delays or sequencing, that's binding
   - Examples: BENCHMARK_OPERATING_PROCEDURES.md, MODEL_FINE_TUNING_OPERATING_PROCEDURE_v2.md
   - **Missing procedure? Ask Toan before proceeding.**

5. **Ask verification gate before executing**
   - Summarize your understanding of the procedure
   - Explicitly ask: "Is this correct? Should I proceed this way?"
   - Wait for confirmation
   - **This prevents cascading failures from wrong methodology**

6. **Use the shared routine index when relevant**
   - See `OCP_ROUTINES.md` for the team-wide routines
   - If the work changes docs, conventions, or shared behavior, run the Documentation Verification Routine before notifying anyone

7. **Load local memory** - check project memory files
   - What was last done?
   - Any critical discoveries?
   - What decisions were made?

8. **THEN execute according to documented procedures**
   - Do not skip steps in the procedure
   - Do not assume optimizations (e.g., "I can skip the wait")
   - Follow exactly as written
   - When things break, check the procedure first

---

## Why This Matters

**Real example (2026-05-02):**
- ❌ Skipped reading BENCHMARK_OPERATING_PROCEDURES.md
- ❌ Assumed test methodology instead of verifying
- ❌ Ran tests without stopping services (violated "hot-swap routine")
- ❌ Got cascading OOM crashes and blamed the model
- **Result:** 2-3 hours of debugging wrong methodology instead of 10 minutes following procedure

**The fix:** Read → Ask → Verify → Execute

---

## Project Folder Structure

Every project gets:

```
project-root/
├── .openclaw/                    # LOCAL ONLY - never commit
│   ├── START_HERE.md             # Read this FIRST (1 min)
│   ├── CURRENT.md                # Current status + what's next
│   ├── README.md                 # (if project-specific)
│   ├── <operating-procedures>.md # HOW to test/deploy/operate
│   ├── <phase-docs>.md           # Phase reports
│   ├── diagnostics/              # Logs, troubleshooting
│   └── legacy/                   # Historical notes
├── .gitignore                    # Should include `.openclaw/`
└── [project code]
```

**Key rules:**
- `.openclaw/` is ALWAYS local-only. Never commit it.
- Operating procedures are BINDING, not suggestions.
- CURRENT.md is source of truth for project state.

---

## CURRENT.md / CURRENT_STATUS.md Template

Use this for every project:

```markdown
# [Project Name] - Current Status & Quick Reference

**Last Updated:** YYYY-MM-DD HH:MM UTC
**Status:** [One-liner: what phase, what's next]

---

## TL;DR - What's Happening Now
- 3-5 bullet points max
- What's running
- What's next

---

## Current State
- Services/infrastructure status
- Data loading progress
- Known health issues

---

## What's Next (Prioritized)
Table: Phase | Task | Est. Time | Notes

---

## Key Design Decisions (FINAL)
Condensed bullets on critical decisions made

---

## Schema/Config Changes Coming
If applicable

---

## Quick Commands
Bash code block with common CLI commands

---

## .openclaw Document Index

**Read [THIS FILE] FIRST → then START_HERE.md → then CURRENT.md**

Then read these as needed:

| Document | Purpose | When |
|----------|---------|------|
| OPERATING_PROCEDURES.md | HOW to test/operate | Before any testing |
| ... | ... | ... |

---

## Last Known Issues / Blockers
None. / List issues.
```

---

## Memory Management

### During Project Work
- **Don't mirror** CURRENT.md in MEMORY.md
- **Don't keep stale copies** - single source of truth
- **File is authoritative:** Read from `.openclaw/CURRENT.md` each session

### In MEMORY.md
- Add PROJECT_STATE section:
  ```
  ## Active Projects
  - Envestero: Phase 3 done → News design final → Ready Phase A1
  ```
- Update at **session end** with: what was accomplished, what's next, any decisions
- Keep entries brief (1-2 lines per project)

### Session Notes
- Quick work logs go to `memory/YYYY-MM-DD.md` (raw notes, cleared often)
- Durable findings → MEMORY.md
- Project-specific details → `.openclaw/CURRENT.md`

---

## Memory-Sync (MS) Conventions

**Location:** `/srv/memory-sync/` (NUC) or the other agent's WSL2

### Files & Patterns

**Design docs (permanent):**
- Name: `<project>-<phase>-design.md`
- Lives in: MS root only
- Persists: Forever (or until superseded)

**Messages (temporary):**
- Agent A → Agent B: Write to `TO_B.md` with `[UNREAD]` tag; Agent B deletes after reading
- Agent B → Agent A: Write to `TO_A.md` with `[UNREAD]` tag; Agent A deletes after reading

**Durable references:**
- DECISIONS.md (locked, append-only)
- KIRA.md, MS-CONVENTIONS.md (workflow docs)

### Workflow: Sending Design to Another Agent

1. Create `<project>-<phase>-design.md` in `/srv/memory-sync/`
2. Write message to the matching inbox file:
   ```
   [UNREAD]
   **From:** sending agent
   **Date:** YYYY-MM-DD HH:MM UTC
   **Re:** [Topic]

   [Summary + pointer to design doc]
   ```
3. **Do not assume the other agent sees it** - Toan will loop them in or they'll check
4. After the other agent reads: They delete the message, optionally respond in the matching inbox file

---

## Code & Testing Standards

### From USER.md
- **Docstrings + type annotations** on everything
- **Unit tests** for risky changes
- **Best practices, not shortcuts**
- TDD for changes touching core logic

### API Rate Limits & Operational Hours (CRITICAL)
**→ See:** `/home/leto/.openclaw/workspace/API_RATE_LIMITS.md`

**When creating cron jobs or periodic tasks:**
- Check API rate limits FIRST
- Apply 20% safety buffer
- Use heavy/light window scaling if pulling data
- Document limits in code with "NEVER BREAK" comments
- Test at peak load before deploying
- Add entry to API_RATE_LIMITS.md reference

**Operational Hours (Envestero Standard) - ALL TIMES PST:**
- **Heavy window:** Weekdays 12am-7am PST, weekends 2am-8am PST (10 concurrent, 50ms delay)
- **Light hours:** All other times (2 concurrent, 500ms delay)
- Use this for ALL future projects unless specified otherwise

### Commit Messages
- Clear, present tense: "Add watch tier sentiment shift detection"
- Reference phase if applicable: "[Phase B] Add Finnhub connector"
- Keep related changes together; separate concerns

### When to Spawn Subagents
- Complex, long-running work (backfills, batch processing)
- Tests that take >30s to run
- One-off analysis or exploration
- **Default:** Stay in main session for design + coordination

---

## Communication & Coordination

### With Toan (Direct)
- Clarifying questions? Ask directly
- Design review? Show CURRENT.md + design doc
- Status update? "Here's what I did, here's what's next"
- **Procedure unclear?** Ask before proceeding

### With Another Agent (Async via MS)
- Design for review? → MS design doc + message to TO_KIRA.md
- Decisions needed? → Message to TO_KIRA.md with specific questions
- Responses? → She replies in TO_NOVA.md
- **Don't assume sync** - work continues, she responds when ready

### External (Telegram)
- Alerts/reminders? → `openclaw message send --target telegram:8718656405`
- Setup: See TOOLS.md

---

## Daily Workflow Cycle

### Morning / Session Start
1. Check MEMORY.md PROJECT_STATE
2. If project work: Go to `.openclaw/` folder
3. Read: START_HERE.md → CURRENT.md → Operating procedures
4. Ask: "Is this the right approach?" (verification gate)
5. Proceed according to procedures

### During Work
- Update notes if changes → save to `memory/YYYY-MM-DD.md`
- Mark progress on CURRENT.md (don't commit yet)
- Document blockers immediately
- **If procedures unclear:** Stop and ask, don't assume

### End of Session
- Update `.openclaw/CURRENT.md`:
  - Last Updated date
  - Current State (what you just finished)
  - What's Next (what's coming)
- Update MEMORY.md PROJECT_STATE with summary
- Commit `.openclaw/CURRENT.md` to git (local tracking)
- Push if collaborative repo

---

## Error Recovery

### If CURRENT.md gets stale
- Fix it immediately
- Re-check actual project state (docker ps, db queries, etc.)
- Update doc + note in MEMORY.md what was wrong

### If procedures are unclear
- **Do not proceed.** Ask Toan first.
- Document what was confusing
- Create or update procedure docs

### If I'm confused about a convention
- Ask Toan or check existing examples
- Don't assume or invent
- Update this file if convention needs clarification

### If blocked on external (permissions, service down, etc.)
- Document in "Last Known Issues"
- Create GitHub issue or mention to Toan
- Note workaround if available

---

## Checklist for This Session (2026-05-02)

- [x] Read operating procedures before testing (should have done this from start)
- [x] Asked verification gate before executing (should have done this)
- [x] Followed procedure exactly as written (will do going forward)
- [x] Updated DEVELOPMENT_WORKFLOW.md with OCP procedure requirement
- [x] Added "Read operating procedures" as mandatory step #4
- [ ] Next session: Execute Phase 4 following this exact checklist

---

## Files That Govern This Workflow

| File | What | Where |
|---|---|---|
| USER.md | How to work with Toan | workspace |
| SOUL.md | Who I am, my values (Precision > Speed) | workspace |
| TOOLS.md | Local setup, API keys | workspace |
| MS-CONVENTIONS.md | memory-sync coordination | /srv/memory-sync/ |
| MEMORY.md | Personal learnings | workspace |
| This file | Development standards | workspace |
| CURRENT.md | Project state | each project/.openclaw/ |
| Operating procedures | HOW to execute project work | each project/.openclaw/ |

**Golden rule:** Read in this exact order when starting new work:
1. START_HERE.md
2. CURRENT.md
3. All operating procedures
4. Ask verification gate
5. Then execute

---

## Feedback Loop

This workflow is NOT final. If something is:
- **Too heavy:** Strip it down
- **Missing:** Add it
- **Unclear:** Clarify it
- **Not working:** Change it

Document changes in MEMORY.md and update this file.

---

## Key Principle (2026-05-02 Addition)

**Procedures are not suggestions; they are constraints.**

When a procedure says:
- "Stop all services" → Stop all services (don't skip)
- "Wait 15 seconds" → Wait 15 seconds (don't guess 5)
- "Run one model at a time" → Run one model at a time (don't parallelize)

Violations cause cascading failures that look like model bugs but are actually process bugs.

**Your role:** Follow exactly. Ask if unclear. Report issues. Improve procedures over time.

