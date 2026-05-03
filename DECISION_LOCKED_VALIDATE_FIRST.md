# ✅ Decision Locked: Option B (Validate-First)

**Date:** 2026-04-21 06:49 UTC  
**Status:** Sequencing finalized, moving forward

---

## Your Decision

**Option B: Validate-First**

> "Validation reveals information for the next step. Doing it sequentially will reveal more information for the next step."

**Translation:** Each validation checkpoint gives us data to improve the next phase.

---

## What This Means

### Phase 1C.1: Executive Data (2-3h + 30-45 min validation)
**Build:** Collect exec data from SEC filings  
**Validate:** Verify completeness + accuracy before moving to Phase 1C.2  
**Reveals:** Is exec data clean enough to use in sentiment analysis?

### Phase 1C.2: Consumer Sentiment (3-4h + 30-45 min validation)
**Build:** Collect sentiment from Reddit, Twitter, Glassdoor  
**Validate:** Verify accuracy + thresholds before moving to Phase 1C.3  
**Reveals:** Is sentiment data clean enough for correlation analysis?

### Phase 1C.3: Influence Network (4-5h)
**Build:** Detect correlations between execs → sentiment → price  
**Use:** Clean validated data from both previous phases  
**Result:** High-confidence relationships, no cascading errors

---

## Timeline

| Phase | Build | Validate | Total |
|-------|-------|----------|-------|
| 1C.1 | 2-3h | 30-45 min | 2.5-3.5h |
| 1C.2 | 3-4h | 30-45 min | 3.5-4.5h |
| 1C.3 | 4-5h | Review | 4-5h |
| Scale + tests | — | 1h | 1h |
| **TOTAL** | 9-12h | 2h | **11-14h** |

---

## Validation Checkpoints

### ✅ After Phase 1C.1
- [ ] Each ticker has ≥3 executives
- [ ] Spot-check 5 execs against SEC filings (names, titles, dates correct)
- [ ] Career transitions captured (joins/exits with dates)
- [ ] No gaps in timeline

**If FAILS:** Fix missing data, revalidate  
**If PASSES:** Move to Phase 1C.2

### ✅ After Phase 1C.2
- [ ] Each ticker has ≥50 sentiment entries
- [ ] Manual accuracy check: 20 labels sampled, >80% correct
- [ ] Thresholds working: low-quality posts filtered out
- [ ] Categories meaningful: leadership/product/service distinct

**If FAILS:** Adjust thresholds, retrain, revalidate  
**If PASSES:** Move to Phase 1C.3

### ✅ After Phase 1C.3
- [ ] Each ticker shows ≥1 influence relationship
- [ ] Relationships make sense (not spurious)
- [ ] Confidence scores > 0.5
- [ ] Lag windows plausible (1-5 days)

**If OK:** Scale to all 20 tickers  
**If issues:** Refine correlation engine, retest

---

## What Gets Created

✅ **VALIDATE_FIRST_ROADMAP.md** (6.4 KB)
- Detailed implementation path with validation checklists
- Timelines, decision trees, failure paths
- In both workspace + memory-sync

✅ **DECISIONS.md** (updated)
- Sequencing decision locked: Option B
- Validation approach documented

✅ **NOVA.md** (updated)
- Toan's decision recorded
- Timeline updated (11-14h)
- Remaining questions listed

---

## Still Pending (3 More Decisions)

1. **Consumer Sources:** All 4 or Reddit MVP?
2. **Confidence Threshold:** r > 0.5, 0.6, or 0.7?
3. **5m Bars:** Fix now or defer?

Once you answer these, I can refine the implementation guide and we're ready to start Phase 1C.1.

---

## Ready to Begin?

When you're ready, I'll:
1. ✅ Update PHASE_1C_IMPLEMENTATION_GUIDE.md with validation checklists
2. ✅ Lock in remaining 3 decisions
3. ✅ Start Phase 1C.1 (Executive data collection)
4. ✅ Notify Kira so she can prepare for async collaboration

---

**Sequencing decision locked. 3 more decisions needed. Then we ship.** 🚀

---

**Updated:** 2026-04-21 06:49 UTC
