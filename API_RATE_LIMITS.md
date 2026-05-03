# API Rate Limits & Operational Hours Reference

**For all future projects and cron jobs.**

## Quick Limits Reference

| API | Free Tier | Limit | Buffer Applied | Implementation |
|-----|-----------|-------|-----------------|-----------------|
| **MarketAux** | Yes | Unlimited | N/A | No throttling needed |
| **Finnhub** | Yes | 60/min | 50/min (17% buffer) | 1 req/sec minimum |
| **yfinance** | Yes | ~2000/hr | 1900/hr (5% buffer) | 1.9s/req |
| **Alpha Vantage** | Yes | 5/min | 4/min (20% buffer) | 15s/req |
| **NewsAPI** | No | 500/day | 400/day (20% buffer) | ~1 per 3-4 min |
| **Alpaca** | Yes | 200/min | 160/min (20% buffer) | 375ms/req |

## Operational Hours (Envestero Standard)

**ALL TIMES ARE IN PST (Pacific Standard Time)**

### Heavy Data Window (Aggressive Mode)
**Use when:** Data pulls can be intensive  
**Weekdays:** 12:00am-7:00am PST (7 hours)  
**Weekends:** 2:00am-8:00am PST (6 hours)

**Settings:**
- Max concurrent requests: **10**
- Delay between requests: **50ms**
- Suitable for: Backfill, bulk sync, large dataset pulls

### Light Hours (Conservative Mode)
**Use when:** Normal daytime usage (internet in use)  
**All other times:** 7am-12am weekdays, 8am-2am weekends

**Settings:**
- Max concurrent requests: **2**
- Delay between requests: **500ms**
- Suitable for: Incremental updates, monitoring jobs

## New Project Checklist

When setting up a new cron job or periodic task:

- [ ] List all APIs it will call
- [ ] Verify rate limits from provider docs
- [ ] Apply 20% safety buffer
- [ ] Choose heavy or light window (or both with scaling)
- [ ] Set concurrency & delay appropriately
- [ ] Add rate limit comments to source code
- [ ] Log actual request counts (for monitoring)
- [ ] Document in config file with limits
- [ ] Test at peak load (heavy window)
- [ ] Verify no 429 errors in logs after 24 hours
- [ ] Add entry to this reference guide
- [ ] Update MEMORY.md if limits change

## Implementation Pattern

```python
# Example: Safe API caller with heavy/light window support

async def safe_api_call(url: str, is_heavy_window: bool) -> dict:
    """
    Rate limit: 60 calls/min (Finnhub)
    Heavy window: 10 concurrent, 50ms delay → 12 calls/sec max
    Light window: 2 concurrent, 500ms delay → 0.25 calls/sec
    """
    delay = 0.05 if is_heavy_window else 0.5  # seconds
    await asyncio.sleep(delay)
    response = await http_client.get(url)
    
    if response.status == 429:
        logger.error("RATE LIMIT HIT: Check delays vs API limits")
        # Alert ops team
    
    return response.json()
```

## Rate Limit Violation Recovery

If you hit 429 (Too Many Requests):

1. **Immediate:** Stop the job, wait 60 seconds
2. **Check:** Current window (heavy vs light)?
3. **Adjust:** Reduce concurrency by 50% OR increase delay by 2x
4. **Verify:** Run at reduced rate for 1 hour
5. **Monitor:** Check logs for additional 429s
6. **Document:** Update limits in code/config

## Reference: Provider Documentation

- **MarketAux:** https://www.marketaux.com/api (docs mention unlimited)
- **Finnhub:** https://finnhub.io/docs/api (60 req/min)
- **yfinance:** https://github.com/ranaroussi/yfinance (observe-based: 2000/hr)
- **Alpha Vantage:** https://www.alphavantage.co/documentation/ (5 req/min)
- **Alpaca:** https://docs.alpaca.markets/ (200 req/min)

---

**Last Updated:** 2026-04-24 03:55 UTC  
**By:** Nova (Envestero operational setup)
