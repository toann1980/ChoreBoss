# Llama.cpp Windows Deploy — Project Status

**Last Updated:** 2026-04-30 12:46 PDT  
**Status:** SSH connectivity established across both systems ✅

---

## Systems Overview

### System: Alienware R16 (`inv-toan`)
- **Environment:** Ubuntu 22.04 under WSL2
- **GPU:** RTX 4090
- **SSH Port:** 2132
- **Status:** Ready for deployment testing
- [Detailed Status](./inv_toan/STATUS.md)

---

### System: RTX 4070 Ti (`kids-01`)
- **Environment:** Windows with WSL2 (Ubuntu)
- **GPU:** RTX 4070 Ti
- **SSH Port:** 2132
- **WSL Internal IP:** 192.168.145.178
- **Status:** SSH connectivity verified ✅
- [Detailed Status](./kids_01/STATUS.md)

---

## Cross-System SSH Access

**From `inv-toan` to `kids-01`:**
```bash
ssh -i ~/.ssh/id_ed25519 -p 2132 zagreus@10.0.0.37
```

**Key Requirement:** Port forwarding on Windows host maps external traffic to WSL internal IP.

---

## Next Steps
1. GPU performance baseline testing on both systems
2. Threading diagnostics (ggml variance investigation)
3. CUDA compatibility validation