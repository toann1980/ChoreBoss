# For Kira: Critical Troubleshooting Methodology

**From Toan's feedback during NUC debugging session (2026-04-22)**

## The Lesson

After every fix attempt, **immediately validate locally before asking the user to test.**

### What I Did Wrong
1. Applied fix (firewall config)
2. Assumed problem was persistent
3. Deep-dived into complex infrastructure troubleshooting
4. Spent 3 hours on firewall debugging
5. Finally asked user to test
6. **Discovery: Docker containers weren't running** (would've found in 10 seconds with `docker ps`)

### The Right Way
1. Apply fix
2. **Immediately run local diagnostics:**
   ```bash
   docker ps                                  # Services running?
   docker compose logs --tail=20              # Any errors?
   curl -s http://localhost:8000/api/status  # Service responding?
   ss -tlnp | grep 3000                       # Port listening?
   ```
3. **Validate assumption:** Does the problem still exist?
4. Only then ask user to test from remote

### Why This Matters
- **Local validation:** 10 seconds
- **User testing:** 2-5 minutes per attempt
- **3 hours of firewall deep-dive:** Should've been 10 seconds with docker ps

**Optimization:** Local tools are orders of magnitude faster. Use them relentlessly before infrastructure diving.

## Apply to All Remote System Work

When diagnosing issues on:
- NUC (Toan's machine)
- Any WSL2/remote system
- Docker deployments
- Network services

**Pattern:** Validate locally → check logs → verify assumption persists → THEN pursue deep investigation

Don't get locked into a hypothesis. Data beats assumptions.

---

**From:** Nova  
**To:** Kira  
**Date:** 2026-04-22 02:01 UTC  
**Context:** NUC remote access troubleshooting session
