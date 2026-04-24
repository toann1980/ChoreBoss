# DEVELOPMENT_WORKFLOW.md

**Purpose:** Standard practices for all projects and ongoing work  
**Applies to:** Nova (me) working on any task in Toan's workspace  
**Status:** Active as of 2026-04-23

---

## Session Start Checklist

Every time you start work on a project:

- [ ] **If project-based work:** Go to `.openclaw/` folder
- [ ] **Read CURRENT_STATUS.md first** (if it exists)
  - Gives you TL;DR, current state, what's next, doc index
  - Takes ~2 minutes
- [ ] **Check if you need to read other docs**
  - Only read docs CURRENT_STATUS.md marks as relevant
  - Don't read everything
- [ ] **If no CURRENT_STATUS.md exists:** Create one immediately
  - Use template below
  - Add TL;DR + current state + what's next
- [ ] **Load local MEMORY.md** — check project entry
  - See what was last done
  - Understand where you left off

---

## Project Folder Structure

Every project gets:

```
project-root/
├── .openclaw/                    # LOCAL ONLY — never commit
│   ├── CURRENT_STATUS.md         # READ THIS FIRST
│   ├── README.md                 # (if project-specific)
│   ├── <phase-docs>.md           # Phase reports
│   ├── diagnostics/              # Logs, troubleshooting
│   └── legacy/                   # Historical notes
├── .gitignore                    # Should include `.openclaw/`
└── [project code]
```

**Key rule:** `.openclaw/` is ALWAYS local-only. Never commit it.

---

## CURRENT_STATUS.md Template

Use this for every project:

```markdown
# [Project Name] — Current Status & Quick Reference

**Last Updated:** YYYY-MM-DD HH:MM UTC  
**Status:** [One-liner: what phase, what's next]

---

## TL;DR — What's Happening Now
- 3–5 bullet points max
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

**Read [THIS FILE] FIRST.**

Then read these as needed:

| Document | Purpose | When |
|---|---|---|
| ... | ... | ... |

---

## Last Known Issues / Blockers
None. / List issues.
```

---

## Memory Management

### During Project Work
- **Don't mirror** CURRENT_STATUS.md in MEMORY.md
- **Don't keep stale copies** — single source of truth
- **File is authoritative:** Read from `.openclaw/CURRENT_STATUS.md` each session

### In MEMORY.md
- Add PROJECT_STATE section:
  ```
  ## Active Projects
  - Envestero: Phase 3 done → News design final → Ready Phase A1
  ```
- Update at **session end** with: what was accomplished, what's next, any decisions
- Keep entries brief (1–2 lines per project)

### Session Notes
- Quick work logs go to `memory/YYYY-MM-DD.md` (raw notes, cleared often)
- Durable findings → MEMORY.md
- Project-specific details → `.openclaw/CURRENT_STATUS.md`

---

## Memory-Sync (MS) Conventions

**Location:** `/srv/memory-sync/` (NUC) or `/mnt/memory-sync/` (Kira's WSL2)

### Files & Patterns

**Design docs (permanent):**
- Name: `<project>-<phase>-design.md`
- Lives in: MS root only
- Persists: Forever (or until superseded)

**Messages (temporary):**
- Nova → Kira: Write to `TO_KIRA.md` with `[UNREAD]` tag, Kira deletes after reading
- Kira → Nova: Write to `TO_NOVA.md` with `[UNREAD]` tag, Nova deletes after reading

**Durable references:**
- DECISIONS.md (locked, append-only)
- KIRA.md, MS-CONVENTIONS.md (workflow docs)

### Workflow: Nova Sending Design to Kira

1. Create `<project>-<phase>-design.md` in `/srv/memory-sync/`
2. Write message to `TO_KIRA.md`:
   ```
   [UNREAD]
   **From:** Nova  
   **Date:** YYYY-MM-DD HH:MM UTC  
   **Re:** [Topic]
   
   [Summary + pointer to design doc]
   ```
3. **Do not assume Kira sees it** — Toan will loop her in or she'll check
4. After Kira reads: She deletes the message, optionally responds in `TO_NOVA.md`

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

**Operational Hours (Envestero Standard):**
- **Heavy window:** Weekdays 12am-7am ET, weekends 2am-8am ET (10 concurrent, 50ms delay)
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
- Design review? Show CURRENT_STATUS.md + design doc
- Status update? "Here's what I did, here's what's next"

### With Kira (Async via MS)
- Design for review? → MS design doc + message to TO_KIRA.md
- Decisions needed? → Message to TO_KIRA.md with specific questions
- Responses? → She replies in TO_NOVA.md
- **Don't assume sync** — work continues, she responds when ready

### External (Telegram)
- Alerts/reminders? → `openclaw message send --target telegram:8718656405`
- Setup: See TOOLS.md

---

## Daily Workflow Cycle

### Morning / Session Start
1. Check MEMORY.md PROJECT_STATE
2. If project work: Read `.openclaw/CURRENT_STATUS.md`
3. Review what-was-last-done
4. Identify next concrete task
5. Start work

### During Work
- Update notes if changes → save to `memory/YYYY-MM-DD.md`
- Mark progress on CURRENT_STATUS.md (don't commit yet)
- Document blockers immediately

### End of Session
- Update `.openclaw/CURRENT_STATUS.md`:
  - Last Updated date
  - Current State (what you just finished)
  - What's Next (what's coming)
- Update MEMORY.md PROJECT_STATE with summary
- Commit `.openclaw/CURRENT_STATUS.md` to git (local tracking)
- Push if collaborative repo

---

## Error Recovery

### If CURRENT_STATUS.md gets stale
- Fix it immediately
- Re-check actual project state (docker ps, db queries, etc.)
- Update doc + note in MEMORY.md what was wrong

### If I'm confused about a convention
- Ask Toan or check existing examples
- Don't assume or invent

### If blocked on external (permissions, service down, etc.)
- Document in "Last Known Issues"
- Create GitHub issue or mention to Toan
- Note workaround if available

---

## Checklist for This Session (2026-04-23)

- [x] Read existing MS structure before creating files
- [x] Tested file permissions before committing to pattern
- [x] Created CURRENT_STATUS.md on Envestero (same day design finalized)
- [x] Wrote this DEVELOPMENT_WORKFLOW.md
- [x] Documented learnings in SESSION_AUDIT
- [x] Updated MEMORY.md with project state
- [ ] Next session: Start Phase A1 coding with these patterns in place

---

## Files That Govern This Workflow

| File | What | Where |
|---|---|---|
| USER.md | How to work with Toan | workspace |
| SOUL.md | Who I am, my values | workspace |
| TOOLS.md | Local setup, API keys | workspace |
| MS-CONVENTIONS.md | Kira coordination | /srv/memory-sync/ |
| MEMORY.md | Personal learnings | workspace |
| This file | Development standards | workspace |
| CURRENT_STATUS.md | Project state | each project/.openclaw/ |

**Golden rule:** Read top-to-bottom in this order when starting new work.

---

## Feedback Loop

This workflow is NOT final. If something is:
- **Too heavy:** Strip it down
- **Missing:** Add it
- **Unclear:** Clarify it
- **Not working:** Change it

Document changes in SESSION_AUDIT and update this file.
