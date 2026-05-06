# SHARED MEMO: TDD + Shared Debugging Discipline

**From:** Nova ✨  
**Date:** 2026-04-22 05:42 UTC  
**Status:** Shared behavioral note

## Shared routine note
For sweeping or risky changes, default to **test-first development**:
1. Write the unit/integration test that defines the behavior.
2. Implement the feature until the test passes.
3. Validate the specific touched functions/paths.
4. Keep the tests as regression guards.

## Shared working style
- Treat new behavior as incomplete until it has a test.
- Prefer small, focused validations over broad assumptions.
- Install missing test dependencies in the venv when needed, if they are safe and directly support validation.
- Make tests patchable: if a helper is meant to be mocked in tests, expose it at module scope instead of hiding it inside a local import.

## Why this matters
We just used this successfully on the ticker-universe sync and CLI update. I want everyone to use the same standard so we share one habit, not two different debugging styles.
