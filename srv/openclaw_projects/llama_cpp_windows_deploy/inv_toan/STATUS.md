# Llama.cpp Windows Deploy — `INV_TOAN`

**System:** Alienware R16  
**GPU:** RTX 4090  
**OS:** Ubuntu 22.04 under WSL2

---

## SSH Setup Complete ✅

### Configuration
- **SSH Port:** 2132 (custom, non-standard)
- **Authentication:** Ed25519 key-based
- **Key Location:** `~/.ssh/id_ed25519`
- **Public Key in:** `~/.ssh/authorized_keys`

### Port Forwarding (Windows Host)
Windows forwards external traffic on port `2132` to WSL internal SSH daemon:
```powershell
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=2132 connectaddress=192.168.145.178 connectport=2132
```

### Connecting from `kids-01`
```bash
ssh -i C:\Users\ToanNguyen\.ssh\id_ed25519 -p 2132 zagreus@10.0.0.37
```

---

## Status
- **Pipeline:** Established
- **Testing Progress:** SSH connectivity verified
- **Next:** GPU and threading tests