# ENVESTERO CRON JOBS & TICKER/NEWS COLLECTION — SETUP SUMMARY
**Date:** 2026-05-03  
**Source:** /srv/github/Envestero/envestero/tasks/scheduler.py  
**Status:** 🟢 ACTIVE (APScheduler embedded in FastAPI)

---

## ACTIVE CRON JOBS (13 Total)

All jobs use **America/Los_Angeles** timezone. Format: `CronTrigger(...)`

### 🟢 ALWAYS RUNNING

#### 1. **refresh_proxies**
- **Schedule:** Every 30 minutes (`minute="*/30"`)
- **Time:** 24/7
- **Purpose:** Scrape + validate free proxy pool
- **Job ID:** `refresh_proxies`

#### 2. **collect_macro_news**
- **Schedule:** Daily noon ET (17:00 UTC)
- **Time:** `CronTrigger(hour=17, minute=0)`
- **Purpose:** Collect macro RSS headlines → `macro_news` table
- **Max Instances:** 1 (coalesce=True)

#### 3. **score_news**
- **Schedule:** Nightly 9:00 PM ET (21:00 UTC)
- **Time:** `CronTrigger(hour=21, minute=0)`
- **Purpose:** LLM-score unanalyzed articles
- **Max Instances:** 1 (coalesce=True)

#### 4. **generate_signals**
- **Schedule:** Every hour at :15 minutes
- **Time:** `CronTrigger(hour="*", minute=15)`
- **Purpose:** Generate trading signals for watched tickers (Phase I)
- **Max Instances:** 1 (coalesce=True)

#### 5. **execute_paper_trades**
- **Schedule:** Every hour at :20 minutes
- **Time:** `CronTrigger(hour="*", minute=20)`
- **Purpose:** Execute paper trades from fresh signals (Phase I.2)
- **Max Instances:** 1 (coalesce=True)

#### 6. **analyze_sentiment**
- **Schedule:** 4x daily (00:00, 06:00, 12:00, 18:00 UTC)
- **Time:** `CronTrigger(hour="0,6,12,18")`
- **Purpose:** FinancialBERT sentiment scoring (~1000 articles/run)
- **Max Instances:** 1 (coalesce=True)

#### 7. **sync_universe_and_backfill**
- **Schedule:** Weekly Sunday 2:00 AM UTC
- **Time:** `CronTrigger(day_of_week="sun", hour=2, minute=0)`
- **Purpose:** Ticker universe sync + OHLCV backfill
- **Grace Time:** 86400s (24h, allows recovery)

---

### 🟡 WEEKDAYS ONLY (Mon-Fri)

#### 8. **collect_daily**
- **Schedule:** Weekdays 5:30 PM ET (17:30)
- **Time:** `CronTrigger(day_of_week="mon-fri", hour=17, minute=30)`
- **Purpose:** Collect today's intraday (5-min) OHLCV data
- **Grace Time:** 3600s

#### 9. **collect_daily_1d**
- **Schedule:** Weekdays 10:00 PM ET (22:00 UTC)
- **Time:** `CronTrigger(day_of_week="mon-fri", hour=22, minute=0)`
- **Purpose:** Collect today's 1d bars for Strategy Lab universe
- **Grace Time:** 3600s

#### 10. **analyze_daily**
- **Schedule:** Weekdays 8:00 PM ET (20:00 UTC)
- **Time:** `CronTrigger(day_of_week="mon-fri", hour=20, minute=0)`
- **Purpose:** Detect candlestick patterns + technical indicators
- **Grace Time:** 3600s

#### 11. **generate_day_narrative**
- **Schedule:** Weekdays 6:00 PM ET (23:00 UTC)
- **Time:** `CronTrigger(day_of_week="mon-fri", hour=23, minute=0)`
- **Purpose:** LLM → `DayNarrative` table (post-market summary)
- **Grace Time:** 3600s
- **Max Instances:** 1 (coalesce=True)

---

### 🔵 CONDITIONAL (IF scraper_enabled=True in config)

#### 12. **scrape_watched_tickers**
- **Schedule:** Every N hours (default: 1h, can throttle to 3h)
- **Time:** `CronTrigger(hour=f"*/{settings.scraper_watched_interval_hours}")`
- **Purpose:** MarketAux + Finnhub + RSS for watched tickers
- **Sources:** 
  - MarketAux (unlimited)
  - Finnhub (60 calls/min max)
  - RSS feeds
- **Concurrency:** Scales based on heavy/light data window
  - Heavy window (midnight-7am ET weekdays): aggressive
  - Light hours: throttled
- **Max Instances:** 1 (coalesce=True)
- **Grace Time:** 1800s

#### 13. **scrape_sector**
- **Schedule:** 4x daily at specific UTC hours
- **Time:** `CronTrigger(hour=settings.scraper_sector_times)`
- **Default Times:** 6, 12, 18, 0 UTC (can throttle to 12, 0)
- **Purpose:** Sector-wide news collection (all tickers in each sector)
- **Sources:** MarketAux + Finnhub + RSS
- **Max Instances:** 1 (coalesce=True)
- **Grace Time:** 3600s

#### 14. **scrape_persona_tickers** (NEW)
- **Schedule:** 4x daily
- **Time:** `CronTrigger(hour="3,9,15,21")` (3am, 9am, 3pm, 9pm UTC)
- **Purpose:** Strategy Lab persona tickers (49 tickers)
- **Sources:** Finnhub + Yahoo RSS (NO MarketAux to preserve budget)
- **Max Instances:** 1 (coalesce=True)
- **Grace Time:** 3600s

---

## TICKER COLLECTION STRATEGY

### Universe Scope
- **Active Tickers:** ~12,491 registered
- **Backfill Status:** 2.68M+ OHLCV bars loaded (as of 2026-04-23)

### Tiered Collection (NEWS)

| Tier | Criteria | Frequency (Day Trade) | Frequency (Non-Day) | Est. Count | Sources |
|------|----------|----------------------|----------------------|-----------|---------|
| **Watch** | Manual flag OR sentiment shift trigger | Hourly + trigger | Daily + trigger | ~100 | MarketAux, Finnhub, RSS |
| **Tier 1** | Top 500 market cap | Hourly | Daily | ~500 | MarketAux, Finnhub |
| **Tier 2** | Active watchlist/portfolio | Daily | Daily | ~100-200 | Finnhub, RSS |
| **Tier 3** | All remaining active | Weekly or on-demand | Weekly | ~11,900 | Sector scrapes |
| **Macro** | No ticker (geo/sector tagged) | Hourly/Daily | Daily | N/A | RSS feeds |

### OHLCV Data Collection (INTRADAY & DAILY)

**5-Minute Bars:**
- Scheduled: `collect_daily` (5:30 PM ET weekdays)
- Scope: Strategy Lab universe + watched tickers
- Retention: Real-time for live trading

**Daily Bars (1d):**
- Scheduled: `collect_daily_1d` (10:00 PM ET weekdays)
- Scope: Strategy Lab universe + all active tickers
- Backfill: Weekly Sunday (catch-up + historical)

---

## NEWS INGESTION ARCHITECTURE

### Sources Integrated

| Source | API/RSS | Cost | Rate Limit | Purpose |
|--------|---------|------|-----------|---------|
| **MarketAux** | API | Free | 100 req/day | Ticker-bound news, clean JSON |
| **Finnhub** | API | Free | 60 req/min | Real-time, ticker-specific |
| **GNews** | API | Free | 100 req/day | General news (deprecated in favor of MarketAux) |
| **Google News RSS** | RSS | Free | N/A | General financial news |
| **Yahoo Finance RSS** | RSS | Free | N/A | High volume, broad coverage |
| **Seeking Alpha RSS** | RSS | Free | N/A | Deep analysis, strong signal |
| **MarketWatch RSS** | RSS | Free | N/A | Fast-breaking news |

### Sentiment Scoring Pipeline

**Cascading Providers:**
1. OpenAI (GPT-4, primary)
2. Ollama (local LLM fallback)
3. FinancialBERT (heuristic fallback)

**Schedule:** `score_news` job runs nightly 9 PM ET (21:00 UTC)
- Scores only unanalyzed articles
- Stores: sentiment_score, sentiment_label, model_used
- Rate limiting: respects API constraints

---

## MACRO NEWS & SECTOR MAPPING

### Macro News Table (`macro_news`)
- **Fetch Schedule:** Daily noon ET (17:00 UTC)
- **Job:** `collect_macro_news`
- **Tags:** geopolitical, commodity, rates, macro, supply_chain
- **Regions:** middle_east, china, us, eu, global
- **Sector Mapping:** Additive weighting (20-30% signal contribution)
  - Weighted by: recency × source quality × sector relevance
  - Manual hard-override flag (v1 only)

### Day Narrative (`DayNarrative`)
- **Generate Schedule:** Weekdays 6 PM ET (23:00 UTC)
- **Job:** `generate_day_narrative`
- **Purpose:** LLM summary of macro headlines + market context
- **Cache:** Enables fast re-use for UI + period summaries

---

## SIGNAL GENERATION & PAPER TRADING

### Signal Generation
- **Schedule:** Every hour at :15 minutes
- **Job:** `generate_signals` (Phase I)
- **Scope:** Watched tickers
- **Inputs:** 
  - Candlestick patterns (technical)
  - News sentiment (past 24h)
  - Macro sentiment (sector-weighted)
- **Output:** `SignalHistory` table

### Paper Trading Execution
- **Schedule:** Every hour at :20 minutes
- **Job:** `execute_paper_trades` (Phase I.2)
- **Scope:** Signals from previous 5-minute window
- **Output:** `scenario_trade` table + position tracking

---

## TECHNICAL ANALYSIS & REGIME DETECTION

### Candlestick Pattern Detection
- **Schedule:** Weekdays 8 PM ET (20:00 UTC)
- **Job:** `analyze_daily`
- **Patterns Detected:** Standard candlestick formations (hammer, doji, engulfing, etc.)
- **Output:** Technical indicator signals

### Sentiment Analysis
- **Schedule:** 4x daily (00:00, 06:00, 12:00, 18:00 UTC)
- **Job:** `analyze_sentiment`
- **Scope:** ~1000 articles per run
- **Model:** FinancialBERT (local)
- **Purpose:** Bulk sentiment scoring for non-urgent articles

---

## RATE LIMITING & CONCURRENCY CONTROLS

### Heavy/Light Data Windows (Proxy Conservation)

**Weekdays:**
- Heavy: midnight-7am ET (IP rotation aggressive)
- Light: 7am-midnight ET (IP rotation normal)

**Weekends:**
- Heavy: 2am-8am ET
- Light: 8am-2am ET

**Concurrency Scaling:**
- Heavy window: `settings.heavy_window_concurrent_tickers` (default: 10-20)
- Light hours: `settings.light_window_concurrent_tickers` (default: 5-10)
- Request delay: Scales per window (heavy: 50ms, light: 200ms)

### Coalesce & Max Instances
- **Coalesce=True:** Prevents duplicate runs if previous job still executing
- **Max Instances=1:** Only one instance of job runs at a time
- **Misfire Grace Time:** Job allowed to run late by this duration before skipping
  - Critical jobs: 3600s (1h)
  - Standard: 1800s (30min)
  - Light jobs: 300s (5min)

---

## CONFIGURATION (envestero/config.py)

### Scraper Control
```
scraper_enabled: bool                              # Enable news scraping jobs
scraper_watched_interval_hours: int = 1            # How often to scrape watched tier
scraper_sector_times: str = "6,12,18,0"           # UTC hours for sector scrapes (4x/day)
```

### Data Windows
```
heavy_data_window_weekday_start: int = 0           # midnight ET
heavy_data_window_weekday_end: int = 7             # 7am ET
heavy_data_window_weekend_start: int = 2           # 2am ET
heavy_data_window_weekend_end: int = 8             # 8am ET
```

### Concurrency
```
heavy_window_concurrent_tickers: int = 20          # Parallel requests in heavy window
light_window_concurrent_tickers: int = 10          # Parallel requests in light hours
heavy_window_request_delay_ms: int = 50            # ms between requests (heavy)
light_window_request_delay_ms: int = 200           # ms between requests (light)
```

---

## DEPLOYMENT STATUS

✅ **Active:** All 14 cron jobs registered + running  
✅ **News Collection:** Watchlist + sector + persona tickers  
✅ **OHLCV Backfill:** Weekly sync + daily intraday  
✅ **Sentiment Scoring:** LLM-driven 4x daily  
✅ **Signal Generation:** Hourly (Phase I)  
✅ **Paper Trading:** Hourly execution (Phase I.2)  

---

## WHAT WAS MISSING (YOU WERE RESET)

**OpenClaw Cron Jobs:** ZERO
- You had no persistent cron jobs configured when reset
- Envestero has its own APScheduler (embedded in FastAPI, not OpenClaw cron)
- This is by design: app-level scheduling, not system-level

**Next Step:** Wire Envestero cron jobs to OpenClaw for:
1. Monitoring job health (success/failure alerts)
2. Cross-session coordination (if needed)
3. Audit logging for compliance
4. Persistent job status tracking

---

**Last Updated:** 2026-05-03 13:14 PDT  
**Source:** /srv/github/Envestero/envestero/tasks/scheduler.py (1094 lines)
