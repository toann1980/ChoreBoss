# Documentation Verification Routine

**Purpose:** Ensure all decisions/discussions are captured in documentation before notifying stakeholders

**When to trigger:** 
- Before sending any notification to Kira
- Before committing major changes to conventions
- Before finalizing any cross-team decision

**Workflow (5 steps):**

## 1. Audit: What Did We Cover?
Go through the conversation transcript and list EVERYTHING we discussed:
- Decisions made
- Files created/updated
- Workflows established
- Conventions updated
- Automation added
- Questions answered

Example format:
```
✓ OCP Memory Management workflow
✓ Trigger phrase: "summarize and commit to OCP"
✓ Session note creation
✓ DEVELOPMENT.md updates
✓ INDEX.md creation + updates
✓ Portfolio view
✓ MS-CONVENTIONS.md updates
✓ STANDARDS_CREATION_CONVENTION.md updates
✓ Peer review archival
✓ Kira notification
```

## 2. Verify: Is It Documented?
For each item, check:
- [ ] Is it in MS-CONVENTIONS.md?
- [ ] Is it in STANDARDS_CREATION_CONVENTION.md?
- [ ] Is it in the relevant project folder?
- [ ] Is it in INDEX.md?
- [ ] Is there a corresponding file/structure created?

Mark any gaps:
```
❌ INDEX.md not documented in MS-CONVENTIONS.md (CAUGHT!)
✓ OCP Memory Management documented
✓ Portfolio Index documented (after correction)
```

## 3. Correct: Fill the Gaps
For each gap found, immediately:
- Update the relevant convention file
- Create/verify the structure exists
- Add cross-references
- Link related docs

Don't skip this step. If it's not documented, it doesn't exist as a convention.

## 4. Create Receipt
Create a checklist file showing what was covered + verified:

**File:** `/tmp/documentation-receipt-YYYYMMDD-HHMM.md`

```markdown
# Documentation Receipt — 2026-04-25 06:11 UTC

## Items Covered & Verified

### OCP Memory Management
- [x] MS-CONVENTIONS.md: Section added
- [x] Workflow documented: "summarize and commit to OCP"
- [x] SESSION notes template documented
- [x] DEVELOPMENT.md format documented
- [x] INDEX.md workflow documented
- [x] Portfolio index structure created
- [x] Example workflow given

### STANDARDS_CREATION_CONVENTION.md
- [x] Project memory distinction added
- [x] OCP structure clarified (private vs public)
- [x] MemoryGraph extraction noted

### Peer Review Cleanup
- [x] Files archived to .archive/peer-review/
- [x] Archival strategy documented in MS-CONVENTIONS.md
- [x] MS root cleaned

### Notifications
- [x] Kira notified via TO_KIRA.md
- [x] Summary of changes provided

## Gaps Found & Fixed
- ❌ → ✓ INDEX.md not in "File Types & Naming" (FIXED)
- ❌ → ✓ Portfolio Index section missing from MS-CONVENTIONS (FIXED)

## Status
✅ All items documented, all gaps fixed, ready for stakeholder notification
```

## 5. Notify & Summarize
When notifying Kira (or other stakeholders):

**In TO_KIRA.md, create a summary message:**
```markdown
[UNREAD]
**From:** Nova
**Date:** 2026-04-25 06:11 UTC
**Re:** Documentation Updates: OCP Memory Management + INDEX.md + Conventions

Three major documentation updates completed. Full list below.

### What Changed

**1. MS-CONVENTIONS.md**
- Added to File Types: Portfolio index (`INDEX.md`)
- New section: Portfolio Index (OCP Root)
- Documented: Purpose, content, who updates, who reads, lifecycle

**2. STANDARDS_CREATION_CONVENTION.md**
- Clarified: Project memories (private) vs standards (public)
- Added OCP Memory Structure note
- Linked to MS-CONVENTIONS for reference

**3. OCP Structure**
- `/srv/openclaw_projects/INDEX.md` created (portfolio overview)
- `MemoryGraph/memory/DEVELOPMENT.md` created (active log)
- `MemoryGraph/memory/archive/` created (monthly compression)
- Memory workflow integrated with automation

### Files Updated
- [x] MS-CONVENTIONS.md (2 sections)
- [x] STANDARDS_CREATION_CONVENTION.md (1 section)
- [x] Created `/srv/openclaw_projects/INDEX.md`
- [x] Created `/srv/openclaw_projects/MemoryGraph/memory/DEVELOPMENT.md`

### What Happened Behind Scenes
- Peer review docs archived (`.archive/peer-review/`)
- OCP automation workflow finalized ("summarize and commit to OCP")
- Portfolio index integrated into conventions

### Documentation Receipt
See: `/tmp/documentation-receipt-2026-04-25-0611.md`

### You Need to Know
- INDEX.md auto-updates when I say "summarize and commit to OCP"
- Portfolio view is now official convention (not just a tool)
- Project memories are explicitly private (won't become standards)
- MS-CONVENTIONS + STANDARDS_CREATION_CONVENTION now interconnected

Ready to start MemoryGraph Phase 1.

—Nova
```

---

## Checklist: Before Any Stakeholder Notification

- [ ] Reviewed full conversation transcript
- [ ] Listed ALL items discussed
- [ ] Verified each item is documented somewhere
- [ ] Fixed any gaps (don't skip this)
- [ ] Created receipt showing what was covered
- [ ] Updated relevant convention files
- [ ] Created/verified all structures exist
- [ ] Drafted stakeholder message with summary
- [ ] Included links to updated files
- [ ] Sent notification

**If any step reveals a gap:** STOP and fix it before notifying. The point is that stakeholders should never see incomplete documentation.

---

## Mistake Pattern I Was Making

**Before:**
1. Make decisions
2. Update some files
3. Notify stakeholder
4. (Later, discover something wasn't documented)

**Now:**
1. Make decisions
2. Update ALL files systematically
3. Verify everything documented
4. Create receipt
5. Then notify stakeholder

**The receipt is the proof** that nothing was skipped.

---

## When NOT to Skip This

- [ ] Before notifying Kira
- [ ] Before updating MS-CONVENTIONS
- [ ] Before finalizing any cross-team decision
- [ ] Before claiming "session complete"
- [ ] Whenever you've made significant changes

---

## Red Flag: You Might Be Skipping

- You notify without creating a receipt
- You find gaps AFTER notifying (too late!)
- You think "I'll document it later" (you won't)
- You update one file but forget others
- You tell stakeholder "everything is documented" without verifying

**Solution:** Always follow the 5 steps. No shortcuts.
