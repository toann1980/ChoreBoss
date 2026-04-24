# 5-Minute Bars Diagnostic (2026-04-21 05:32 UTC)

## Problem Statement
Phase 1 backfill returned 0 rows for 5-minute OHLCV data, while daily data loaded successfully (4,769 rows for 20 tickers).

## Root Cause Analysis

### What Works ✓
- **yfinance fetch:** Direct test with `period="60d"` returns 4,680 rows/ticker
- **Code logic:** `backfill_ohlcv_batch()` calls yfinance with correct parameters
- **SQL generation:** Massive INSERT statements logged correctly (9,360 rows for AAPL+MSFT)

### What Fails ✗
- **Database commit:** INSERT logs show success, but data never appears in DB
- **Error handling:** No exception raised; function returns results dict but data absent
- **Transaction isolation:** Likely silent rollback during batch upsert of 1000-row chunks

## Evidence

**Direct yfinance test (successful):**
```python
ticker = yf.Ticker("AAPL")
df = ticker.history(interval="5m", period="60d")
# Result: 4,680 rows ✓
```

**Backfill function test (failed):**
```python
await backfill_ohlcv_batch(
    session, ['AAPL', 'MSFT'],
    interval='5m', period='60d'
)
# Logs: INSERT statements with ~9,360 rows
# DB check: 0 rows saved ✗
```

## Hypothesis
1. **Batch size issue:** 1000-row batches may exceed PostgreSQL statement complexity limits
2. **Constraint violation:** Silent conflict resolution (UPSERT) failing
3. **Session isolation:** AsyncSession transaction not committing in `backfill_ohlcv_batch()`

## Recommended Fixes (Priority Order)

### Quick Fix (5 min)
Add explicit session commit after each batch:
```python
# In backfill_ohlcv_batch(), after each upsert:
await session.commit()
```

### Thorough Fix (30-45 min)
1. Reduce batch size 1000 → 100
2. Add try/except around each batch with logging
3. Enable detailed SQL logging for one retry
4. Check for constraint violations

### Pragmatic Fix (Option A - Recommended)
Skip 5m bars for MVP Phase 1:
- Daily data is sufficient for news sentiment + signals
- 5m bars are intraday-only feature
- Save 5m for Phase 1.5 after Phase 2/3 validation
- Invest time in Phase 3 (paper trading) instead

---

**Recommendation:** Option A (pragmatic). Phase 1 daily data is complete. Proceed to Phase 2 test validation, then Phase 3 development. Return to 5m bars later if needed for detailed backtest analysis.
