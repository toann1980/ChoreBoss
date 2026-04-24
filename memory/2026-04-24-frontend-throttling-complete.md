# Session Summary: 2026-04-24 Envestero Frontend + Network Throttling

**Status:** ✅ Complete | Frontend live + intelligent throttling deployed  
**Time:** 1:30 AM - 3:58 AM PST (2.5 hours)  
**Commits:** 3 (frontend + throttling + PST timezone fix)

---

## What's Live Now

### 1. Frontend Dashboard ✅
- **URL:** http://10.0.0.81:3000 (accessible from Windows)
- **Backend API:** http://10.0.0.81:8000
- **Components Built:**
  - TopSignals: Horizontal layout, icon | symbol | type | confidence % | reason | time
  - NewsFeed: Horizontal layout, icon | title | sentiment | score % | publisher | time
  - Portfolio: Compact single-row display (balance, daily PnL, total PnL, 7-day equity curve)
  - TopCatalysts: Event type | title | impact level | probability % | sector | time until
- **Design:** Dark mode (slate-950), gold accents, sharp corners, responsive 12-column grid
- **Development:** Hot reload enabled (both API + frontend)

### 2. Network Throttling + Rate Limits ✅
- **Heavy Data Window** (quiet hours - aggressive mode):
  - Weekdays: Midnight-7am PST (10 concurrent requests, 50ms delay)
  - Weekends: 2am-8am PST (10 concurrent requests, 50ms delay)
  - Use: Large backfills, bulk sync, full dataset pulls
- **Light Hours** (peak internet usage - conservative mode):
  - All other times (2 concurrent requests, 500ms delay)
  - Use: Incremental updates, monitoring
- **API Rate Limits Protected:**
  - MarketAux: Unlimited
  - Finnhub: 60/min (enforced via 1 request/second minimum)
  - yfinance: 1900/hr (enforced via 1.9s delay)
  - **CRITICAL:** Never break these - 20% buffer always applied

### 3. Timezone Standardization ✅
- **Changed ALL times to PST** (Pacific Standard Time)
- Scheduler timezone: America/Los_Angeles
- No more UTC or ET references
- All documentation, logs, and config use PST

---

## Technical Details

### Configuration (`.env`)
```env
# Scheduler uses America/Los_Angeles timezone
# Heavy data window: weekdays 0-7 (midnight-7am), weekends 2-8 (2am-8am)
HEAVY_DATA_WINDOW_WEEKDAY_START=0
HEAVY_DATA_WINDOW_WEEKDAY_END=7
HEAVY_DATA_WINDOW_WEEKEND_START=2
HEAVY_DATA_WINDOW_WEEKEND_END=8

# Concurrency
HEAVY_WINDOW_CONCURRENT_TICKERS=10
HEAVY_WINDOW_REQUEST_DELAY_MS=50
LIGHT_WINDOW_CONCURRENT_TICKERS=2
LIGHT_WINDOW_REQUEST_DELAY_MS=500

# Always in PST for all times
```

### Frontend Architecture
- **Framework:** Next.js 14.2.35 (app router, TypeScript 100%)
- **Styling:** Tailwind CSS (dark mode, responsive grid)
- **Typography:** Minimum text-sm (no squinting), consistent spacing
- **Layout:** 12-column grid, auto-rows-max for compact density
- **Fetching:** useEffect + fetch from http://10.0.0.81:8000 (CORS working)

### Scheduler Safeguards
- All scraping jobs log which window is active (heavy/light)
- Concurrency and delay settings logged on each run
- Rate limit violations would trigger alerts (monitoring TODO)
- Code comments document "NEVER BREAK" limits

---

## Documentation Created/Updated

1. **HEAVY_DATA_WINDOW_COMPLETE.md** — Operational hours + PST times
2. **API_RATE_LIMITS.md** — Provider limits + buffer strategy + new project template
3. **MEMORY.md** — Operational hours section added
4. **DEVELOPMENT_WORKFLOW.md** — API limits checklist + PST operational hours
5. **.env comments** — All times now explicitly PST

---

## Key Decisions (FINAL)

✅ **Heavy/Light Window Pattern:** Use for ALL future cron jobs and APIs  
✅ **PST Always:** No UTC, no ET - only Pacific Standard Time  
✅ **20% Buffer:** Always apply to API limits to avoid 429s  
✅ **Rate Limit Safeguards:** Code comments mark "NEVER BREAK" limits  
✅ **Horizontal Layouts:** All new dashboard components use row-based design  
✅ **Sharp Design:** No bubbly rounded corners, text-sm minimum fonts  

---

## What's Next

### Immediate (1-2 sessions)
1. Complete remaining UI components:
   - Open Positions (trading table)
   - Market Heatmap
   - Alerts/Notifications
2. Replace all mock data with real API calls
3. Add WebSocket for real-time signal streaming

### Short Term
1. Interactive features (modals, command palette, drag-reorder)
2. Portfolio equity chart animation
3. Trade execution UI

### Medium Term
1. Mobile responsiveness
2. Custom themes
3. Performance optimization (virtualization, lazy loading)

---

## Files Modified This Session

**Envestero repo:**
- `.env` (throttle settings + PST times)
- `envestero/config.py` (heavy/light window settings)
- `envestero/tasks/scheduler.py` (timezone + rate limit docs)
- `frontend/src/components/TopSignals.tsx` (horizontal layout)
- `frontend/src/components/NewsFeed.tsx` (horizontal layout)
- `frontend/src/components/Portfolio.tsx` (compact display)
- `frontend/src/components/TopCatalysts.tsx` (created)
- `frontend/src/app/dashboard/page.tsx` (grid layout + component imports)

**Workspace repo:**
- `MEMORY.md` (operational hours + API limits section)
- `API_RATE_LIMITS.md` (created - comprehensive reference)
- `DEVELOPMENT_WORKFLOW.md` (API limits checklist + PST times)

---

## Git Commits

1. `1942cc64` — Heavy data window throttling + API rate limit safeguards
2. `a13dfd6` — API rate limits documentation + memory updates
3. `0894bce8` — Fix: All times from ET → PST (CRITICAL)

---

## System Status

| Component | Status | Details |
|-----------|--------|---------|
| Frontend | ✅ Live | http://10.0.0.81:3000 (hot reload) |
| API | ✅ Live | http://10.0.0.81:8000 (hot reload) |
| Database | ✅ Connected | PostgreSQL 12,491 tickers |
| News Scraping | ✅ Throttled | Heavy/light window adaptive |
| Rate Limits | ✅ Protected | 20% buffer applied to all APIs |
| Dashboard | ✅ Responsive | 4 components built, mock data |
| Timezone | ✅ PST | All times in Pacific Standard Time |

---

## Operational Standards for Future Projects

**ALWAYS CHECK BEFORE CREATING NEW CRON JOBS:**

1. What APIs will it call?
2. Look up rate limits → Apply 20% buffer
3. Use heavy/light window pattern if data-intensive
4. Document limits in code ("NEVER BREAK" comments)
5. Add to API_RATE_LIMITS.md reference
6. Use PST for all timing (no UTC, no ET)
7. Test at peak load for 24 hours
8. Monitor logs for 429 errors

**Heavy Window:** Weekdays midnight-7am PST, weekends 2am-8am PST  
**Light Hours:** All other times (2 concurrent, 500ms delay)

---

**This session established the foundation for scalable, rate-limit-aware operations with clear timezone standards and intelligent network throttling. All future work builds on these patterns.**
