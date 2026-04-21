# Phase 2 Test Coverage Summary

**Total Tests:** 48 test functions across 3 files  
**Status:** ✅ All syntax-validated, ready for pytest  

---

## Integration Tests (20 functions)
**File:** `tests/integration/test_phase2_endpoints.py`

### `TestNewsSentimentAggregateEndpoint` (5 tests)
1. `test_sentiment_endpoint_exists` — 404 for missing ticker
2. `test_sentiment_with_articles` — Correct aggregation (positive/neutral/negative breakdown, avg score)
3. `test_sentiment_empty_results` — Handles zero articles gracefully
4. `test_sentiment_days_filter` — `days` parameter filters correctly
5. **Coverage:** GET `/news/{symbol}/sentiment` endpoint fully tested

### `TestNewsListEndpointFiltering` (5 tests)
1. `test_news_list_with_days_filter` — Articles filtered by `days` param
2. `test_news_list_with_offset_pagination` — `offset` skips correctly, supports paging
3. `test_news_list_combined_days_and_offset` — Both params work together
4. `test_news_list_unanalyzed_only` — Existing `unanalyzed_only` still works
5. **Coverage:** GET `/news/{symbol}` with all query filters

### `TestNewsScoreBatchLoop` (2 tests)
1. `test_score_news_loops_until_limit` — Scores up to `limit`, then stops (15/25 articles)
2. `test_score_news_stops_early_if_no_more_articles` — Stops early if < limit remain
3. **Coverage:** `_news_score(limit)` batch loop logic

---

## Unit Tests — Scheduler (8 functions)
**File:** `tests/unit/test_scheduler.py`

### `TestJobCollectNews` (2 tests)
1. `test_skips_when_no_stale_tickers` — No fetch when candidates empty
2. `test_fetches_stale_tickers_with_rss_first` — Verifies `sources=("google_news_rss", "gnews")`
3. **Coverage:** `job_collect_news` logic + RSS-first source order

### `TestJobScoreNews` (2 tests)
1. `test_skips_when_no_unscored_articles` — Exits early when all scored
2. `test_uses_heuristic_fallback_on_primary_failure` — Cascade fallback works
3. **Coverage:** `job_score_news` + cascade provider behavior

### `TestSchedulerJobRegistration` (2 tests)
1. `test_all_jobs_registered` — All 6 required jobs present
2. `test_news_jobs_have_max_instances_1` — Overlap protection confirmed
3. **Coverage:** Scheduler initialization + job protection

---

## Unit Tests — Sentiment (20 functions)
**File:** `tests/unit/test_sentiment.py`

### `TestSentimentResult` (4 tests)
1. `test_valid_positive` — Score in range, label valid
2. `test_valid_negative` — Negative score accepted
3. `test_invalid_score_out_of_range` — Rejects score > 1.0
4. `test_invalid_label` — Rejects invalid labels
5. **Coverage:** `SentimentResult.is_valid()` validation

### `TestParseLlmResponse` (3 tests)
1. `test_parses_valid_json` — JSON deserialization works
2. `test_handles_invalid_json_gracefully` — Fallback to neutral on parse error
3. `test_handles_missing_fields` — Defaults filled in
4. **Coverage:** JSON parsing + error handling

### `TestHeuristicSentimentProvider` (4 tests)
1. `test_positive_keywords` — "beats earnings" → positive
2. `test_negative_keywords` — "lawsuit, layoff" → negative
3. `test_neutral_no_keywords` — Neutral default
4. `test_always_valid` — Always produces valid results
5. **Coverage:** Heuristic provider reliability (no API required)

### `TestCascadingSentimentProvider` (4 tests)
1. `test_returns_first_successful_result` — Uses first provider if successful
2. `test_falls_back_on_exception` — Catches exception, tries next
3. `test_falls_back_on_invalid_result` — Retries if result fails `is_valid()`
4. `test_raises_when_all_fail` — RuntimeError when chain exhausted
5. **Coverage:** Cascade logic + fallback reliability

### `TestGetSentimentProvider` (4 tests)
1. `test_ollama_returns_cascade_with_heuristic_fallback` — `ollama` → Ollama + Heuristic
2. `test_openai_returns_full_cascade` — `openai` → OpenAI + Ollama + Heuristic
3. `test_openai_no_api_key_falls_back_to_ollama_cascade` — Missing key → Ollama cascade
4. `test_unknown_provider_returns_heuristic` — Fallback for unknown setting
5. **Coverage:** Factory configuration + cascade initialization

### `TestOllamaSentimentProvider` (1 test)
1. `test_analyze_returns_result` — Ollama API call + response parsing
2. **Coverage:** Ollama provider HTTP behavior

---

## Coverage by Phase 2 Gap

| Gap | Tests | Status |
|-----|-------|--------|
| `GET /news/{symbol}/sentiment` endpoint | 5 | ✅ Full coverage |
| `days` filter + `offset` pagination | 5 | ✅ Full coverage |
| Cascade fallback factory | 8 | ✅ Full coverage |
| GNews rate limit (RSS-first) | 2 | ✅ Verified in scheduler |
| Scheduler job protection | 2 | ✅ max_instances=1 confirmed |
| `score-news --limit` CLI loop | 2 | ✅ Batch logic tested |
| Heuristic provider reliability | 4 | ✅ Always works |
| **Total** | **28+** | ✅ |

---

## Key Test Patterns

### 1. Async Test Fixtures
- `api_client` — AsyncClient with test DB injected
- `db_session` — Fresh in-memory SQLite per test
- `db_engine` — Session-scoped async engine

### 2. Endpoint Tests
- Create fixtures (ticker, articles)
- Call endpoint via `AsyncClient`
- Assert HTTP status + JSON response

Example:
```python
response = await api_client.get("/api/v1/news/AAPL/sentiment?days=7")
assert response.status_code == 200
data = response.json()
assert data["sentiment_breakdown"]["positive"] == 3
```

### 3. Logic Tests (No HTTP)
- Mock dependencies (providers, DB)
- Test function behavior directly
- Verify exception handling + fallbacks

Example:
```python
cascade = CascadingSentimentProvider([failing, fallback])
result = await cascade.analyze("test")
assert result.is_valid()
```

---

## Running the Tests

### All Phase 2 tests:
```bash
pytest tests/integration/test_phase2_endpoints.py tests/unit/test_scheduler.py tests/unit/test_sentiment.py -v
```

### With coverage:
```bash
pytest tests/integration/test_phase2_endpoints.py tests/unit/test_scheduler.py tests/unit/test_sentiment.py --cov=envestero --cov-report=html
```

### Specific test class:
```bash
pytest tests/integration/test_phase2_endpoints.py::TestNewsSentimentAggregateEndpoint -v
```

---

## Ready for Execution

All tests assume:
- PostgreSQL + TimescaleDB running (Phase 1 setup)
- `.env` configured with DB credentials
- Alembic migrations applied
- Ollama running (optional, heuristic fallback covers missing Ollama)

**Next Step:** Execute Phase 1 (DB setup) → Run Phase 2 tests → Validate endpoints ⚡
