# ENVESTERO PHASE 2 — DETAILED DESIGN FOR PEER REVIEW

**Prepared for:** Kira 🦾  
**Date:** 2026-04-21 01:18 UTC  
**Status:** Ready for architectural review before implementation  
**Phase 1 Status:** ✅ Complete (Nasdaq screener + batch OHLCV backfill)

---

## EXECUTIVE SUMMARY

Phase 2 adds **news ingestion + sentiment analysis** to Envestero. Takes stock ticker data from Phase 1 and enriches it with market sentiment (positive/negative/neutral scores on articles).

**Timeline:** 2–2.5 hours  
**Scope:** 3 components  
**Risk:** Low (services mostly exist, just wire + test)  
**Dependencies:** Phase 1 complete (ticker + OHLCV data in DB)

---

## CURRENT STATE (What Already Exists)

### Services Already Built
1. **newser.py** — GNews API integration
   - `fetch_news_for_symbols(symbols, limit, period)` — fetch articles
   - `get_news_refresh_candidates(session)` — stale ticker detection
   - Handles GNews rate limits + error recovery

2. **sentiment.py** — LLM sentiment analysis
   - `score_batch(session, batch_size)` — batch sentiment scoring
   - Supports: OpenAI API OR Ollama local OR heuristic fallback
   - Outputs: sentiment_score (-1.0 to 1.0), sentiment_label (positive/negative/neutral)

3. **NewsArticle model** — DB schema ready
   ```python
   class NewsArticle(Base):
       __tablename__ = "news_article"
       id, ticker_id, published_at, title, url, publisher
       sentiment_score, sentiment_label, model_used, sentiment_raw
       analyzed_at, created_at
   ```

### What Works
- Database schema (Alembic migration exists)
- NewsArticle ORM model
- Base GNews + sentiment infrastructure
- Error handling for API failures

---

## PHASE 2 DESIGN

### Component 1: Scheduled News Refresh Job (60 min)

**Current State:**  
- `job_collect_news()` exists in scheduler but incomplete

**What We Build:**
```python
async def job_refresh_news():
    """Every 4 hours: fetch news for top 100 tickers, upsert to DB."""
    
    # Step 1: Get top 100 tickers by volume/market cap
    symbols = await get_active_symbols(
        session, 
        limit=100, 
        order_by='market_cap'
    )
    
    # Step 2: Check which ones need news (>24h old or never fetched)
    stale_symbols = await get_news_refresh_candidates(
        session,
        min_age_hours=24,  # config
    )
    
    # Step 3: Fetch articles (GNews API, rate-limited)
    for symbol in stale_symbols:
        articles = await fetch_news_for_symbols(
            [symbol],
            limit=10,  # config: NEWS_COLLECTION_LIMIT
            period="7d",  # news from last 7 days
        )
        # Upsert to DB (handle duplicates via URL unique constraint)
        for article in articles:
            session.add(NewsArticle(
                ticker_id=...,
                title=article['title'],
                url=article['url'],
                published_at=article['published_at'],
                publisher=article['source'],
                sentiment_score=None,  # Will score later
            ))
    
    await session.commit()
    logger.info(f"Fetched news for {len(stale_symbols)} tickers")
```

**Configuration:**
```env
NEWS_COLLECTION_LIMIT=100           # Top N tickers per cycle
NEWS_REFRESH_HOURS=24               # Min hours between refreshes per ticker
NEWS_REQUEST_PAUSE_SECONDS=0.5      # Pause between ticker requests
SENTIMENT_BATCH_SIZE=20             # Articles per batch
SENTIMENT_CONCURRENCY=5             # Parallel sentiment workers
```

**Schedule:**
```python
_scheduler.add_job(
    job_refresh_news,
    CronTrigger(hour="*/4"),  # Every 4 hours
    id="refresh_news",
    name="Fetch news for top 100 tickers",
    replace_existing=True,
    misfire_grace_time=1800,
)
```

**Rate Limiting:**
- GNews API: Typically 500 requests/day free tier
- Our strategy: 100 tickers × 0.5s pause = 50s per cycle
- Every 4h × 6/day = 600 fetches/day (may need paid tier or backoff)
- Fallback: Heuristic sentiment if GNews unavailable

**Error Handling:**
- Network timeout → skip ticker, continue
- Rate limit (429) → exponential backoff, retry next cycle
- GNews down → log warning, skip article fetch

---

### Component 2: Sentiment Scoring Pipeline (45 min)

**Current State:**  
- `sentiment.py` has `score_batch()` but needs wiring

**What We Build:**

```python
async def job_score_news():
    """Nightly (9 PM ET): LLM-score all unscored articles."""
    
    # Get unscored articles (batch them for efficiency)
    unscored = await session.execute(
        select(NewsArticle)
        .where(NewsArticle.sentiment_score == None)
        .limit(1000)  # Don't score all at once (cost/time)
    )
    articles = unscored.scalars().all()
    
    if not articles:
        logger.info("No unscored articles")
        return
    
    # Score in batches (e.g., 20 articles per LLM call)
    settings = get_settings()
    provider = sentiment.get_provider(
        provider_type=settings.llm_provider,  # "openai" or "ollama"
    )
    
    batch_size = settings.sentiment_batch_size  # 20
    for i in range(0, len(articles), batch_size):
        batch = articles[i : i + batch_size]
        
        try:
            results = await provider.score_articles(batch)
            # results = [{article_id, score, label, raw_response}, ...]
            
            for result in results:
                article = next(a for a in batch if a.id == result['article_id'])
                article.sentiment_score = result['score']  # -1.0 to 1.0
                article.sentiment_label = result['label']  # positive/negative/neutral
                article.model_used = provider.model_name
                article.sentiment_raw = result['raw_response']
                article.analyzed_at = datetime.now(tz=timezone.utc)
            
            await session.commit()
        except Exception as e:
            logger.error(f"Sentiment batch failed: {e}")
            # Try heuristic fallback
            await score_with_heuristic(batch)
```

**Sentiment Providers (Cascading Fallback):**

```python
class SentimentProvider(ABC):
    async def score_articles(
        self, 
        articles: list[NewsArticle]
    ) -> list[dict]:
        """Return [{article_id, score, label, raw_response}, ...]"""
        pass

class OpenAISentimentProvider(SentimentProvider):
    """Use OpenAI GPT to score articles."""
    async def score_articles(self, articles):
        # Call OpenAI API with batch of articles
        # Prompt: "Rate sentiment: positive (1.0), neutral (0.0), negative (-1.0)"
        
class OllamaSentimentProvider(SentimentProvider):
    """Use local Ollama (free, fast, private)."""
    async def score_articles(self, articles):
        # Call local Ollama API (qwen2.5-coder or llama3.2)
        
class HeuristicSentimentProvider(SentimentProvider):
    """Fallback: keyword-based scoring (no API calls)."""
    async def score_articles(self, articles):
        # Simple word lists: positive words → +1, negative → -1, neutral → 0
        # E.g., "surge", "growth" → positive; "decline", "loss" → negative
```

**Configuration:**
```env
LLM_PROVIDER=ollama                 # "openai" or "ollama"
OPENAI_API_KEY=sk-...               # If using OpenAI
OPENAI_MODEL=gpt-4o-mini            # Cheaper than gpt-4
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:32b      # Or llama3.2
```

**Schedule:**
```python
_scheduler.add_job(
    job_score_news,
    CronTrigger(hour=21, minute=0),  # 9 PM ET nightly
    id="score_news",
    name="LLM-score unscored articles",
    replace_existing=True,
    misfire_grace_time=3600,
)
```

**Cost Analysis:**
- OpenAI gpt-4o-mini: ~$0.0001–0.0003 per article
- 100 tickers × 10 articles/day × 30 days = 30K articles/month
- Cost: ~$3–9/month (cheap, but Ollama is free)
- **Recommendation:** Use Ollama (local, free, private)

---

### Component 3: REST Endpoints (30 min)

**Current State:**  
- No endpoints for news/sentiment queries

**What We Build:**

```python
# envestero/api/routers/news.py (NEW FILE)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/{symbol}")
async def get_ticker_news(
    symbol: str,
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db_session),
):
    """Get recent news articles for a ticker.
    
    Args:
        symbol: Ticker symbol (e.g., "AAPL")
        days: Lookback period (default: 7 days)
    
    Returns:
        List of NewsArticle objects (most recent first)
    """
    ticker = await db.execute(
        select(TickerInfo).where(TickerInfo.symbol == symbol.upper())
    )
    ticker = ticker.scalar_one_or_none()
    if not ticker:
        raise HTTPException(status_code=404, detail=f"Ticker {symbol} not found")
    
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
    articles = await db.execute(
        select(NewsArticle)
        .where(NewsArticle.ticker_id == ticker.id)
        .where(NewsArticle.published_at >= cutoff)
        .order_by(NewsArticle.published_at.desc())
    )
    
    return {
        "symbol": symbol.upper(),
        "articles": [
            {
                "id": a.id,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "publisher": a.publisher,
                "sentiment_score": a.sentiment_score,
                "sentiment_label": a.sentiment_label,
                "analyzed_at": a.analyzed_at,
            }
            for a in articles.scalars()
        ]
    }


@router.get("/{symbol}/sentiment")
async def get_ticker_sentiment_summary(
    symbol: str,
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db_session),
):
    """Get aggregate sentiment for a ticker.
    
    Returns:
        {
            "symbol": "AAPL",
            "period_days": 7,
            "total_articles": 42,
            "sentiment_breakdown": {
                "positive": 28,
                "neutral": 10,
                "negative": 4,
            },
            "sentiment_score_avg": 0.62,
            "last_updated": "2026-04-21T01:00:00Z"
        }
    """
    ticker = await db.execute(
        select(TickerInfo).where(TickerInfo.symbol == symbol.upper())
    )
    ticker = ticker.scalar_one_or_none()
    if not ticker:
        raise HTTPException(status_code=404, detail=f"Ticker {symbol} not found")
    
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
    articles = await db.execute(
        select(NewsArticle)
        .where(NewsArticle.ticker_id == ticker.id)
        .where(NewsArticle.published_at >= cutoff)
        .where(NewsArticle.sentiment_score != None)  # Only scored articles
    )
    articles = articles.scalars().all()
    
    if not articles:
        return {
            "symbol": symbol.upper(),
            "period_days": days,
            "total_articles": 0,
            "sentiment_breakdown": {"positive": 0, "neutral": 0, "negative": 0},
            "sentiment_score_avg": None,
        }
    
    positive = sum(1 for a in articles if a.sentiment_score > 0.5)
    neutral = sum(1 for a in articles if -0.5 <= a.sentiment_score <= 0.5)
    negative = sum(1 for a in articles if a.sentiment_score < -0.5)
    avg_score = sum(a.sentiment_score for a in articles) / len(articles)
    
    return {
        "symbol": symbol.upper(),
        "period_days": days,
        "total_articles": len(articles),
        "sentiment_breakdown": {
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
        },
        "sentiment_score_avg": round(avg_score, 3),
        "last_updated": max(a.analyzed_at for a in articles),
    }
```

**Integration into FastAPI app:**
```python
# envestero/api/main.py

from envestero.api.routers import news

app = FastAPI(...)

app.include_router(news.router)
```

**Usage Examples:**
```bash
# Get recent news for Apple
curl http://localhost:8000/news/AAPL?days=7

# Get sentiment summary
curl http://localhost:8000/news/AAPL/sentiment

# Response:
{
  "symbol": "AAPL",
  "period_days": 7,
  "total_articles": 42,
  "sentiment_breakdown": {
    "positive": 28,
    "neutral": 10,
    "negative": 4
  },
  "sentiment_score_avg": 0.62,
  "last_updated": "2026-04-21T01:00:00Z"
}
```

---

## ARCHITECTURE DECISIONS

### 1. Why GNews Instead of NewsAPI or Bloomberg?
- **GNews:** Free tier (500/day), no signup, fast
- **NewsAPI:** Better coverage but paid ($449/month)
- **Bloomberg:** Requires subscription
- **Recommendation:** GNews free tier + upgrade to paid if needed

### 2. Why Ollama Over OpenAI for Sentiment?
- **Cost:** $0 vs $0.0001–0.0003 per article
- **Privacy:** Local, no data sent to cloud
- **Speed:** Faster (local network)
- **Fallback:** Still support OpenAI if user prefers
- **Trade-off:** Accuracy slightly lower (but good enough for sentiment)

### 3. Why Batch Sentiment Scoring?
- 20 articles per LLM call vs 1 article per call
- 95% fewer API calls / lower cost
- Batch processing is faster (parallel inference)

### 4. Why Cascading Fallback (OpenAI → Ollama → Heuristic)?
- **Resilience:** If OpenAI down, fall back to Ollama
- **Cost control:** User can choose (cheap vs fast)
- **Always works:** Heuristic baseline never fails

### 5. Why Top 100 Tickers Only?
- 3000+ tickers = 30K articles/day (cost + rate limits)
- Top 100 = 1K articles/day (manageable, focused)
- Volume/market cap usually correlates with news relevance

---

## DATA FLOW

```
Phase 1: OHLCV Data
    ↓
Phase 2: News Enrichment
    ├─ job_refresh_news (every 4h)
    │   └─ Fetch articles (GNews) → NewsArticle table
    │
    ├─ job_score_news (nightly 9 PM)
    │   └─ Score articles (LLM) → update sentiment_score/label
    │
    └─ REST endpoints
        ├─ GET /news/{symbol} → recent articles + sentiment
        └─ GET /news/{symbol}/sentiment → aggregate stats

Phase 3: Signal Generation (next)
    └─ CandlestickSignal (OHLCV patterns)
        + NewsArticle (sentiment)
        → TradeSignal (buy/sell recommendation)
```

---

## ERROR HANDLING & RESILIENCE

| Failure | Handling |
|---------|----------|
| **GNews API down** | Skip news fetch, retry next cycle |
| **OpenAI API timeout** | Fall back to Ollama or heuristic |
| **Ollama down** | Fall back to heuristic keyword scoring |
| **Rate limit (429)** | Exponential backoff, retry next cycle |
| **DB connection lost** | Rollback current batch, log error |
| **Duplicate article URL** | Ignore (unique constraint) |
| **Article has no text** | Skip sentiment scoring |

---

## TESTING STRATEGY

### Unit Tests
```python
# tests/unit/test_sentiment.py
- Test OpenAI sentiment scorer
- Test Ollama sentiment scorer
- Test heuristic sentiment scorer
- Verify score range (-1.0 to 1.0)
- Verify label correctness (positive/negative/neutral)

# tests/unit/test_newser.py
- Test GNews API parsing
- Test URL deduplication
- Test error recovery (timeout, rate limit)
```

### Integration Tests
```python
# tests/integration/test_news_pipeline.py
- Fetch news for 5 test tickers
- Score articles with Ollama
- Verify sentiment_score populated in DB
- Verify last_updated timestamp

# tests/integration/test_news_endpoints.py
- GET /news/AAPL → returns articles
- GET /news/AAPL/sentiment → returns aggregate stats
- Verify sentiment_breakdown math
```

### Smoke Tests
```python
# tests/integration/test_fasttrack_phase2.py
- Can import newser, sentiment services
- Can connect to GNews (or mock)
- Can connect to Ollama (or mock)
- REST endpoints are wired
- Scheduler job is registered
```

---

## TIMELINE & EFFORT

| Task | Duration | Effort |
|------|----------|--------|
| **Component 1: News Refresh Job** | 45 min | Medium |
| **Component 2: Sentiment Scoring** | 60 min | Medium |
| **Component 3: REST Endpoints** | 30 min | Low |
| **Testing & Validation** | 30 min | Medium |
| **Documentation** | 15 min | Low |
| **TOTAL** | **180 min (3 hours)** | **Medium** |

**Can parallelize:** News job + Sentiment job (independent implementations)

---

## RISKS & MITIGATIONS

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| GNews API rate limit | High | Medium | Use top 100 tickers only, 4h cycle |
| LLM sentiment cost | Medium | Low | Use Ollama (free) by default |
| Duplicate articles | High | Low | Unique constraint on URL |
| Poor sentiment accuracy | Medium | Medium | Use heuristic fallback + feedback loop |
| Scheduler job overlaps | Low | High | Use `misfire_grace_time` + job locks |

---

## SUCCESS CRITERIA

Phase 2 is successful when:

✅ News refresh job runs every 4 hours  
✅ 100 top tickers have fresh news (< 24h old)  
✅ Sentiment scoring job runs nightly (9 PM ET)  
✅ >95% of articles are scored  
✅ GET /news/{symbol} returns articles + sentiment  
✅ GET /news/{symbol}/sentiment returns aggregate stats  
✅ No major errors in logs (warnings OK for API timeouts)  
✅ All tests pass (unit + integration + smoke)

---

## DEPENDENCIES

- Phase 1 complete (ticker + OHLCV data)
- GNews API access (free tier)
- Ollama running locally (or OpenAI API key)
- Database (PostgreSQL + migrations)

---

## NEXT: PHASE 3 (Paper Trading)

Once Phase 2 complete:

1. **Signal Executor** (90 min)
   - Listen to TradeSignal table
   - Execute buy/sell on paper portfolio
   - Respect PDT rules

2. **Portfolio Snapshots** (30 min)
   - Daily NAV snapshots
   - Backtest reports (Sharpe, drawdown, returns)

3. **Algorithm Tuning** (120 min)
   - Test different signal combinations
   - Optimize entry/exit thresholds
   - Measure win rate, profit factor

---

## APPENDIX: OPEN QUESTIONS FOR KIRA

1. **Sentiment provider:** Preference for Ollama (free, local) vs OpenAI (more accurate, cost)?
2. **News refresh frequency:** Every 4 hours optimal, or prefer daily/hourly?
3. **Batch size:** 20 articles/batch for LLM scoring — too conservative?
4. **Fallback behavior:** If GNews down, should we skip news entirely or use cached articles?
5. **Article filtering:** Should we filter by relevance score, or keep all articles?
6. **Scoring labels:** Current 3-way (positive/neutral/negative) — want more granularity?
7. **REST endpoint pagination:** Limit articles per request (e.g., max 50)?
8. **Rate limiting on endpoints:** Throttle requests per IP to avoid scraping?

---

**Ready for Kira's feedback. What concerns/improvements?** 🦾

