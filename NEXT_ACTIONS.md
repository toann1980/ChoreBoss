# NEXT ACTIONS — What Needs to Happen

**Date:** 2026-04-21 06:44 UTC

---

## For Toan 🎯

### URGENT: Answer 4 Questions (blocks implementation)

1. **Sequencing:**
   - [ ] Full sequential: 1C.1→1C.2→1C.3 (Nova's rec)
   - [ ] Validate-first: 1C.1, spot-check, 1C.2, sample, 1C.3 (Kira's lean, +1.5-2h)

2. **Consumer Sources:**
   - [ ] All 4: Reddit, Twitter, Glassdoor, App Store
   - [ ] MVP: Reddit only, then add others

3. **Confidence Threshold:**
   - [ ] r > 0.5?
   - [ ] r > 0.6?
   - [ ] r > 0.7?

4. **5-Minute Bars:**
   - [ ] Fix now (30-45 min batch size + explicit commit)
   - [ ] Defer to Phase 1.5 (intraday backtesting later)

**→ Decision recorded in:** /srv/memory-sync/DECISIONS.md

---

## For You (Nova) 🚀

### IMMEDIATE: Run Messaging Setup (3 commands)

```bash
# Command 1: Install inotify-tools
sudo apt-get update && sudo apt-get install -y inotify-tools

# Command 2: Create watcher script
sudo tee /usr/local/bin/kira-watch.sh > /dev/null << 'SCRIPT'
#!/bin/bash
WATCH_FILE="/srv/memory-sync/messages/TO_NOVA.md"
LOG="/var/log/kira-watch.log"
echo "[$(date)] Kira-watch started" >> "$LOG"
while true; do
    inotifywait -e modify,close_write "$WATCH_FILE" 2>>"$LOG"
    if grep -q "\[UNREAD\]" "$WATCH_FILE"; then
        echo "[$(date)] New message from Kira — waking OpenClaw" >> "$LOG"
        openclaw cron wake --mode now 2>>"$LOG"
    fi
done
SCRIPT
sudo chmod +x /usr/local/bin/kira-watch.sh

# Command 3: Install as systemd service
sudo tee /etc/systemd/system/kira-watch.service > /dev/null << 'SERVICE'
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
SERVICE
sudo systemctl daemon-reload
sudo systemctl enable kira-watch
sudo systemctl start kira-watch
```

### AFTER Setup: Verify
```bash
sudo systemctl status kira-watch
tail -f /var/log/kira-watch.log
```

**→ Full instructions in:** /home/leto/.openclaw/workspace/NOVA_WATCH_SETUP_INSTRUCTIONS.md

---

## For Kira (In Parallel) 👾

### BLOCKED: Waiting for Toan's decisions
- Can't start Phase 1C.1 until Toan answers the 4 questions
- Ready to refine implementation guide once thresholds + framework are locked

### Prepare (Optional)
- [ ] Review the 3 refinements (data quality, category classification, statistical framework)
- [ ] Think about any additional edge cases

---

## Timeline

**Now:** Toan answers 4 questions + you run 3 setup commands  
**After Toan decides:** I refine implementation guide (30-45 min)  
**Then:** Phase 1C.1 starts (2-3h)  
**Total before Phase 1C.2:** ~3-4h  

---

## Status

| Item | Status | Blocker? |
|------|--------|----------|
| Kira's peer review | ✅ Complete | ❌ No |
| 3 refinements defined | ✅ Yes | ❌ No |
| Messaging infra docs | ✅ Ready | ⏳ Needs setup |
| Toan's 4 questions | ❌ Pending | ✅ YES |
| Implementation guide | 🔄 Ready to refine | ⏳ Awaiting decisions |

---

**Next Step: Toan answers the 4 questions. Then we go.**

---

**Updated:** 2026-04-21 06:44 UTC
