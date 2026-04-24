# PHASE 0: Single-Ticker Validation (MVP Proof of Concept)

**For:** Toan, Nova, Kira  
**Date:** 2026-04-21 07:05 UTC  
**Duration:** ~2-3 hours  
**Goal:** Prove that sentiment signals predict price direction on one ticker before cascading

---

## Phase 0 Overview

**Instead of building all 20 tickers from day 1, validate the signal chain on ONE ticker first.**

### Why Phase 0?

1. **Fast validation:** 2-3 hours, not 13-17 hours
2. **Proof of concept:** Show that sentiment → price works before scaling
3. **Early feedback:** If signal doesn't work, pivot before major build
4. **Cascade plan:** If valid on AAPL, replicate to all 20

### What Gets Built in Phase 0

**Single ticker (Apple - AAPL) only:**
- [ ] Executive data (Apple execs)
- [ ] Sentiment data (Apple sentiment from 4 sources)
- [ ] Daily OHLCV validation (did signals predict price?)
- [ ] Correlation detection (simple: which sources predicted price)

---

## Phase 0: Single-Ticker Validation (2-3 hours)

### Task 0.1: Executive Data for AAPL (45 min)
**Deliverable:** Apple executive profiles + career events

1. Build Executive + ExecutiveEvent tables
2. Fetch from SEC Edgar (Apple only)
3. Store: CEO, CFO, CTO, COO + tenure dates
4. Validate: ≥3 execs captured, dates correct

**Output:** 3-5 executive records for Apple

**Key events to capture:**
- Tim Cook tenure start/events
- Craig Federighi (Sr VP Software)
- Any recent exec changes (if available in period)

### Task 0.2: Consumer Sentiment for AAPL (1 hour)
**Deliverable:** 7 days of sentiment from all 4 sources

1. Implement Reddit collector (PRAW)
2. Implement Twitter collector (tweepy)
3. Implement Glassdoor scraper
4. Implement App Store collector
5. Set data quality thresholds
6. Collect: 7 days of sentiment (Mon-Sun)

**Output:** ~100-200 sentiment entries (mixed sources)

**Example:**
- Reddit: 20 posts about Apple (upvotes > 10)
- Twitter: 50 tweets about Apple (>50/day threshold)
- Glassdoor: 30 employee reviews
- App Store: 50 customer reviews

### Task 0.3: Daily OHLCV Validation (30 min)
**Deliverable:** Check if sentiment predicted price direction

1. Get sentiment data: 7 days (Mon-Sun)
2. Get daily OHLCV: Same 7 days
3. For each day with sentiment shift:
   - Check next day's price direction (up/down/neutral)
   - Record: Sentiment predicted correctly? YES/NO

**Validation table:**

| Date | Sentiment | Prediction | Actual Close vs Open | Match? |
|------|-----------|------------|----------------------|--------|
| Mon | Negative | DOWN | -0.8% | ✓ |
| Tue | Neutral | FLAT | +0.2% | ✗ |
| Wed | Positive | UP | +1.2% | ✓ |
| Thu | Negative | DOWN | -0.5% | ✓ |
| Fri | Positive | UP | +0.3% | ✓ |
| **Accuracy** | — | — | — | **80%** |

**Success criteria:**
- Accuracy > 60% (better than random)
- At least 3 days with clear signals
- Sentiment direction matches price direction (most of the time)

### Task 0.4: Simple Correlation (30 min)
**Deliverable:** Which sources predicted price best?

1. For each source separately (Reddit, Twitter, Glassdoor, App Store):
   - Measure: How often did this source's sentiment predict price?
   
2. Example results:
   - Twitter: 85% accuracy (most reliable for Apple)
   - Glassdoor: 60% accuracy
   - Reddit: 55% accuracy
   - App Store: 50% accuracy

**Output:** Source ranking for Apple

---

## Phase 0: Success Criteria

### Go Criteria (Proceed to Phase 1C with all 20 tickers)
- ✅ Sentiment predicts price direction >60% of time
- ✅ At least one source shows >70% accuracy
- ✅ Cross-source patterns detected (e.g., Twitter > Reddit)

### No-Go Criteria (Pivot required)
- ❌ Sentiment predicts price <50% (random)
- ❌ All sources equally unreliable
- ❌ No clear patterns in 7-day sample

---

## If Phase 0 Succeeds (Go Criteria Met)

**Proceed to Phases 1C.1-1C.3 with all 20 tickers:**

### Phase 1C.1: Executive Data (All 20 tickers)
- Build executive data for remaining 19 tickers
- Run in parallel with Phase 1C.2 (independent)
- Time: 2-3h

### Phase 1C.2: Consumer Sentiment (All 20 tickers)
- Build sentiment collection for remaining 19 tickers
- Run in parallel with Phase 1C.1 (independent)
- Time: 3-4h

### Phase 1C.3: Correlation Detection (All 20 tickers)
- Wait for 1C.1 + 1C.2 complete
- Measure cross-source correlations
- Learn per-ticker source weights
- Time: 5-6h

**Total Phase 1C time:** ~7-9h (1C.1 + 1C.2 parallel, then 1C.3 sequential)

---

## If Phase 0 Fails (No-Go Criteria Met)

**Decision point: Pivot or investigate?**

### Option 1: Extend Sample
- Test on 2 more tickers (MSFT, NVDA)
- See if pattern was ticker-specific or general issue

### Option 2: Pivot
- Reassess: Is sentiment signal viable?
- Could be: Need longer sample (7 days too short?)
- Could be: Different source combinations needed
- Could be: Different sentiment categories needed

---

## Phase 0 Timeline

| Task | Time |
|------|------|
| 0.1: Execs (AAPL) | 45 min |
| 0.2: Sentiment (AAPL, all 4 sources) | 1h |
| 0.3: Daily validation | 30 min |
| 0.4: Source correlation | 30 min |
| **TOTAL** | **~2.5-3h** |

---

## Phase 0: Why This Matters

**Risk mitigation:**
- Don't build Phase 1C (13-17h) on unvalidated assumptions
- Test signal chain on one ticker (fast feedback)
- If signal works: Confidence to scale
- If signal doesn't work: Pivot before major effort

**Empirical validation:**
- See real market data (actual price reactions)
- Measure source reliability (not theoretical)
- Inform Phase 1C design (which sources to prioritize)

---

## Parallelization After Phase 0

**If Phase 0 succeeds:**

### Phases 1C.1 and 1C.2: RUN IN PARALLEL
- Phase 1C.1: Collect executive data (20 tickers)
- Phase 1C.2: Collect sentiment data (20 tickers)
- **No dependency between them** (independent data sources)
- **Combined time:** ~4h (not 7h sequential)

### Phase 1C.3: RUN SEQUENTIALLY (after 1C.1 + 1C.2)
- Requires both Phase 1C.1 + 1C.2 outputs
- Measures correlations between sources
- **Time:** 5-6h

**Total Phase 1C:** ~9-10h (vs 13-17h if all sequential)

---

## Updated Project Timeline

| Phase | Time | Notes |
|-------|------|-------|
| **Phase 0** | 2.5-3h | Single-ticker validation (MVP) |
| **Phase 1C.1** | 2-3h | Parallel with 1C.2 |
| **Phase 1C.2** | 3-4h | Parallel with 1C.1 |
| **Phase 1C.3** | 5-6h | Sequential (needs 1C.1 + 1C.2) |
| **Scale** | 1h | Apply to remaining tickers |
| **Phase 3** | 12-15h | Persona backtesting |
| **TOTAL** | **25-31h** | (same as before, but Phase 0 replaces Task 0) |

---

## Implementation Plan

### Now: Phase 0 (2.5-3h)
1. Start with AAPL only
2. Build minimal stack (execs + sentiment + daily validation)
3. Test signal chain end-to-end
4. Measure accuracy

### If Phase 0 Succeeds
1. Phase 1C.1 + 1C.2 run in parallel (AAPL + remaining 19 tickers)
2. Phase 1C.3 runs after both complete
3. Proceed to Phase 3

### Decision Required
**Toan:** Approve Phase 0 as MVP validation step?

---

## Files to Create/Update

✅ PHASE_0_SINGLE_TICKER_VALIDATION.md (this file)  
✅ PHASE_1C_PARALLELIZATION.md (1C.1 + 1C.2 parallel, 1C.3 sequential)  
✅ DECISIONS.md (Phase 0 decision added)  
✅ NOVA.md (Phase 0 start timestamp)  

---

**Ready to start Phase 0 (2.5-3 hour MVP validation)?**

---

**Updated:** 2026-04-21 07:05 UTC by Nova ✨
