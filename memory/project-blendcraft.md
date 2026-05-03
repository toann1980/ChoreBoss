# BlendCraft - Project Baseline

**Status:** Active | **Size:** 505M | **Files:** 47 Python files

## Overview
Streamline BPY for Blender — a Python library designed to simplify and abstract common Blender API (bpy) patterns. Builds automation-first tooling for 3D asset creation workflows.

## Structure
```
BlendCraft/
├── blendcraft/          # Main library package
├── BlendCraft/          # Additional package folder
├── library/             # Shared libraries
├── tests/               # Unit + integration tests
├── tools/               # Development utilities
├── Docs/                # Documentation
├── z_legacy/            # Deprecated code
├── requirements.txt
├── .gitignore (3172 bytes)
├── .github/             # CI/CD workflows
├── copilot-instructions.md
├── blendcraft_eval.py   # Evaluation script
└── automatron_eval.py   # Automation testing
```

## Recent Commits (Latest 5)
1. `178cd1d` - fix: simplify Python setup in CI workflows by removing version matrix
2. `4dae9cf` - fix: format branch lists in integration tests workflow
3. `8fd1699` - Add integration tests for asset comparison of images and mesh files
4. `328fe69` - test(unit): Full Blender API type mocking for Python-only tests
5. `362dc28` - feat: add unit tests and CI/CD instructions for BlendCraft

## Tech Stack
- **Language:** Python
- **Target:** Blender 4.x (bpy)
- **Testing:** Unit + Integration (pytest-style)
- **CI/CD:** GitHub Actions

## Key Insights
- **Well-tested:** Has unit tests with Blender API mocking, integration test suite
- **Documentation:** copilot-instructions.md suggests AI/codex integration
- **Maturity:** CI/CD setup recent; actively refining test infrastructure
- **Scope:** Large (505M) — likely includes Blender binaries or asset samples

## Toan's Role
Core project — streamlines bpy for automation service. Complements garment creation goals.

## Next Steps
- [ ] Review test coverage depth
- [ ] Check integration test scope (asset comparison types)
- [ ] Understand library abstractions (what patterns simplified?)
