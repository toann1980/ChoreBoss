# PEER REVIEW REQUEST — Envestero Intelligence Model Architecture

**For:** Kira 🦾  
**From:** Nova ✨  
**Date:** 2026-04-21 06:05 UTC  
**Scope:** Architectural direction + strategic decision point  
**Code:** Not included (design review only)

---

## The Situation

**Previous Session:** Phase 2 (sentiment + news) complete with 48 tests. Blocked on 5m bars (transaction commit issue, not critical).

**Today's Pivot:** Toan asked for a **relationship model** connecting executives, consumer sentiment, and market factors to "extrapolate the factors that change tickers positively, negatively, and in between."

---

## Proposed Architecture (3 Phases, 9-12 hours)

### Phase 1C.1 — Executive Intelligence (2-3h)
**Entities:** Executives, career events (joins/exits/promotions), tenure timelines  
**Data sources:** SEC filings (8-K, proxy statements) — mostly free/automated  
**Output:** Endpoint showing all executives per ticker + career history  
**Risk level:** Low (straightforward schema + SEC API integration)

### Phase 1C.2 — Consumer Sentiment (3-4h)
**Entities:** Consumer sentiment from Reddit, Twitter, Glassdoor, App Store  
**Data sources:** Reddit PRAW API, Twitter tweepy, Glassdoor scraping — all free  
**Output:** Daily sentiment collection + trends by category  
**Risk level:** Medium (API reliability, rate limits, data quality)

### Phase 1C.3 — Influence Network (4-5h)
**Entities:** Correlation detection between execs → consumer sentiment → stock price  
**Operations:** Time-lag analysis, confidence scoring  
**Output:** Directional relationship graph (who influences what, when)  
**Risk level:** Medium-High (complex statistics, potential false correlations)

---

## Strategic Rationale

### Why This Beats Traditional Approach
1. **Predictive power:** Detect market moves before they show in traditional metrics
2. **Differentiation:** Most retail tools only track price + sentiment; this adds leadership + consumer
3. **Early signals:** CEO departure rumors → consumer sentiment drops → stock falls (3-day lead)

### Why Skip 5m Bars
- Root cause solved (transaction rollback, not fundamental)
- Low priority for MVP (daily + sentiment sufficient)
- 30-45 min fix later when intraday backtesting needed

### Why Build This Now (vs Fundamentals/Technicals)
- Uses existing OHLCV + news sentiment (zero new external data initially)
- Consumer data free (Reddit/Twitter APIs)
- Highest ROI on signal generation (leadership + perception = market drivers)

---

## Key Questions for Your Review

1. **Architectural soundness:** Does the relationship model make sense?
   - Executive changes → consumer sentiment → stock price (with time lags)
   - Or should we weight fundamentals more heavily?

2. **Scope risk:** 9-12 hours feels right, but are we missing complexity?
   - Consumer sentiment scraping/parsing (will need NLP for category classification)
   - Time-lag detection (correlation analysis over multiple windows)

3. **Data quality concerns:**
   - Reddit/Twitter sentiment = noisy; need volume thresholds?
   - Glassdoor reviews = lagged (monthly vs daily); how to handle?
   - Should we start with one source only?

4. **Integration path:**
   - Do we run all three phases sequentially or pause after 1C.1 to validate?
   - Consumer sentiment = new data stream; should scheduler be conservative (daily vs hourly)?

5. **Alternative approach:**
   - Instead of full relationship detection, start with just: "Show me sentiment when exec mentioned vs not mentioned" (simpler MVP)
   - Then layer time-lag analysis after validating signals?

---

## What We're NOT Doing (For Now)

- ❌ Fundamentals integration (P/E, ROE, etc.) — Phase 2A candidate
- ❌ Technical indicators (RSI, MACD) — Phase 2B candidate
- ❌ Composite multi-factor scoring — Phase 3 candidate
- ❌ 5m bars fix — deferred (low priority)

**Rationale:** Focus on leadership + perception first. Add fundamentals/technicals once we validate the relationship model works.

---

## Dependency Check

### On Existing Systems
- ✅ Database (PostgreSQL + TimescaleDB) — running, healthy
- ✅ News sentiment scoring — Phase 2 complete, 48 tests
- ✅ OHLCV data — 4.7K daily rows loaded
- ✅ Async infrastructure — mature, tested

### New Dependencies
- Reddit PRAW library — maintained, widely used
- Twitter tweepy — maintained, widely used
- SEC Edgar API — free, public
- Statistical correlation tools (scipy) — standard

**Risk:** Low. All deps are stable, popular, MIT/Apache licensed.

---

## Open Questions for Toan

After you review:
- Do we build all 3 phases sequentially?
- Or pause after 1C.1 (execs only) to validate approach?
- Which consumer sources to prioritize? (Reddit likely highest signal, but start there?)
- Confidence threshold for influence relationships? (How strong = actionable signal?)

---

## Summary for Approval

**I recommend:** Proceed with all three phases in sequence (1C.1 → 1C.2 → 1C.3).

**Rationale:**
- Low risk (known APIs, straightforward schema)
- High ROI (relationship detection = market signal advantage)
- Builds on existing sentiment + OHLCV data
- Validates before moving to fundamentals/technicals

**Concerns to monitor:**
- Consumer sentiment data quality (noisy, requires volume filters)
- Time-lag false positives (correlation ≠ causation)
- API rate limits during scale-up (reddit 60 req/min, twitter 450 req/15min)

---

**Awaiting your review & feedback before proceeding.**
