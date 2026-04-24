# Backend Wiring Lesson: Configuration & Endpoint Mismatch (2026-04-24)

## What Broke

After building the frontend dashboard components + switching timezone from ET to PST, the API wouldn't start. The frontend then showed "Not Found" errors because it was calling endpoints that don't exist.

## Root Causes

### 1. Configuration Key Rename — Incomplete Search & Replace
**What happened:**
- When we switched from ET to PST, we renamed config keys in `config.py`:
  - `scraper_quiet_hours_start` → `heavy_data_window_weekday_start`
  - `scraper_quiet_hours_end` → `heavy_data_window_weekday_end`
- But `scheduler.py` still referenced the OLD keys in job names (line 164)
- Scheduler crashed on startup trying to access non-existent attributes

**Error:**
```
AttributeError: 'Settings' object has no attribute 'scraper_quiet_hours_start'
```

**Fix:**
- Searched and replaced all references in scheduler.py
- But should have done a FULL codebase search first

**Lesson for next time:**
```bash
# After renaming config keys, ALWAYS do this:
grep -r "scraper_quiet_hours" /srv/github/Envestero/envestero/
grep -r "database_url" /srv/github/Envestero/envestero/
# Make sure output is EMPTY before considering the refactor done
```

### 2. Inconsistent Configuration Naming — Database Connection
**What happened:**
- `signal_events.py` used `settings.database_url`
- But the actual setting is `settings.db_url` (check: `db/engine.py`)
- Service crashed with auth error because it was constructing a broken connection string

**Error:**
```
AttributeError: 'Settings' object has no attribute 'database_url'
```

**Lesson:**
- Configuration naming should be consistent across all services
- Always check `config.py` for the EXACT key name before using it
- Add a single "source of truth" comment in config.py for connection URLs

### 3. Frontend Called Endpoints That Don't Exist
**What happened:**
- Components tried to call `/api/v1/signals/` (doesn't exist)
- Should have called `/api/v1/signals/{symbol}/summary` 
- Same with `/api/v1/tickers/watched` (should check routers)

**Why it wasn't caught:**
- Built components in isolation with mock data
- Only tested against backend after entire dashboard was built
- Should have tested endpoint wiring incrementally

**Lesson:**
- Don't build UI components with mock data then try to wire backend later
- **Test endpoint wiring immediately**: build 1 component → wire backend → test → move to next
- Keep a reference list of all backend endpoints in `.openclaw/ENDPOINTS.md`

## Prevention Checklist for Next Time

✅ **Configuration Changes:**
- [ ] Make the change in config.py
- [ ] Search entire codebase: `grep -r "old_key_name" /srv/github/Envestero/`
- [ ] Verify output is EMPTY
- [ ] Commit with message: "Renamed config key X → Y, updated all references"

✅ **Endpoint Changes:**
- [ ] Update router definition in `envestero/api/routers/*.py`
- [ ] Update frontend component fetch URL to match
- [ ] Test with curl: `curl http://10.0.0.81:8000/api/v1/new/endpoint`
- [ ] Commit with message: "Added/changed endpoint X, updated frontend caller Y"

✅ **Frontend → Backend Wiring:**
- [ ] Build component #1
- [ ] Wire to backend endpoint (don't use mock data)
- [ ] Test fetch succeeds or shows real error
- [ ] Move to component #2
- [ ] Repeat

## Template for Future Config Changes

```python
# config.py
class Settings:
    # Database connection
    db_host: str  # Updated from database_host (Jan 2026)
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    
    @property
    def db_url(self) -> str:
        """SQLAlchemy async connection string"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
```

Then grep for all usages:
```bash
grep -r "database_url\|Database_url\|DATABASE_URL" /srv/github/Envestero/
```

## Template for Endpoint Documentation

Create `.openclaw/ENDPOINTS.md`:
```markdown
# Available API Endpoints

## Signals
- GET `/api/v1/signals/{symbol}` - Single signal
- GET `/api/v1/signals/{symbol}/summary` - Signal summary
- Used by: TopSignals.tsx

## News
- GET `/api/v1/news/{symbol}` - Articles for symbol
- GET `/api/v1/news/{symbol}/sentiment` - Sentiment only
- Used by: NewsFeed.tsx

## Paper Trading
- GET `/api/v1/paper-trading/portfolio` - Portfolio metrics
- GET `/api/v1/paper-trading/positions` - Open positions
- Used by: OpenPositions.tsx, Portfolio.tsx

## Catalysts
- GET `/api/v1/catalysts` - All catalysts
- GET `/api/v1/catalysts/sleepers` - Sleeper picks
- Used by: TopCatalysts.tsx
```

Then components check this file first before guessing endpoints.

---

**Key Insight:** The error cascade happened because:
1. Config key mismatch → scheduler died → API never started
2. Frontend kept trying to call backend that was down
3. Showed "Not Found" instead of real error (timeout or connection refused)

**Prevent by:** Testing config changes immediately + wiring UI incrementally + keeping endpoint docs.
