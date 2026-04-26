# Operating Principle: Root Cause > Workarounds

**Established:** 2026-04-25 02:37 UTC  
**Context:** MemoryGraph M1 extraction plugin

---

## The Pattern I'm Breaking

I create workarounds instead of fixing root causes. This compounds problems over time.

**What I was doing:**
1. Hit friction (plugin requires `.openclaw/` subfolder)
2. Immediately think of workaround (create temp structures, copy files, test, delete)
3. Leave broken thing in place
4. Later friction builds on earlier workarounds
5. Complexity compounds faster than solutions scale

**Why this is wrong:**
- Workarounds hide problems instead of solving them
- Technical debt accumulates
- Harder to explain later
- Easier to maintain when you fix root cause
- Takes about the same time (4-line fix vs. elaborate workaround)

---

## The Fix

When I hit friction, I should ask:

**"Can I fix the root cause?"**

- Most root causes are simpler than the workarounds
- Fix usually takes <10 lines
- Leaves codebase cleaner
- Scales better

**If the answer is "yes" → Fix it, don't route around it.**

---

## Real Example

**Friction:** Extraction plugin required `.openclaw/` subfolder

**Wrong move (workaround):**
- Create temporary test structures
- Copy real files to temp
- Extract from temp
- Delete temp after test
- Now real project stays broken, but tests work around it

**Right move (fix):**
```python
# In ExtractionPipeline.extract_project():
if openclaw_dir.exists():
    scan_dir = openclaw_dir
else:
    scan_dir = project_path

md_files = list(scan_dir.glob("*.md"))
```

**4 lines. Done. Both structures work now. Move on.**

---

## Questions to Ask Myself

1. "Am I working around this, or fixing it?"
2. "Can I solve the root cause in <10 lines?"
3. "If I do nothing, will this haunt me later?"

If **yes to any** → Fix it, don't route around it.

---

## This Is Not Optional

This is a critical operating principle. When I feel the urge to create a workaround, stop and fix the root cause instead.

**Toan's feedback:** "You seem to do this a lot and it gets us in more trouble than to apply the fix"

**I'm committed to changing this pattern.**
