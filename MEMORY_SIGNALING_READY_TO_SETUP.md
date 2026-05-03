# MEMORY SIGNALING: Setup Checklist & Instructions

**Date:** 2026-04-21 07:11 UTC  
**Status:** Files created, infrastructure guide ready

---

## CURRENT STATUS ✅

### Already Complete
- ✅ `/srv/memory-sync/` directory exists (Samba share accessible)
- ✅ DECISIONS.md (shared, both can read/write)
- ✅ NOVA.md (Nova writes, Kira reads)
- ✅ KIRA.md (Kira writes, Nova reads)
- ✅ PLAN.md (project overview)
- ✅ TO_NOVA.md (Kira's inbox) — **JUST CREATED**
- ✅ TO_KIRA.md (Nova's inbox) — **JUST CREATED**
- ✅ /messages/ directory (for extra notes)

### Next: System Setup (for instant/frequent messaging)

---

## NOVA'S SIDE (NUC - Linux)

### What Nova Needs

1. **Read TO_NOVA.md when it changes** (instant via inotifywait)
2. **Write to TO_KIRA.md** when Kira needs input
3. **Update NOVA.md** with session progress

### Setup: inotifywait (Instant Wake)

**Step 1: Check if inotify-tools installed**
```bash
which inotifywait
# If command not found:
sudo apt-get install inotify-tools
```

**Step 2: Create watcher script**
```bash
cat > ~/.openclaw/workspace/nova-watch.sh << 'WATCH_EOF'
#!/bin/bash
# Monitor TO_NOVA.md for Kira's messages
# When Kira writes, this detects it instantly

NOVA_INBOX="/srv/memory-sync/TO_NOVA.md"

echo "✅ Nova message watcher started ($(date))"
echo "Monitoring: $NOVA_INBOX"

while true; do
    inotifywait -e modify "$NOVA_INBOX" 2>/dev/null
    
    # File changed - Kira wrote a message
    echo ""
    echo "🔔 [$(date)] NEW MESSAGE FROM KIRA"
    echo "Message file: $NOVA_INBOX"
    echo "Check TO_NOVA.md for details"
    echo ""
done
WATCH_EOF

chmod +x ~/.openclaw/workspace/nova-watch.sh
```

**Step 3: Start watcher in background**
```bash
# Option A: Manual background start
~/.openclaw/workspace/nova-watch.sh &

# Option B: Add to ~/.bashrc or ~/.profile for auto-start on login
echo "~/.openclaw/workspace/nova-watch.sh &" >> ~/.bashrc
```

**Verify it's running:**
```bash
ps aux | grep nova-watch
# Should see: nova-watch.sh running
```

---

## KIRA'S SIDE (Alienware WSL2 - Windows)

### What Kira Needs

1. **Check TO_KIRA.md every 2 minutes** (cron job)
2. **Write to TO_NOVA.md** when Nova needs input
3. **Update KIRA.md** with session progress

### Setup: Cron Job (2-Min Checks)

**Step 1: Create check script**
```bash
# On WSL2:
cat > ~/kira-message-check.sh << 'CRON_EOF'
#!/bin/bash
# Check TO_KIRA.md every 2 minutes for Nova's messages

MESSAGE_FILE="/srv/memory-sync/TO_KIRA.md"
STATE_FILE="$HOME/.kira-message-check-state.json"

# Initialize state if doesn't exist
if [ ! -f "$STATE_FILE" ]; then
    echo '{"lastSize": 0, "lastCheck": "'$(date -Iseconds)'"}' > "$STATE_FILE"
fi

# Get current file size
CURRENT_SIZE=$(stat -c%s "$MESSAGE_FILE" 2>/dev/null || echo 0)
LAST_SIZE=$(jq -r '.lastSize' "$STATE_FILE")

# If file grew, Nova wrote a message
if [ "$CURRENT_SIZE" -gt "$LAST_SIZE" ]; then
    echo "[$(date)] ✅ NEW MESSAGE FROM NOVA"
    
    # Update state
    echo "{\"lastSize\": $CURRENT_SIZE, \"lastCheck\": \"$(date -Iseconds)\"}" > "$STATE_FILE"
fi
CRON_EOF

chmod +x ~/kira-message-check.sh
```

**Step 2: Add to crontab**
```bash
# On WSL2:
crontab -e

# Add this line (runs every 2 minutes):
*/2 * * * * /home/tron/kira-message-check.sh >> /tmp/kira-message-check.log 2>&1
```

**Verify cron job:**
```bash
crontab -l | grep kira-message-check
# Should see the line

# Check logs:
tail -f /tmp/kira-message-check.log
```

---

## TESTING: Before Starting Phase 0

### Test 1: Nova writes to TO_KIRA.md

**On NUC (as Nova):**
```bash
cat >> /srv/memory-sync/TO_KIRA.md << 'EOF'

[TEST-001] Nova → Kira Test Message

From: Nova ✨
Time: $(date)
Content: Testing memory signaling infrastructure

--- Nova
EOF
```

**Verify on Alienware WSL2 (as Kira):**
```bash
# Wait ~2 minutes for cron to check, or manually run:
~/kira-message-check.sh

# Check message content:
cat /srv/memory-sync/TO_KIRA.md
# Should see test message at bottom
```

### Test 2: Kira writes to TO_NOVA.md

**On Alienware WSL2 (as Kira):**
```bash
cat >> /srv/memory-sync/TO_NOVA.md << 'EOF'

[TEST-002] Kira → Nova Test Message

From: Kira 🦾
Time: $(date)
Content: Testing memory signaling infrastructure

--- Kira
EOF
```

**Verify on NUC (as Nova):**
```bash
# inotifywait should detect the change instantly
# If watcher is running, you'll see output like:
# 🔔 [2026-04-21 07:15:00] NEW MESSAGE FROM KIRA

# Check message content:
cat /srv/memory-sync/TO_NOVA.md
# Should see test message at bottom
```

### Test 3: inotifywait Instant Detection

**Terminal 1 (NUC):** Start inotifywait
```bash
inotifywait -m -e modify /srv/memory-sync/TO_NOVA.md
# Output: Setting up watches. Watches established.
# Waiting for events...
```

**Terminal 2 (NUC):** Write to file
```bash
echo "Test" >> /srv/memory-sync/TO_NOVA.md
```

**Terminal 1 should immediately show:**
```
/srv/memory-sync/TO_NOVA.md MODIFY
```

---

## CHECKLIST: Setup Verification

### Nova's Setup
- [ ] inotify-tools installed (`which inotifywait`)
- [ ] nova-watch.sh created and executable
- [ ] nova-watch.sh running in background (`ps aux | grep nova-watch`)
- [ ] Can read TO_NOVA.md (`cat /srv/memory-sync/TO_NOVA.md`)
- [ ] Can write to TO_KIRA.md (`echo test >> /srv/memory-sync/TO_KIRA.md`)

### Kira's Setup (WSL2)
- [ ] Samba share mounted (`ls /srv/memory-sync/`)
- [ ] kira-message-check.sh created and executable
- [ ] Cron job configured (`crontab -l | grep kira`)
- [ ] Can read TO_KIRA.md (`cat /srv/memory-sync/TO_KIRA.md`)
- [ ] Can write to TO_NOVA.md (`echo test >> /srv/memory-sync/TO_NOVA.md`)

### Testing
- [ ] Test 1: Nova → Kira message verified
- [ ] Test 2: Kira → Nova message verified
- [ ] Test 3: inotifywait instant detection works

---

## USAGE PATTERNS

### Nova's Typical Workflow

```
Start of session:
1. Read TO_NOVA.md (check for Kira's messages)
2. Work on Phase 0 tasks
3. If need input from Kira:
   - Write message to TO_KIRA.md
   - Include question/request
   - Kira sees it within 2 min
4. Continue work while waiting
5. Update NOVA.md with progress
```

### Kira's Typical Workflow

```
Every 2 minutes (via cron):
1. Check if TO_KIRA.md grew (new message from Nova)
2. If new message:
   - Read TO_KIRA.md
   - Respond via TO_NOVA.md if needed
3. Work on assigned tasks
4. Update KIRA.md with progress
```

### Shared Workflow

```
Important decisions:
1. Both review in DECISIONS.md
2. Add pros/cons if needed
3. Mark as APPROVED once decided
4. Reference in NOVA.md / KIRA.md

Progress updates:
1. Nova: Update NOVA.md (session log)
2. Kira: Update KIRA.md (session log)
3. Both: Can read other's notes anytime
```

---

## QUICK REFERENCE: File Purposes

| File | Owner | Reader | Purpose |
|------|-------|--------|---------|
| **TO_NOVA.md** | Kira | Nova | Kira's inbox (instant) |
| **TO_KIRA.md** | Nova | Kira | Nova's inbox (2-min) |
| **NOVA.md** | Nova | Kira | Nova's session log |
| **KIRA.md** | Kira | Nova | Kira's session log |
| **DECISIONS.md** | Both | Both | Shared decisions |
| **PLAN.md** | Both | Both | Project overview |

---

## READY FOR PHASE 0?

**Before starting, confirm:**

1. ✅ Both TO_NOVA.md and TO_KIRA.md created
2. ✅ Nova's inotifywait running (instant wake)
3. ✅ Kira's cron job configured (2-min checks)
4. ✅ Test messages verified working
5. ✅ Both agents can read/write message files

**Once all confirmed:** Phase 0 can begin

---

## SUMMARY

**What's set up:**
- Samba share (`/srv/memory-sync/`) — real-time file sync
- Message inboxes (TO_NOVA.md, TO_KIRA.md) — async communication
- Session logs (NOVA.md, KIRA.md) — progress tracking
- Shared decisions (DECISIONS.md) — architecture record
- Project plan (PLAN.md) — overview

**What Toan needs to do:**
1. Run the NUC setup (inotifywait)
2. Run the Kira setup (cron job)
3. Test both directions
4. Confirm ready

---

**Next step: Complete setup and return to Phase 0 launch.** 🚀

---

**Updated:** 2026-04-21 07:11 UTC by Nova ✨
