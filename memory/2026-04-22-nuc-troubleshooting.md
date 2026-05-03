# NUC Troubleshooting Session: 2026-04-22

## Issue Summary
Remote access to Envestero services (ports 3000, 8000, 5432) failed from Windows despite services appearing to be running.

## Root Cause
**Docker containers were NOT actually running** — they had been stopped/crashed at some point.

We spent 3+ hours investigating firewall issues when the real problem was simply "no services listening on those ports."

## Critical Methodology Lesson (From Toan)

**After EVERY fix attempt, immediately:**
1. Query services locally (on NUC) — instant feedback
2. Check pertinent logs right away
3. Test locally first (curl/netstat) before asking user to test
4. Verify the assumed problem STILL EXISTS before proceeding
5. Don't assume — validate with actual data

**Why:** I can diagnose on NUC in seconds. User testing from Windows takes minutes. Avoid slow feedback loops.

### Troubleshooting Sequence (CORRECT WAY)

```bash
# IMMEDIATELY after a fix (do this on NUC):
docker ps                                          # Services running?
docker compose logs --tail=20                      # Any errors?
ss -tlnp | grep -E "3000|8000|5432"               # Ports listening?
curl -s http://localhost:3000 | head -5            # Local test: Dashboard
curl -s http://localhost:8000/api/dashboard/status # Local test: API

# Only THEN ask user to test from Windows:
# Test-NetConnection -ComputerName 10.0.0.81 -Port 3000
```

### Anti-Pattern (What I Did Wrong)
❌ Assume problem persists → Deep dive into firewall → Spend 3 hours → Ask user to test → Discover services weren't running

### Better Pattern
✅ Fix applied → Immediate local validation → Ask user to test from Windows → Done in minutes

**Key lesson:** Don't get locked into a hypothesis. Verify assumptions constantly with local diagnostics.

---

## What Actually Happened (Timeline)

1. **Reported:** Windows → NUC TCP connections timing out (ping worked, TCP failed)
2. **Initial diagnosis:** Assumed Windows Firewall blocking
3. **Secondary discovery:** UFW was uninstalled, iptables rules corrupted
4. **Deep dive:** Fixed UFW config, added rules, verified iptables
5. **The real issue:** After all firewall fixes, ran `docker ps` — **no containers running**

## Key Learnings

### 1. Always Check Services First
**Next time approach:**
```bash
# FIRST check services are actually running
docker ps
docker compose ps

# THEN check network/firewall
ping <host>
ss -tlnp | grep <port>
```

Don't assume services are running just because Docker is installed.

### 2. UFW + Docker Interaction Issues
**What we learned:**
- UFW can be uninstalled during Docker updates without user confirmation
- Iptables rules file can become corrupted with duplicate/malformed blocks
- Docker's iptables chains must be reinitialized after firewall changes
- UFW config persists even if command is removed

**Prevention:**
```bash
# After any system/Docker update, check:
which ufw && sudo ufw status || echo "UFW MISSING"
dpkg -l | grep ufw
sudo iptables-restore -t < /etc/iptables/rules.v4 2>&1 | head -5
```

### 3. Firewall Rules Are Loaded, But Services Must Listen
**Discovery:**
- UFW rules were correctly configured: `ALLOW 3000/tcp`, `ALLOW 8000/tcp`
- Iptables showed rules loaded: `-A ufw-user-input ... --dport 8000 -j ACCEPT`
- Packet counters showed some traffic being accepted: `25 1300` for port 8000
- **But** no service was listening on those ports

**Lesson:** Firewall rules passing traffic doesn't mean services are running.

### 4. Docker Compose Auto-Restart Policy
**Problem we fixed:**
- No `restart_policy` defined in docker-compose.yml
- Containers stayed stopped after system reboot or crash
- No automatic recovery mechanism

**Solution applied:**
```yaml
restart_policy:
  condition: always
  delay: 5s
  max_attempts: 3
  window: 120s
```

All three services now auto-restart on failure.

## NUC Production Checklist

- [ ] Docker services have `restart_policy: condition: always`
- [ ] UFW installed and running (`sudo ufw status`)
- [ ] Iptables rules valid (no errors on `sudo ufw reload`)
- [ ] Docker ports open: 3000/tcp, 8000/tcp, 5432/tcp
- [ ] Containers auto-start on reboot
- [ ] Monitor UFW logs for blocked traffic: `sudo journalctl -u ufw -f`

## Files Modified

- `/srv/github/Envestero/docker-compose.yml` — Added restart policies
- `/etc/ufw/after.rules` — Fixed corrupted DOCKER FIX blocks
- `/etc/iptables/rules.v4` — Validated iptables configuration

## Time Spent

- **Investigation:** ~3 hours (mostly firewall deep dive)
- **Actual fix:** 2 minutes (add restart policies)
- **Lesson learned:** Massive — methodology fix for future

## Future Prevention

1. **Validate assumptions immediately** — Don't get locked into a hypothesis
2. **Always restart Docker after UFW changes:**
   ```bash
   sudo systemctl restart docker
   ```

3. **Monitor container health:**
   ```bash
   docker compose logs -f
   ```

4. **Test full reboot cycle:**
   ```bash
   sudo reboot
   sleep 30
   docker compose ps  # Verify auto-start worked
   ```

5. **Local diagnostics first** — Use NUC tools before asking user to test

## Bottom Line

**Check services (docker ps) before debugging infrastructure.** I can validate locally in 10 seconds. You testing from Windows takes 2+ minutes. Optimization: local validation → early problem discovery → faster user testing → fewer iterations.
