# HouseHunter - Project Baseline

**Status:** Early-stage | **Size:** 1.9M | **Files:** 8 Python files

## Overview
Real estate search and analysis tool. Frontend + API backend architecture for property hunting workflows.

## Structure
```
HouseHunter/
├── api/                 # Backend API (likely FastAPI or Flask)
├── frontend/            # Frontend application
└── .gitignore
```

## Recent Commits (Latest 5)
1. `45acfa6` - frontend merged
2. `fbac843` - Moved to subfolder to accommodate frontend
3. `9e13323` - v2_app, modularized
4. `8204464` - v1_standalone
5. `2529041` - Initial commit

## Tech Stack
- **Architecture:** Separate api/ and frontend/ folders
- **Status:** Early iteration (v1 → v2 refactor visible in history)
- **Focus:** Modularization (moved to subfolder for frontend)

## Key Insights
- **Minimal codebase:** Only 8 Python files (~1.9M total)
- **Recent refactor:** Frontend integration (commit `45acfa6`)
- **Modularity push:** v2 app refactor with clearer separation
- **Early-stage:** No Docker config, minimal documentation observed

## Toan's Role
Personal real estate research tool.

## Unknowns
- [ ] What data sources (Zillow, Redfin, local APIs)?
- [ ] Frontend framework (React, Vue, vanilla JS)?
- [ ] Current feature set & maturity level?
- [ ] Integration status (api ↔ frontend)?

## Next Steps
- [ ] Review api/ structure (REST endpoints, data models)
- [ ] Check frontend/ tech stack
- [ ] Assess data pipeline & search logic
