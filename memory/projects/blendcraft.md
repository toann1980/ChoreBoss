# BlendCraft — Project Detail

**Alias:** BC
**Location:** `/home/tron/app/BlendCraft`
**Purpose:** Python library that streamlines `bpy` (Blender's Python API) for automation — garment asset creation, thumbnail rendering, material assignment, lighting rigs.
**Status:** Stable (was wonky before Kira stabilized it). CI/CD in progress.
**Branch convention:** development → main

## Package Structure

**core/** — Low-level bpy wrappers
- bpy_object: Object transforms (dimensions, move, rotate, scale)
- camera: Camera creation, framing, positioning
- compositor: Compositor node setup
- constants: Enums (PBRMapType, LightType, RenderEngine, FileFormat, etc.)
- constraints: Object constraint helpers
- light: Light creation and management
- mesh: Mesh import, auto-smooth
- render: Render resolution, engine settings
- scene: Scene reset, load/save blend, unit system, view transform
- texture: Texture loading, dictionary building
- uv: UV operations
- utilities: Logger

**pipeline/** — High-level workflows
- automatron: Automation orchestration
- clo3d: CLO3D GLB import pipeline
- image: Image processing
- lighting: create_three_point_lighting()
- thumbnail: render_all_thumbnails(), check_dimensions()

**Other:**
- library/: Asset library helpers
- tools/: run_headless_tests.py (Blender headless integration test runner)
- z_legacy/: Old code, kept for reference

## Dependencies (current: bpy 4.2.0)

- `bpy==4.2.0` — Blender Python API
- `numpy==2.0.0`, `pillow==10.4.0`
- `getfiles` — custom lib from github.com/toann1980/GetFiles
- `pytest`, `pytest-cov`, `mypy`, `flake8`

## Test Architecture

Two completely separate test tiers:

### Unit Tests (`tests/unit/`)
- Run with **Python only** — no Blender needed
- `conftest.py` mocks entire `bpy` module tree with `MagicMock` + typed dummy classes
- Run: `PYTHONPATH=. pytest tests/unit --cov=blendcraft`
- Covers: bpy_object, camera, constants, image, imports, mesh, render, scene, utilities

### Integration Tests (`tests/integration/`)
- Run **inside Blender headless** via `tools/run_headless_tests.py`
- Uses real `bpy` context, actual `.blend` files
- Run: `blender --background --python tools/run_headless_tests.py`
- Golden test folders in `tests/golden/`:
 - INV001M001_CREW-FITTED
 - INV001M002_CREW-FITTED-POCKET
 - Nike_M_Longsleeve_Slim

## CI/CD (`.github/workflows/`)

- `unit-tests.yml` — Python 3.11, pytest with coverage, uploads to Codecov
- `integration-tests.yml` — Python 3.11, downloads Blender 4.2.0, runs headless via xvfb
- `lint.yml` — mypy + flake8

## Known Issues / State

- `.venv` uses Python 3.11; pytest not always installed in venv (install with `pip install pytest pytest-cov` if needed)
- `blendcraft_eval.py` — dev eval script with hardcoded Windows paths (`L:\Assets\...`) — not for CI, local testing only

## Pending Work

**bpy 5.x upgrade** — planned but not started. Breaking change risk:
- `bpy.types` API changes expected
- Unit test mocks in `conftest.py` will need updating
- Integration CI workflow will need Blender 5.x download step
- Golden tests may need new reference renders
- Strategy: upgrade on a branch, run full test suite, compare golden outputs

CI/CD process still being established (good progress made 2026-04-17).