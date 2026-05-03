# COMPREHENSIVE PLAN: Phase 0 → Phase 1C (Parallel) → Phase 3

**Date:** 2026-04-21 07:05 UTC  
**Status:** Revised after Toan's MVP optimization question  
**Total Duration:** 24.5-31.5 hours

---

## REVISION SUMMARY

### Previous Plan (Task 0 + Sequential Phases)
- Task 0: Fix 5m bars (45 min)
- Phase 1C: Sequential (13-17h)
- Total: 25.75-31h

### Revised Plan (Phase 0 MVP + Parallel Phases)
- **Phase 0:** Single-ticker validation (2.5-3h)
- **Phase 1C:** Parallel (9-10h)
- Total: 24.5-31.5h

**Improvements:**
- ✅ Validates signal chain before scaling (risk mitigation)
- ✅ Eliminates Task 0 (not needed for position trading)
- ✅ Parallelizes 1C.1 + 1C.2 (saves ~2h)
- ✅ Same total time, better approach

---

## PHASE 0: Single-Ticker Validation (MVP) — 2.5-3 hours

**Goal:** Prove sentiment → price direction works before scaling to 20 tickers

**Ticker:** Apple (AAPL) only

### Tasks

**0.1: Executive Data (45 min)**
- Build Executive + ExecutiveEvent tables
- Fetch Apple execs from SEC Edgar
- Store: CEO, CFO, CTO + dates
- Validate: ≥3 execs, dates correct

**0.2: Consumer Sentiment (1h)**
- Implement 4 collectors (Reddit, Twitter, Glassdoor, App Store)
- Apply data quality thresholds
- Collect: 7 days of Apple sentiment
- Output: ~100-200 sentiment entries

**0.3: Daily Validation (30 min)**
- Get sentiment data (7 days)
- Get daily OHLCV (same 7 days)
- Measure: Did sentiment predict next day's price?
- Target: Accuracy > 60%

**0.4: Source Ranking (30 min)**
- Measure each source independently
- Which source most reliable for Apple?
- Rank: Twitter > Glassdoor > Reddit > App Store

### Success Criteria
- ✅ Accuracy > 60% (better than random)
- ✅ At least one source > 70% accurate
- ✅ Clear patterns in 7-day sample

### If Success → Go to Phase 1C
### If Failure → Investigate or pivot

---

## PHASE 1C: Three Phases, Two Run in Parallel — 9-10 hours

### Architecture

```
Phase 1C.1 (Execs)      [2-3h]  ─┐
                                  ├─ Parallel, independent
Phase 1C.2 (Sentiment)  [3-4h]  ─┤ 
                                  │
                                  └─► Phase 1C.3 (Correlations) [5-6h]
                                       (sequential, needs 1C.1 + 1C.2)
```

### Phase 1C.1: Executive Data (All 20 Tickers) — 2-3 hours

**Extends Phase 0.1 from AAPL to all 20 tickers**

- Implement full Executive + ExecutiveEvent collection
- Fetch from SEC Edgar for all 20 tickers
- Validate: Each ticker ≥3 execs
- Database table: Fully populated

**Validation:**
- Spot-check 5 execs per ticker
- Verify dates, titles, career transitions

**Output:** Executive table with 60-100 exec records

---

### Phase 1C.2: Consumer Sentiment (All 20 Tickers) — 3-4 hours

**Extends Phase 0.2 from AAPL to all 20 tickers**

- Full sentiment collection (all 4 sources)
- Apply thresholds: Reddit >10 upvotes, Twitter >50/day, Glassdoor >20 helpful, App Store by volume
- Category classification: Leadership, Product, Service
- Collect: 7+ days per ticker

**Validation:**
- Sample 20 sentiment labels
- Accuracy check: >80% correct
- Verify thresholds work

**Output:** ConsumerSentiment table with ~2000-4000 entries (20 tickers × 100-200 entries)

---

### Phase 1C.3: Influence Network Detection — 5-6 hours

**Requires:** Phase 1C.1 + 1C.2 outputs

- Build InfluenceNetwork table
- Detect correlations:
  - Source-to-source (Reddit → Twitter)
  - Source-to-price (Sentiment → Daily close)
  - Cross-ticker patterns
- Measure lags using daily data:
  - Lag windows: 1-day, 3-day, 5-day
  - Min r > 0.5, min 20 observations
- Learn per-ticker source weights

**Output:** InfluenceNetwork table with relationships + weights

---

## Phase 1C Timeline (After Phase 0 Success)

| Phase | Duration | Parallelizable? | Depends On |
|-------|----------|-----------------|-----------|
| 1C.1 | 2-3h | ✅ YES (parallel with 1C.2) | Phase 0 |
| 1C.2 | 3-4h | ✅ YES (parallel with 1C.1) | Phase 0 |
| 1C.3 | 5-6h | ❌ NO (sequential) | 1C.1 + 1C.2 |
| Scale | 1h | ✅ YES | All phases |
| **Total** | **9-10h** | — | — |

**vs Sequential:** 13-17h → 9-10h savings: 4-7 hours

---

## PHASE 3: Persona-Based Paper Trading — 12-15 hours

**Requires:** Phase 1C complete

### Personas (5+)

1. **Conservative Hedgefund Veteran**
   - Confidence: r > 0.7
   - Max trades: 5/month
   - Strategy: Wait for very strong signals

2. **Information-Overload Hedgefund Veteran**
   - Confidence: r > 0.3
   - Max trades: 50/month
   - Strategy: Use all signals, heavy filtering

3. **Algorithmic Trader**
   - Confidence: r > 0.5
   - Max trades: 20/month
   - Strategy: Balanced, Sharpe optimization

4. **Contrarian**
   - Confidence: Negative correlations
   - Max trades: 10/month
   - Strategy: Bet against consensus

5. **Sector Specialist**
   - Confidence: Per-sector thresholds
   - Max trades: Varies
   - Strategy: Domain expertise

### Backtesting

- **Data:** 20 tickers, 365 days
- **Entry:** Sentiment signal detected
- **Exit:** Target hit or stop loss
- **Measure:** Win rate, Sharpe ratio, max drawdown

### Output

- Which persona won?
- Which threshold works best?
- Per-ticker optimal strategy
- Confidence for production deployment

---

## COMPLETE TIMELINE

| Phase | Duration | Notes |
|-------|----------|-------|
| **Phase 0** | 2.5-3h | MVP validation (AAPL only) |
| **Phase 1C.1 + 1C.2** | 3.5-4h | Parallel (independent) |
| **Phase 1C.3** | 5-6h | Sequential (needs both above) |
| **Scale** | 1h | Consolidate all data |
| **Phase 3** | 12-15h | Persona backtesting |
| **TOTAL** | **24.5-31.5h** | Ready for deployment |

---

## Key Decisions Locked

✅ **Sequencing:** Validate-first (Phase 0 proves concept)  
✅ **Consumer sources:** All 4 (Reddit, Twitter, Glassdoor, App Store)  
✅ **Confidence threshold:** Dynamic via persona testing  
✅ **5m bars:** Not needed (daily OHLCV sufficient for position trading)  
✅ **Parallelization:** 1C.1 + 1C.2 parallel, 1C.3 sequential  

---

## Risk Mitigation

**Phase 0 (MVP):**
- Tests signal chain on ONE ticker
- Fast feedback (2.5-3h, not 13-17h)
- If fails: Pivot before major effort
- If succeeds: Confidence to scale

**Parallelization:**
- 1C.1 + 1C.2 independent (no conflicts)
- Saves ~2 hours
- Same total time, better approach

**Persona Testing:**
- Multiple confidence thresholds
- Multiple strategies
- Empirical validation (not theoretical)
- Learn what actually works

---

## Files to Reference

**Design & Planning:**
- PHASE_0_SINGLE_TICKER_VALIDATION_MVP.md
- PHASE_1C_PARALLELIZATION_STRATEGY.md
- CRITICAL_5M_BARS_VALIDATION_FOUNDATION.md (rationale for skipping)

**Decision History:**
- DECISIONS.md (memory-sync)
- NOVA.md (memory-sync)

**Implementation Guides:**
- PHASE_1C_IMPLEMENTATION_GUIDE.md
- INTELLIGENCE_MODEL_SCHEMA.py

---

## Status

**Ready to start:** Phase 0 (2.5-3h MVP validation on AAPL)

**Decision required from Toan:**
1. ✅ Approve Phase 0 approach?
2. ✅ Approve Phase 1C parallelization?
3. ✅ Ready to begin?

---

**Updated:** 2026-04-21 07:05 UTC by Nova ✨
