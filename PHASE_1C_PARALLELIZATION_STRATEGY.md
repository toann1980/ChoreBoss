# PHASE 1C PARALLELIZATION: Phases 1C.1 + 1C.2 Run in Parallel

**For:** Nova, Kira  
**Date:** 2026-04-21 07:05 UTC  
**Decision:** 1C.1 and 1C.2 are independent; can run in parallel

---

## Parallelization Strategy

### Phases 1C.1 (Executives) and 1C.2 (Sentiment): PARALLEL ✅

**Why they can run in parallel:**
- Phase 1C.1 collects executive data (SEC Edgar API)
- Phase 1C.2 collects consumer sentiment (Reddit, Twitter, Glassdoor, App Store APIs)
- **No dependency between them** (different data sources)
- Both read from same database, write to different tables
- No conflicts

**Timeline benefit:**
- Sequential: 1C.1 (2-3h) + 1C.2 (3-4h) = 5-7h total
- Parallel: 1C.1 (2-3h) + 1C.2 (3-4h) **run together** = ~3.5-4h max

**Savings:** ~2 hours

---

### Phase 1C.3 (Correlation Detection): SEQUENTIAL ⏳

**Why it must wait:**
- 1C.3 inputs: Executive data (from 1C.1) + Sentiment data (from 1C.2)
- 1C.3 outputs: Relationship graph, source weights
- Cannot start until both 1C.1 and 1C.2 complete

**Timeline:**
- Wait for: max(1C.1, 1C.2) to complete
- Start 1C.3: ~4h after start
- Complete 1C.3: ~4h + 5-6h = ~9-10h total

---

## Parallel Execution Model

### Configuration

```
Timeline:
├─ 00:00 - Start
│
├─ Phase 0 (Sequential)
│ ├─ Task 0.1: Execs (AAPL) — 45 min
│ ├─ Task 0.2: Sentiment (AAPL, all 4 sources) — 1h
│ ├─ Task 0.3: Validation — 30 min
│ └─ Task 0.4: Correlation — 30 min
│ └─ Duration: 2.5-3h
│
├─ 03:00 - Phase 0 Complete (Success = Go to Phase 1C)
│
├─ Phase 1C.1 + 1C.2 (PARALLEL)
│ ├─ 1C.1: Executive data (20 tickers) — 2-3h
│ │  ├─ Thread/Worker 1: Fetch + store exec data
│ │  ├─ Run: Sequential per ticker (don't parallelize API calls)
│ │  └─ Output: Executive table populated
│ │
│ ├─ 1C.2: Consumer sentiment (20 tickers) — 3-4h
│ │  ├─ Thread/Worker 2: Fetch from 4 sources
│ │  ├─ Run: Sequential per source (don't parallelize API calls)
│ │  └─ Output: ConsumerSentiment table populated
│ │
│ └─ Duration: ~3.5-4h (longer of the two)
│
├─ 06:30 - Both 1C.1 + 1C.2 Complete
│
├─ Phase 1C.3 (Sequential)
│ ├─ Task 3.1: Correlation detection — 5-6h
│ ├─ Inputs: 1C.1 data + 1C.2 data
│ ├─ Outputs: InfluenceNetwork table
│ └─ Duration: 5-6h
│
├─ 11:30 - Phase 1C.3 Complete
│
├─ Phase 1C.4 (Scale)
│ ├─ Apply rules to remaining data — 1h
│ └─ Duration: 1h
│
└─ 12:30 - Phase 1C Complete (ready for Phase 3)

TOTAL PHASE 1C: ~9-10h (vs 13-17h if fully sequential)
```

---

## Implementation: How to Run Parallel

### Option 1: Two Sequential Processes (Simplest)
```python
# Process 1: Phase 1C.1 (Executives)
for ticker in all_20_tickers:
    execs = fetch_sec_filings(ticker)
    store_executives(execs)
    # ~2-3h total

# Process 2: Phase 1C.2 (Sentiment) - START WHILE PROCESS 1 RUNS
for ticker in all_20_tickers:
    for source in [reddit, twitter, glassdoor, appstore]:
        sentiment = fetch_sentiment(ticker, source)
        store_sentiment(sentiment, source)
    # ~3-4h total
```

**Start both processes at same time, monitor separately.**

### Option 2: Threading (More Efficient)
```python
import threading

# Thread 1: Phase 1C.1
t1 = threading.Thread(target=run_phase_1c1, args=(all_20_tickers,))
t1.start()

# Thread 2: Phase 1C.2
t2 = threading.Thread(target=run_phase_1c2, args=(all_20_tickers,))
t2.start()

# Wait for both to complete
t1.join()
t2.join()

# Then run Phase 1C.3
run_phase_1c3()
```

**Note:** Don't parallelize API calls (rate limits). Parallelize only the overall phases.

---

## Resource Constraints

### Network Bandwidth
- 1C.1: SEC Edgar API (relatively light)
- 1C.2: Reddit + Twitter + Glassdoor + App Store (moderate)
- **Can run together:** No bottleneck

### Database I/O
- 1C.1 writes to: Executive, ExecutiveEvent tables
- 1C.2 writes to: ConsumerSentiment table
- **Can run together:** Different tables, no lock conflicts

### API Rate Limits
- **Don't parallelize within phase** (e.g., don't fetch AAPL + MSFT simultaneously from same API)
- **Do parallelize across phases** (fetch execs from SEC while fetching sentiment from Reddit)

---

## Validation Timing

### Phase 0 Complete → Phase 1C.1 + 1C.2 Start
```
Timeline:
Phase 0:      [2.5h]
               |
Phase 1C.1:    [2-3h] ────────────┐
               |                    |
Phase 1C.2:         [3-4h] ────────┤
               |                    |
               └────────────────────┘ (max of 1C.1, 1C.2)
                                     |
Phase 1C.3:                      [5-6h]
```

**After Phase 0:** Both 1C.1 + 1C.2 start immediately (no waiting)

---

## Checkpoints

### After Phase 0 (2.5-3h)
- ✅ Signal chain validated (AAPL)
- ✅ Source ranking established
- ✅ Ready to scale to 20 tickers

### After Phase 1C.1 (2-3h into parallel window)
- ✅ Executive data loaded (20 tickers)
- ✅ Can validate against sentiment separately if needed

### After Phase 1C.2 (3-4h into parallel window)
- ✅ Sentiment data loaded (20 tickers)
- ✅ Can validate accuracy separately if needed

### After Phase 1C.1 + 1C.2 (3.5-4h total)
- ✅ Both phases complete
- ⏳ Phase 1C.3 can now start

### After Phase 1C.3 (5-6h more)
- ✅ Correlations detected
- ✅ Source weights learned
- ✅ Ready for Phase 3 (Personas)

---

## Total Timeline (After Phase 0 Success)

| Phase | Duration | Start | End | Notes |
|-------|----------|-------|-----|-------|
| **Phase 0** | 2.5-3h | 0:00 | 3:00 | Single-ticker validation |
| **1C.1 + 1C.2** | 3.5-4h | 3:00 | 6:30 | Parallel (independent) |
| **1C.3** | 5-6h | 6:30 | 11:30 | Sequential (needs 1C.1 + 1C.2) |
| **Scale** | 1h | 11:30 | 12:30 | Apply to remaining data |
| **TOTAL** | **9-10h** | — | — | (vs 13-17h if fully sequential) |

**Phase 3 (Personas):** 12-15h (after Phase 1C complete)

---

## Kira's Role (Parallel Opportunity)

### Can Kira Help with Parallelization?

**Option 1:** Kira runs Phase 1C.1, Nova runs Phase 1C.2
- Kira: Fetch executive data (SEC Edgar) — 2-3h
- Nova: Fetch sentiment data (Reddit, Twitter, etc.) — 3-4h
- **Both run in parallel on different machines**

**Option 2:** Kira runs Phase 1C.3, Nova validates
- Kira: Correlation detection engine — 5-6h
- Nova: Validate results + monitor
- **Depends on when 1C.1 + 1C.2 complete**

**Recommendation:** Option 1 (Phase 0 success) → Both 1C.1 + 1C.2, then Kira helps with 1C.3

---

## Decision Required

**Toan:** Approve parallelization of Phases 1C.1 + 1C.2?

---

**Nova's note:** Phase 0 → Success? → Phase 1C.1 + 1C.2 parallel (3.5-4h) → Phase 1C.3 sequential (5-6h) → Phase 3 (12-15h)

---

**Updated:** 2026-04-21 07:05 UTC by Nova ✨
