# MEMORY.md - Nova's Long-Term Knowledge

---

## ENVESTERO CURRENT STATE (2026-05-05 08:27 PDT)

**Dashboard:** Live at http://10.0.0.22/dashboard (6 components, 504 fixes applied)

**T001 + T002 Complete (2026-05-05 00:15):**
- Price fallback: 8-source cascade (cache → DB → APIs → degrade)
- OHLCV fallback: 4-source cascade (yfinance → Polygon → IEX → DB)
- Never times out, no data gaps
- Free APIs: Alpha Vantage, Finnhub, Tiingo, Polygon.io, IEX Cloud
- Next: Add keys to .env, test endpoints
- Commit: 4bd3b478

**Fault Tolerance Risks (identified 2026-05-04):**
- 🔴 yfinance timeouts (HIGH)
- 🔴 Nightly OHLCV job (HIGH)
- 🟡 Hermes sentiment, proxy scraper (MEDIUM)

---

## OTHER PROJECTS (Brief Status)

- **MemoryGraph Cron:** ✅ Restored (4 jobs, Phase 2 → 2026-05-06)
- **BenchModel v3.0:** ✅ Complete (102/102 tests, 3,110 LOC)
- **ImageForge:** DCC-agnostic rendering, local models, tenant isolation (Nike/Converse)
- **BenchModel hot-swap profiles (2026-05-05):** added safe `--start-profiles` support for Windows hot-swap machines; whitelisted startup keys are `ngl`, `parallel`, `ctx`; nuc stays on systemd

---

---

## Project: openclaw_projects (ImageForge Phase)
- ✓ DCC-agnostic rendering architecture
- ✓ Local model hosting (no API cost)
- ✓ Tenant isolation (Nike/Converse data never cross)
- ✓ OCP Standards: Read CURRENT.md first

---
