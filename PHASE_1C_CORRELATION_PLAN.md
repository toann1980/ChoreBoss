# Market Data Analysis Plan — Summary

**Session:** 2026-04-21 05:50 UTC  
**Status:** Pivot from 5m-bars debugging → multi-factor market analysis  
**Toan's Goal:** "Extrapolate the factors of the market that change tickers positively, negatively, and somewhere in between"

---

## The 8 Data Categories You Need

### 1. **Valuation** (Currently have: Stock price OHLC)
- **P/E Ratio** — High = overvalued, Low = undervalued
- **P/B Ratio, P/S Ratio, PEG Ratio** — Value metrics
- ✅ **Source:** yfinance (free, easy)

### 2. **Profitability** (Currently have: None)
- **ROE, ROA, Net Margin** — How efficient is the company?
- **EPS, Free Cash Flow** — Real earnings & cash
- ✅ **Source:** yfinance fundamentals

### 3. **Growth** (Currently have: None)
- **Revenue Growth (YoY), EPS Growth** — Is the company expanding?
- **5-10 Year CAGR** — Long-term trajectory
- ✅ **Source:** yfinance + SEC Edgar (free)

### 4. **Debt & Liquidity** (Currently have: None)
- **Debt-to-Equity, Current Ratio** — Can they pay their bills?
- **Interest Coverage** — Debt servicing ability
- ✅ **Source:** yfinance fundamentals

### 5. **Dividends** (Currently have: None)
- **Dividend Yield, Payout Ratio** — Income + sustainability
- **5-Year Dividend Growth** — Increasing payouts
- ✅ **Source:** yfinance

### 6. **Technical Indicators** (Currently have: OHLC data → can compute)
- **RSI (Relative Strength Index)** — Overbought/oversold
- **MACD** — Momentum & trend changes
- **Bollinger Bands** — Volatility extremes
- **Moving Averages (SMA 20/50/200)** — Trend direction
- ✅ **Source:** Computed from existing OHLCV data (free)

### 7. **Candlestick Patterns** (Currently have: Code exists, needs testing)
- **Bullish patterns:** Hammer, Engulfing, Morning Star
- **Bearish patterns:** Hanging Man, Dark Cloud, Evening Star
- ✅ **Source:** Already coded in `/services/signals.py`

### 8. **News Sentiment** (Currently have: ✓ 50-100 articles/ticker)
- **Sentiment score:** -1.0 to +1.0
- **Sentiment label:** positive/neutral/negative
- ✅ **Source:** Already collected & LLM-scored

---

## Your Immediate Advantage

You already have **#8 (sentiment) + #1 (OHLC)** in the database. That's enough to start building **correlation analysis** — showing how sentiment changes relate to price movement.

---

## Implementation Phases

### **Phase 1C — Correlation Analysis** (RECOMMENDED NEXT)
**Time:** <2 hours  
**Effort:** Low (uses existing data)  
**Output:** Endpoint showing sentiment ↔ price relationship

```python
# Example: GET /api/v1/analysis/AAPL/correlation?days=30
{
  "symbol": "AAPL",
  "period_days": 30,
  "price_change_pct": +5.2,
  "sentiment_trend": +0.15,  # Average sentiment moved positive
  "correlation_coeff": 0.72,  # Strong correlation
  "insights": [
    "Positive sentiment correlated with +5.2% price move",
    "Peak sentiment on 2026-04-15, price peaked 2 days later",
    "Negative sentiment spike on 2026-04-10 preceded -2.1% drawdown"
  ]
}
```

**What it does:**
- Compare sentiment trajectory vs price movement over time window
- Calculate correlation coefficient (Pearson)
- Identify lead/lag relationships (does sentiment predict price?)
- Show confidence levels

---

### **Phase 2A — Fundamental Data** (AFTER 1C)
**Time:** 3-4 hours  
**Effort:** Medium (new data collection + schema)  
**Output:** Complete financial snapshot per ticker

1. Create `FundamentalMetric` table
2. Backfill yfinance fundamentals for 20 tickers
3. Endpoint: `GET /api/v1/{symbol}/fundamentals`

**Data you'll get:**
- P/E, P/B, P/S, PEG
- ROE, ROA, Net Margin
- EPS, Free Cash Flow
- Debt-to-Equity, Current Ratio
- Dividend Yield, Payout Ratio

---

### **Phase 2B — Technical Indicators** (AFTER 2A)
**Time:** 2-3 hours  
**Effort:** Low (computed from existing OHLCV)  
**Output:** Technical analysis per day

1. Create `TechnicalIndicator` table
2. Compute RSI, MACD, Bollinger Bands for each OHLCV bar
3. Endpoint: `GET /api/v1/{symbol}/technicals?days=30`

**Indicators:**
- RSI-14, MACD, Bollinger Bands
- SMA 20/50/200
- ATR (volatility)
- Volume moving average

---

### **Phase 3 — Composite Scoring** (FINAL)
**Time:** 4-5 hours  
**Effort:** High (integration + weighting)  
**Output:** Buy/Sell/Hold signal

Combine:
- ✅ Sentiment (positive/negative trend)
- ✅ Candlestick patterns (bullish/bearish)
- ✅ Fundamentals (valuation, growth, profitability)
- ✅ Technicals (RSI, MACD, trend)

**Example output:**
```json
{
  "symbol": "AAPL",
  "composite_score": 7.2,  // 0-10 scale
  "signal": "BUY",
  "factors": {
    "sentiment": { "score": 8, "trend": "+0.25", "weight": 0.25 },
    "technicals": { "score": 6, "rsi": 45, "trend": "bullish", "weight": 0.25 },
    "fundamentals": { "score": 8, "pe": 22, "roe": 15, "weight": 0.30 },
    "candlesticks": { "score": 7, "pattern": "bullish_engulfing", "strength": 0.85, "weight": 0.20 }
  },
  "confidence": 0.78,
  "reasoning": "Strong sentiment + bullish technicals + solid fundamentals"
}
```

---

## Database Schema (What to add)

Already documented in `/home/leto/.openclaw/workspace/MARKET_DATA_INVENTORY.md`

Key additions:
- `FundamentalMetric` — P/E, ROE, dividend, growth rates
- `TechnicalIndicator` — RSI, MACD, Bollinger Bands
- `CorrelationAnalysis` — Cached sentiment ↔ price relationship

---

## Your Next Decision

**Which phase do you want to start with?**

1. **Phase 1C (Recommended)** — Correlation analysis (<2h, uses existing data, shows quick win)
2. **Phase 2A** — Jump straight to fundamentals (more data, more analysis power)
3. **Phase 2B** — Technical indicators (if you want trend-based analysis first)
4. **Phase 3** — Composite scoring (if you want the full integrated model)

---

## One More Thing

The 5-minute bars issue is **solved but deferred**:
- Root cause: Transaction rollback during batch inserts
- Not critical for MVP (daily data + sentiment is enough)
- Fix when you need intraday backtesting
- Estimated fix time: 30-45 min when needed

**My recommendation:** Skip 5m for now. Build the correlation engine first. It's more valuable for understanding market relationships than 5-minute price ticks.
