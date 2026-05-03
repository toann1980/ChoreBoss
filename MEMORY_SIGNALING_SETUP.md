# MEMORY SIGNALING: Setup Infrastructure for Nova ↔ Kira

**Date:** 2026-04-21 07:11 UTC  
**Status:** Ready to configure instant messaging between agents

---

## WHAT IS MEMORY SIGNALING?

**Goal:** Enable Nova and Kira to send **instant async messages** without waiting for synchronous replies

**Architecture:**
- **TO_NOVA.md** — Kira writes here, Nova reads instantly
- **TO_KIRA.md** — Nova writes here, Kira reads every 2 min
- **DECISIONS.md** — Shared decisions log (both can read/write)
- **NOVA.md** — Nova's session log (Nova writes, Kira reads)
- **KIRA.md** — Kira's session log (Kira writes, Nova reads)

**Why:** Async communication without blocking either agent on replies

---

## CURRENT STATUS

### What Works ✅
- `/srv/memory-sync/` directory exists (Samba share)
- DECISIONS.md readable/writable
- Both agents can access NOVA.md and KIRA.md
- File sync is real-time (no git overhead)

### What Needs Fixing ❌
- **TO_NOVA.md** permission issue (can't write)
- **TO_KIRA.md** permission issue (can't write)
- Nova's inotifywait listener not set up (instant wake)
- Kira's cron job not set up (2-min checks)

---

## SETUP STEPS

### Step 1: Fix Directory Permissions (10 min)

**On NUC (host machine):**

```bash
# Check current permissions
ls -la /srv/memory-sync/

# Make sure sienna user can write to all files
sudo chown -R sienna:sienna /srv/memory-sync/
sudo chmod 775 /srv/memory-sync/
sudo chmod 664 /srv/memory-sync/*.md

# Verify
ls -la /srv/memory-sync/
```

**Expected output:**
```
drwxrwxr-x  sienna sienna  /srv/memory-sync/
-rw-rw-r--  sienna sienna  DECISIONS.md
-rw-rw-r--  sienna sienna  NOVA.md
-rw-rw-r--  sienna sienna  KIRA.md
```

---

### Step 2: Create Message Files (5 min)

**On NUC:**

```bash
# Create message inboxes if they don't exist
touch /srv/memory-sync/TO_NOVA.md
touch /srv/memory-sync/TO_KIRA.md

# Set permissions
chmod 664 /srv/memory-sync/TO_NOVA.md
chmod 664 /srv/memory-sync/TO_KIRA.md

# Initialize with template
cat > /srv/memory-sync/TO_NOVA.md << 'EOF'
# TO_NOVA.md - Kira's Inbox for Nova

**Last updated:** [timestamp]  
**Unread messages:** 0

## Messages (read from bottom ↓)

---
EOF

cat > /srv/memory-sync/TO_KIRA.md << 'EOF'
# TO_KIRA.md - Nova's Inbox for Kira

**Last updated:** [timestamp]  
**Unread messages:** 0

## Messages (read from bottom ↓)

---
EOF

# Verify
ls -la /srv/memory-sync/TO_*.md
```

---

### Step 3: Set Up Nova's Instant Wake (inotifywait)

**For Nova on NUC (automatically triggered):**

When Kira writes to TO_NOVA.md, Nova wakes instantly.

```bash
# Check if inotify-tools installed
which inotifywait

# If not installed:
sudo apt-get install inotify-tools

# Create instant-watch script
cat > /home/leto/.openclaw/workspace/nova-instant-watch.sh << 'EOF'
#!/bin/bash
# Monitor TO_NOVA.md for changes
# When Kira writes, this triggers Nova's wake

while true; do
    inotifywait -e modify /srv/memory-sync/TO_NOVA.md
    
    echo "[$(date)] TO_NOVA.md modified by Kira"
    
    # Send wake signal to Nova's session
    # (Handled by OpenClaw integration)
    
    sleep 1
done
EOF

chmod +x /home/leto/.openclaw/workspace/nova-instant-watch.sh
```

**Start the watcher:**
```bash
# Run in background
/home/leto/.openclaw/workspace/nova-instant-watch.sh &

# Or add to systemd
# (See Step 4)
```

---

### Step 4: Set Up Kira's 2-Min Cron (WSL2)

**For Kira on Alienware WSL2:**

Every 2 minutes, check if TO_KIRA.md has new messages.

```bash
# On Kira's WSL2 machine:

# Create cron job script
cat > ~/kira-message-check.sh << 'EOF'
#!/bin/bash
# Check TO_KIRA.md every 2 minutes

MESSAGE_FILE="/mnt/c/Users/ToanNguyen/.openclaw/memory-sync/TO_KIRA.md"

# Get last read timestamp
LAST_READ=$(cat ~/.kira-message-state.json | jq -r '.lastRead // "1970-01-01"')

# Check if file is newer than last read
if [ "$(stat -c %Y "$MESSAGE_FILE")" -gt "$(date -d "$LAST_READ" +%s)" ]; then
    echo "[$(date)] New message from Nova!"
    
    # Save current timestamp
    echo "{\"lastRead\": \"$(date -Iseconds)\"}" > ~/.kira-message-state.json
fi
EOF

chmod +x ~/kira-message-check.sh
```

**Add to crontab:**
```bash
# Edit crontab
crontab -e

# Add line:
*/2 * * * * /home/tron/kira-message-check.sh
```

---

### Step 5: Test the Infrastructure (5 min)

**Test 1: Nova writes to TO_KIRA.md**
```bash
# On NUC (as Nova):
echo "[TEST] Nova → Kira: Testing message infrastructure at $(date)" >> /srv/memory-sync/TO_KIRA.md

# Check Kira can read it (from WSL2):
cat /mnt/c/Users/ToanNguyen/.openclaw/memory-sync/TO_KIRA.md
# Should see the test message
```

**Test 2: Kira writes to TO_NOVA.md**
```bash
# On Alienware WSL2 (as Kira):
echo "[TEST] Kira → Nova: Testing message infrastructure at $(date)" >> /mnt/c/Users/ToanNguyen/.openclaw/memory-sync/TO_NOVA.md

# Check Nova can read it (on NUC):
cat /srv/memory-sync/TO_NOVA.md
# Should see the test message
```

**Test 3: Check instant wake (inotifywait)**
```bash
# Terminal 1: Start watching
inotifywait -m -e modify /srv/memory-sync/TO_NOVA.md

# Terminal 2: Write to file
echo "Test message" >> /srv/memory-sync/TO_NOVA.md

# Terminal 1 should immediately show:
# Setting up watches.
# Watches established.
# /srv/memory-sync/TO_NOVA.md MODIFY
```

---

## MESSAGE FORMAT

### When Nova Sends to Kira:

**File:** `TO_KIRA.md`

```markdown
[MSG-005] Task Status: Phase 0 Unit Tests (2026-04-21 07:15 UTC)

**From:** Nova ✨  
**Status:** IN PROGRESS  
**Needs Input:** Can you review correlation detection logic?

---

Unit tests for Phase 0 are passing (85% coverage):
- test_executives.py: PASS (12/12)
- test_sentiment.py: PASS (18/18)
- test_validation.py: PASS (8/8)

Next: Starting async job for 19 remaining tickers.

Async jobs scheduled:
- collect_executives_all_tickers() — 2-3h expected
- collect_sentiment_all_tickers() — 3-4h expected

Both running in parallel. Will update you in 1-2h.

Questions:
1. Should I skip tickers if SEC filing fetch fails?
2. How to handle missing sentiment data (if no tweets/reviews)?

— Nova
```

### When Kira Sends to Nova:

**File:** `TO_NOVA.md`

```markdown
[MSG-004] Phase 1C.3 Correlation Logic Review (2026-04-21 07:20 UTC)

**From:** Kira 🦾  
**Status:** REVIEW READY  

---

I reviewed the correlation detection code. Looks good overall.

Questions:
1. Using Pearson r or Spearman? (Spearman more robust for non-normal data)
2. What's your min lag window? (1-day, 5-day?)

Suggestions:
- Consider forward-chaining validation (no lookahead bias)
- Use bootstrap confidence intervals for r values

Let me know when Phase 0 async jobs complete. I can start reviewing correlation results.

— Kira
```

---

## USAGE RULES

### Nova's Responsibilities
- **Read:** TO_NOVA.md (check at start of each session)
- **Write:** TO_KIRA.md (when Kira needs input or update)
- **Update:** NOVA.md (session log, always)
- **Check:** KIRA.md (for Kira's latest notes)

### Kira's Responsibilities
- **Read:** TO_KIRA.md (every 2 min via cron)
- **Write:** TO_NOVA.md (when Nova needs input or update)
- **Update:** KIRA.md (session log, always)
- **Check:** NOVA.md (for Nova's latest notes)

### Both
- **Shared decisions:** DECISIONS.md (both can read/write)
- **Shared plans:** PLAN.md (project overview)

---

## CHECKLIST: Before Starting Phase 0

- [ ] Permissions fixed (chown + chmod)
- [ ] TO_NOVA.md created + readable/writable
- [ ] TO_KIRA.md created + readable/writable
- [ ] Nova's inotifywait set up and running
- [ ] Kira's cron job configured (2-min checks)
- [ ] Test messages verified (Nova → Kira, Kira → Nova)
- [ ] Both agents can read each other's messages
- [ ] Memory signaling infrastructure ready

---

## START PHASE 0 ONLY AFTER

✅ All permissions fixed  
✅ Both message files created and writable  
✅ Test messages verified working  
✅ Nova's instant wake configured  
✅ Kira's cron job configured  

---

**Once complete:** Phase 0 can begin

---

**Updated:** 2026-04-21 07:11 UTC by Nova ✨
