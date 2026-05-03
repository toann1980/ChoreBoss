# SYSTEM ARCHITECTURE CLARIFIED

**Date:** 2026-04-21 07:35 UTC

---

## TWO SYSTEMS, ONE SHARED MEMORY

### System 1: Intel NUC (Nova)
- **Hostname:** nuc (or 10.0.0.81)
- **User:** leto
- **SSH:** `ssh leto@nuc`
- **Shell:** `leto@nuc:~$`
- **Memory Path:** `/srv/memory-sync/` (source)
- **Service:** Samba (SMB/CIFS server)

**What it does:**
- Hosts the memory-sync files
- Runs `nova-watch.sh` (monitors TO_NOVA.md)
- Updates `/srv/memory-sync/` directly

### System 2: Alienware Aurora R16 WSL2 (Kira)
- **Hostname:** inv-toan (Windows machine name)
- **User:** tron
- **SSH:** From Windows Terminal or WSL2 terminal
- **Shell:** `tron@inv-toan:~$`
- **Memory Path:** `/mnt/memory-sync/` (mounted share from NUC)
- **Service:** CIFS client (mounts NUC's Samba share)

**What it does:**
- Mounts NUC's memory-sync via Samba
- Runs `kira-message-check.sh` (cron, checks TO_KIRA.md)
- Accesses `/mnt/memory-sync/` through the mount

---

## THE SHARED MEMORY (Single Source of Truth)

**Physical location:** `/srv/memory-sync/` on NUC  
**Access from NUC:** `/srv/memory-sync/` (direct)  
**Access from Alienware:** `/mnt/memory-sync/` (mounted via Samba)

**Both paths point to the same files:**
```
NUC:       /srv/memory-sync/TO_NOVA.md
           ↓ (Samba share)
Alienware: /mnt/memory-sync/TO_NOVA.md

Same file, two different paths
```

---

## CORRECT PATHS FOR EACH SYSTEM

### When you're on NUC (`leto@nuc`)
```bash
# Read/write these paths:
cat /srv/memory-sync/TO_NOVA.md
echo "message" >> /srv/memory-sync/TO_KIRA.md
tail -20 /srv/memory-sync/DECISIONS.md
```

### When you're on Alienware WSL2 (`tron@inv-toan`)
```bash
# Read/write these paths:
cat /mnt/memory-sync/TO_NOVA.md
echo "message" >> /mnt/memory-sync/TO_KIRA.md
tail -20 /mnt/memory-sync/DECISIONS.md
```

---

## MEMORY FILES (What They're For)

| File | Owner | Reader | Path NUC | Path Alienware | Purpose |
|------|-------|--------|----------|----------------|---------|
| **TO_NOVA.md** | Kira | Nova | `/srv/memory-sync/` | `/mnt/memory-sync/` | Kira's messages to Nova (instant delivery) |
| **TO_KIRA.md** | Nova | Kira | `/srv/memory-sync/` | `/mnt/memory-sync/` | Nova's messages to Kira (2-min cron) |
| **NOVA.md** | Nova | Both | `/srv/memory-sync/` | `/mnt/memory-sync/` | Nova's session log |
| **KIRA.md** | Kira | Both | `/srv/memory-sync/` | `/mnt/memory-sync/` | Kira's session log |
| **DECISIONS.md** | Both | Both | `/srv/memory-sync/` | `/mnt/memory-sync/` | Shared decision record |
| **PLAN.md** | Both | Both | `/srv/memory-sync/` | `/mnt/memory-sync/` | Project overview |

---

## SETUP PROCESS (Correct Version)

### NUC Side (`leto@nuc`)
1. Install inotify-tools
2. Create `nova-watch.sh`
3. Start watching `/srv/memory-sync/TO_NOVA.md`
4. Nova detects changes instantly (inotifywait)

### Alienware Side (`tron@inv-toan`)
1. Verify `/mnt/memory-sync/` is mounted (already is)
2. Create `kira-message-check.sh`
3. Add to crontab (runs every 2 minutes)
4. Kira checks `/mnt/memory-sync/TO_KIRA.md` every 2 min

### Communication Flow
```
Nova writes to:          /srv/memory-sync/TO_KIRA.md
    ↓ (file updated)
Kira reads from:         /mnt/memory-sync/TO_KIRA.md
    (same file, different path)

Kira writes to:          /mnt/memory-sync/TO_NOVA.md
    ↓ (file updated)
Nova detects instantly:  /srv/memory-sync/TO_NOVA.md
    (inotifywait fires)
```

---

## FILES TO USE

**For NUC setup:** Use `QUICK_START_MEMORY_SIGNALING_CORRECT.md`
**For clear reference:** This document

---

## VERIFICATION

**On NUC (`leto@nuc`):**
```bash
# Should use /srv/memory-sync/
ls -la /srv/memory-sync/TO_*.md
cat /srv/memory-sync/TO_NOVA.md
```

**On Alienware (`tron@inv-toan`):**
```bash
# Should use /mnt/memory-sync/
ls -la /mnt/memory-sync/TO_*.md
cat /mnt/memory-sync/TO_NOVA.md
```

If paths work, setup can proceed.

---

**Key point:** Same files, different paths based on system location.
NUC = `/srv/`, Alienware = `/mnt/`

---

**Updated:** 2026-04-21 07:35 UTC
