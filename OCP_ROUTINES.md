# OCP Shared Routines

These routines are team-wide. They are not Nova-specific or Kira-specific.
Use them whenever you are working in OCP or making cross-project decisions.

---

## 1) Session Start Routine

Before touching a project:
1. Read the project `START_HERE.md`.
2. Read `CURRENT.md` or `CURRENT_STATUS.md`.
3. Read any project operating procedures.
4. Read the project-local `.openclaw/` notes, if present.
5. Check workspace notes and memory only for relevant context.

## 2) Development / Testing Routine

For any dev or OCP work:
1. Confirm the current state and constraints.
2. Write a short plan before executing multi-step changes.
3. Follow the documented procedure exactly.
4. Record the exact files, paths, ports, models, or components involved.
5. Update `CURRENT.md` when the work lands.

## 3) Documentation Verification Routine

Use before notifying someone about a meaningful change:
1. Audit what changed.
2. Verify each item is documented in the right place.
3. Fix any gaps immediately.
4. Create a receipt or summary if the change is coordination-heavy.
5. Only then notify stakeholders.

## 4) Shared TDD / Debugging Routine

For risky or sweeping changes:
1. Write the test or validation first.
2. Implement the smallest change that satisfies it.
3. Validate the touched path directly.
4. Keep the test as a regression guard.
5. Prefer small, targeted checks over broad assumptions.

## 5) Session Close Routine

Before ending a session:
1. Update the project `CURRENT.md`.
2. Save any durable notes to the right memory file.
3. Sync shared notes if the work affects other agents.
4. Commit significant workspace changes.
5. Leave the next step obvious.

---

## Quick Rule

If a routine feels persona-specific, rewrite it until any agent on the team can use it.
