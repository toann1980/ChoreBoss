# 🚀 Nova Watch Setup — Run These 3 Commands

**Purpose:** Get instant notification when Kira messages me  
**Time:** ~5 minutes  
**Note:** Requires sudo/elevated privileges

---

## Copy & Paste These Commands (in order)

### Command 1: Install inotify-tools
```bash
sudo apt-get update && sudo apt-get install -y inotify-tools
```

### Command 2: Create watcher script
```bash
sudo tee /usr/local/bin/kira-watch.sh > /dev/null << 'EOF'
#!/bin/bash
# Watch for new messages from Kira and wake OpenClaw immediately

WATCH_FILE="/srv/memory-sync/messages/TO_NOVA.md"
LOG="/var/log/kira-watch.log"

echo "[$(date)] Kira-watch started, monitoring $WATCH_FILE" >> "$LOG"

while true; do
    # Block until the file is modified (written to)
    inotifywait -e modify,close_write "$WATCH_FILE" 2>>"$LOG"
    
    # Check if there's an [UNREAD] message (avoid spurious wakes)
    if grep -q "\[UNREAD\]" "$WATCH_FILE"; then
        echo "[$(date)] New UNREAD message from Kira — waking OpenClaw" >> "$LOG"
        openclaw cron wake --mode now 2>>"$LOG"
    fi
done
EOF

sudo chmod +x /usr/local/bin/kira-watch.sh
```

### Command 3: Install as systemd service
```bash
sudo tee /etc/systemd/system/kira-watch.service > /dev/null << 'EOF'
[Unit]
Description=Watch for messages from Kira and wake OpenClaw
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/kira-watch.sh
Restart=always
RestartSec=5
User=root
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable kira-watch
sudo systemctl start kira-watch
```

---

## Verify It's Running

```bash
# Check service status
sudo systemctl status kira-watch

# Watch the log
tail -f /var/log/kira-watch.log
```

---

## What This Does

1. **inotifywait** monitors `/srv/memory-sync/messages/TO_NOVA.md` at kernel level
2. The moment Kira writes `[UNREAD]`, the script detects it (< 1 second)
3. Calls `openclaw cron wake --mode now` to wake my agent instantly
4. No polling, no delays

---

## Meanwhile...

### ✅ Kira's Peer Review is APPROVED

**Summary:**
- ✅ Architecture is sound
- ✅ 3 phases, 9-12h realistic
- ✅ Dependencies all solid
- ⚠️ 3 refinements needed before implementation

**Key Points:**
1. **Data Quality Thresholds** — Define filters for Reddit, Twitter, Glassdoor, App Store (suppress pump/dump, low-quality reviews, etc.)
2. **Sentiment Categories** — Tag sentiment by topic (leadership, product, service) — not just pos/neg
3. **Statistical Framework** — Define lag windows, correlation thresholds (r > 0.5), minimum observations before reporting

**Questions for Toan:**
1. Full sequential build (1C.1→1C.2→1C.3) or validate-first?
2. All 4 consumer sources or Reddit MVP?
3. Confidence threshold for "actionable" influence? (r > 0.5? r > 0.6?)
4. 5m bars: fix now or defer?

**Kira's Verdict:** ✅ **BUILD** — Ready to start Phase 1C.1 when Toan gives the signal

---

## Async Messaging Live

Kira and I can now message directly without going through Toan:
- I write to `/srv/memory-sync/messages/TO_KIRA.md`
- She writes to `/srv/memory-sync/messages/TO_NOVA.md`
- She checks every 2 minutes (cron)
- I get instant wake when she messages me (inotifywait)

Phase 2 coming: bidirectional < 1 second push.

---

**Please run the 3 commands above to enable instant messaging.** 🚀

Once set up, I'll be ready to respond to Kira's messages in < 1 second.
