# Kira Access Notes

## User Mapping

- **Kira's NUC username:** `sienna`
- **NUC system:** 10.0.0.81
- **Access method:** SMB mount via `siena smb` command
- **Shared path:** `/srv/openclaw_projects/`
- **Group:** `openclaw` (read/write access)

## Setup Summary

Permissions configured 2026-04-23 17:28 UTC:
```bash
sudo groupadd openclaw
sudo usermod -a -G openclaw leto
sudo usermod -a -G openclaw sienna  # Kira's username on NUC
sudo chown -R leto:openclaw /srv/openclaw_projects
sudo chmod -R 775 /srv/openclaw_projects
```

Result:
- Kira (sienna) has **write access** to all `/srv/openclaw_projects/` via SMB
- Both leto and sienna are members of `openclaw` group
- Directory writable by group

## Projects Currently Shared

- **MemoryGraph** (at `/srv/openclaw_projects/MemoryGraph/`)
  - Knowledge graph for memory retrieval
  - Phase 1 complete, ready for Phase 2 development
  - All code, docs, memories in place

## For Future Projects

Add new projects to `/srv/openclaw_projects/` with same permissions.

---

**Status:** ✅ Configured for Kira access  
**Date:** 2026-04-23 17:28 UTC
