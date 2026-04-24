# Project Workflow — .openclaw Folder Convention

## The Pattern (Use This For Every Project)

When you start work on ANY project:

1. **Go to `.openclaw/` folder in the project root**
2. **Read CURRENT_STATUS.md first** — this is your index
3. **CURRENT_STATUS.md tells you:**
   - What the project's current state is
   - What you're working on next
   - A **smart index** of other docs (with "when to read" guidance)
   - Key commands to run
   - Known blockers/issues
4. **Only read the other docs if CURRENT_STATUS.md says you need to**

---

## CURRENT_STATUS.md Template

Every project should have one. Copy this structure:

```markdown
# [Project Name] — Current Status & Quick Reference

**Last Updated:** YYYY-MM-DD  
**Status:** [one-liner]

---

## TL;DR — What's Happening Now
- Bullet points (3–5 lines max)

---

## Current State
- What's running
- What's loaded
- What's healthy/broken

---

## What's Next (Prioritized)
Table with: Phase | Task | Est. Time | Notes

---

## Key Design Decisions (FINAL)
Condensed bullets on critical decisions made

---

## Schema/Config Changes Coming
If applicable

---

## Quick Commands
Bash block with common commands

---

## .openclaw Document Index

**Read [THIS FILE] FIRST** — contains all critical info to start work.

Then read these as needed:

| Document | Purpose | When |
|---|---|---|
| ... | ... | ... |

---

## Last Known Issues / Blockers
None. / List issues.

---

## .openclaw Folder Convention
- Local only — never commit to git
- One central status file updated each session
- Indexes all other docs
```

---

## Why This Works

1. **No guessing** — you know what to read and when
2. **No context loss** — all critical info in one place
3. **Fast onboarding** — next person (or future you) has a roadmap
4. **Scalable** — works for 1-doc projects or 50-doc projects
5. **Maintainable** — one file updated each session, not fifty

---

## When to Update CURRENT_STATUS.md

- **Each session** — update "Last Updated" + "Current State"
- **When priorities shift** — update "What's Next"
- **When design decisions are final** — add to "Key Design Decisions"
- **When blockers appear** — add to "Known Issues"
- **When docs are added/removed** — update the index

---

## Workflow Checklist (For Nova)

When starting work on a project:

- [ ] Check `.openclaw/CURRENT_STATUS.md` exists
- [ ] Read CURRENT_STATUS.md first
- [ ] Check the Document Index for what else I need
- [ ] Only read docs listed as relevant to my task
- [ ] At end of session, update CURRENT_STATUS.md with new status

Before finishing a session:

- [ ] Update CURRENT_STATUS.md "Last Updated" date
- [ ] Update "Current State" with what I just did
- [ ] Update "What's Next" if priorities changed
- [ ] Add any new docs to the index
- [ ] Note any blockers in "Known Issues"

---

## Applied To

- **Envestero** — `.openclaw/CURRENT_STATUS.md` ✅
- **Future projects** — apply this pattern from day one
