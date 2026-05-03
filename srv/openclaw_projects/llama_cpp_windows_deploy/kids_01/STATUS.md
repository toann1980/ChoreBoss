# Llama.cpp Windows Deploy — `KIDS_01`

**System:** RTX 4070 Ti Node  
**OS:** Windows with WSL2 (Ubuntu)

---

## SSH Setup Complete ✅

### WSL Configuration
- **SSH Port:** 2132 (custom, non-standard)
- **WSL Internal IP:** `192.168.145.178`
- **SSH Daemon:** Running in WSL, listening on `0.0.0.0:2132`

### Port Forwarding (Windows Host)
Windows forwards external traffic to WSL internal SSH daemon:
```powershell
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=2132 connectaddress=192.168.145.178 connectport=2132
```

### Accepting SSH from `inv-toan`
- Public key stored: `~/.ssh/authorized_keys` (zagreus user)
- Key fingerprint: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIfMqreWLJLHYu85RDayjmwZsqIVjHokTJXEDXAgdlgf toann1980@gmail.com`

---

## Status
- **SSH Ready:** Connected from inv-toan via `10.0.0.37:2132` ✅
- **Next:** GPU baseline testing