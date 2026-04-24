# STRATEGIC INSIGHT: Multi-Source Correlation Learning + Persona-Based Backtesting

**From:** Toan's Decision (2026-04-21 06:54 UTC)  
**Implications:** Architecture shift from "source of truth" to "correlation learning engine"  
**Impact on:** Phase 1C (sentiment collection), Phase 3 (paper trading design)

---

## The Insight

> "I don't want source of truth. I want to glean correlations between and create an algorithm that understands what impacts what."

### What This Changes

**Traditional approach (rejected):**
- Pick "best" sentiment source (e.g., Reddit)
- Use that as signal for trading
- Problem: Single source bias, misses cross-source dynamics

**Toan's approach (new direction):**
- Collect ALL sources (Reddit, Twitter, Glassdoor, App Store)
- Learn which sources predict price changes for which tickers
- Detect meta-signals: "When Reddit talks about product, Twitter sentiment follows 1-day later, then stock moves"
- Algorithm discovers correlations automatically

### Implication: Phase 1C.2 Design

**Each source is independent:**
- Reddit collector: independent data quality thresholds
- Twitter collector: independent thresholds
- Glassdoor collector: independent thresholds
- App Store collector: independent thresholds

**Then Phase 1C.3 (Influence Detection) learns:**
- Which sources correlate with each other
- Which combinations predict stock moves
- Time-lag patterns between sources
- Ticker-specific source weights

**Example output:**
```
Apple:
  - Reddit product sentiment → Twitter sentiment (1-day lag, r=0.62)
  - Twitter sentiment → Stock price (2-day lag, r=0.58)
  - Combined chain: Reddit → Twitter → Price (3-day total)
  - Confidence in this chain: HIGH

Tesla:
  - Glassdoor employee reviews → Twitter sentiment (5-day lag, r=0.71)
  - Twitter sentiment → Stock price (1-day lag, r=0.55)
  - Reddit product sentiment → Stock price (direct, r=0.48, not strong)
  - Confidence in Glassdoor→Twitter→Price: HIGH
  - Confidence in Reddit signal: LOW (skip it for Tesla)
```

### Implication: Phase 3 (Paper Trading) Design

Instead of fixed confidence threshold, use **persona-based backtesting**:

**Persona 1: Hedgefund Veteran (Conservative)**
- Uses only r > 0.7 signals
- Waits for very strong correlation
- Fewer trades, higher conviction
- Strategy: "I've seen many correlations. I only trade the strongest ones."

**Persona 2: Hedgefund Veteran (Information Overload)**
- Uses r > 0.3 signals (even weak ones)
- Synthesizes many signals
- More trades, lower per-signal conviction
- Strategy: "I monitor everything. My edge is synthesis, not single signals."

**Persona 3: Algorithmic Trader**
- Uses r > 0.5 (balanced)
- Optimizes for Sharpe ratio
- Medium trade frequency
- Strategy: "I'm not smart, I'm efficient. Moderate threshold, tight stops."

**Persona 4: Contrarian**
- Uses negative correlations
- Bets against consensus
- High risk, high reward
- Strategy: "When Reddit hates it, buy it."

**Persona 5: Sector Specialist**
- Different thresholds per sector
- Tech: r > 0.6, Consumer: r > 0.4, Energy: r > 0.7
- Expertise-driven
- Strategy: "I know tech better than energy. Adjust signals accordingly."

**Backtesting Framework:**
```
For each persona:
    For each threshold (or threshold set):
        Backtest on 20 tickers, 365 days
        Record: Win rate, Sharpe ratio, max drawdown, trades per year
        Compare to persona's "expected behavior"

Aggregate: Which persona won? Why?
→ Inform Phase 3.5 (Automated Strategy Selection)
```

---

## Implementation Sequence

### Phase 1C.1: Executive Data
- Build as planned
- No changes

### Phase 1C.2: Consumer Sentiment (All 4 Sources)
**Change from single-source approach:**
- Build 4 independent collectors
- Each has own data quality thresholds
- All feed into same database (ConsumerSentiment table)
- Tag each entry with source (reddit, twitter, glassdoor, app_store)

### Phase 1C.3: Influence Detection (Correlation Learning)
**Key change: Learn source interactions**
- Detect not just: exec event → price
- But also: Reddit sentiment → Twitter sentiment → price
- Calculate correlations between sources
- Output: Relationship graph with cross-source paths

### Phase 3: Paper Trading (Persona-Based Testing)
**Major change: Multiple strategy personas**
- Implement trading logic for each persona
- Each persona uses different confidence thresholds / signal combinations
- Run all personas on same data
- Compare outcomes empirically
- Learn which confidence level(s) work best

**Outcome:** Instead of "r > 0.5 is the answer," we get "r > 0.5 works for Tesla with Twitter data, but r > 0.7 works better for Apple with Reddit data."

---

## What This Unlocks

### Adaptive Confidence Thresholds
- Per-ticker thresholds (learn what works for each stock)
- Per-source thresholds (learn which sources are reliable)
- Per-sector thresholds (tech vs energy vs finance)
- Dynamic thresholds (adjust as market regime changes)

### Cross-Source Signal Synthesis
- Detect when multiple weak signals align (Reddit + Glassdoor both negative)
- Weight by source reliability (Twitter > Reddit for TSLA, reverse for others)
- Cascade detection (signal A → signal B → price move)
- Anticipatory signals (when does Reddit move before Twitter?)

### Explainability
- Instead of "this signal fired," output why: "CEO departure (exec data) caused negative sentiment in Glassdoor (employee reviews), which preceded Twitter discussion, which preceded stock drop"
- Full causal chain visible
- Easier to explain to investors / clients

### Robustness
- Single source failure (Twitter API down) doesn't break system
- System adapts to missing sources
- Multi-source consensus = higher confidence

---

## Timeline Impact

**Phase 1C.2 (Consumer Sentiment):**
- Implementing 4 collectors instead of 1 = ~+15-20% effort
- Still 3-4h (now 3.5-4.5h realistically)

**Phase 1C.3 (Influence Detection):**
- Learning cross-source correlations = +30% effort
- Was 4-5h, now 5-6h

**Phase 3 (Paper Trading):**
- Persona-based backtesting framework = +50% effort vs simple single-strategy trading
- Was ~8-10h (estimated), now ~12-15h
- But much more valuable output

**Overall impact:** +2-3h added to total (now ~13-17h for Phases 1C + 3)

---

## Implementation Priority

### Immediate (Phase 1C)
1. Build all 4 sentiment sources (not just Reddit)
2. Learn which sources correlate in Phase 1C.3
3. Document cross-source relationship graphs

### Phase 3 (Paper Trading)
1. Define 5 trading personas (conservative, overload, algo, contrarian, specialist)
2. Implement persona-specific trading logic
3. Backtest all personas on same data
4. Compare outcomes, learn optimal thresholds

### Phase 3.5 (Optimization)
1. Use backtesting results to auto-tune thresholds
2. Implement per-ticker threshold adaptation
3. Consider machine learning for threshold selection (train on backtesting results)

---

## Key Quotes (Decision Rationale)

> "I don't want source of truth."

Translation: Don't optimize for the "most accurate" source. Instead, optimize for information synthesis.

> "I want to glean correlations between and create an algorithm that understands what impacts what."

Translation: The magic is in understanding HOW sources relate to each other, not which one is most accurate.

> "Paper trading should involve running scenarios with different assumptions."

Translation: Theory won't tell us the right confidence threshold. Only empirical testing will.

> "Different personas will help us understand based on trade assumptions and the actual outcome."

Translation: Different trading strategies will reveal different optimal thresholds. Learn from all of them.

---

## Decision Recorded

✅ **DECISIONS.md** — All locked in  
✅ **NOVA.md** — Updated  
✅ **Phase 1C.2 scope:** All 4 sources confirmed  
✅ **Phase 3 scope:** Persona-based backtesting required  

---

## What's Next

1. **Phase 1C Implementation:** Start with all 4 sentiment sources
2. **Phase 1C.3 Planning:** Design cross-source correlation learning
3. **Phase 3 Planning:** Define trading personas + backtesting framework

---

**This is a clever approach. Multi-source learning + empirical persona testing beats single-threshold tuning.** 🎯

---

**Updated:** 2026-04-21 06:54 UTC by Nova ✨
