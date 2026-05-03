# OpenClaw Session Timeout — Configuration Guide

**Goal:** Extend device session from daily to weekly reauth

---

## Direct Solution (3 Steps)

### Step 1: Check Current Gateway Config
```bash
# View main OpenClaw config
cat ~/.openclaw/openclaw.json | jq '.gateway'

# Output will show something like:
# {
#   "mode": "local",
#   "auth": {...},
#   "port": 18789,
#   ...
# }
```

### Step 2: Add Session Timeout to Config

Edit `~/.openclaw/openclaw.json` and add this to the `gateway` section:

```json
{
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "sessionTimeout": 604800,      // 7 days = 604800 seconds
      "deviceTrustPeriod": 604800,   // Trust device for 7 days
      "tokenRefreshInterval": 259200  // Refresh tokens every 3 days
    },
    ...rest of config...
  }
}
```

### Step 3: Restart Gateway

```bash
# Restart to apply changes
openclaw gateway restart

# Verify it's running
openclaw gateway status

# Should show session timeout in the status output
```

---

## Alternative: Clean Up Duplicate Devices First

You have **3 nearly-identical control-ui entries** that might be triggering re-pairing:

```bash
# View your paired devices
jq 'to_entries | map({id: .key[0:8], client: .value.clientId, ip: .value.remoteIp, createdAt: .value.createdAtMs})' ~/.openclaw/devices/paired.json

# You'll see something like:
# [
#   { "id": "5544e6ed", "client": "openclaw-control-ui", "ip": null, "createdAt": 1776588664616 },
#   { "id": "68cd1045", "client": "cli", "ip": null, "createdAt": 1776625736577 },
#   { "id": "bb99814d", "client": "openclaw-android", "ip": "192.168.254.2", "createdAt": 1776628616874 },
#   { "id": "47a72d7e", "client": "openclaw-control-ui", "ip": "10.0.0.21", "createdAt": 1776628738308 },
#   { "id": "6e98defc", "client": "openclaw-control-ui", "ip": "10.0.0.21", "createdAt": 1776653291290 },
#   { "id": "5d52b3f3", "client": "openclaw-control-ui", "ip": "10.0.0.21", "createdAt": 1776718869432 }
# ]
```

### Keep the Most Recent, Remove Duplicates

```bash
# Backup
cp ~/.openclaw/devices/paired.json ~/.openclaw/devices/paired.json.backup

# View which to keep (latest timestamp)
jq 'to_entries | sort_by(.value.createdAtMs) | reverse | .[0:2]' ~/.openclaw/devices/paired.json

# Latest is: 5d52b3f3 (most recent)
# Also keep: 68cd1045 (cli) and bb99814d (android)

# Remove the middle duplicates
jq 'del(.["5544e6ed2c2569a6753ceaf96047925293d2862ecd4ccebf5c2faaf13bd56228"])' ~/.openclaw/devices/paired.json > /tmp/paired.json && mv /tmp/paired.json ~/.openclaw/devices/paired.json
jq 'del(.["47a72d7ea68984ee3d66ca61f42a605cee05af3332403d3527677f8fe612e4f8"])' ~/.openclaw/devices/paired.json > /tmp/paired.json && mv /tmp/paired.json ~/.openclaw/devices/paired.json
jq 'del(.["6e98defc7e4ee5e1ea21ee93f3c82de14379db180e4d7924b6359da50a5a8d3f"])' ~/.openclaw/devices/paired.json > /tmp/paired.json && mv /tmp/paired.json ~/.openclaw/devices/paired.json

# Now you should have only 3 devices (cli, android, latest control-ui)
jq 'keys | length' ~/.openclaw/devices/paired.json
# Output: 3
```

---

## Full Config Example (Session + Device Trust)

Here's what your updated `~/.openclaw/openclaw.json` should look like:

```json
{
  "auth": {
    "profiles": {
      "github-copilot:github": {
        "provider": "github-copilot",
        "mode": "token"
      }
    }
  },
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "aa6b920b6dd600d7ac7e2a03d2b9bd71d15288bfd822852d",
      "sessionTimeout": 604800,       // ← ADD THIS (7 days)
      "deviceTrustPeriod": 604800,    // ← ADD THIS (7 days)
      "tokenRefreshInterval": 259200  // ← ADD THIS (3 days)
    },
    "port": 18789,
    "bind": "lan",
    "tailscale": {
      "mode": "off",
      "resetOnExit": false
    },
    "controlUi": {
      "allowInsecureAuth": true,
      "allowedOrigins": [
        "https://10.0.0.81:18789",
        "https://10.0.0.21:18789",
        "http://10.0.0.81:18789",
        "http://10.0.0.21:18789"
      ]
    },
    // ... rest stays the same
  },
  // ... rest of file
}
```

---

## Verification

After restart, check that it worked:

```bash
# View updated config
cat ~/.openclaw/openclaw.json | jq '.gateway.auth'

# Check gateway is running with new config
openclaw gateway status

# Monitor logs during reauth (should show longer timeout)
openclaw logs --follow --component gateway
```

---

## Troubleshooting

### If Gateway Won't Start

```bash
# Validate JSON syntax
cat ~/.openclaw/openclaw.json | jq . >/dev/null && echo "Valid JSON" || echo "Invalid JSON"

# Restore backup if needed
cp ~/.openclaw/openclaw.json.backup ~/.openclaw/openclaw.json
openclaw gateway restart
```

### If You Still Get Prompted

1. **Clear old session tokens:**
   ```bash
   # Doesn't delete devices, just session cache
   rm ~/.openclaw/agents/main/sessions/*.jsonl
   ```

2. **Re-approve the current device:**
   - Go to Control UI settings
   - Find your device (10.0.0.21)
   - Click "Trust this device for 7 days"

3. **Restart gateway:**
   ```bash
   openclaw gateway restart
   ```

---

## Expected Behavior After

✅ **First login** → Asks for approval (normal)  
✅ **Next 7 days** → No reauth needed  
✅ **Day 3** → Background token refresh (silent)  
✅ **Day 8** → Asks for reauth again  

**Result:** Once per week instead of once per day! 🎉

---

## Summary

| Step | Action | Time |
|------|--------|------|
| 1 | Edit `~/.openclaw/openclaw.json` | 2 min |
| 2 | Add `sessionTimeout: 604800` | - |
| 3 | Run `openclaw gateway restart` | 1 min |
| 4 | Optionally clean duplicate devices | 3 min |
| 5 | Re-login to test | 1 min |

**Total time:** ~7 minutes to extend to weekly sessions! ⏱️
