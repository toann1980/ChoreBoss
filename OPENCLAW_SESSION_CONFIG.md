# OpenClaw Device/Session Timeout Configuration

**Date:** 2026-04-20  
**Issue:** Session requires reauthorization too frequently (want weekly instead)

---

## Current Setup

You have **6 paired devices:**
1. **openclaw-control-ui** (Win32) — 10.0.0.21 — Your main browser UI
2. **openclaw-control-ui** (Win32) — 10.0.0.21 — (duplicate/backup)
3. **openclaw-control-ui** (Win32) — 10.0.0.21 — (current, most recent)
4. **cli** (Linux) — This NUC machine — Operator mode
5. **openclaw-android** (Android) — Your S23 phone — Node + Operator
6. **openclaw-control-ui** (Win32) — (older, from 2026-04-19)

### Token Expiration

Each device has tokens with timestamps but **no explicit expiration field** visible.

---

## Where Session Timeout is Configured

The session/device reauth timeout is likely controlled at:

### 1. **Gateway Level** (Most Likely)
```bash
# Check gateway daemon config
~/.openclaw/gateway/config.json
```

Look for:
- `auth.sessionTimeout` (seconds)
- `auth.tokenExpiry` (seconds)
- `auth.refreshInterval` (seconds)

### 2. **Control UI Level**
The browser UI may have session duration settings:
```bash
~/.openclaw/agents/main/agent/auth-state.json
```

### 3. **Device Auth Policy**
```bash
~/.openclaw/identity/device-auth.json
# (already checked - shows tokens without expiry)
```

---

## How to Extend to Weekly (7 days)

### Option 1: Update Gateway Config (Recommended)

```bash
# Find gateway config
find ~/.openclaw -name "*.json" -path "*gateway*" -type f

# Edit (once located):
cat ~/.openclaw/gateway/config.json | jq . | grep -i "session\|timeout\|expir"
```

Look for these fields and update:
```json
{
  "auth": {
    "sessionTimeout": 604800,  // 7 days in seconds (7 * 24 * 60 * 60)
    "tokenExpiry": 604800,
    "refreshInterval": 604800
  }
}
```

### Option 2: Use OpenClaw CLI

```bash
# Check current settings
openclaw auth status

# Try to configure session timeout
openclaw configure --session-timeout 7d

# Or restart gateway with new config
openclaw gateway restart
```

### Option 3: Manual Token Rotation

The tokens in `paired.json` show `createdAtMs` and `lastUsedAtMs`. If the gateway is enforcing rotation:

```bash
# Approve the device once more with persistent token
# Then it should remember longer

# Check if there's a "trust" or "remember" option in the control UI
# Settings → Devices → [Your Device] → "Trust for 7 days"
```

---

## Quick Fix (Immediate)

### Remove Duplicate Devices

You have **3 nearly-identical Win32 control-ui entries** from 10.0.0.21. This might be causing re-pairing prompts:

```bash
# View current paired devices
jq 'keys' ~/.openclaw/devices/paired.json

# Consider removing older ones:
# - 5544e6ed... (oldest)
# - 47a72d7e... (older)
# - Keep only: 6e98defc... (most recent from 20:55)
```

To remove old devices:
```bash
# Backup first
cp ~/.openclaw/devices/paired.json ~/.openclaw/devices/paired.json.backup

# Edit to keep only the newest ones
# Then restart gateway
openclaw gateway restart
```

---

## Recommended Session Policy

For a home automation system, weekly makes sense:

```json
{
  "auth": {
    "sessionTimeout": 604800,        // 7 days
    "tokenExpiry": 604800,
    "refreshInterval": 259200,       // 3 days (refresh mid-week)
    "rememberDevice": true,          // Trust approved devices
    "requireMfaOnNewDevice": true,   // New devices need approval
    "maxDevicesPerUser": 10
  }
}
```

**Benefits:**
- ✅ Reauth only ~monthly instead of daily
- ✅ New devices still require approval
- ✅ Tokens refresh before expiry
- ✅ Balances security + usability

---

## Steps to Implement

1. **Find the config file:**
   ```bash
   find ~/.openclaw -name "*.json" | xargs grep -l "session\|timeout" 2>/dev/null
   ```

2. **Back it up:**
   ```bash
   cp <file> <file>.backup
   ```

3. **Edit the timeout value:**
   ```bash
   # 604800 seconds = 7 days
   # Update sessionTimeout, tokenExpiry, etc.
   ```

4. **Restart gateway:**
   ```bash
   openclaw gateway restart
   ```

5. **Test:**
   - Log out and log back in
   - Check if session lasts longer

---

## Alternative: Ask at discord.com/invite/clawd

If the config isn't where I think, the OpenClaw community can give exact paths for your setup.

---

## Current Session Status

```bash
# To see current session info
openclaw status

# To see gateway config
openclaw gateway status

# To view all auth tokens
jq '.tokens' ~/.openclaw/identity/device-auth.json
```

---

## Summary

**Problem:** Session timeout too short (you need weekly instead)  
**Root Cause:** Likely 1-day token expiry in gateway config  
**Solution:**
1. Find `~/.openclaw/gateway/config.json` or equivalent
2. Set `sessionTimeout: 604800` (7 days)
3. Restart: `openclaw gateway restart`
4. Optionally clean up duplicate devices

**Expected Result:** Reauth required only ~weekly instead of daily

Let me know if you find the config file and I can help update it! 🔑
