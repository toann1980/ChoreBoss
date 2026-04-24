# Quick Reference — Intelligence Model Implementation

## Files You Need (In Workspace)

1. **ENVESTERO_INTELLIGENCE_MODEL_SUMMARY.md** — Overview & architecture
2. **INTELLIGENCE_MODEL_LEADERSHIP_CONSUMER.md** — Data model design + API endpoints
3. **INTELLIGENCE_MODEL_SCHEMA.py** — Copy this to `envestero/db/models_leadership.py`
4. **PHASE_1C_IMPLEMENTATION_GUIDE.md** — Step-by-step code + examples

---

## Three Implementation Phases (9-12 hours total)

### Phase 1C.1: Executive Data (2-3 hours)
```
Goal: Database schema + backfilled leadership data for 20 tickers

Steps:
1. Copy INTELLIGENCE_MODEL_SCHEMA.py → envestero/db/models_leadership.py
2. Create migration: alembic revision --autogenerate -m "Add executives"
3. Implement CLI: python -m envestero.cli add-executive --symbol AAPL ...
4. Backfill from SEC filings (code provided)
5. Endpoint: GET /api/v1/{symbol}/executives

Output: List of all executives per ticker + their tenure timeline
```

### Phase 1C.2: Consumer Sentiment (3-4 hours)
```
Goal: Collect sentiment from Reddit, Twitter, Glassdoor daily

Steps:
1. Implement ConsumerSentimentCollector (code in guide)
2. Create async collection job (PRAW + tweepy)
3. Schedule daily: 2 AM UTC collection
4. Store in database (already have schema)
5. Endpoint: GET /api/v1/{symbol}/consumer-sentiment?days=30&source=reddit

Output: Daily sentiment trends by source + category
```

### Phase 1C.3: Influence Network (4-5 hours)
```
Goal: Detect relationships (CEO change → consumer sentiment → stock price)

Steps:
1. Compute executive sentiment impact (code provided)
2. Detect correlations: execs ↔ consumer sentiment ↔ price
3. Calculate time lags (X affects Y after N days?)
4. Build influence network graph
5. Endpoint: GET /api/v1/analysis/{symbol}/influence-network

Output: Complete relationship map showing what drives market movement
```

---

## Database Schema (6 tables)

```
Executive
├── name, role, start_date, end_date
├── is_current (boolean)
└── relationships → ExecutiveEvent, ExecutiveSentimentImpact

ExecutiveEvent
├── event_type (APPOINTED, RESIGNED, PROMOTED, RETIRED)
├── event_date, market_reaction_pct, sentiment_shift
└── relationships → Executive, TickerInfo

ExecutiveSentimentImpact
├── articles_mentioning, sentiment_when_mentioned
├── influence_score (0-1)
└── relationships → Executive

ConsumerSentiment
├── date, source (reddit/twitter/glassdoor/appstore)
├── sentiment_score, sentiment_label
├── category (product_quality, price, brand, leadership)
└── relationships → TickerInfo

ExecutiveConsumerInfluence
├── period_start, period_end
├── consumer_sentiment_before/after
├── correlation_to_stock_price, time_lag_days
└── relationships → Executive

InfluenceNetwork
├── source_type, target_type
├── influence_strength, direction
├── time_lag_days, confidence
└── relationships → TickerInfo
```

---

## Data Collection Strategy

### Executive Data (Free)
- SEC EDGAR API: 8-K forms (executive changes), proxy statements
- Company websites: Investor relations pages
- Optional: Crunchbase API (historical leadership)

### Consumer Sentiment (Free + Low Cost)
- **Reddit:** PRAW library, free, real-time
- **Twitter/X:** tweepy library, free, real-time
- **Glassdoor:** Web scraping (legal) or Glassdoor API
- **App Store:** Scraper library or app store API
- **Alternative:** Trustpilot, Google Reviews (web scraping)

---

## API Endpoints (When Complete)

```
# Executive Management
GET /api/v1/{symbol}/executives
GET /api/v1/{symbol}/executives/{exec_id}
GET /api/v1/{symbol}/executives/{exec_id}/timeline
GET /api/v1/{symbol}/executives/{exec_id}/impact

# Consumer Sentiment
GET /api/v1/{symbol}/consumer-sentiment?days=30&source=reddit
GET /api/v1/{symbol}/consumer-sentiment/by-category

# Influence Network
GET /api/v1/analysis/{symbol}/influence-network
GET /api/v1/analysis/{symbol}/executive/{exec_id}/influence
POST /api/v1/analysis/{symbol}/detect-relationships
```

---

## Example: What You Can Do When Complete

**Query:**
```json
GET /api/v1/analysis/AAPL/influence-network

Response:
{
  "executives": [
    {
      "name": "Tim Cook",
      "role": "CEO",
      "influence_score": 0.76,
      "impact": "Highly positive when mentioned"
    }
  ],
  "consumer_sentiment": {
    "trend": "improving",
    "avg_30d": 0.68
  },
  "relationships": [
    {
      "source": "Tim Cook news mentions",
      "target": "consumer brand sentiment",
      "strength": 0.76,
      "direction": "positive"
    },
    {
      "source": "consumer sentiment",
      "target": "stock price",
      "strength": 0.63,
      "time_lag_days": 3
    }
  ]
}
```

**Insight:**
"Tim Cook mentions drive brand sentiment. Brand sentiment predicts stock price within 3 days. Tim Cook retirement news would predict -3% to -5% move."

---

## Timeline Estimate

| Phase | Effort | Duration | Complexity |
|-------|--------|----------|------------|
| 1C.1  | 2-3h   | ~1 day   | Medium     |
| 1C.2  | 3-4h   | ~1 day   | Medium     |
| 1C.3  | 4-5h   | ~1-2 days| High       |
| **Total** | **9-12h** | **2-4 days** | **Medium-High** |

---

## Next Steps

**What do you want to build?**

1. **Phase 1C.1 only** → Executive data model (fastest to first results)
2. **Phase 1C.2 only** → Consumer sentiment (most interesting data)
3. **Phase 1C.1 + 1C.2** → Both in parallel (comprehensive)
4. **All three** → Full intelligence model (complete system)
5. **Something else?**

---

## Support

All code examples are in `PHASE_1C_IMPLEMENTATION_GUIDE.md`:
- Database models ✓
- Collection logic ✓
- CLI commands ✓
- API endpoints ✓
- Scheduler jobs ✓
- Relationship detection ✓

Ready to copy + paste + customize.

---

**Session:** 2026-04-21 06:00 UTC  
**Created by:** Nova  
**Status:** Awaiting your direction on which phase to start
