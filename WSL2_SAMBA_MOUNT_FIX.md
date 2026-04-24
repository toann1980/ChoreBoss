# QUICK FIX: WSL2 Samba Mount Issue

**Problem:** `tail: cannot open '/srv/memory-sync/TO_NOVA.md': No such file or directory`

**Cause:** Samba share not mounted in WSL2

**Solution:** Mount the NUC's Samba share

---

## FIX (Run on Alienware WSL2)

### Option 1: Mount Samba Share (Recommended)

```bash
# Create mount point
mkdir -p /mnt/memory-sync

# Mount the NUC's Samba share
# Replace 10.0.0.81 with NUC IP if different
sudo mount -t cifs //10.0.0.81/memory-sync /mnt/memory-sync -o username=sienna,password=sienna

# Verify it mounted
ls -la /mnt/memory-sync/
# Should see: TO_NOVA.md, TO_KIRA.md, DECISIONS.md, etc.
```

### Option 2: Use Full UNC Path

If mounting doesn't work, use the full path:
```bash
# Instead of /srv/memory-sync/
# Use: //10.0.0.81/memory-sync/

# Example:
cat //10.0.0.81/memory-sync/TO_NOVA.md
```

### Option 3: Map Drive Letter (Windows Terminal)

If you prefer Windows-style:
```bash
# In Windows Command Prompt (not WSL):
net use Z: \\10.0.0.81\memory-sync /user:sienna sienna /persistent:yes

# Then in WSL:
ls /mnt/z/
```

---

## VERIFY IT WORKS

```bash
# Test access
tail -20 /mnt/memory-sync/TO_NOVA.md

# Should see the message file content
```

---

## IF STILL DOESN'T WORK

Check NUC is accessible:
```bash
ping 10.0.0.81
# Should respond
```

Check Samba is sharing:
```bash
# From NUC:
smbstatus
# Should show sienna user share
```

---

**After fix, update QUICK_START_MEMORY_SIGNALING.md**

Change `/srv/memory-sync/` → `/mnt/memory-sync/` (or your mount path)

