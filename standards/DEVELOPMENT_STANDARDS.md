---
tier: 1
category: meta
tags: [principles, decision-drivers, standards]
status: foundational
created: 2026-04-24
last_updated: 2026-04-24
---

# Development Standards - Core Principles

Why we work the way we do. Decision drivers, not just rules.

---

## Principle 1: API First, Never Mock Data

**Statement:** APIs must exist before UI code. Never use mock data fallbacks.

**Why:** Mock data hides broken endpoints. You think the feature works, ship it, and it fails in production.

**Decision made:** 2026-04-24 (Envestero TopSignals hard experience)

**Impact:**
- Component returns error state when endpoint 404s
- Error is visible in UI, not hidden
- Forces us to build the backend endpoint first

**Example (Good):**
```tsx
if (error) return <p className="text-red-400">Error: {error}</p>;
```

**Example (Bad - don't do):**
```tsx
if (error) return <MockData />; // Hides the real problem
```

---

## Principle 2: Full Type Safety (No `any`)

**Statement:** 100% TypeScript typing. No `any` types.

**Why:** Type errors caught at dev time, not runtime. Prevents "Cannot read property X of undefined."

**Decision made:** Project inception

**Impact:**
- Slightly more upfront typing
- Zero runtime surprises
- Self-documenting code (types are documentation)

**Example (Good):**
```tsx
interface Signal {
  symbol: string;
  strength: number;
  timestamp: string;
}

const [signals, setSignals] = useState<Signal[]>([]);
```

**Example (Bad - don't do):**
```tsx
const [data, setData] = useState<any>([]);
```

---

## Principle 3: Error Handling is Not Optional

**Statement:** Every component must handle loading, error, and empty states.

**Why:** Real systems fail. Network timeout, 500 error, no data. UI must gracefully degrade.

**Decision made:** Project inception

**Impact:**
- Slightly longer component code
- Consistent error UX across dashboard
- Users understand what's happening

**Example (Good):**
```tsx
if (loading) return <p className="text-slate-400">Loading...</p>;
if (error) return <p className="text-red-400">Error: {error}</p>;
if (data.length === 0) return <p className="text-slate-400">No data</p>;
```

---

## Principle 4: Clear Contracts via Commits

**Statement:** Commit messages document the API/component contract.

**Why:** When code breaks 3 weeks later, the commit message tells you what was promised.

**Decision made:** 2026-04-24 (learned during wiring)

**Impact:**
- Easier debugging (know what the component expects)
- Easier collaboration (Kira can read commit and understand intent)
- Self-documenting codebase

**Example (Good commit):**
```
add+wire: TopSignals to /api/v1/signals

ENDPOINT:
- GET /api/v1/signals - lists recent signals
- Returns: {total, signals:[{symbol, signal_type, strength, reason, timestamp}]}
- Tested: curl returns 200

COMPONENT:
- Displays: symbol, signal type (BUY/SELL/HOLD), strength %
- Transforms: timestamp to locale time string
- States: loading, error, empty ✅
```

---

## Principle 5: Incremental Development (Small Steps)

**Statement:** Build → Test → Commit. One feature per commit, one component per session if possible.

**Why:** Smaller changes are easier to debug. If something breaks, you know exactly what caused it.

**Decision made:** 2026-04-24 (learned through back-and-forth loops)

**Impact:**
- More commits (good - easier to revert)
- Faster feedback loops (test after each step)
- Lower risk of large breaking changes

**Example (Good):**
```
Commit 1: add /api/v1/signals endpoint
Commit 2: wire TopSignals component
Commit 3: add signal reasoning display
```

**Example (Bad - don't do):**
```
Commit 1: add 5 new endpoints + 5 new components + styling + performance optimization
(If anything breaks, where's the bug?)
```

---

## Principle 6: Consistency Over Perfection

**Statement:** Same patterns everywhere. Patterns > perfect code.

**Why:** If every component works the same way, anyone can debug it. Consistency = maintainability.

**Decision made:** Project inception

**Impact:**
- All components use same fetch pattern
- All components use same error handling
- All components use same styling
- New developers can copy-paste structure

**Related standards:**
- COMPONENT_WORKFLOW.md - the pattern for all components
- STYLING_CONVENTIONS.md - same colors, spacing, typography everywhere

---

## Principle 7: Automation First (Not Manual Trading)

**Statement:** Dashboard surfaces automation decisions, not manual trading tools.

**Why:** Different mental model. Automation UI answers: "Did the system work?" Manual UI answers: "How do I trade?"

**Decision made:** 2026-04-24 (during mockup analysis)

**Impact:**
- Show signal reasoning, not news articles
- Show execution log, not order entry
- Show system status, not technical analysis tools
- Less clutter, more focus

**Examples (Automation Focus):**
- "BUY NVDA (87% strength) - Executed 5m ago" ✅
- "System Status: RUNNING | Last action: 5m ago" ✅
- "Capital deployed: $75K / $125K" ✅

**Examples (Manual Trading - we don't need):**
- News sentiment pie chart ❌
- Market catalysts section ❌
- Manual order entry form ❌
- Detailed technical analysis tools ❌

---

## Principle 8: Code Before Configuration

**Statement:** Hardcode in code first, only extract to config when needed.

**Why:** Configuration is easy to lose. Code is versioned. Start with code, move to config if you have multiple environments.

**Decision made:** Project inception (Envestero still mostly hardcoded, that's fine)

**Impact:**
- Simpler to start
- When ready to configure, extract gradually
- Git history shows why something moved to config

**Example (Good):**
```python
# In code (for now)
HEAVY_DATA_WINDOW_WEEKDAY_START = 0  # AM PST
```

(Later, extract to .env when you have prod/staging/dev)

---

## Principle 9: Questions Before Answers

**Statement:** When unclear, ask 1-3 focused questions. Don't guess.

**Why:** Guessing wastes time. Clear requirements = correct implementation.

**Decision made:** 2026-04-24 (learned through iteration)

**Impact:**
- Fewer rework cycles
- Clearer handoffs
- Faster consensus

**Example (Good):**
"Before I build the system status component:
1. Should it show system ON/OFF or detailed state (RUNNING/PAUSED/ERROR)?
2. How often should it refresh (real-time WebSocket or poll every 5s)?
3. Should alerts (e.g., max drawdown hit) show here or separate banner?"

**Example (Bad - don't do):**
(Guess, build something, it's wrong, rework)

---

## Principle 10: Memory for Sharing

**Statement:** Decisions and patterns live in shared memory, not project folders.

**Why:** Kira + you should follow the same patterns. Standards aren't per-project, they're per-team.

**Decision made:** 2026-04-24 (this session)

**Impact:**
- Shared standards = consistency across projects
- Easy to onboard new developers
- Standards evolve together (you + Kira feedback loop)
- Ready for MemoryGraph ingestion

**Related:**
- MEMORY_ORGANIZATION_ARCHITECTURE.md - how memory is structured
- workspace/standards/ - shared patterns
- project/.openclaw/ - project-specific quirks only

---

## Review & Update Process

**When:** Every 2 weeks or when a principle is questioned
**How:** You + Kira review, discuss, update if needed
**Where:** This file + related standards/
**Git:** Commit updates with rationale

**Example (next session):**
"Principle 7 (Automation First) needs refinement - we also want [X] from manual trading"
→ Update principle, discuss trade-offs, document new rule

---

## Quick Reference

| Principle | Quick Rule |
|-----------|-----------|
| #1 | Never mock data - API first |
| #2 | Full TypeScript - no `any` |
| #3 | Handle loading/error/empty states |
| #4 | Commit messages are contracts |
| #5 | Small incremental commits |
| #6 | Consistency over perfection |
| #7 | Automation focus, not manual trading |
| #8 | Code before configuration |
| #9 | Ask questions before guessing |
| #10 | Shared memory, not project-local |
