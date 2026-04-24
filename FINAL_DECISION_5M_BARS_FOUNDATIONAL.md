# ✅ FINAL DECISION: 5-Minute Bars Are Foundational

**Date:** 2026-04-21 06:58 UTC  
**Status:** Strategic shift locked in

---

## Your Insight

> "We have to figure out how to pull data for tickers in an effective manner. This is one of the most crucial data points. When we scrape news and guess sentiment, we then build data to trade based on what sentiment we saw from the news. We check the price to validate if the decision was right or wrong."

**Translation:** 5m bars are not optional. They're the **validation foundation** for the entire Intelligence Model.

---

## What Changed

### Previous Plan ❌
1. Defer 5m bars to Phase 1.5 (after Phase 3)
2. Build Intelligence Model without validation
3. Test personas on daily data only
4. **Problem:** Build entire system on untested assumptions

### New Plan ✅
1. **Fix 5m bars NOW (Task 0, 45 min)** — Before Phase 1C.1
2. Build Intelligence Model with intraday validation
3. Test personas with precise entry/exit timing
4. **Benefit:** Validate every step empirically

---

## Why 5m Bars Are Critical

### Signal Validation Loop
```
Sentiment Signal Fires (e.g., "CEO departure detected")
    ↓
Check 5m Bars: Did market react?
    ├─ Strong reaction (>2% move) → Signal HIGH confidence
    ├─ Weak reaction (<0.5% move) → Signal LOW confidence
    └─ Opposite reaction → Signal WRONG
    ↓
Learn: Which sources are reliable?
    ├─ Glassdoor > Twitter > Reddit (for this signal)
    └─ Different sources matter for different stocks
    ↓
Measure: How fast does market react?
    ├─ Signal fires 10am → Price reacts 10:15am (15-min lag)
    └─ Can optimize entry timing
    ↓
Optimize: When to exit?
    ├─ Target hit in 30 min? Hold longer?
    ├─ Target hit in 2 hours? Exit immediately?
    └─ Different personas need different timings
```

**5m bars answer all the "when" and "how fast" questions.**

---

## Implementation: Task 0

### Fix 5-Minute Bars (45 minutes)

**Root Cause:**
- yfinance fetch works ✅ (4,680 rows per ticker)
- Batch size 1000 too large ❌ (transaction timeout)

**Solution:**
- Reduce batch size: 1000 → 100
- Add explicit `session.commit()` after each batch
- Test on 2 tickers (Apple, Microsoft)
- Backfill all 20 tickers

**Tasks:**
1. Update batch logic (15 min)
2. Test on 2 tickers (15 min)
3. Backfill all 20 tickers (10 min)

**Success:** All 93,600 rows (20 tickers × 4,680 rows) loaded

---

## Updated Sequence

### Task 0: Fix 5m Bars (45 min) ← START HERE
- Load intraday data for all 20 tickers
- Validate: 93,600 rows total

### Phase 1C.1: Executive Data (2.5-3.5h)
- Build from SEC filings
- Validate: Exec data completeness
- **Use 5m bars:** Check if exec events correlate with intraday volatility

### Phase 1C.2: Consumer Sentiment (4-5h)
- Build all 4 sources (Reddit, Twitter, Glassdoor, App Store)
- Validate: Sentiment accuracy >80%
- **Use 5m bars:** Validate which sources predict price correctly + how fast

### Phase 1C.3: Correlations (5-6h)
- Build cross-source learning
- Measure lags: Reddit → Twitter → Price (with 5m precision)
- Learn: Which sources matter per ticker

### Phase 3: Persona Trading (12-15h)
- Test multiple personas with different thresholds
- **Use 5m bars:** Measure exact entry/exit timing
- Optimize: Which persona + strategy wins

---

## Timeline Impact

| Component | Time |
|-----------|------|
| Task 0: Fix 5m bars | **+45 min** |
| Phase 1C (total) | 11-14h |
| Phase 3 (total) | 12-15h |
| **TOTAL** | **25.75-31h** (vs 25-32h before) |

**Net change:** Negligible (+45 min upfront, saves debugging time later)

---

## What This Unlocks

✅ **Empirical Signal Validation**
- See which sentiment sources actually predict price
- Measure accuracy in real-time (5m bars)

✅ **Timing Optimization**
- Learn how fast market reacts to sentiment
- Optimize entry/exit timing per persona

✅ **Source Weighting**
- Measure which sources matter per stock
- Per-ticker source weights (Reddit works for Tesla, Glassdoor for Apple)

✅ **Persona Precision**
- Backtesting with exact intraday prices
- Not just "did it work on daily close?" but "when did target get hit?"

✅ **Risk Management**
- See intraday volatility (not just daily close)
- Adjust position sizing based on volatility

---

## Documentation Created

✅ **CRITICAL_5M_BARS_VALIDATION_FOUNDATION.md** (11 KB)
- Strategic rationale
- Signal validation loop
- Why now, not later
- Implementation plan

✅ **UPDATED_START_PHASE_1C_CHECKLIST.md** (6.7 KB)
- Task 0: Fix 5m bars
- Phase 1C.1-1C.3 with 5m validation
- Updated timeline

✅ **DECISIONS.md** (memory-sync, updated)
- 5m bars decision changed: "Fix now" instead of "Defer"

✅ **NOVA.md** (memory-sync, updated)
- Critical insight documented
- Strategic implications

---

## Bottom Line

You identified the core insight: **Sentiment means nothing without price validation.**

5-minute bars aren't optional. They're foundational.

- Fix them first (45 min, Task 0)
- Use them to validate every signal
- Learn which sources work empirically
- Build personas with precision timing

---

## Ready?

When you confirm, I'll:
1. Start Task 0 (Fix 5m bars)
2. Notify Kira (MSG-004)
3. Update project timeline
4. Begin Phase 1C.1 after Task 0 completes

---

**All decisions finalized. 5m bars prioritized. Ready to build.** 🚀

---

**Updated:** 2026-04-21 06:58 UTC by Nova ✨
