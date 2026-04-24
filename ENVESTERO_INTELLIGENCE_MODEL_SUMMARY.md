# Envestero: Intelligence Model Architecture

**Updated:** 2026-04-21 06:00 UTC  
**Status:** Pivoted from 5m bars debugging → Multi-factor Leadership + Consumer Intelligence Model

---

## Your Request
"We need both data so we can extrapolate the factors of the market. Give me a list of publicly available data per ticker. Candlestick, P/E, all the inputs that change the ticker positively, negatively, and somewhere in between. **A relationship model would be good too. Influence on key figures like CEOs, CTO, CFO. When they exit and enter a new position. Consumer sentiment should be part of this information as well.**"

---

## What You're Building

A **holistic market intelligence system** that models:

### 1. **Leadership Intelligence**
- Who's in charge (CEO, CTO, CFO, etc.)
- Career timelines (when they joined, left, promoted)
- Their influence on company sentiment
- Succession risks and opportunities

### 2. **Consumer Intelligence**
- What customers think (Reddit, Twitter, Glassdoor, App Store)
- Sentiment by category (product quality, price, brand, leadership)
- How consumer sentiment predicts stock movement

### 3. **Relationship Detection**
- How do executive changes affect consumer sentiment?
- How does consumer sentiment affect stock price?
- How does sentiment relate to fundamentals?
- Which executives are most influential?

---

## The Complete Data Model

### Core Entities

**Executive**
- Name, Role, Tenure (start/end dates)
- Career background, education
- Current status (active/departed)

**ExecutiveEvent**
- What happened: Appointed, Resigned, Promoted, Retired
- When: Event date + announcement date
- Impact: Market reaction %, sentiment shift
- Context: Reason, replacement

**ConsumerSentiment**
- Source: Reddit, Twitter, Glassdoor, App Store, Trustpilot
- Score: -1.0 to +1.0
- Category: Product Quality, Price, Brand, Leadership, Innovation
- Volume: Mention count, engagement rate

**ExecutiveSentimentImpact**
- Which exec influences news sentiment most?
- Articles mentioning them: sentiment +/- vs baseline
- Influence score: 0-1, how much this exec drives sentiment

**ExecutiveConsumerInfluence**
- When executive changes → how does consumer sentiment shift?
- Does consumer sentiment predict stock price?
- Time lag: How many days between sentiment shift and price move?

**InfluenceNetwork**
- Directional relationships: Source → Target
- Examples:
  - CEO departure → Consumer sentiment drops → Stock falls (lag 3 days)
  - Product quality sentiment → Stock price (lag 5 days)
  - New VP of AI → Tech enthusiasm up → Consumer sentiment → Price up

---

## Implementation Phases

### Phase 1C.1 — Executive Data Model (2-3 hours)
**What you'll have:**
- Database schema for executives, events, sentiment impact
- CLI to add executives
- Backfilled data for 20 tickers (AAPL, MSFT, NVDA, etc.)
- Endpoint: `GET /api/v1/{symbol}/executives`

**Data sources:**
- SEC filings (8-K, proxy statements) — free, automated
- Company investor relations pages — manual
- Crunchbase API — auto if budget allows

### Phase 1C.2 — Consumer Sentiment Collection (3-4 hours)
**What you'll have:**
- Consumer sentiment table in DB
- Automated collection from Reddit, Twitter, Glassdoor
- Daily sentiment aggregation
- Endpoint: `GET /api/v1/{symbol}/consumer-sentiment?days=30&source=reddit`

**Data sources:**
- Reddit API — free, real-time
- Twitter API v2 — free, real-time
- Glassdoor — web scraping (free but manual) or API
- App Store reviews — web scraping or third-party API

### Phase 1C.3 — Relationship Detection Engine (4-5 hours)
**What you'll have:**
- Influence network graph
- Correlation analysis: Do executives affect consumer sentiment? Stock price?
- Time lag detection: X → Y after N days?
- Endpoint: `GET /api/v1/analysis/{symbol}/influence-network`

**Output example:**
```json
{
  "symbol": "AAPL",
  "executives": [
    {
      "name": "Tim Cook",
      "role": "CEO",
      "influence_score": 0.76,
      "impact": "Highly influential in positive sentiment"
    }
  ],
  "relationships": [
    {
      "source": "CEO Tim Cook mentions in news",
      "target": "consumer sentiment",
      "strength": 0.76,
      "direction": "positive",
      "confidence": 0.89
    },
    {
      "source": "consumer sentiment (brand)",
      "target": "stock price",
      "strength": 0.63,
      "direction": "positive",
      "time_lag_days": 3,
      "confidence": 0.82
    }
  ]
}
```

---

## Why This Matters

### Traditional Analysis
"AAPL stock moved 5% today because earnings beat estimates."

### Your Intelligence Model
"AAPL's new VP of AI drove positive coverage (+0.23 sentiment), which increased consumer enthusiasm about AI features (+0.31 consumer sentiment), which historically predicts stock movement within 3-5 days. We expect 2-4% upside."

**You can predict market moves before they happen.**

---

## Files Created

1. **INTELLIGENCE_MODEL_LEADERSHIP_CONSUMER.md** — Complete data model & API design
2. **INTELLIGENCE_MODEL_SCHEMA.py** — Database models (copy to your project)
3. **PHASE_1C_IMPLEMENTATION_GUIDE.md** — Step-by-step implementation (code examples)
4. **MARKET_DATA_INVENTORY.md** — All available data sources (for future phases)
5. **PHASE_1C_CORRELATION_PLAN.md** — Quick-start guide (sentiment ↔ price)

---

## Quick Start (Next 30 Minutes)

### Option A: Start with Phase 1C.1 (Executive Data)
**Time:** 2-3 hours to first working endpoint

```bash
# 1. Copy schema to your project
cp INTELLIGENCE_MODEL_SCHEMA.py envestero/db/models_leadership.py

# 2. Create migration
cd /srv/github/Envestero
alembic revision --autogenerate -m "Add leadership + consumer sentiment tables"
alembic upgrade head

# 3. Implement CLI for adding executives
# (Code provided in PHASE_1C_IMPLEMENTATION_GUIDE.md)

# 4. Backfill executives from SEC filings
# (Code provided for automated SEC parsing)

# 5. Create endpoint
# GET /api/v1/{symbol}/executives
```

### Option B: Start with Phase 1C.2 (Consumer Sentiment)
**Time:** 3-4 hours to first data collection

```bash
# 1. Same schema setup as above
# 2. Implement consumer sentiment collector (Reddit, Twitter)
# 3. Schedule daily collection job
# 4. Create endpoint: GET /api/v1/{symbol}/consumer-sentiment
```

### Option C: Full Intelligence Model
**Time:** 9-12 hours for all three phases

Start with 1C.1 → 1C.2 → 1C.3 in sequence.

---

## Your Decision

**What do you want to build first?**

1. **Phase 1C.1** — Executive data model (foundation)
2. **Phase 1C.2** — Consumer sentiment collection (parallel stream)
3. **Both in parallel** (requires splitting effort)
4. **Something else?**

---

## Technical Stack

- **Database:** PostgreSQL (already running)
- **ORMs:** SQLAlchemy (already in project)
- **APIs:** 
  - SEC EDGAR (free)
  - Reddit PRAW (free)
  - Twitter tweepy (free)
  - Crunchbase (paid, optional)
- **Processing:** Async/await for efficient collection
- **ML/Sentiment:** Ollama + llama3.2 (already running)

---

## Next Session Readiness

All code is ready to copy:
- ✅ Database schema (`INTELLIGENCE_MODEL_SCHEMA.py`)
- ✅ Collection logic (in `PHASE_1C_IMPLEMENTATION_GUIDE.md`)
- ✅ API endpoints (in same guide)
- ✅ CLI commands (in same guide)

Just need to:
1. Copy files
2. Run migration
3. Implement collection jobs
4. Test endpoints

**Estimated effort:** 9-12 hours for full implementation.

---

## Success Criteria

When complete, you'll be able to:
- ✅ Query all executives for a ticker + their tenure
- ✅ See how consumer sentiment evolves (daily)
- ✅ Identify which executives most influence sentiment
- ✅ Detect relationships: CEO change → consumer sentiment shift → stock move
- ✅ Predict market moves based on leadership + sentiment changes

That's your intelligence advantage.
