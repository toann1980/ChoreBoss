# MANIFEST.md – Shared State Index

**Last Updated:** 2026-04-21 02:38 UTC (Nova)  
**Version:** 1.0

## Files in This Directory

1. **AGENT-SYNC.md** — Protocol document (this explains how we sync)
2. **agents-state.json** — Nova + Kira active status
3. **projects-state.json** — All project statuses
4. **kira-sync.md** — Kira's session notes
5. **nova-sync.md** — Nova's session notes
6. **sync-log.md** — Sync history + timestamps

## What Each Agent Owns

### Nova (Ubuntu NUC)
- Updates `nova-sync.md` after each session
- Can read/reference Kira's `kira-sync.md`
- Updates shared `projects-state.json`
- Commits to git with clear message

### Kira (WSL2 Windows)
- Updates `kira-sync.md` after each session
- Can read/reference Nova's `nova-sync.md`
- Updates shared `projects-state.json`
- Pulls + commits to git with clear message

## How to Use This

**Before starting work:**
```bash
git pull origin main  # Get latest from the other agent
cat memory-shared/MANIFEST.md  # See what changed
cat memory-shared/projects-state.json  # Check blockers + status
```

**After finishing work:**
```bash
# Update your sync file
echo "- Completed [task]" >> memory-shared/nova-sync.md  # or kira-sync.md

# Update shared project status
# (edit memory-shared/projects-state.json as needed)

# Commit
git add memory-shared/ && git commit -m "Nova sync: [summary]"

# Done — other agent will pull next time
```

## Conflict Handling

**If both agents edit projects-state.json:**
- Timestamp wins (newer update)
- Check `sync-log.md` for history
- Ask Toan if unclear

## Example projects-state.json

```json
{
  "Envestero": {
    "status": "IN_PROGRESS",
    "phase": 2,
    "last_updated_by": "Nova",
    "last_updated_at": "2026-04-21T02:38:00Z",
    "next_action": "Run Phase 2 tests against live DB",
    "blocker": null,
    "notes": "Phase 1 foundation complete (20 tickers, daily OHLCV)"
  }
}
```

---

**Ready to sync!** Both agents can now use this directory as a shared reference point.
