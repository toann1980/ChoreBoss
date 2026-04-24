# Market Data Inventory for Multi-Factor Analysis

## Goal
Build a comprehensive data model to extrapolate market factors that move tickers positively, negatively, or neutrally.

---

## Current State ✅

### In Database Now
1. **OHLCV Daily Bars** (4,769 rows)
   - Open, High, Low, Close, Volume
   - 1-year history × 20 tickers
   
2. **News Sentiment** (50-100 articles/ticker)
   - LLM-scored sentiment (-1.0 to +1.0)
   - Published date, source, URL

---

## Data Categories to Collect

### Category 1: Valuation (POSITIVE/NEGATIVE drivers)
- **P/E Ratio** — High = overvalued (negative signal), Low = undervalued (positive signal)
- **P/B Ratio** — Book value comparison
- **P/S Ratio** — Sales multiple
- **PEG Ratio** — Growth-adjusted P/E
- **Market Cap** — Size factor

### Category 2: Profitability (POSITIVE drivers)
- **ROE (Return on Equity)** — Higher = better management (positive)
- **ROA (Return on Assets)** — Asset efficiency
- **Net Margin** — Profitability per revenue
- **EPS (Earnings Per Share)** — Bottom line
- **Free Cash Flow** — Real cash generation

### Category 3: Growth (POSITIVE drivers)
- **Revenue Growth (YoY)** — Year-over-year sales increase
- **EPS Growth** — Earnings expansion
- **Free Cash Flow Growth** — Sustainable growth
- **5-10 Year CAGR** — Long-term trajectory

### Category 4: Debt & Liquidity (NEGATIVE if high)
- **Debt-to-Equity Ratio** — Leverage level
- **Current Ratio** — Short-term liquidity
- **Debt-to-EBITDA** — Debt burden relative to earnings
- **Interest Coverage** — Can they pay debt?

### Category 5: Dividends (POSITIVE for income)
- **Dividend Yield** — Annual payout %
- **Payout Ratio** — % of earnings paid out
- **5-Year Dividend Growth** — Increasing payouts

### Category 6: Technical Indicators (Computed, POSITIVE/NEGATIVE)
- **RSI (Relative Strength Index)** — Overbought (>70) = negative signal, Oversold (<30) = positive signal
- **MACD** — Momentum crossovers
- **Moving Averages (SMA 20/50/200)** — Trend direction
- **Bollinger Bands** — Volatility and extremes
- **ATR (Average True Range)** — Volatility level

### Category 7: Candlestick Patterns (Already coded)
- Bullish patterns (Hammer, Engulfing, Morning Star) = POSITIVE
- Bearish patterns (Hanging Man, Dark Cloud, Evening Star) = NEGATIVE
- Pattern confidence/strength score

### Category 8: Macro Factors (POSITIVE/NEGATIVE context)
- **Sector Performance** — Relative strength vs market
- **VIX (Volatility Index)** — Market fear level
- **Interest Rates** — Cost of capital
- **Earnings Surprises** — Beat/miss vs expectations

---

## Data Sources by Category

| Category | Best Source | API | Rate Limit | Cost |
|----------|-------------|-----|-----------|------|
| OHLCV | yfinance | Yes | ~2000 req/hr | Free |
| Sentiment | Already collected | - | - | - |
| Fundamentals | yfinance | Yes | ~2000 req/hr | Free |
| Technicals | Computed from OHLCV | - | - | Free |
| Patterns | Computed from OHLCV | - | - | Free |
| Earnings | yfinance + SEC Edgar | Yes | Limited | Free |
| Macro | Fred API (Fed data) | Yes | Unlimited | Free |

---

## Implementation Roadmap

### Phase 1C (Immediate - Skip 5m bars, do this instead)
**Goal:** Create correlation analysis endpoint

1. **Add new API endpoint:** `GET /api/v1/analysis/{symbol}/factors`
   - Returns: sentiment, price movement, volatility for time window
   - No new data collection needed (use existing DB)

2. **Create correlation endpoint:** `GET /api/v1/analysis/{symbol}/correlation`
   - Input: symbol, days (e.g., AAPL, 30)
   - Output: JSON showing how sentiment changed vs price movement
   ```json
   {
     "symbol": "AAPL",
     "period_days": 30,
     "price_change": +5.2,
     "sentiment_trend": +0.15,
     "correlation": 0.72,
     "insights": [
       "Positive sentiment correlated with +5.2% price move",
       "Peak sentiment on 2026-04-15, price peaked 2 days later",
       "Negative sentiment spikes preceded -2.1% drawdown"
     ]
   }
   ```

### Phase 2A (Add Fundamentals)
1. Create `FundamentalMetric` table
2. Backfill yfinance fundamentals for 20 tickers
3. Endpoint: `GET /api/v1/{symbol}/fundamentals` (snapshot)

### Phase 2B (Add Technical Indicators)
1. Create `TechnicalIndicator` table
2. Compute RSI, MACD, Bollinger Bands from OHLCV
3. Store daily; endpoint: `GET /api/v1/{symbol}/technicals`

### Phase 3 (Composite Scoring)
1. Combine: Sentiment + Fundamentals + Technicals + Candlesticks
2. Weight each factor (configurable)
3. Output: Buy/Sell/Hold score per ticker
4. Endpoint: `GET /api/v1/analysis/{symbol}/composite-score`

### Phase 4 (Paper Trading Engine)
Use composite scores as entry/exit signals. Backtest + live trade.

---

## Database Schema Extensions

```python
# envestero/db/models.py

class FundamentalMetric(Base):
    """Quarterly/annual fundamental ratios from yfinance."""
    __tablename__ = "fundamental_metrics"
    __table_args__ = (
        UniqueConstraint("ticker_id", "period_end", name="uq_fundamental_ticker_period"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))
    period_end: Mapped[date]  # Quarterly or annual
    
    # Valuation
    pe_ratio: Mapped[float | None]
    pb_ratio: Mapped[float | None]
    ps_ratio: Mapped[float | None]
    peg_ratio: Mapped[float | None]
    
    # Profitability
    roe: Mapped[float | None]
    roa: Mapped[float | None]
    net_margin: Mapped[float | None]
    eps: Mapped[float | None]
    fcf: Mapped[int | None]  # Free Cash Flow
    
    # Growth
    revenue_growth: Mapped[float | None]
    eps_growth: Mapped[float | None]
    fcf_growth: Mapped[float | None]
    
    # Debt
    debt_to_equity: Mapped[float | None]
    current_ratio: Mapped[float | None]
    
    # Dividend
    dividend_yield: Mapped[float | None]
    
    # Meta
    market_cap: Mapped[int | None]
    collected_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    ticker: Mapped[TickerInfo] = relationship(back_populates="fundamentals")


class TechnicalIndicator(Base):
    """Daily technical indicators computed from OHLCV."""
    __tablename__ = "technical_indicators"
    __table_args__ = (
        UniqueConstraint("ticker_id", "time", "interval", name="uq_tech_ticker_time"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))
    time: Mapped[datetime]
    interval: Mapped[str]  # "1d", "1h", etc.
    
    # Momentum
    rsi_14: Mapped[float | None]
    
    # Trend
    macd: Mapped[float | None]
    macd_signal: Mapped[float | None]
    sma_20: Mapped[float | None]
    sma_50: Mapped[float | None]
    sma_200: Mapped[float | None]
    
    # Volatility
    bb_upper: Mapped[float | None]
    bb_lower: Mapped[float | None]
    atr: Mapped[float | None]
    
    # Volume
    obv: Mapped[int | None]
    
    ticker: Mapped[TickerInfo] = relationship(back_populates="technicals")


class CorrelationAnalysis(Base):
    """Cached correlation analysis results."""
    __tablename__ = "correlation_analysis"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))
    period_days: Mapped[int]
    
    price_change: Mapped[float]  # %
    sentiment_trend: Mapped[float]  # -1.0 to +1.0
    correlation_coeff: Mapped[float]  # Pearson correlation
    
    computed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    ticker: Mapped[TickerInfo] = relationship()
```

---

## Next Question for You

**Which of these would you like to tackle first?**

1. **Phase 1C (Quick win):** Build sentiment ↔ price correlation endpoint using existing data
2. **Phase 2A (Fundamentals):** Integrate yfinance fundamentals (P/E, ROE, dividend, etc.)
3. **Phase 2B (Technicals):** Compute RSI, MACD, Bollinger Bands from daily OHLCV

My recommendation: **Start with Phase 1C** — it requires zero new data collection, shows how sentiment relates to price movement, and gives you a working correlation analysis in <2 hours.
