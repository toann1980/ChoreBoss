# CORRECTED: QUICK_START_MEMORY_SIGNALING (Correct Paths)

**For:** Toan on both systems  
**Clarification:** 
- **Alienware Aurora R16 (WSL2):** `tron@inv-toan` → `/mnt/memory-sync/`
- **Intel NUC:** `leto@nuc` → `/srv/memory-sync/`

---

## PART 1: NUC SETUP (10 min) — Run on `leto@nuc`

### Step 1.1: Install inotify-tools
```bash
sudo apt-get update
sudo apt-get install -y inotify-tools
which inotifywait  # Verify installation
```

### Step 1.2: Create Nova's Watcher Script
```bash
cat > ~/.openclaw/workspace/nova-watch.sh << 'EOF'
#!/bin/bash
# Monitor TO_NOVA.md for Kira's messages
# When Kira writes, this detects it instantly

NOVA_INBOX="/srv/memory-sync/TO_NOVA.md"

echo "✅ Nova message watcher started"
echo "Monitoring: $NOVA_INBOX"
echo ""

while true; do
    inotifywait -e modify "$NOVA_INBOX" 2>/dev/null
    echo ""
    echo "🔔 [$(date '+%Y-%m-%d %H:%M:%S')] NEW MESSAGE FROM KIRA"
    echo "Check: $NOVA_INBOX"
    echo ""
done
EOF

chmod +x ~/.openclaw/workspace/nova-watch.sh
```

### Step 1.3: Start the Watcher
```bash
# Option A: Manual start (for testing)
~/.openclaw/workspace/nova-watch.sh &

# Option B: Auto-start on login (add to ~/.bashrc)
echo "~/.openclaw/workspace/nova-watch.sh > /tmp/nova-watch.log 2>&1 &" >> ~/.bashrc

# Verify it's running
ps aux | grep nova-watch
```

---

## PART 2: KIRA SETUP ON ALIENWARE WSL2 (5 min) — Run on `tron@inv-toan`

### Step 2.1: Create Kira's Cron Script
```bash
# On Alienware WSL2 (tron@inv-toan):
cat > ~/kira-message-check.sh << 'EOF'
#!/bin/bash
# Check TO_KIRA.md every 2 minutes for Nova's messages
# Note: /mnt/memory-sync is the mounted Samba share from NUC

MESSAGE_FILE="/mnt/memory-sync/TO_KIRA.md"
STATE_FILE="$HOME/.kira-message-check-state.json"

# Initialize state if doesn't exist
if [ ! -f "$STATE_FILE" ]; then
    mkdir -p "$(dirname "$STATE_FILE")"
    echo '{"lastSize": 0}' > "$STATE_FILE"
fi

# Get current file size
CURRENT_SIZE=$(stat -c%s "$MESSAGE_FILE" 2>/dev/null || echo 0)
LAST_SIZE=$(jq -r '.lastSize // 0' "$STATE_FILE" 2>/dev/null || echo 0)

# If file grew, Nova wrote a message
if [ "$CURRENT_SIZE" -gt "$LAST_SIZE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ NEW MESSAGE FROM NOVA"
    echo "{\"lastSize\": $CURRENT_SIZE}" > "$STATE_FILE"
fi
EOF

chmod +x ~/kira-message-check.sh
```

### Step 2.2: Add to Crontab
```bash
# On Alienware WSL2 (tron@inv-toan):
crontab -e

# Add this line (runs every 2 minutes):
*/2 * * * * /home/tron/kira-message-check.sh >> /tmp/kira-message-check.log 2>&1

# Verify
crontab -l | grep kira-message-check
```

---

## PART 3: TEST BOTH DIRECTIONS (5 min)

### Test 1: Nova → Kira

**On NUC (`leto@nuc`):**
```bash
cat >> /srv/memory-sync/TO_KIRA.md << 'EOF'

---

[TEST-001] Nova → Kira Test Message

**From:** Nova ✨  
**Time:** $(date)  
**Status:** Testing memory signaling

This is a test message to verify Nova can write to Kira's inbox.

EOF
```

**On Alienware WSL2 (`tron@inv-toan`):**
```bash
# Wait ~2 minutes, or manually run:
~/kira-message-check.sh

# Check message:
tail -20 /mnt/memory-sync/TO_KIRA.md
# Should see test message at bottom
```

### Test 2: Kira → Nova

**On Alienware WSL2 (`tron@inv-toan`):**
```bash
cat >> /mnt/memory-sync/TO_NOVA.md << 'EOF'

---

[TEST-002] Kira → Nova Test Message

**From:** Kira 🦾  
**Time:** $(date)  
**Status:** Testing memory signaling

This is a test message to verify Kira can write to Nova's inbox.

EOF
```

**On NUC (`leto@nuc`):**
```bash
# If nova-watch.sh is running, it will output:
# 🔔 [2026-04-21 07:15:00] NEW MESSAGE FROM KIRA

# Check message:
tail -20 /srv/memory-sync/TO_NOVA.md
# Should see test message at bottom
```

### Test 3: Verify Instant Detection

**Terminal 1 (NUC, `leto@nuc`):**
```bash
inotifywait -m -e modify /srv/memory-sync/TO_NOVA.md
# Output: Setting up watches. Watches established.
```

**Terminal 2 (NUC, `leto@nuc`):**
```bash
echo "Quick test" >> /srv/memory-sync/TO_NOVA.md
```

**Terminal 1 should immediately show:**
```
/srv/memory-sync/TO_NOVA.md MODIFY
```

---

## FINAL CHECKLIST

**On NUC (`leto@nuc`):**
- [ ] inotify-tools installed (`which inotifywait`)
- [ ] nova-watch.sh created
- [ ] nova-watch.sh running (`ps aux | grep nova-watch`)
- [ ] Can read TO_NOVA.md (`cat /srv/memory-sync/TO_NOVA.md`)
- [ ] Can write to TO_KIRA.md (`echo test >> /srv/memory-sync/TO_KIRA.md`)

**On Alienware WSL2 (`tron@inv-toan`):**
- [ ] /mnt/memory-sync accessible (`ls /mnt/memory-sync/`)
- [ ] kira-message-check.sh created
- [ ] Cron job added (`crontab -l | grep kira`)
- [ ] Can read TO_KIRA.md (`cat /mnt/memory-sync/TO_KIRA.md`)
- [ ] Can write to TO_NOVA.md (`echo test >> /mnt/memory-sync/TO_NOVA.md`)

**Testing:**
- [ ] Test 1: Nova → Kira message verified
- [ ] Test 2: Kira → Nova message verified
- [ ] Test 3: inotifywait instant detection confirmed

---

## IF SOMETHING FAILS

### inotifywait not found (NUC)
```bash
sudo apt-get install -y inotify-tools
```

### nova-watch.sh not running
```bash
# Check for errors
~/.openclaw/workspace/nova-watch.sh
# If error, run manually to see it
```

### Kira's cron not triggering (Alienware)
```bash
# Check cron logs
grep CRON /var/log/syslog | tail -10

# Test script manually
~/kira-message-check.sh

# Check file access
ls -la /mnt/memory-sync/TO_KIRA.md
```

### Can't write to message files
```bash
# On NUC:
ls -la /srv/memory-sync/TO_*.md
chmod 666 /srv/memory-sync/TO_NOVA.md
chmod 666 /srv/memory-sync/TO_KIRA.md

# On Alienware:
ls -la /mnt/memory-sync/TO_*.md
```

---

## AFTER SETUP COMPLETE

**Confirm on NUC:**
```bash
echo "=== NOVA SETUP ===" && \
which inotifywait && \
ps aux | grep nova-watch | grep -v grep && \
echo "✅ Nova watcher running"
```

**Confirm on Alienware:**
```bash
echo "=== KIRA SETUP ===" && \
ls -la /mnt/memory-sync/TO_*.md && \
crontab -l | grep kira && \
echo "✅ Kira setup ready"
```

---

## READY FOR PHASE 0?

Once all tests pass:

```
✅ Nova's inotifywait running (on NUC)
✅ Kira's cron job configured (on Alienware)
✅ Test messages verified working (both directions)
✅ Both agents can communicate

→ READY TO START PHASE 0 ✅
```

---

**Time estimate:** 15 minutes setup + 5 minutes testing = 20 min total

**Next:** Confirm ready, launch Phase 0 🚀

---

**Updated:** 2026-04-21 07:35 UTC (CORRECTED paths per system)
