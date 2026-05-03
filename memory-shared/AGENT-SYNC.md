# AGENT-SYNC.md – Shared Memory Protocol

**Purpose:** Single source of truth for Nova (Ubuntu NUC) and Kira (WSL2 Windows)

**Location:** `/home/leto/.openclaw/workspace/memory-shared/`

**Last Sync:** 2026-04-21 02:38 UTC

---

## Shared State Files

All files in `memory-shared/` are kept in sync via git push/pull.

| File | Owner | Updated | Purpose |
|------|-------|---------|---------|
| `MANIFEST.md` | Nova | Every sync | Index of shared state + versioning |
| `agents-state.json` | Shared | Per-session | Nova + Kira active status, runtime |
| `projects-state.json` | Shared | Per-update | Project status, blockers, next steps |
| `kira-sync.md` | Kira | Per-session | Kira's notes, decisions, findings |
| `nova-sync.md` | Nova | Per-session | Nova's notes, decisions, findings |
| `sync-log.md` | Shared | Per-sync | Sync timestamps, version info |

---

## Sync Protocol

### Nova's Update (Ubuntu)
```bash
# 1. Update nova-sync.md with session work
# 2. Update projects-state.json with status changes
# 3. Commit: git add memory-shared/ && git commit -m "Nova sync: [what changed]"
# 4. Done — Kira pulls next session
```

### Kira's Update (WSL2)
```bash
# 1. Pull from git (get Nova's changes)
# 2. Update kira-sync.md with session work
# 3. Update projects-state.json with status changes
# 4. Commit: git add memory-shared/ && git commit -m "Kira sync: [what changed]"
# 5. Done — Nova pulls next session
```

---

## What's NOT Shared

**Private to each agent:**
- SOUL.md (agent personality/vibe)
- HEARTBEAT.md (local task checklist)
- Personal notes in `memory/` (daily logs are per-agent)

---

## Conflict Resolution

**If both updated the same file:**
1. Check `sync-log.md` for last known state
2. Newer timestamp wins
3. If unclear, ask Toan for tiebreak

---

## Fields in projects-state.json

```json
{
  "project_name": {
    "status": "IN_PROGRESS | BLOCKED | COMPLETE",
    "phase": "1 | 2 | 3",
    "last_updated_by": "Nova | Kira",
    "last_updated_at": "ISO-8601",
    "next_action": "description",
    "blocker": "what's blocking | null",
    "notes": "any relevant context"
  }
}
```

---

## Why This Works

- **Git is the sync layer** — both agents commit, both can pull
- **Ownership is clear** — who updated what, when
- **Merge conflicts are rare** — different files per agent
- **Toan is the arbiter** — ask for tiebreaks if needed
- **Read is free** — either agent can read anything in `memory-shared/`

---

## First Sync

1. Nova creates this directory + files (NOW)
2. Commit to git
3. Kira pulls + verifies she can read
4. Both use this protocol going forward

Done ✅
