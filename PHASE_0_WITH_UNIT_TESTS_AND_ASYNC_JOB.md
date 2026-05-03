# PHASE 0 UPDATED: Include Unit Tests + Async Job

**Date:** 2026-04-21 07:11 UTC  
**Status:** Phase 0 now includes unit tests and async job scheduling

---

## REVISED PHASE 0 TASKS

### Task 0.1: Executive Data (45 min)
- Build Executive + ExecutiveEvent tables
- Fetch Apple execs from SEC Edgar
- Store: CEO, CFO, CTO + dates
- Validate: ≥3 execs, dates correct

### Task 0.2: Consumer Sentiment (1h)
- Implement 4 collectors (Reddit, Twitter, Glassdoor, App Store)
- Apply data quality thresholds
- Collect: 7 days of Apple sentiment
- Output: ~100-200 sentiment entries

### Task 0.3: Daily Validation (30 min)
- Get sentiment data (7 days)
- Get daily OHLCV (same 7 days)
- Measure: Did sentiment predict next day's price?
- Target: Accuracy > 60%

### Task 0.4: Source Ranking (30 min)
- Measure each source independently
- Which source most reliable for Apple?
- Rank sources by accuracy

### ⭐ **NEW - Task 0.5: Unit Tests (30 min)**
**AFTER AAPL VALIDATION SUCCEEDS**

Unit tests for all functions:

**Test Executive Collection:**
```python
def test_fetch_sec_filings():
    """Verify SEC Edgar fetch returns valid executives"""
    execs = fetch_sec_filings("AAPL")
    assert len(execs) >= 3
    assert all(exec.name, exec.title, exec.since_date for exec in execs)

def test_store_executives():
    """Verify executives stored correctly in database"""
    execs = [Executive(name="Tim Cook", title="CEO", ticker="AAPL")]
    store_executives(execs)
    assert db.query(Executive).filter(ticker="AAPL").count() == 1

def test_executive_data_quality():
    """Verify no duplicates, dates are valid"""
    # ... validation tests
```

**Test Sentiment Collection:**
```python
def test_fetch_reddit_sentiment():
    """Verify Reddit PRAW integration"""
    posts = fetch_reddit_sentiment("AAPL", min_upvotes=10)
    assert all(post.upvotes >= 10 for post in posts)

def test_fetch_twitter_sentiment():
    """Verify Twitter tweepy integration"""
    tweets = fetch_twitter_sentiment("AAPL", min_count=50)
    assert len(tweets) >= 0  # May be 0 if no tweets

def test_sentiment_category_classification():
    """Verify leadership/product/service categories"""
    sentiment = ConsumerSentiment(text="CEO leaving is bad", category="leadership")
    assert sentiment.category in ["leadership", "product", "service"]

def test_sentiment_data_quality():
    """Verify no duplicates, dates, sentiment scores valid"""
    # ... validation tests
```

**Test Daily Validation:**
```python
def test_sentiment_predicts_price():
    """Verify sentiment → price direction correlation"""
    results = validate_sentiment_to_price(ticker="AAPL", days=7)
    assert results['accuracy'] > 0.6  # >60% accuracy
    assert results['samples'] >= 3

def test_source_accuracy():
    """Verify each source accuracy measured independently"""
    for source in ["reddit", "twitter", "glassdoor", "appstore"]:
        accuracy = measure_source_accuracy("AAPL", source)
        assert 0 <= accuracy <= 1.0
```

**Coverage Target:** >80% code coverage

**Test Execution:**
```bash
pytest tests/unit/test_executives.py -v
pytest tests/unit/test_sentiment.py -v
pytest tests/unit/test_validation.py -v
pytest --cov=envestero tests/unit/
```

---

### ⭐ **NEW - Task 0.6: Create Async Job for Remaining 19 Tickers (5 min setup)**
**AFTER UNIT TESTS PASS**

**What:** Create background job to collect data for remaining 19 tickers

**Job Configuration:**
```python
# envestero/tasks/phase_0_scale.py

from celery import shared_task

@shared_task
def collect_executives_all_tickers():
    """Collect executive data for all 20 tickers"""
    tickers = [
        "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL",
        "TSLA", "BRK", "META", "AVGO", "COST",
        "XOM", "MCD", "BA", "DIS", "KO",
        "JPM", "V", "JNJ", "PG"  # 19 remaining
    ]
    
    for ticker in tickers:
        try:
            execs = fetch_sec_filings(ticker)
            store_executives(execs)
            logger.info(f"✅ {ticker}: {len(execs)} executives stored")
        except Exception as e:
            logger.error(f"❌ {ticker}: {e}")
            # Continue on failure (retry later)

@shared_task
def collect_sentiment_all_tickers():
    """Collect sentiment data for all 20 tickers"""
    tickers = [... same list ...]
    
    for ticker in tickers:
        for source in ["reddit", "twitter", "glassdoor", "appstore"]:
            try:
                sentiment = fetch_sentiment(ticker, source)
                store_sentiment(sentiment, source)
                logger.info(f"✅ {ticker}/{source}: {len(sentiment)} entries")
            except Exception as e:
                logger.error(f"❌ {ticker}/{source}: {e}")

# Schedule jobs
collect_executives_all_tickers.delay()  # Start immediately
collect_sentiment_all_tickers.delay()   # Start immediately (parallel)
```

**Job Properties:**
- **Type:** Background async tasks (Celery/APScheduler)
- **Duration:** 2-3h each (1C.1 and 1C.2)
- **Parallelization:** Both start at same time
- **Monitoring:** Logging + progress tracking
- **Error handling:** Log failures, continue
- **Output:** Data added to database

**Job Status Tracking:**
```python
# Can check progress while job runs
collect_execs_job = collect_executives_all_tickers.delay()
collect_sentiment_job = collect_sentiment_all_tickers.delay()

# Monitor
while not collect_execs_job.ready() or not collect_sentiment_job.ready():
    print(f"Execs: {collect_execs_job.state}")
    print(f"Sentiment: {collect_sentiment_job.state}")
    time.sleep(30)

print("Both jobs complete!")
```

---

## REVISED PHASE 0 TIMELINE

| Task | Duration | Notes |
|------|----------|-------|
| 0.1: Executives (AAPL) | 45 min | Sequential |
| 0.2: Sentiment (AAPL) | 1h | Sequential |
| 0.3: Validation | 30 min | Check if >60% accurate |
| 0.4: Source ranking | 30 min | Rank sources |
| **0.5: Unit tests** | 30 min | **AFTER 0.4 SUCCESS** |
| **0.6: Schedule jobs** | 5 min | **AFTER 0.5 SUCCESS** |
| **Async collection** | 2-3h | **RUNS IN PARALLEL** |
| **TOTAL Phase 0** | **3-3.5h active** | +2-3h async (parallel) |

---

## PHASE 0 SUCCESS FLOW

```
Start
 │
 ├─ Task 0.1: Execs (AAPL) [45 min]
 │   └─ Success? → Continue
 │   └─ Fail? → Debug + Retry
 │
 ├─ Task 0.2: Sentiment (AAPL, all 4 sources) [1h]
 │   └─ Success? → Continue
 │   └─ Fail? → Debug + Retry
 │
 ├─ Task 0.3: Validation [30 min]
 │   └─ Accuracy > 60%? → Continue
 │   └─ Accuracy < 60%? → PHASE 0 FAIL (pivot)
 │
 ├─ Task 0.4: Source Ranking [30 min]
 │   └─ Clear patterns? → Continue
 │   └─ No patterns? → PHASE 0 FAIL (investigate)
 │
 ├─ **Task 0.5: Unit Tests [30 min]** ✅ NEW
 │   └─ Coverage > 80%? → Continue
 │   └─ Coverage < 80%? → Add tests
 │
 ├─ **Task 0.6: Schedule Jobs [5 min]** ✅ NEW
 │   └─ Jobs scheduled? → Start collection
 │   └─ Error? → Debug scheduler
 │
 ├─ **Background Async Jobs [2-3h in parallel]** ✅ NEW
 │   ├─ collect_executives_all_tickers() [2-3h]
 │   ├─ collect_sentiment_all_tickers() [3-4h]
 │   └─ Both run simultaneously (independent)
 │
 ├─ Database now has:
 │   ├─ ✅ 60-100 executives (20 tickers)
 │   ├─ ✅ 2000-4000 sentiment entries (20 tickers)
 │   └─ Ready for Phase 1C.3
 │
 └─ Phase 1C.3 starts (Correlations)
```

---

## KEY CHANGES

✅ **Unit tests added** (30 min, Task 0.5)
- Tests all functions created in 0.1-0.4
- Coverage target: >80%
- Run before scaling

✅ **Async job scheduling** (5 min, Task 0.6)
- Two jobs: `collect_executives_all_tickers()` + `collect_sentiment_all_tickers()`
- Start after unit tests pass
- Run in parallel (independent data sources)
- Update database

✅ **No additional wait time**
- Tests run after AAPL validation (30 min)
- Jobs scheduled immediately (5 min)
- Jobs run in parallel while you do other work
- Phase 0 "active" time: 3-3.5h, but async jobs run during + after

---

## MEMORY SIGNALING: The Other Priority

Before starting Phase 0, Toan wants:

> "We should finish the memory signaling for you and Kira first and then begin the phases."

This means setting up the message infrastructure:
- **TO_NOVA.md** — Kira's inbox (instant wake via inotifywait)
- **TO_KIRA.md** — Nova's inbox (2-min cron check)
- Fix permissions on memory-sync
- Confirm bidirectional messaging works

---

**Next: Set up memory signaling infrastructure, then begin Phase 0.** 🚀

---

**Updated:** 2026-04-21 07:11 UTC by Nova ✨
