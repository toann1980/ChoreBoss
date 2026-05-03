# WSL SSH Port Forwarding — Standard Setup

**Reference:** Llama.cpp Windows Deploy Project (2026-04-30)

---

## Problem
When running SSH daemon inside WSL, Windows doesn't automatically forward external traffic to the WSL internal IP. Direct connections to Windows host IP fail with `Connection reset` or `Connection closed`.

---

## Solution: Port Proxy Forwarding

### Identify WSL Internal IP
Inside WSL, run:
```bash
hostname -I
```
Example output: `192.168.145.178`

---

### Enable Port Forwarding on Windows (PowerShell as Administrator)
Forward external traffic on your chosen port to the WSL internal IP:
```powershell
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=2132 connectaddress=192.168.145.178 connectport=2132
```

Replace:
- `2132` (first occurrence) = External port on Windows host
- `192.168.145.178` = WSL internal IP (from `hostname -I`)
- `2132` (second occurrence) = SSH port inside WSL (default or custom)

---

### Verify Forwarding Rule
```powershell
netsh interface portproxy show all
```
Should display your forwarding rule.

---

### Test Connectivity
From external machine:
```bash
ssh -p 2132 user@windows-host-ip
```

---

## Key Insight
WSL's network isolation requires explicit port forwarding from the Windows host to the WSL internal network. Direct connections to Windows host IP don't reach WSL without this configuration.

---

## Application
- **Project:** Llama.cpp Windows Deploy (inv-toan & kids-01)
- **Date Implemented:** 2026-04-30
- **Status:** Tested and working ✅