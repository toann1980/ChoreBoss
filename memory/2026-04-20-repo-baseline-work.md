# Repo Baseline & Copilot Instructions — 2026-04-20

## Summary of Work Done

Created comprehensive baseline for all 5 repos at `/srv/github/`:

### Files Created in Memory
- `memory/project-blendcraft.md` — 47 py files, 505M (asset bloat), CI mature, garment pipelines
- `memory/project-choreboss.md` — 37 py files, 11M, Flask + SQLAlchemy, stable
- `memory/project-envestero.md` — 76 py files, 11M, stock signals v2, async + TimescaleDB, Python 3.13
- `memory/project-househunter.md` — 8 py files, 1.9M, early-stage real estate search, v2 refactor in progress
- `memory/project-imageforge3d.md` — 17 py files, 1.3M, Blender→AI pipeline, WebSocket relay, production-ready
- `memory/repo-improvement-analysis.md` — Full per-repo issues, priorities, quick wins

### Files Created in Workspace
- `workspace/copilot-instructions.md` — Nova's universal standards across all 5 repos

### Files Created in Each Repo (`.copilot/copilot-instructions.md`)
- **BlendCraft** — Architecture, core/pipeline split, bpy conventions, test commands
- **ChoreBoss** — Data model tables, **3 bugs called out**, 3-layer pattern rules
- **Envestero** — Security alert (`.google-cookie` in repo), critical rules, dev patterns
- **HouseHunter** — Hardcoded IP fix, config via env, test bootstrap
- **ImageForge3D** — WebSocket format, relay arch, startup sequence, references `.github/` for detail

---

## ChoreBoss Setup Complete

### Bugs Fixed (3 data-corruption issues)
✅ `Chore.validate_id` — added missing `return value` (was silently setting id=None on every insert)
✅ `People.validate_birthday` — fixed error message ("must be a datetime.date object" not "string")
✅ `Chore.validate_description` — fixed constraint message (10-500 not 20-500)

### Quick Start Guide Created
- `QUICKSTART.md` in /srv/github/ChoreBoss/ with Docker setup (recommended)
- Persistent data volume config included
- Family usage tips and PIN setup instructions
- Fallback Python local dev instructions

### Recommendation
**Use Docker** — Stable, isolated, easy for family members on different machines later
```bash
cd /srv/github/ChoreBoss
docker-compose up --build
# Browse to http://localhost:8055
```

---

## Copilot Instructions Strategy

All 5 repos now have `.copilot/copilot-instructions.md` (IDE-accessible):
- **BlendCraft**: Asset bloat warning, public API facade needed, z_legacy cleanup
- **ChoreBoss**: 3 bugs front-loaded (now fixed), 3-layer pattern rules
- **Envestero**: `.google-cookie` security alert, TradeSignal contract guarantee
- **HouseHunter**: Hardcoded IP / path hack callouts, env-var config pattern
- **ImageForge3D**: WebSocket format reference, relay architecture, test gap

Also created in workspace root: `copilot-instructions.md` (universal standards for all)
