# CRITICAL: 5-Minute Bars as Validation Foundation

**For:** Toan  
**From:** Nova ✨  
**Date:** 2026-04-21 06:58 UTC  
**Status:** Strategic requirement shift — 5m bars are foundational, not optional

---

## The Insight

> "We have to figure out how to pull data for tickers in an effective manner. This is one of the most crucial data points. When we scrape news and guess sentiment, we then build data to trade based on what sentiment we saw from the news. We check the price to validate if the decision was right or wrong."

### What This Means

**Current approach (what we were planning):**
1. Collect sentiment from Reddit, Twitter, Glassdoor, App Store
2. Detect correlations (sentiment → price)
3. Trade based on correlations
4. **Validate:** Check daily OHLCV to see if signal was right

**Problem with daily-only validation:**
- Signal fires on Monday (sentiment shift detected)
- We predict price move
- We check Tuesday's OHLCV to validate
- **But we miss:** Where did price go during Monday's trading day?
- **We miss:** Did price spike 2% in first 5 min, then reverse? Or steady climb?
- **We miss:** Intraday volatility that tells us about signal strength

**What 5m bars unlock:**
1. Sentiment signal fires (e.g., "CEO departure detected Monday 9am")
2. Check 5m bars to see immediate market reaction (9:30am-4pm Monday)
3. See if market agreed with sentiment (price up/down by how much in first hour?)
4. Validate signal strength in real-time (not next-day)
5. Detect false positives immediately (if sentiment said "down" but price went up)
6. Understand **lag between sentiment + price response** (how many minutes/hours?)

---

## Why This Changes Everything

### For Signal Validation
**With daily bars only:**
- Sentiment: "Reddit says CEO leaving is bad" (Mon 10am)
- Check: Tuesday close vs Monday close
- Problem: Can't see if market reacted immediately or took time
- Can't validate signal timing

**With 5m bars:**
- Sentiment: "Reddit says CEO leaving is bad" (Mon 10am)
- Check: 5m bars from Mon 10am through end of day
- See: Market reaction in first 15 minutes (strong/weak?)
- See: Did reaction persist or reverse?
- See: Exact timing of price response to sentiment signal
- Can validate: "This sentiment signal predicts price within 30 minutes"

### For Cross-Source Learning
**Without 5m bars:**
- Correlation: "Reddit → Twitter (1-day lag) → Stock (2-day lag)"
- Problem: Can't see intraday dynamics
- Can't tell if Twitter sentiment responds within hours or days

**With 5m bars:**
- See: Reddit spike Monday 2pm
- See: Twitter follows Monday 4pm (within 2 hours, not 1 day)
- See: Stock price follows Tuesday 10am (specific timing)
- Can measure exact cascades

### For Persona Trading Validation
**Without 5m bars:**
- Conservative persona trades Monday based on sentiment
- Check: Friday close vs Monday close
- Can't see: Did signal work but trader exited too early? Too late?
- Can't optimize: Best entry/exit times

**With 5m bars:**
- See: When signal fired, exact price at that moment
- See: How price moved next 5, 15, 30, 60 min
- Can optimize: Conservative persona should hold 30 min? 2 hours?
- Can validate: Which persona timing works best

---

## The Root Problem We Need to Solve

**Current state (from earlier session):**
- Phase 1: Loaded 4,680 daily OHLCV rows (✅ works)
- Phase 1: Attempted to load 5m bars (❌ 0 rows, transaction rollback)

**Root cause identified:**
- Batch size 1000 rows per transaction (too large)
- yfinance fetches work (✅ data available)
- Database commit fails (transaction timeout during upsert)

**Solution required:**
- Reduce batch size 1000 → 100 rows per transaction
- Add explicit `session.commit()` after each batch
- Ensure 5m bars for 20 tickers, ~1 year history load successfully

**Estimated fix effort:** 30-45 minutes

---

## Strategic Decision: Fix Now, Not Defer

### Previous plan: Defer to Phase 1.5 ❌
**Reason given:** "Low priority for MVP"

### New plan: Fix before Phase 1C.1 ✅
**Reason:** 5m bars are **the validation foundation** for Intelligence Model

### Why This Is Critical

**Phase 1C's entire value depends on:**
1. Build sentiment signals (Reddit, Twitter, etc.)
2. **Validate against 5m bars** (did market agree?)
3. Learn which sources matter (Reddit works, Twitter doesn't for Tech sector)
4. Measure signal timing (how fast does market react?)
5. **Only THEN** build correlations with confidence

**Without 5m bars:**
- We're guessing "did our sentiment signal work?"
- We can't validate sentiment accuracy against actual market reaction
- We can't optimize signal timing
- Phase 1C becomes theory without empirical validation

**With 5m bars:**
- We see immediate market reaction to sentiment signals
- We can measure signal quality (how often is sentiment right?)
- We can measure signal timing (how fast does market respond?)
- Phase 1C becomes data-driven validation

---

## Implementation Plan: Fix 5m Bars First

### Task 1: Identify Root Cause (Already Done ✅)
- Transaction rollback during 1000-row batch upsert
- yfinance fetch works fine
- Database commit is the bottleneck

### Task 2: Fix Batch Size Logic (~15 min)
```python
# Current (broken)
all_bars = yfinance.fetch(period="60d")  # ~4,680 rows per ticker
db.insert_batch(all_bars, batch_size=1000)  # ❌ Fails at ~3000 rows

# Fixed
all_bars = yfinance.fetch(period="60d")
for i in range(0, len(all_bars), 100):
    batch = all_bars[i:i+100]
    db.insert_batch(batch)
    session.commit()  # Explicit commit per batch
```

### Task 3: Test Batch Size (~15 min)
- Test on 2 tickers first (Apple, Microsoft)
- Verify: 4,680 rows load per ticker without error
- Check: Database has correct row counts

### Task 4: Full Backfill (10 min)
- Run on all 20 tickers
- Verify: All 5m bars loaded (~93,600 rows total)

**Total time:** ~45 min

---

## Updated Implementation Sequence

### Before Phase 1C.1 Starts

**Task 0: Fix 5-Minute Bars (NEW, CRITICAL) — 45 min**
1. Update batch logic (reduce 1000 → 100)
2. Add explicit session.commit() per batch
3. Test on 2 tickers
4. Backfill all 20 tickers
5. Verify: All 5m bars loaded

**Then proceed:**
- Phase 1C.1: Executives
- Phase 1C.2: Sentiment (all 4 sources)
- Phase 1C.3: Correlations + 5m validation

---

## Why 5m Bars Are Crucial for Envestero

### Signal Validation Loop
```
Sentiment Signal Detected (e.g., CEO departure)
    ↓
Check 5m Bars: Did market react?
    ├─ Strong reaction (>2% move in first hour) → Signal is HIGH confidence
    ├─ Weak reaction (<0.5% move) → Signal is LOW confidence
    └─ Reverse reaction (opposite direction) → Signal is WRONG
    ↓
Learn: Which sentiments predict price?
    ├─ Reddit sentiment accurate? (check price reaction)
    ├─ Twitter sentiment accurate? (check price reaction)
    ├─ Glassdoor sentiment accurate? (check price reaction)
    └─ App Store sentiment accurate? (check price reaction)
    ↓
Optimize: Which sources matter for which tickers?
    ├─ Apple: Twitter > Reddit > Glassdoor > App Store
    ├─ Tesla: Reddit > Twitter > Glassdoor > App Store
    └─ Energy stocks: Glassdoor > Twitter > Reddit (employees know first)
    ↓
Persona Trading: Test different thresholds
    ├─ Conservative: Wait for 2-3 confirmations before trading
    ├─ Overloaded: Use any signal, but hedge with stops
    └─ Specialist: Different rules per sector (learned from 5m validation)
    ↓
Paper Trading: Did profit targets hit? How fast?
    ├─ Entry signal fired 10am
    ├─ Check 5m bars: When did target get hit? 10:15am? 2pm?
    ├─ Optimize: When to exit? How long to hold?
    └─ Learn: Which persona timing works best?
```

**5m bars answer:** All the "when" and "how fast" questions.

---

## Decision: Fixing 5m Bars Is Part of Phase 1 Foundation

### New Sequencing
1. **Fix 5m bars** (45 min) — FOUNDATIONAL
2. **Phase 1C.1:** Executives (2-3h build + 30-45 min validate)
3. **Phase 1C.2:** Sentiment, all 4 sources (3.5-4.5h build + 30-45 min validate)
4. **Phase 1C.3:** Correlations with 5m validation (5-6h build)

### Updated Timeline

| Task | Time |
|------|------|
| Fix 5m bars | 45 min |
| Phase 1C.1 | 2.5-3.5h |
| Phase 1C.2 | 4-5h |
| Phase 1C.3 | 5-6h |
| Scale + tests | 1h |
| Phase 3 | 12-15h |
| **TOTAL** | **25.75-31h** |

**Impact:** +45 min, but enables **entire validation framework**

---

## Why This Is Worth It

### What We Gain
✅ Intraday signal validation (immediate market reaction)  
✅ Source reliability measurement (which sources matter)  
✅ Signal timing optimization (how fast to react)  
✅ Persona backtesting precision (exact entry/exit points)  
✅ Risk management (see volatility, adjust position sizing)  

### What We Avoid
❌ Building sentiment signals on unvalidated data  
❌ Discovering Phase 3 that signals don't actually work  
❌ Persona trading without real timing constraints  
❌ Missing intraday risk (only seeing daily close)  

---

## Recommendation

**Fix 5m bars NOW (before Phase 1C.1) instead of deferring to Phase 1.5.**

Reason: 5m bars are the validation foundation for the entire Intelligence Model. Without them, we're building sentiment signals in a vacuum. With them, we can empirically validate every signal as we build.

---

## Files to Update

✅ DECISIONS.md — 5m bars decision changed from "defer" to "fix now"  
✅ NOVA.md — Updated rationale  
✅ START_PHASE_1C_CHECKLIST.md — Add "Fix 5m bars" as Task 0  

---

## Implementation

**Task 0: Fix 5-Minute Bars (45 min)**
1. Locate batch upsert logic in Phase 1 code
2. Change batch size: 1000 → 100
3. Add explicit `session.commit()` after each batch
4. Test on 2 tickers (Apple, Microsoft)
5. Run full backfill on all 20 tickers
6. Verify: All 5m bars loaded (~93,600 rows)

**Then: Phase 1C.1 starts**

---

## Bottom Line

5-minute bars aren't optional. They're the validation foundation.

- Sentiment signals mean nothing without price validation
- Cross-source learning requires intraday timing data
- Persona trading needs precise entry/exit timing
- Risk management requires volatility understanding

**Fix it now. 45 minutes. Unlocks everything.**

---

**Ready to prioritize 5m bars fix before Phase 1C.1?** ✅

---

**Updated:** 2026-04-21 06:58 UTC by Nova ✨
