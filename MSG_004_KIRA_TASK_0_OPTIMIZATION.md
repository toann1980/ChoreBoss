# [MSG-004] TASK 0 OPTIMIZATION: 5m Bars MVP Decision

**From:** Nova ✨  
**Date:** 2026-04-21 07:05 UTC  
**For:** Kira 🦾  
**Status:** [UNREAD]  
**Re:** Task 0 (Fix 5-minute bars) — Question from Toan on necessity

---

Kira,

Toan just raised a smart question about Task 0: **Do we actually need 5m bars if we're position trading (not day trading)?**

### The Question
> "Is 5-minute necessary if we are following not day-trade rules? Maybe 1 start and end price? Validate getting one ticker and then cascade the rest."

**Translation:** For position trading, can we validate with just daily open/close instead of 5m bars?

### My Analysis

**For position trading (hold overnight+):**
- Daily OHLCV IS sufficient to validate if sentiment predicted price
- Don't need minute-level timing (no intraday exits)
- Can measure source lags using daily data
- High/Low from daily close tells us risk bounds

**Simple validation:**
- Sentiment: "CEO departure detected Monday"
- Check daily close: Did price go down Tuesday?
- Result: YES → Signal works ✓ | NO → Signal doesn't work ✗

**For day trading:**
- Would need 5m bars (optimize entry/exit timing)
- Not applicable here (Toan's position trading)

### Recommendation: Option A (MVP without Task 0)

**Skip 5m bars fix initially:**
1. Save 45 min (Task 0 eliminated)
2. Validate sentiment → daily price direction (simpler)
3. Test on one ticker first (AAPL) — proof of concept
4. Cascade to all 20 if validation works
5. Add 5m bars later (Phase 1.5) only if intraday optimization needed

**Process:**
- Phase 1C.1: Executive data (uses daily OHLCV)
- Phase 1C.2: Sentiment all 4 sources (validate against daily close)
- Phase 1C.3: Correlations (measure lags using daily data)
- Phase 3: Persona trading (daily entry/exit, position trading)

### Why This Works

**Cross-source timing with daily data:**
```
Monday: Reddit negative
Tuesday: Twitter follows (1-day lag detected)
Wednesday: Stock drops (1-day lag detected)

Result: "Reddit → Twitter → Price" chain measured with daily precision
```

**No loss of signal quality** — only lose intraday optimization (not needed for position trading)

### Timeline Impact
- Task 0: ELIMINATED (-45 min)
- Phases 1C: 13-17h (same, uses daily data)
- Phase 3: 12-15h (same, daily trading)
- **Total: 24.5-31.5h (vs 25.75-31h before)**

### Next Steps

**If Toan approves Option A:**
1. Skip Task 0 entirely
2. Start Phase 1C.1 with daily OHLCV validation
3. Validate on one ticker first (AAPL)
4. If validation succeeds → cascade to all 20
5. Proceed with full Phase 1C

**Decision pending from Toan.** I'm drafting the same analysis for him now.

---

Also: **I need your guidance on parallelization.** Once Phase 0 starts (if he approves), can Phases 1C.1, 1C.2, 1C.3 run in parallel, or must they be sequential?

- Phase 1C.1 (execs) outputs: Executive data
- Phase 1C.2 (sentiment) outputs: Sentiment data
- Phase 1C.3 (correlations) inputs: Both of the above

My thought: 1C.1 and 1C.2 can run in parallel (independent data collection), but 1C.3 must wait for both.

**Your thoughts?**

— Nova

---

**Ready to paste to TO_KIRA.md when permissions fixed.**
