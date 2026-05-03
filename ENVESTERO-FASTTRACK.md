# Envestero Fast-Track Plan — Mon 2026-04-20 21:14 UTC

**Goal:** Get three systems running concurrently: stock data, news ingestion, paper trading.  
**Baseline:** Modern modernized architecture is _already in place_ — we're extending it.  
**Timeline:** Sprint delivery in phases.

---

## Current State Summary

**Good news:** The hard architecture work is already done.

### What Exists (envestero/ package)
- ✅ **FastAPI server** (`envestero/api/`)
- ✅ **SQLAlchemy 2.x async** (TimescaleDB + asyncpg ready)
- ✅ **Config system** (Pydantic Settings, .env-based)
- ✅ **Stock collector** (`envestero/services/collector.py`) — yfinance + proxy rotation
- ✅ **News ingestion** (`envestero/services/newser.py`)
- ✅ **Sentiment analysis** (`envestero/services/sentiment.py`)
- ✅ **Paper trading engine** (`envestero/services/paper_trading.py`) — with $$ arithmetic (Decimal)
- ✅ **Database models** (OHLCV, TickerInfo, NewsArticle, Portfolio, etc.)
- ✅ **Scheduler** (`envestero/tasks/scheduler.py`) — APScheduler for periodic jobs
- ✅ **Alembic migrations** — reversible DB schema evolution

### What Needs Work
- ⚠️ No unified entry point for "fast-track three systems" flow
- ⚠️ Paper trading not wired to live signals yet
- ⚠️ Day trader protection / backtest constraints not implemented
- ⚠️ Stock data batch fetch optimized but untested at scale
- ⚠️ Python 3.13 migration incomplete (path shebangs, string formatting, SQLAlchemy edge cases)

---

## Phase 1: Stock Data Batch Acquisition (2–3 hours)

**Goal:** Get all active NASDAQ stocks' latest info + OHLCV in one fell swoop, respecting rate limits.

### 1a. Nasdaq Screener Refresh
Current code has `get_nasdaq_screener_tickers()` in `Envestero/stocker.py` — pull all stocks with sector/industry.

**Action:**
```python
# envestero/services/collector.py — add function:

async def refresh_nasdaq_screener(
    session: AsyncSession,
    force: bool = False,
) -> int:
    """
    Fetch all Nasdaq-listed tickers from screener CSV.
    Returns count of tickers upserted to DB.
    
    Rate limit: Call once per 24h (cached locally).
    Uses existing get_nasdaq_screener_tickers() or yfinance's Ticker("^GSPC").info.
    """
    # Fetch latest tickers + metadata
    # Upsert into TickerInfo table
    # Cache CSV locally (avoid repeated fetches)
    # Return count
```

**Deliverable:** 
- 3000–4000 tickers in `TickerInfo` table
- Each with: symbol, name, sector, industry, market_cap, country

### 1b. Batch OHLCV Fetch (Lean Data)
For fast trading research, don't grab 20 years. Grab smart:
- **Daily bars:** Last 252 days (1 year trading days)
- **5-min bars:** Last 60 days (recent action)
- **Skip:** Dividends, stock splits (not needed for price action)

**Action:**
```python
# envestero/services/collector.py — add function:

async def backfill_ohlcv_batch(
    session: AsyncSession,
    symbols: list[str],
    interval: str = "1d",      # "1d" or "5m"
    period: str = "1y",        # "1y" or "60d"
    max_concurrent: int = 5,   # Throttle concurrent fetches
) -> dict[str, int]:
    """
    Fetch OHLCV for multiple tickers concurrently, respecting rate limits.
    
    Rate strategy:
    - yfinance: 2000 req/hour = ~1 req/1.8 sec max
    - Proxy rotation: avoid IP blocks
    - Batch upsert: 1000 rows/batch to asyncpg
    
    Returns: {symbol: rows_upserted}
    """
    # Parallel fetches (5 at a time) via asyncio.gather()
    # Proxy from ProxyAgent.next()
    # Retry on 429 (exponential backoff)
    # Batch upsert to OHLCV table
```

**Rate-limit strategy:**
- **Sequential ticker loop** with 2-second pause between each
- **Proxy rotation** every 5 tickers (avoid 429s)
- **Batch upsert** to reduce transaction overhead
- **Parallel intervals** (1d and 5m can fetch separately, no overlap)

**Deliverable:**
- 1yr daily bars for 3000+ tickers (~750K rows)
- 60-day 5-min bars for ~500 active tickers (~144K rows)
- Compression: ~900K total OHLCV rows in DB

### 1c. Scheduler Job + CLI Backfill Command
Wire into existing scheduler:

```python
# envestero/tasks/scheduler.py — add job:

async def job_backfill_nasdaq():
    """Run once per 24h: refresh screener + daily bars for all."""
    async with get_session() as session:
        await refresh_nasdaq_screener(session)
        symbols = await get_active_symbols(session)  # top 3000 by market cap
        await backfill_ohlcv_batch(
            session, symbols, 
            interval="1d", period="1y"
        )

# envestero/cli/main.py — add command:
@click.command()
@click.option("--force", is_flag=True)
async def backfill_nasdaq(force):
    """Fetch all Nasdaq tickers + 1y daily bars."""
    async with get_session() as session:
        await refresh_nasdaq_screener(session, force=force)
        symbols = await get_active_symbols(session)
        count = await backfill_ohlcv_batch(session, symbols)
        click.echo(f"Backfilled {count} symbols")
```

**Command:**
```bash
python -m envestero backfill-nasdaq --force
# Output: "Backfilled 3042 symbols in 2h 14m (rate: 1.5 req/sec avg)"
```

---

## Phase 2: News Ingestion + Sentiment (2 hours)

**Status:** Newser service exists. Wire it into scheduled refresh.

### 2a. Scheduled News Refresh
Already have:
- `newser.py` — fetches news from GNews
- `sentiment.py` — scores via OpenAI / Ollama (or heuristic fallback)

**Action:**
```python
# envestero/tasks/scheduler.py — add job:

async def job_refresh_news():
    """Every 4h: fetch news for top 100 tickers, score sentiment."""
    async with get_session() as session:
        # Get top 100 by recent volume/market cap
        symbols = await get_top_symbols(session, limit=100)
        
        # Fetch news (GNews API)
        for symbol in symbols:
            articles = await newser.fetch_articles(symbol, limit=10)
            session.add_all([
                NewsArticle(
                    ticker_symbol=symbol,
                    title=a['title'],
                    source=a['source'],
                    published_at=a['published_at'],
                    url=a['url'],
                    sentiment_score=None,  # Will score async
                )
                for a in articles
            ])
        await session.commit()
        
        # Score all unscored articles (batch sentiment)
        await sentiment.score_batch(session, batch_size=20)
```

**Config:**
```env
# .env
NEWS_COLLECTION_LIMIT=100          # Refresh top N tickers per run
NEWS_REFRESH_HOURS=4               # Run every 4 hours
NEWS_REQUEST_PAUSE_SECONDS=0.5     # Pause between ticker news fetches
SENTIMENT_BATCH_SIZE=20            # Articles per sentiment batch
SENTIMENT_CONCURRENCY=5            # Parallel sentiment workers
```

**Deliverable:**
- Fresh news (4h cycle) for top 100 tickers
- Sentiment scores (positive/negative/neutral) on all articles

### 2b. News Dashboard Endpoint
Add REST endpoint to see recent news + sentiment by ticker:

```python
# envestero/api/routers/news.py — add:

@router.get("/news/{symbol}")
async def get_ticker_news(
    symbol: str,
    days: int = 7,
    db: AsyncSession = Depends(get_db_session),
):
    """Get last 7 days of news + sentiment for a ticker."""
    articles = await db.execute(
        select(NewsArticle)
        .where(NewsArticle.ticker_symbol == symbol.upper())
        .where(NewsArticle.published_at >= datetime.now() - timedelta(days=days))
        .order_by(NewsArticle.published_at.desc())
    )
    return articles.scalars().all()

@router.get("/sentiment/{symbol}")
async def get_ticker_sentiment_summary(symbol: str, db):
    """Get aggregate sentiment (positive/negative count) for last 7d."""
    # Count articles by sentiment_score > 0.5 (positive), < -0.5 (negative)
```

---

## Phase 3: Paper Trading Setup (3–4 hours)

**Goal:** Run $500 sim account, auto-execute signals, backtest without PDT.

### 3a. Paper Portfolio Creation + State Machine
Already have `PaperTradingEngine` in `paper_trading.py`. Wire it:

```python
# envestero/api/routers/portfolio.py — add:

@router.post("/portfolio")
async def create_portfolio(
    name: str,
    starting_cash: float,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a $500 paper portfolio."""
    engine = PaperTradingEngine()
    portfolio = await engine.create_portfolio(
        db, name=name, starting_cash=starting_cash
    )
    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "cash": float(portfolio.cash_balance),
        "status": "active"
    }

@router.get("/portfolio/{portfolio_id}")
async def get_portfolio_state(portfolio_id: int, db):
    """Get current cash, holdings, NAV."""
    engine = PaperTradingEngine()
    portfolio = await engine._get_portfolio(db, portfolio_id)
    holdings = await engine.get_holdings(db, portfolio_id)
    
    # Fetch current prices for holdings
    prices = await get_current_prices(db, list(holdings.keys()))
    
    return {
        "id": portfolio.id,
        "cash": float(portfolio.cash_balance),
        "holdings": {k: {"qty": str(v), "current_price": ...} for k, v in holdings.items()},
        "nav": float(portfolio.cash_balance + sum(...)),
    }

@router.post("/portfolio/{portfolio_id}/buy")
async def buy_signal(
    portfolio_id: int,
    symbol: str,
    quantity: float,
    price: float | None = None,  # If None, use current price
    db: AsyncSession = Depends(get_db_session),
):
    """Execute a paper buy order."""
    if price is None:
        price = await get_current_price(db, symbol)
    
    engine = PaperTradingEngine()
    trade = await engine.buy(db, portfolio_id, symbol, quantity, price)
    return {"trade_id": trade.id, "side": "buy", "symbol": symbol, "qty": quantity}
```

### 3b. Signal → Paper Trade Executor
Create a service that:
1. Listens to `TradeSignal` table (new signals)
2. For each signal, execute buy/sell on paper portfolio
3. Log trade → PortfolioTrade table
4. Avoid PDT rule violations (max 3 day trades / 5 business days)

```python
# envestero/services/signal_executor.py — new file:

class SignalExecutor:
    """Convert signals → paper trades, respecting PDT constraints."""
    
    async def execute_signal(
        self,
        session: AsyncSession,
        signal: TradeSignal,
        portfolio_id: int,
    ) -> PortfolioTrade:
        """
        Execute a trade signal on a paper portfolio.
        
        Checks:
        - PDT rule: max 3 day trades / 5 business days (for $500 account)
        - Sufficient funds/holdings
        - Risk limits (optional: max % of portfolio per trade)
        """
        # Get current price for signal.symbol
        price = await get_current_price(session, signal.symbol)
        
        # Check PDT rule
        day_trades_last_5d = await self.count_day_trades(session, portfolio_id, days=5)
        if day_trades_last_5d >= 3:
            logger.warn(f"PDT limit hit ({day_trades_last_5d} trades). Skipping signal.")
            return None
        
        # Execute trade
        engine = PaperTradingEngine()
        if signal.side == "buy":
            qty = await self._calc_position_size(session, portfolio_id, price)
            trade = await engine.buy(session, portfolio_id, signal.symbol, qty, price)
        else:
            # Sell all or % of position
            holdings = await engine.get_holdings(session, portfolio_id)
            qty = holdings.get(signal.symbol.upper(), 0)
            if qty > 0:
                trade = await engine.sell(session, portfolio_id, signal.symbol, qty, price)
        
        return trade
```

### 3c. Daily Snapshot + Backtest Reports
Capture NAV each day, compute returns:

```python
# envestero/services/portfolio_reporter.py — new file:

async def snapshot_daily(session: AsyncSession, portfolio_id: int):
    """Record daily NAV snapshot."""
    engine = PaperTradingEngine()
    holdings = await engine.get_holdings(session, portfolio_id)
    prices = await get_current_prices(session, list(holdings.keys()))
    snap = await engine.snapshot(session, portfolio_id, prices)
    return snap

async def backtest_report(
    session: AsyncSession,
    portfolio_id: int,
    start_date: datetime,
    end_date: datetime,
) -> dict:
    """
    Generate backtest stats: returns, Sharpe, max drawdown, trade count, win%.
    """
    snapshots = await session.execute(
        select(PortfolioSnapshot)
        .where(PortfolioSnapshot.portfolio_id == portfolio_id)
        .where(PortfolioSnapshot.date >= start_date)
        .where(PortfolioSnapshot.date <= end_date)
        .order_by(PortfolioSnapshot.date)
    )
    snapshots = snapshots.scalars().all()
    
    if not snapshots:
        return {"error": "No snapshots"}
    
    # Compute returns, Sharpe, max drawdown
    nav_values = [float(s.total_value) for s in snapshots]
    
    return {
        "start_value": nav_values[0],
        "end_value": nav_values[-1],
        "return_pct": ((nav_values[-1] - nav_values[0]) / nav_values[0]) * 100,
        "max_drawdown_pct": max_dd(nav_values),
        "sharpe": compute_sharpe(nav_values),
        "trade_count": await count_trades(session, portfolio_id, start_date, end_date),
        "win_pct": await win_percentage(session, portfolio_id, start_date, end_date),
    }
```

### 3d. Config for $500 Account
```env
# .env
PAPER_TRADING_ENABLED=true
PAPER_STARTING_CASH=500
PAPER_RISK_PER_TRADE=0.1        # Max 10% of account per trade
PAPER_MAX_POSITION=0.3          # Max 30% in single stock
BACKTEST_PDT_PROTECT=true       # Enforce PDT rules in backtest
```

---

## Phase 4: Integration + Testing (2 hours)

### 4a. Unified CLI
```bash
# Start everything at once
python -m envestero run-all

# Individual commands
python -m envestero backfill-nasdaq --force
python -m envestero refresh-news --top-100
python -m envestero create-portfolio --name "Test-1" --cash 500
python -m envestero backtest --portfolio 1 --days 30

# API server
uvicorn envestero.api.main:app --host 0.0.0.0 --port 8000
```

### 4b. Smoke Tests
```python
# tests/integration/test_fasttrack.py — new:

@pytest.mark.asyncio
async def test_nasdaq_screener_fetch():
    """Verify we can fetch 3000+ tickers."""
    async with get_session() as session:
        count = await refresh_nasdaq_screener(session, force=True)
        assert count >= 3000

@pytest.mark.asyncio
async def test_ohlcv_backfill():
    """Verify 1y daily bars for 100 test tickers."""
    async with get_session() as session:
        symbols = ["AAPL", "MSFT", "TSLA", ...]  # top 100
        result = await backfill_ohlcv_batch(session, symbols)
        assert all(count > 200 for count in result.values())  # 1y = ~252 days

@pytest.mark.asyncio
async def test_paper_trading_pdt_protect():
    """Verify PDT rule prevents >3 day trades / 5d."""
    async with get_session() as session:
        engine = PaperTradingEngine()
        portfolio = await engine.create_portfolio(session, "test", 500)
        
        executor = SignalExecutor()
        
        # Execute 3 trades (OK)
        for i in range(3):
            signal = TradeSignal(side="buy", symbol="AAPL", ...)
            trade = await executor.execute_signal(session, signal, portfolio.id)
            assert trade is not None
        
        # 4th trade should be blocked
        signal = TradeSignal(side="buy", symbol="MSFT", ...)
        trade = await executor.execute_signal(session, signal, portfolio.id)
        assert trade is None  # PDT blocked
```

---

## Implementation Order (Fast-Track)

1. **Phase 1a (30m):** Pull nasdaq screener, upsert tickers
2. **Phase 1b (90m):** Build batch OHLCV fetch, test on 100 tickers, then scale to 3000
3. **Phase 1c (30m):** Wire scheduler + CLI command
4. **Phase 2a (60m):** Schedule news refresh, batch sentiment scoring
5. **Phase 2b (30m):** REST endpoints for news/sentiment
6. **Phase 3a (90m):** Wire PaperTradingEngine to REST API
7. **Phase 3b (60m):** SignalExecutor + PDT protection
8. **Phase 3c (30m):** Daily snapshots + backtest reporter
9. **Phase 3d (15m):** .env config
10. **Phase 4 (120m):** CLI, smoke tests, integration checks

**Total:** 8–9 hours. Can parallelize phases 1b + 1c + 2a.

---

## Key Design Decisions

### Stock Data
- **Batch over individual:** Fetch all 3000+ once, then differential updates
- **Lean intervals:** 1d (1yr) + 5m (60d) — don't bulk 20-year history
- **Proxy rotation:** Avoid IP blocks on yfinance hammering
- **Upsert strategy:** Composite key (ticker, time, interval) prevents dupes

### News
- **4h refresh cycle:** Balance freshness vs. GNews rate limits
- **Top 100 tickers:** Most liquid/volatile; sentiment most relevant
- **Batch sentiment:** Score 20–50 articles at once (1 LLM call per batch)

### Paper Trading
- **$500 starting:** Tests money management, position sizing, PDT compliance
- **PDT protection:** Max 3 day trades / 5 business days (standard rule)
- **Decimal arithmetic:** No float rounding on money
- **Backtest-friendly:** Snapshots enable retrospective NAV / Sharpe / drawdown analysis

### Infrastructure
- **Database:** TimescaleDB (hypertables for OHLCV time series)
- **Async everywhere:** SQLAlchemy 2.x + asyncio concurrency
- **Config:** Pydantic Settings + .env (no hardcoded paths)
- **Scheduler:** APScheduler for periodic jobs

---

## Success Metrics

- ✅ 3000+ tickers in TickerInfo within 1h
- ✅ 1yr daily bars for all, 60d 5m bars for top 500, <2h fetch
- ✅ Fresh news (4h old max) for top 100 tickers
- ✅ Sentiment scores on 95%+ of articles (Ollama fallback if OpenAI down)
- ✅ Paper portfolio live, trades recorded, PDT rules enforced
- ✅ Backtest report: returns, Sharpe, max drawdown, win %
- ✅ Zero day-trader violations in test runs

---

## Blockers / Risks

| Risk | Mitigation |
|------|-----------|
| yfinance rate limits | Proxy rotation + 2sec pause + retry backoff |
| GNews API quota | Batch to top 100; fallback to heuristic sentiment |
| LLM sentiment (OpenAI down) | Ollama local fallback or simple keyword scoring |
| Database timeout (3000 tickers) | Batch upsert (1000 rows), connection pooling |
| PDT rule complexity | White-box test: verify 3 trades → 4th blocked |

---

## Next: Code Sprint

Ready to spin this up. Pick a starting point:

**Option A:** Start with Phase 1a (nasdaq screener) → validate DB layer → scale up  
**Option B:** Start with Phase 3a (paper trading API) → validate trade execution → wire signals  
**Option C:** Start with Phase 2a (news refresh) → validate sentiment pipeline → integrate  

**My rec:** A → B → C (data → trading → research). But B is a good independence check.

What's your preference?
