# Phase 1C Implementation Guide — Leadership + Consumer Intelligence

**Goal:** Build a relationship model connecting executives, consumer sentiment, and market behavior.

**Timeline:** 9-12 hours (3 focused sprints)

---

## Sprint 1: Executive Data Model (2-3 hours)

### Step 1: Migrate Database Schema
```bash
# Copy the schema models into your project
cp INTELLIGENCE_MODEL_SCHEMA.py envestero/db/models_leadership.py

# Create migration
alembic revision --autogenerate -m "Add executive and consumer sentiment tables"
alembic upgrade head
```

### Step 2: Backfill Executive Data

**Data sources (ranked by ease):**

1. **Company Websites** (Manual, 30 min)
   - Visit AAPL, MSFT, NVDA investor relations pages
   - Extract: Name, Role, Start Date, Bio
   - Paste into CSV

2. **SEC Filings** (Semi-automated, 1 hour)
   ```python
   # Use SEC EDGAR API (free)
   # Get Form 8-K (executive changes) for past 2 years
   # Get Proxy Statements (complete leadership list + compensation)
   
   from sec_api import QueryApi
   
   query_api = QueryApi(api_key="your_key")
   filings = query_api.get_filings(
       query=f"ticker:{symbol} AND formType:8-K AND filedAt:[2024-01-01 TO NOW]",
       limit=100
   )
   ```

3. **Crunchbase API** (Automated, 1.5 hours)
   - Historical leadership changes
   - Previously held positions
   - Education background

### Step 3: Create CLI for Executive Data Entry

```python
# envestero/cli/leadership.py

@click.command()
@click.option("--symbol", required=True, help="Ticker symbol")
@click.option("--exec-name", required=True)
@click.option("--role", required=True, help="CEO, CTO, CFO, etc.")
@click.option("--start-date", type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option("--end-date", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.option("--bio", help="Short biography")
async def add_executive(symbol: str, exec_name: str, role: str, start_date, end_date, bio):
    """Add an executive to the database."""
    factory = get_session_factory()
    async with factory() as session:
        # Get ticker
        ticker = await session.execute(
            select(TickerInfo).where(TickerInfo.symbol == symbol.upper())
        )
        ticker = ticker.scalar_one_or_none()
        if not ticker:
            click.echo(f"Ticker {symbol} not found")
            return

        # Create executive
        exec = Executive(
            ticker_id=ticker.id,
            name=exec_name,
            role=role,
            start_date=start_date.date(),
            end_date=end_date.date() if end_date else None,
            is_current=(end_date is None),
            bio_summary=bio,
        )
        session.add(exec)
        await session.commit()
        click.echo(f"✓ Added {exec_name} ({role}) to {symbol}")
```

**Usage:**
```bash
python -m envestero.cli add-executive \
  --symbol AAPL \
  --exec-name "Tim Cook" \
  --role CEO \
  --start-date 2011-08-24 \
  --bio "Former SVP at Apple, known for supply chain expertise"
```

---

## Sprint 2: Consumer Sentiment Collection (3-4 hours)

### Step 1: Create Consumer Sentiment Collector

```python
# envestero/services/consumer_sentiment.py

import asyncio
import praw  # Reddit
import tweepy  # Twitter
from trustpilot import reviews  # Trustpilot

class ConsumerSentimentCollector:
    """Collect sentiment from multiple sources."""
    
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id="...",
            client_secret="...",
            user_agent="...",
        )
        self.twitter = tweepy.Client(bearer_token="...")
    
    async def collect_reddit(self, symbol: str, days: int = 30) -> list[dict]:
        """Collect sentiment from Reddit for brand mentions."""
        sentiments = []
        
        # Search subreddits: investing, stocks, [ticker]
        for subreddit_name in ["investing", "stocks", symbol.lower()]:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                # Search posts mentioning the company
                for post in subreddit.search(
                    query=symbol,
                    time_filter="month",
                    limit=100,
                ):
                    # Score sentiment from comments
                    sentiment = await self._score_reddit_post(post)
                    sentiments.append({
                        "source": "reddit",
                        "date": datetime.fromtimestamp(post.created_utc).date(),
                        "text": post.title,
                        "sentiment_score": sentiment,
                        "engagement": post.score,
                    })
            except:
                continue
        
        return sentiments
    
    async def collect_twitter(self, symbol: str, company_name: str, days: int = 30) -> list[dict]:
        """Collect sentiment from Twitter/X."""
        sentiments = []
        
        # Search for brand mentions
        query = f'("{symbol}" OR "{company_name}") -is:retweet lang:en'
        tweets = self.twitter.search_recent_tweets(
            query=query,
            tweet_fields=["created_at", "public_metrics"],
            max_results=100,
        )
        
        for tweet in tweets.data or []:
            sentiment = await self._score_text(tweet.text)
            sentiments.append({
                "source": "twitter",
                "date": tweet.created_at.date(),
                "text": tweet.text,
                "sentiment_score": sentiment,
                "engagement": sum(
                    [
                        tweet.public_metrics["like_count"],
                        tweet.public_metrics["retweet_count"],
                    ]
                ),
            })
        
        return sentiments
    
    async def collect_glassdoor(self, company_name: str, days: int = 30) -> list[dict]:
        """Collect employee sentiment from Glassdoor reviews."""
        # Note: Glassdoor doesn't have official API
        # Use web scraping (legal with rate limits) or partner API
        
        sentiments = []
        # This would use Selenium or similar for scraping
        # Or use third-party API like apify
        return sentiments
    
    async def _score_text(self, text: str) -> float:
        """Score text using LLM or transformer model."""
        from envestero.services.sentiment import get_sentiment_provider
        
        provider = get_sentiment_provider()
        score = await provider.score(text)
        return score
    
    async def _score_reddit_post(self, post) -> float:
        """Score Reddit post by aggregating comment sentiments."""
        # Get top comments
        comments = [comment.body for comment in post.comments[:10]]
        
        scores = []
        for comment in comments:
            score = await self._score_text(comment)
            scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0.0
```

### Step 2: Schedule Consumer Sentiment Collection

```python
# In envestero/tasks/scheduler.py

@scheduler.task(
    id="collect_consumer_sentiment",
    trigger="cron",
    hour=2,  # Daily at 2 AM
    minute=0,
)
async def job_collect_consumer_sentiment(session: AsyncSession):
    """Daily: Collect consumer sentiment from all sources."""
    collector = ConsumerSentimentCollector()
    
    # Get all active tickers
    tickers = await get_active_symbols(session)
    
    for symbol in tickers:
        # Collect from each source
        reddit_sentiments = await collector.collect_reddit(symbol, days=1)
        twitter_sentiments = await collector.collect_twitter(symbol, days=1)
        glassdoor_sentiments = await collector.collect_glassdoor(symbol, days=1)
        
        # Aggregate and save
        all_sentiments = reddit_sentiments + twitter_sentiments + glassdoor_sentiments
        
        for sentiment in all_sentiments:
            consumer_sentiment = ConsumerSentiment(
                ticker_id=get_ticker_id(symbol),
                date=sentiment["date"],
                source=sentiment["source"],
                sentiment_score=sentiment["sentiment_score"],
                sentiment_label=_label_sentiment(sentiment["sentiment_score"]),
                mentions_count=1,  # Will aggregate later
                engagement_rate=sentiment.get("engagement", 0),
                category="general",  # Can be refined
            )
            session.add(consumer_sentiment)
        
        await session.commit()
```

### Step 3: Test Consumer Sentiment Collection

```bash
# Run manually for AAPL
python -m envestero.cli consumer-sentiment collect --symbol AAPL --days 7

# View results
python -m envestero.cli consumer-sentiment view --symbol AAPL
```

---

## Sprint 3: Relationship Detection Engine (4-5 hours)

### Step 1: Compute Executive Sentiment Impact

```python
# envestero/services/influence.py

async def compute_executive_sentiment_impact(
    session: AsyncSession,
    ticker_id: int,
    executive_id: int,
    period_start: date,
    period_end: date,
) -> ExecutiveSentimentImpact:
    """
    Compute how much an executive influences news sentiment.
    
    Does: Count articles mentioning exec vs not mentioning, compare sentiment.
    """
    from sqlalchemy import func, and_
    
    # Articles mentioning this executive
    articles_with = await session.execute(
        select(func.count(NewsArticle.id))
        .select_from(NewsArticle)
        .join(TickerInfo)
        .where(
            and_(
                TickerInfo.id == ticker_id,
                NewsArticle.published_at >= period_start,
                NewsArticle.published_at <= period_end,
                # Check if article text contains executive name
                func.lower(NewsArticle.title).contains(
                    func.lower(select(Executive.name).where(Executive.id == executive_id))
                ),
            )
        )
    )
    
    articles_with_count = articles_with.scalar()
    
    # Sentiment when mentioned
    sentiment_with = await session.execute(
        select(func.avg(NewsArticle.sentiment_score))
        .select_from(NewsArticle)
        .join(TickerInfo)
        .where(
            and_(
                TickerInfo.id == ticker_id,
                NewsArticle.published_at >= period_start,
                NewsArticle.published_at <= period_end,
                func.lower(NewsArticle.title).contains(
                    func.lower(select(Executive.name).where(Executive.id == executive_id))
                ),
            )
        )
    )
    
    sentiment_with_score = sentiment_with.scalar() or 0.0
    
    # Total articles in period (for % calculation)
    total_articles = await session.execute(
        select(func.count(NewsArticle.id))
        .select_from(NewsArticle)
        .join(TickerInfo)
        .where(
            and_(
                TickerInfo.id == ticker_id,
                NewsArticle.published_at >= period_start,
                NewsArticle.published_at <= period_end,
            )
        )
    )
    
    total_count = total_articles.scalar()
    
    # Sentiment when NOT mentioned
    sentiment_without = await session.execute(
        select(func.avg(NewsArticle.sentiment_score))
        .select_from(NewsArticle)
        .join(TickerInfo)
        .where(
            and_(
                TickerInfo.id == ticker_id,
                NewsArticle.published_at >= period_start,
                NewsArticle.published_at <= period_end,
                ~func.lower(NewsArticle.title).contains(
                    func.lower(select(Executive.name).where(Executive.id == executive_id))
                ),
            )
        )
    )
    
    sentiment_without_score = sentiment_without.scalar() or 0.0
    
    # Influence score: How much does this exec's presence affect sentiment?
    influence_score = abs(sentiment_with_score - sentiment_without_score) / 2.0
    
    # Create impact record
    impact = ExecutiveSentimentImpact(
        executive_id=executive_id,
        ticker_id=ticker_id,
        period_start=period_start,
        period_end=period_end,
        articles_mentioning=articles_with_count,
        articles_total=total_count,
        sentiment_when_mentioned=sentiment_with_score,
        sentiment_when_not_mentioned=sentiment_without_score,
        sentiment_difference=sentiment_with_score - sentiment_without_score,
        influence_score=influence_score,
    )
    
    session.add(impact)
    await session.commit()
    
    return impact
```

### Step 2: Build Influence Network

```python
# envestero/services/influence.py

async def detect_influence_relationships(
    session: AsyncSession,
    ticker_id: int,
) -> list[InfluenceNetwork]:
    """
    Detect relationships between:
    - Executive changes → consumer sentiment shift
    - Consumer sentiment → stock price movement
    - News sentiment → stock price movement
    """
    relationships = []
    
    # 1. Executive Changes → Consumer Sentiment Shift
    executives = await session.execute(
        select(Executive).where(Executive.ticker_id == ticker_id)
    )
    
    for executive in executives.scalars():
        for event in executive.tenure_events:
            # Get consumer sentiment before/after event
            days_before = 30
            days_after = 30
            
            sentiment_before = await session.execute(
                select(func.avg(ConsumerSentiment.sentiment_score))
                .where(
                    and_(
                        ConsumerSentiment.ticker_id == ticker_id,
                        ConsumerSentiment.date >= (event.event_date - timedelta(days=days_before)),
                        ConsumerSentiment.date < event.event_date,
                    )
                )
            )
            
            sentiment_after = await session.execute(
                select(func.avg(ConsumerSentiment.sentiment_score))
                .where(
                    and_(
                        ConsumerSentiment.ticker_id == ticker_id,
                        ConsumerSentiment.date > event.event_date,
                        ConsumerSentiment.date <= (event.event_date + timedelta(days=days_after)),
                    )
                )
            )
            
            before = sentiment_before.scalar() or 0.0
            after = sentiment_after.scalar() or 0.0
            shift = after - before
            
            if abs(shift) > 0.05:  # Only significant shifts
                relationship = InfluenceNetwork(
                    ticker_id=ticker_id,
                    source_type="executive",
                    source_id=executive.id,
                    target_type="consumer_sentiment",
                    target_description=f"Consumer sentiment post-{event.event_type}",
                    influence_strength=min(abs(shift), 1.0),
                    direction="positive" if shift > 0 else "negative",
                    time_lag_days=0,
                    sample_size=days_before + days_after,
                    confidence=0.7,  # Estimate
                    observed_start=event.event_date - timedelta(days=days_before),
                    observed_end=event.event_date + timedelta(days=days_after),
                )
                relationships.append(relationship)
    
    # 2. Consumer Sentiment → Stock Price Movement
    # (Similar pattern: correlate consumer sentiment with daily price changes)
    
    # 3. News Sentiment → Stock Price Movement
    # (Similar pattern: correlate news sentiment with daily price changes)
    
    # Save all relationships
    for rel in relationships:
        session.add(rel)
    
    await session.commit()
    return relationships
```

### Step 3: Create Influence Network Endpoint

```python
# envestero/api/routers/intelligence.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from envestero.api.deps import db

router = APIRouter()

@router.get("/{symbol}/influence-network")
async def get_influence_network(
    symbol: str,
    session: AsyncSession = Depends(db),
) -> dict:
    """
    Get the complete influence network for a ticker.
    
    Shows:
    - Executive profiles and their impact on sentiment
    - Consumer sentiment trends
    - Relationships between all factors
    """
    ticker = await session.execute(
        select(TickerInfo).where(TickerInfo.symbol == symbol.upper())
    )
    ticker = ticker.scalar_one_or_none()
    
    if not ticker:
        raise HTTPException(status_code=404, detail=f"Ticker {symbol} not found")
    
    # Get executives
    executives = await session.execute(
        select(Executive).where(Executive.ticker_id == ticker.id)
    )
    
    # Get consumer sentiment
    consumer_sentiment = await session.execute(
        select(ConsumerSentiment).where(ConsumerSentiment.ticker_id == ticker.id)
        .order_by(ConsumerSentiment.date.desc())
        .limit(90)
    )
    
    # Get influence relationships
    relationships = await session.execute(
        select(InfluenceNetwork).where(InfluenceNetwork.ticker_id == ticker.id)
    )
    
    return {
        "symbol": symbol.upper(),
        "executives": [
            {
                "name": exec.name,
                "role": exec.role,
                "start_date": exec.start_date.isoformat(),
                "end_date": exec.end_date.isoformat() if exec.end_date else None,
                "is_current": exec.is_current,
                "influence_score": (
                    exec.sentiment_impacts[-1].influence_score
                    if exec.sentiment_impacts
                    else None
                ),
            }
            for exec in executives.scalars()
        ],
        "consumer_sentiment": {
            "sources": list(set(cs.source for cs in consumer_sentiment.scalars())),
            "avg_score_30d": (
                sum(cs.sentiment_score for cs in consumer_sentiment.scalars()[:30])
                / 30
                if consumer_sentiment.scalars()
                else None
            ),
            "trend": "improving" if len(consumer_sentiment.scalars()) > 30 and 
                     (sum(cs.sentiment_score for cs in consumer_sentiment.scalars()[:15]) / 15) >
                     (sum(cs.sentiment_score for cs in consumer_sentiment.scalars()[15:30]) / 15)
                     else "declining",
        },
        "relationships": [
            {
                "source": rel.source_type,
                "target": rel.target_type,
                "strength": rel.influence_strength,
                "direction": rel.direction,
                "time_lag_days": rel.time_lag_days,
                "confidence": rel.confidence,
            }
            for rel in relationships.scalars()
        ],
    }
```

---

## Testing the Intelligence Model

```bash
# 1. Add executives
python -m envestero.cli add-executive \
  --symbol AAPL --exec-name "Tim Cook" --role CEO \
  --start-date 2011-08-24

# 2. Collect consumer sentiment
python -m envestero.cli consumer-sentiment collect --symbol AAPL --days 30

# 3. Compute relationships
python -m envestero.cli intelligence detect-relationships --symbol AAPL

# 4. View network
curl http://localhost:8000/api/v1/analysis/AAPL/influence-network
```

---

## Next: What to Build First?

1. **Sprint 1 (Now):** Executive data model + backfill 20 tickers' leadership
2. **Sprint 2 (Parallel):** Consumer sentiment collection (Reddit + Twitter)
3. **Sprint 3 (Final):** Relationship detection + influence network endpoints

**Timeline:** 9-12 hours for full implementation.

Want to start with Sprint 1?
