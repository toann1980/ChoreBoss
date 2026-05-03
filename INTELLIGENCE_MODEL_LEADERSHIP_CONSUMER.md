# Market Intelligence Relationship Model

**Goal:** Model how leadership changes, executive influence, and consumer sentiment affect stock performance and market perception.

---

## Core Entities

### 1. Executive (Leadership Profiles)
```python
class Executive(Base):
    """Key company leaders and their influence."""
    __tablename__ = "executives"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))
    
    # Identity
    name: Mapped[str]
    role: Mapped[str]  # CEO, CTO, CFO, COO, etc.
    title: Mapped[str | None]  # Full title e.g. "Chief Executive Officer"
    
    # Career Timeline
    start_date: Mapped[date]
    end_date: Mapped[date | None]  # NULL if currently employed
    is_current: Mapped[bool]  # True if active at ticker now
    
    # Background
    bio_summary: Mapped[str | None]
    previous_roles: Mapped[str | None]  # JSON list of prior positions
    education: Mapped[str | None]
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ticker: Mapped[TickerInfo] = relationship(back_populates="executives")
    tenure_events: Mapped[list["ExecutiveEvent"]] = relationship(back_populates="executive")
    sentiment_impact: Mapped[list["ExecutiveSentimentImpact"]] = relationship(back_populates="executive")
```

### 2. Executive Events (Career Transitions)
```python
class ExecutiveEvent(Base):
    """Track when executives join/leave/change roles."""
    __tablename__ = "executive_events"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    executive_id: Mapped[int] = mapped_column(ForeignKey("executives.id"))
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))
    
    # Event Details
    event_type: Mapped[str]  # "APPOINTED", "RESIGNED", "PROMOTED", "RETIRED"
    event_date: Mapped[date]
    role_previous: Mapped[str | None]  # What they did before (if promotion)
    role_new: Mapped[str]  # What they're doing now
    
    # Impact Assessment
    market_reaction: Mapped[float | None]  # Stock price % change on announcement day
    sentiment_shift: Mapped[float | None]  # News sentiment change (-1.0 to +1.0)
    investor_confidence: Mapped[str | None]  # "positive", "negative", "neutral"
    
    # Details
    announcement_date: Mapped[date | None]
    reason: Mapped[str | None]  # Why they left (retirement, new opportunity, etc.)
    replacement: Mapped[str | None]  # Who replaced them (if applicable)
    
    # Relationships
    executive: Mapped[Executive] = relationship(back_populates="tenure_events")
    ticker: Mapped[TickerInfo] = relationship()
```

### 3. Executive Sentiment Impact (How leadership affects news sentiment)
```python
class ExecutiveSentimentImpact(Base):
    """Track how mentions of specific executives correlate with sentiment."""
    __tablename__ = "executive_sentiment_impact"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    executive_id: Mapped[int] = mapped_column(ForeignKey("executives.id"))
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))
    
    period_start: Mapped[date]
    period_end: Mapped[date]
    
    # Sentiment when mentioned
    articles_mentioning: Mapped[int]  # How many articles mentioned them
    sentiment_when_mentioned: Mapped[float]  # Avg sentiment in those articles
    sentiment_when_not_mentioned: Mapped[float]  # Baseline sentiment
    
    # Influence Score
    influence_score: Mapped[float]  # 0-1, how much they drive sentiment
    # If influence_score = 0.8, means 80% of sentiment changes correlate with this exec
    
    # Keywords
    associated_keywords: Mapped[str | None]  # JSON: ["innovation", "growth", "scandal"]
    
    executive: Mapped[Executive] = relationship(back_populates="sentiment_impact")
```

### 4. Consumer Sentiment (Separate from News)
```python
class ConsumerSentiment(Base):
    """Track consumer/customer perception separately from news sentiment."""
    __tablename__ = "consumer_sentiment"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))
    
    # Time Period
    date: Mapped[date]
    
    # Data Collection
    source: Mapped[str]  # "reddit", "twitter", "trustpilot", "glassdoor", "appstore"
    
    # Sentiment
    sentiment_score: Mapped[float]  # -1.0 to +1.0
    sentiment_label: Mapped[str]  # "positive", "neutral", "negative"
    
    # Volume & Engagement
    mentions_count: Mapped[int]
    engagement_rate: Mapped[float | None]  # likes, retweets, upvotes normalized
    
    # Category
    category: Mapped[str]  # "product_quality", "customer_service", "price", "brand", "leadership"
    
    # Raw Data
    sample_texts: Mapped[str | None]  # JSON: ["Great product", "Overpriced", ...]
    
    # Metadata
    collected_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    ticker: Mapped[TickerInfo] = relationship()
```

### 5. Executive-Consumer Relationship (Influence on Consumer Sentiment)
```python
class ExecutiveConsumerInfluence(Base):
    """How leadership changes affect consumer sentiment."""
    __tablename__ = "executive_consumer_influence"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    executive_id: Mapped[int] = mapped_column(ForeignKey("executives.id"))
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))
    
    # Timeline
    period_start: Mapped[date]  # Before executive change
    period_end: Mapped[date]    # After executive change
    
    # Consumer Sentiment Shift
    consumer_sentiment_before: Mapped[float]
    consumer_sentiment_after: Mapped[float]
    sentiment_change_pct: Mapped[float]  # % shift
    
    # Stock Price Correlation
    price_change_pct: Mapped[float]
    correlation_to_consumer_sentiment: Mapped[float]  # Does price follow consumer sentiment?
    
    # Insights
    key_changes: Mapped[str | None]  # JSON: ["product launches improved", "customer service declined"]
    causality_confidence: Mapped[float]  # 0-1, how confident is the relationship?
```

### 6. Influence Network (Who influences whom)
```python
class InfluenceNetwork(Base):
    """Map relationships between executives, consumer sentiment, and market metrics."""
    __tablename__ = "influence_network"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    source_type: Mapped[str]  # "executive", "event", "market_condition"
    source_id: Mapped[int]  # ID of the source entity
    
    target_type: Mapped[str]  # "consumer_sentiment", "news_sentiment", "stock_price"
    target_id: Mapped[int]  # ID of the target
    
    # Relationship Strength
    influence_strength: Mapped[float]  # 0-1, how strong the relationship
    direction: Mapped[str]  # "positive", "negative", "neutral"
    time_lag_days: Mapped[int | None]  # Does X affect Y after N days?
    
    # Evidence
    sample_size: Mapped[int]  # How many data points support this?
    confidence: Mapped[float]  # 0-1, statistical confidence
    
    # Timeline
    observed_start: Mapped[date]
    observed_end: Mapped[date]
    
    # Notes
    notes: Mapped[str | None]
```

---

## API Endpoints (Phase 1C Extended)

### Executive Management
```
GET  /api/v1/{symbol}/executives
     → List all current executives

GET  /api/v1/{symbol}/executives/{exec_id}
     → Get executive profile + timeline

GET  /api/v1/{symbol}/executives/{exec_id}/timeline
     → Career events (joins, promotions, exits)

GET  /api/v1/{symbol}/executives/{exec_id}/impact
     → How this executive affects sentiment & stock price
```

### Consumer Sentiment
```
GET  /api/v1/{symbol}/consumer-sentiment
     → Consumer sentiment trend over time
     Params: days=30, source=reddit/twitter/all

GET  /api/v1/{symbol}/consumer-sentiment/by-category
     → Breakdown: product_quality vs price vs brand
```

### Influence Analysis
```
GET  /api/v1/analysis/{symbol}/influence-network
     → How executives → consumer sentiment → stock price

GET  /api/v1/analysis/{symbol}/executive/{exec_id}/influence
     → Specific executive's impact on market

POST /api/v1/analysis/{symbol}/detect-relationships
     → Compute correlations between all entities
```

---

## Data Collection Strategy

### Leadership Data (Sources)
1. **SEC Filings (Free)**
   - Form 8-K (executive changes)
   - Proxy Statements (compensation, bio)
   - Annual Reports (management discussion)

2. **Company Websites**
   - Executive bio pages
   - Press releases (appointments/departures)

3. **APIs**
   - **Finnhub** (executive changes, insider trading)
   - **Intrinio** (executive data)
   - **Crunchbase** (company leadership history)

### Consumer Sentiment (Sources)
1. **Social Media (Free)**
   - Twitter/X API (brand mentions, sentiment)
   - Reddit API (subreddit discussions)
   - Discord/Telegram communities

2. **Review Platforms (Free/API)**
   - Google Reviews
   - Trustpilot
   - App Store reviews
   - Glassdoor reviews (employee satisfaction proxy)

3. **Commercial APIs**
   - Brandwatch (paid, monitors 100M+ conversations)
   - Sprout Social (paid, social listening)
   - Talkwalker (paid, sentiment analysis at scale)

---

## Implementation Timeline

### Phase 1C.1 — Executive Data Model (2-3 hours)
- [ ] Create `Executive`, `ExecutiveEvent` tables
- [ ] Backfill leadership data from SEC filings for 20 tickers (manual + automated)
- [ ] Endpoint: `GET /api/v1/{symbol}/executives` + timeline

### Phase 1C.2 — Consumer Sentiment Collection (3-4 hours)
- [ ] Create `ConsumerSentiment` table
- [ ] Collect Reddit/Twitter mentions (free APIs)
- [ ] Parse Glassdoor reviews (web scraping)
- [ ] Endpoint: `GET /api/v1/{symbol}/consumer-sentiment`

### Phase 1C.3 — Relationship Detection (4-5 hours)
- [ ] Create `InfluenceNetwork` table
- [ ] Compute correlations: executive changes → consumer sentiment → stock price
- [ ] Calculate time lags (does sentiment change X days after exec departure?)
- [ ] Endpoint: `GET /api/v1/analysis/{symbol}/influence-network`

### Phase 2A — Integrated Dashboard (6-8 hours)
- [ ] Combine: Executives + Consumer + News Sentiment + OHLCV
- [ ] Composite influence scoring
- [ ] Predictive signals (when exec change coming, what will happen to sentiment?)

---

## Example: Apple Inc. Intelligence Model

```json
{
  "symbol": "AAPL",
  "executives": [
    {
      "id": 1,
      "name": "Tim Cook",
      "role": "CEO",
      "start_date": "2011-08-24",
      "is_current": true,
      "sentiment_influence": 0.76,
      "impact": "High — mentioned in 65% of positive articles about strategic vision"
    },
    {
      "id": 2,
      "name": "Luca Maestri",
      "role": "CFO",
      "start_date": "2014-05-26",
      "is_current": true,
      "sentiment_influence": 0.42,
      "impact": "Moderate — mentioned when discussing financial performance"
    }
  ],
  "recent_events": [
    {
      "date": "2026-03-15",
      "type": "APPOINTED",
      "executive": "New VP of AI Strategy",
      "market_reaction": +2.1,
      "sentiment_shift": +0.18,
      "insight": "Market positive on AI focus, consumer sentiment on tech innovation improved"
    }
  ],
  "consumer_sentiment": {
    "overall": 0.68,  // Positive
    "by_source": {
      "twitter": 0.72,
      "reddit": 0.65,
      "glassdoor": 0.71,
      "appstore": 0.64
    },
    "by_category": {
      "product_quality": 0.82,
      "price": 0.52,  // Negative (complaints about pricing)
      "customer_service": 0.69,
      "brand": 0.85,  // Highly positive
      "leadership": 0.71   // Positive (Tim Cook approval)
    }
  },
  "influence_network": {
    "tim_cook_mentions": {
      "affects": "news_sentiment",
      "strength": 0.76,
      "direction": "positive",
      "lag_days": 0
    },
    "product_quality_sentiment": {
      "affects": "stock_price",
      "strength": 0.63,
      "direction": "positive",
      "lag_days": 3  // Product sentiment predicts price 3 days later
    }
  },
  "predictive_signals": {
    "warning": "Glassdoor employee satisfaction down 12% this quarter",
    "opportunity": "Consumer brand sentiment at 2-year high — buying opportunity?",
    "risk": "CFO nearing retirement age — successor clarity needed"
  }
}
```

---

## Why This Matters

**Traditional Model:**
- Price moves because of earnings & macro factors

**Your Intelligence Model:**
- Price moves because of *people* (leadership changes) + *perception* (consumer sentiment) + market factors
- When Tim Cook's retirement rumors surface → consumer confidence drops → stock falls
- New AI-focused VP hired → tech enthusiasts positive → product demand increases
- Glassdoor reviews show talent exodus → future productivity concern → long-term risk

You can predict these shifts *before* they show up in earnings reports.

---

## Next Steps

**Want to start building this?**

1. **Phase 1C.1** — Executive data model + SEC filing integration (2-3h)
2. **Phase 1C.2** — Consumer sentiment collection (3-4h)
3. **Phase 1C.3** — Relationship detection engine (4-5h)

Or would you prefer to:
- Focus on a specific company first (e.g., AAPL)
- Target a specific data source (e.g., Reddit + Glassdoor)
- Build the full model end-to-end?

