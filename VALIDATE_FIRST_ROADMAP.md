# IMPLEMENTATION ROADMAP — Validate-First Approach

**For:** Toan, Nova, Kira  
**Decision:** Option B (Validate-First Sequencing)  
**Date:** 2026-04-21 06:49 UTC  
**Timeline:** ~11-14 hours total (includes validation pauses)

---

## Phase 1C.1: Executive Data Collection (2-3 hours)

### Build (2-3h)
1. Create Executive + ExecutiveEvent database tables
2. Implement SEC Edgar API integration
3. Build CLI command: `python -m envestero.cli execs backfill --tickers AAPL MSFT NVDA`
4. Collect exec data for 20 tickers (fetch from SEC 8-K, proxy statements)
5. Test on 2-3 tickers

### ✅ **VALIDATE (30-45 minutes)**
**Stop here. Do NOT move to Phase 1C.2 until validation passes.**

**Validation checklist:**
- [ ] **Completeness:** Each ticker has ≥3 executives listed
- [ ] **Accuracy:** Spot-check 5 execs manually against SEC filings
  - Verify names correct
  - Verify titles correct (CEO vs CFO vs CTO)
  - Verify tenure dates correct
- [ ] **Career transitions:** Find at least 2 exec changes in historical data
  - Verify join/exit dates are captured
  - Verify timeline is continuous (no gaps)
- [ ] **Data format:** All fields populated (name, role, join_date, exit_date)

**If validation FAILS:**
- Fix gaps (add missing execs, correct dates)
- Revalidate
- Do NOT proceed to Phase 1C.2 until passing

**If validation PASSES:**
- ✅ Move to Phase 1C.2

---

## Phase 1C.2: Consumer Sentiment Collection (3-4 hours)

### Build (3-4h)
1. Create ConsumerSentiment database table
2. Implement PRAW integration (Reddit)
3. Implement tweepy integration (Twitter)
4. Implement Glassdoor scraper
5. Build sentiment aggregation logic
   - Apply **data quality thresholds** (Reddit >10 upvotes, Twitter >50/day, Glassdoor >20 helpful votes)
   - Apply **category classification** (leadership, product, service)
6. CLI: `python -m envestero.cli sentiment collect --tickers AAPL MSFT NVDA --days 7`
7. Test on 2-3 tickers, collect 7 days of sentiment data

### ✅ **VALIDATE (30-45 minutes)**
**Stop here. Do NOT move to Phase 1C.3 until validation passes.**

**Validation checklist:**
- [ ] **Volume:** Each ticker has ≥50 sentiment entries across all sources
- [ ] **Accuracy:** Manually check 20 sentiment labels
  - Sample 20 Reddit posts: are labels correct (pos/neg/neutral)?
  - Sample 20 tweets: are labels correct?
  - Aim for >80% accuracy
- [ ] **Thresholds working:** Check that filters reduce noise
  - Reddit: Verify low-upvote posts are excluded
  - Twitter: Verify volume gate works (only >50/day signals)
  - Glassdoor: Verify low-helpfulness reviews excluded
- [ ] **Categories:** Check that classification is meaningful
  - Sample 10 "leadership" sentiment entries: are they about executives?
  - Sample 10 "product" entries: are they about features/quality?
  - Sample 10 "service" entries: are they about support/response?
- [ ] **Date coverage:** Ensure you have sentiment data for full 7-day window

**If validation FAILS:**
- Adjust thresholds (e.g., lower upvote threshold if too much data excluded)
- Retrain category classifier if accuracy <80%
- Revalidate
- Do NOT proceed to Phase 1C.3 until passing

**If validation PASSES:**
- ✅ Move to Phase 1C.3

---

## Phase 1C.3: Influence Network Detection (4-5 hours)

### Build (4-5h)
1. Create InfluenceNetwork database table
2. Implement correlation detection engine
   - Test lag windows: 1-day, 3-day, 5-day, 10-day
   - Calculate correlation between:
     - Exec changes (events) → sentiment (daily) → stock price (OHLCV)
   - Apply **statistical thresholds:**
     - Minimum r > 0.5 to register correlation
     - Minimum 20 observations (days) before reporting
     - Forward chaining only (exec event → sentiment → price, no retroactive fitting)
3. Build `/api/v1/analysis/{symbol}/influence-network` endpoint
   - Returns: Relationships, confidence scores, lag windows
4. CLI: `python -m envestero.cli influence analyze --tickers AAPL MSFT NVDA`
5. Test on 2-3 tickers

### ✅ **VALIDATE (not formally paused, but review results)**
- [ ] **Relationships found:** Each ticker shows ≥1 influence relationship
- [ ] **Confidence scores:** Relationships have r > 0.5
- [ ] **Lag windows:** Strongest relationships show plausible lag (1-5 days typical)
- [ ] **No spurious correlations:** Spot-check relationships make sense
  - CEO change → sentiment drop → stock drop (plausible)
  - Not: random exec name → random sentiment (unlikely)

---

## After All 3 Phases Pass Validation ✅

1. **Scale to all 20 tickers**
   - Run full backfill: `python -m envestero.cli execs backfill --tickers ALL`
   - Run sentiment collection: `python -m envestero.cli sentiment collect --tickers ALL --days 365`
   - Run influence analysis: `python -m envestero.cli influence analyze --tickers ALL`

2. **Run integration tests**
   - Phase 2 tests still pass with Intelligence Model data added
   - New endpoints work: `/api/v1/news/{symbol}/sentiment`, `/api/v1/analysis/{symbol}/influence-network`

3. **Ready for Phase 3 (Paper Trading)**

---

## Timeline Breakdown

| Phase | Build | Validate | Total |
|-------|-------|----------|-------|
| **1C.1** | 2-3h | 30-45 min | 2.5-3.5h |
| **1C.2** | 3-4h | 30-45 min | 3.5-4.5h |
| **1C.3** | 4-5h | Review | 4-5h |
| **Scale + tests** | — | 1h | 1h |
| **TOTAL** | 9-12h | 2h | **11-14h** |

---

## Key Principle: Validation Reveals Information

**Why validate after each phase:**
1. **Phase 1C.1 validation reveals:** Are exec changes accurately captured? This affects Phase 1C.2 (we need clean input).
2. **Phase 1C.2 validation reveals:** Is sentiment data clean enough for correlation? This affects Phase 1C.3 (bad sentiment = false correlations).
3. **Phase 1C.3 review:** Do relationships make sense? Inform Phase 2A/2B (fundamentals/technicals) design.

Each step builds on the previous one — validating early prevents cascading errors.

---

## Files to Update

- ✅ PHASE_1C_IMPLEMENTATION_GUIDE.md — Add validation sections
- ✅ INTELLIGENCE_MODEL_SCHEMA.py — Already complete
- ✅ DECISIONS.md — Sequencing decision locked
- ✅ NOVA.md — Session log (will update after work starts)

---

## Ready to Start?

Once you confirm, I'll:
1. ✅ Refine PHASE_1C_IMPLEMENTATION_GUIDE.md with validation checklists
2. ✅ Update NOVA.md with start timestamp
3. ✅ Begin Phase 1C.1 (Executive data collection)

---

**Decision locked: Option B (Validate-First). Ready to implement.** 🚀

---

**Updated:** 2026-04-21 06:49 UTC by Nova ✨
