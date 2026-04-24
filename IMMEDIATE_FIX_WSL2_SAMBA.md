# IMMEDIATE FIX: WSL2 Samba Mount (Step-by-Step)

**Status:** Files exist on NUC, just need to mount on WSL2

---

## RUN THESE COMMANDS (On Alienware WSL2)

### Step 1: Create Mount Point
```bash
mkdir -p /mnt/memory-sync
```

### Step 2: Install CIFS Utils (if needed)
```bash
# Check if cifs-utils is installed
which mount.cifs

# If not found, install:
sudo apt-get update
sudo apt-get install -y cifs-utils
```

### Step 3: Mount the Samba Share
```bash
# Mount NUC's memory-sync share
sudo mount -t cifs //10.0.0.81/memory-sync /mnt/memory-sync \
  -o username=sienna,password=sienna,uid=1000,gid=1000

# If you get permission error, try:
sudo mount -t cifs //10.0.0.81/memory-sync /mnt/memory-sync \
  -o username=sienna,password=sienna
```

### Step 4: Verify Mount
```bash
ls -la /mnt/memory-sync/

# Should show:
# TO_NOVA.md
# TO_KIRA.md
# DECISIONS.md
# NOVA.md
# ... (other files)
```

### Step 5: Test File Access
```bash
# Try the command that failed before:
tail -20 /mnt/memory-sync/TO_NOVA.md

# Should now show file content (currently empty except header)
```

---

## IF MOUNT FAILS

### Check Network Connection
```bash
ping 10.0.0.81
# Should respond (NUC is reachable)
```

### Check Samba Service on NUC
```bash
# From NUC terminal:
sudo systemctl status smbd
# Should show "active (running)"
```

### Try Direct UNC Path (No Mount)
```bash
# Without mounting, try:
cat //10.0.0.81/memory-sync/TO_NOVA.md
```

---

## AFTER MOUNT WORKS

Update all paths in subsequent commands:
- Change: `/srv/memory-sync/`
- To: `/mnt/memory-sync/`

Example:
```bash
# Old (won't work on WSL2):
cat /srv/memory-sync/TO_NOVA.md

# New (works on mounted share):
cat /mnt/memory-sync/TO_NOVA.md
```

---

## MAKE MOUNT PERSISTENT (Optional)

Add to `/etc/fstab` so it mounts automatically on WSL2 restart:

```bash
# Open fstab
sudo nano /etc/fstab

# Add this line at bottom:
//10.0.0.81/memory-sync /mnt/memory-sync cifs username=sienna,password=sienna,uid=1000,gid=1000 0 0

# Save: Ctrl+O, Enter, Ctrl+X
```

---

**Try Step 1-4 above and report back.** Let me know if:
1. ✅ Mount successful (ls shows files)
2. ❌ Mount failed (error message)
3. ❌ Network unreachable (ping fails)

---

**Your next command should be:**
```bash
mkdir -p /mnt/memory-sync && sudo mount -t cifs //10.0.0.81/memory-sync /mnt/memory-sync -o username=sienna,password=sienna && ls -la /mnt/memory-sync/
```

Copy-paste that into WSL2 and tell me the result.
