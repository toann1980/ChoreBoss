# 3 Remaining Decisions — What You Need to Decide

**For:** Toan  
**From:** Nova ✨  
**Date:** 2026-04-21 06:50 UTC

---

## 1️⃣ Consumer Sources: All 4 or Reddit MVP?

### Option A: All 4 Sources (Default)
**Build:** Reddit + Twitter + Glassdoor + App Store simultaneously

**Why all 4:**
- ✅ Maximum signal coverage
- ✅ Redundancy (if one source is noisy, others compensate)
- ✅ Different perspectives (Reddit = general users, Glassdoor = employees, App Store = app experience)

**Effort:** +15% complexity (handle 4 different APIs)  
**Data quality:** Better (more sources = more consensus)

### Option B: Reddit MVP First
**Build:** Reddit only, then add others in Phase 2A

**Why Reddit first:**
- ✅ Fastest to implement (1 API, PRAW)
- ✅ Largest discussion volume (most signal)
- ✅ Easiest to validate
- ⚠️ Single source bias (may miss employee/app insights)

**Effort:** Simpler (only 1 API)  
**Data quality:** OK for MVP, gaps in employee/app feedback

**My recommendation:** **All 4** — Twitter + Glassdoor add valuable perspectives (employees know product issues early)

---

## 2️⃣ Confidence Threshold: Which r-value?

### Understanding r-values
- **r = correlation coefficient** (strength of relationship between two things)
- r = 0: no relationship
- r = 0.5: moderate relationship
- r = 0.7: strong relationship
- r = 1.0: perfect relationship

### Your Options

**Option A: r > 0.5 (Lenient)**
- Registers more relationships
- Might include false positives (noise)
- Better for exploration/discovery
- Risk: May generate false signals

**Option B: r > 0.6 (Moderate) — Default**
- Balanced between discovery and confidence
- Filters obvious noise
- Risk: May miss subtle signals

**Option C: r > 0.7 (Strict)**
- Only strongest relationships
- High confidence, low false positives
- Risk: May miss valid signals (too strict)

**My recommendation:** **r > 0.5** — Start lenient, filter with other heuristics (time-lag plausibility, domain sense)

**Why:**
- Correlation is one signal, not the whole story
- We have other filters: time-lag windows (must be 1-10 days), domain checks (CEO changes should matter, random execs shouldn't)
- Better to find relationships + filter in code than miss them

---

## 3️⃣ 5-Minute Bars: Fix Now or Defer?

### Current Status
- **Problem:** 0 rows loaded (transaction rollback during batch upsert)
- **Root cause:** Batch size too large (1000 rows), database transaction times out
- **Fix:** Reduce to 100 rows/batch, add explicit `session.commit()` after each
- **Effort:** 30-45 minutes
- **Impact:** Intraday backtesting will work (currently broken)

### Option A: Fix Now
**When:** Before Phase 1C.1  
**Impact:** +45 min to total timeline (now 11.75-14.5h)  
**Benefit:** Intraday data available immediately after Phase 1  
**Risk:** Distracts from Intelligence Model focus

### Option B: Defer to Phase 1.5 (After Phase 3)
**When:** After paper trading engine works  
**Impact:** No timeline impact now  
**Benefit:** Focus on Intelligence Model (higher ROI)  
**Risk:** Intraday features delayed by ~20+ hours

**My recommendation:** **Defer to Phase 1.5**

**Why:**
- Daily bars sufficient for Intelligence Model (executives, sentiment, price correlation)
- Paper trading doesn't need intraday (daily candles enough for entry/exit signals)
- Intraday analysis is a "nice-to-have" feature (detailed backtest optimization)
- Fix is straightforward (low risk to defer)

---

## Summary Table

| Decision | Option | Recommendation | Reasoning |
|----------|--------|----------------|-----------|
| **Consumer Sources** | All 4 vs Reddit MVP | **All 4** | Better signal diversity, Twitter + Glassdoor add employee/product insights |
| **Confidence r-value** | r > 0.5 vs 0.6 vs 0.7 | **r > 0.5** | Start lenient, filter with time-lag + domain logic in code |
| **5m Bars** | Fix now vs defer | **Defer to Phase 1.5** | Daily sufficient for Intelligence Model; fix is low-risk deferral |

---

## What I Need From You

Reply with:
1. **Consumer sources:** All 4 or Reddit MVP?
2. **Confidence threshold:** r > 0.5, 0.6, or 0.7?
3. **5m bars:** Fix now or defer to Phase 1.5?

Once I have these, I'll:
- ✅ Lock in all decisions
- ✅ Update PHASE_1C_IMPLEMENTATION_GUIDE.md with specifics
- ✅ Start Phase 1C.1

---

**These 3 are the last blockers. Everything else is ready.** 🚀

---

**Updated:** 2026-04-21 06:50 UTC
