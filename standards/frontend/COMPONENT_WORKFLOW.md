---
tier: 2
category: frontend
tags: [components, react, development, testing, typescript]
related_standards: [STYLING_CONVENTIONS, ERROR_HANDLING, STATE_MANAGEMENT]
status: stable
created: 2026-04-24
last_updated: 2026-04-24
---

# Component Development Workflow

Safe, repeatable process for building dashboard components without debugging loops.

## Phase 1: Validate API First (5 min)

**Before touching UI code:**

```bash
# 1. Test endpoint exists and returns expected data
curl -s http://10.0.0.81:8000/api/v1/your-endpoint | jq .

# 2. Check response structure
# - What fields exist?
# - What's the type of each field? (string, number, array, object)
# - Is pagination needed?
# - Are there nullable fields?

# 3. Document the contract
# - Save response shape as comment in component
# - Note any transformations needed (date parsing, number formatting)
```

**Endpoint doesn't exist?** → Build it now, don't hardcode empty state

```bash
# Add to appropriate router (signals.py, news.py, etc.)
# Test immediately
# Commit separately from component
```

---

## Phase 2: Component Structure (10 min)

**Template (TypeScript safe):**

```typescript
'use client';

import { useEffect, useState } from 'react';

interface DataItem {
  // Copy from API response
  field1: string;
  field2: number;
  // ... all fields typed
}

export default function ComponentName() {
  const [data, setData] = useState<DataItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await fetch('http://10.0.0.81:8000/api/v1/endpoint');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        
        // Transform if needed (e.g., wrap in .data or .items)
        setData(Array.isArray(json.items) ? json.items : []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown');
      } finally {
        setLoading(false);
      }
    };
    
    fetch();
  }, []);

  // No inline fetch URLs - use constants at top if you have multiple
  // No useState for URL building - that's a code smell
  
  if (loading) return <p className="text-slate-400 text-sm">Loading...</p>;
  if (error) return <p className="text-red-400 text-sm">Error: {error}</p>;
  if (data.length === 0) return <p className="text-slate-400 text-sm">No data</p>;

  return (
    <div className="space-y-0.5">
      {data.map((item) => (
        <div key={item.id} className="flex items-center gap-2 border-b border-slate-700/30 py-1 px-1">
          {/* Map fields to UI */}
        </div>
      ))}
    </div>
  );
}
```

**Rules:**
- Full TypeScript - no `any`
- Always handle loading/error/empty states
- No mock data fallbacks (show real error if API fails)
- URL goes in one place (top of component or env)
- `useEffect` with empty dependency array (fetch once on mount)

---

## Phase 3: Incremental Testing (5 min)

**Before showing UI:**

1. **API call validated?** → Yes ✅
2. **Type definitions match API response?** → Grep response for each field
3. **Transformations correct?** (date parsing, null handling)
4. **Empty state tested?** (what if API returns `[]`?)
5. **Error state tested?** (what if API returns 500?)

**Testing checklist:**

```bash
# In component code, add inline test (temp):
console.log('Fetched data:', json); // See raw response
console.log('Mapped data:', data);  // See transformed data

# Refresh browser
# Check console for both logs
# Remove logs before committing
```

---

## Phase 4: UI Layout (10 min)

**Constraints (current design):**
- Horizontal single-row layout (no vertical stacking)
- Flex items fit in viewport at 100% zoom
- text-sm minimum (no text-xs)
- Spacing: gap-2, py-1, px-1 (compact)
- Border radius: minimal (sharp aesthetic)
- Icons: emoji only, no custom SVG

**Layout template:**

```tsx
<div className="flex items-center gap-2 border-b border-slate-700/30 py-1 px-1">
  {/* Icon */}
  <span className="text-base flex-shrink-0">📊</span>
  
  {/* Primary (flex-1 = takes remaining space) */}
  <div className="font-semibold text-slate-100 text-sm flex-shrink-0 w-12">Label</div>
  
  {/* Secondary (fixed width) */}
  <div className="text-sm text-slate-400 flex-shrink-0 w-20">Value</div>
  
  {/* Tertiary (fixed width) */}
  <div className="text-sm text-slate-500 flex-shrink-0 w-14">Detail</div>
</div>
```

**Color coding:**
- Green: positive/bullish (`text-green-400`)
- Red: negative/bearish (`text-red-400`)
- Yellow: warning/neutral (`text-yellow-400`)
- Blue: info (`text-blue-400`)
- Slate: neutral text (`text-slate-400`, `text-slate-500`)

---

## Phase 5: Commit & Hand Off (2 min)

**Commit message format:**

```
add+wire: ComponentName to /api/v1/endpoint

ENDPOINT:
- GET /api/v1/endpoint - description
- Returns: {shape}
- Tested: curl returns 200 with {example}

COMPONENT:
- Displays: [fields]
- Transforms: [any data transformations]
- States: loading, error, empty ✅

Ready for UI validation (no errors expected).
```

**Hand off checklist:**
- [ ] Endpoint tested with curl
- [ ] Component has no console errors
- [ ] All data fields typed
- [ ] Loading/error/empty states handled
- [ ] No hardcoded mock data
- [ ] Commit message explains contract

---

## Why This Works

1. **API first** - validates endpoint before code
2. **Type safety** - catch mismatches early
3. **No debugging loops** - issues caught before UI
4. **Clear contract** - commit documents what's expected
5. **Repeatable** - same steps every time, same result

---

## Common Mistakes (Don't Do These)

❌ Build component before endpoint exists → endpoint doesn't exist, component shows "no data"
❌ Use `any` types → type mismatches at runtime
❌ Hardcode mock data → hides real errors
❌ Stack components vertically → doesn't fit viewport
❌ Use text-xs → can't read on dashboards
❌ Forget empty state handling → "Cannot read property X of undefined"
❌ Put URL in multiple places → inconsistent endpoints
❌ Fetch on every render → infinite API calls

---

## Estimated Time per Component

- Validate endpoint: 5 min
- Build component: 10 min
- Test + debug: 5 min
- Commit: 2 min
- **Total: 22 min per component** (no back-and-forth)

Currently: 6 components × 22 min = ~2 hours to full dashboard
