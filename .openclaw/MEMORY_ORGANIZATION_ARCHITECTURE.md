# Memory Organization Architecture

## Goal
Structure project standards + knowledge so they:
1. Are shared between you + Kira (workspace-level, not project-local)
2. Can be ingested by MemoryGraph later (queryable entities/relationships)
3. Avoid polluting project folders
4. Stay human-readable now, machine-queryable later

---

## Proposed Folder Structure

```
/home/leto/.openclaw/workspace/
│
├── MEMORY.md                          # Tier 0: Quick pointers only
│
├── memory/
│   ├── YYYY-MM-DD.md                 # Raw daily notes (discovery phase)
│   └── ...
│
├── standards/                         # ← NEW: Shared knowledge base
│   │
│   ├── DEVELOPMENT_STANDARDS.md      # Tier 1: Principles & decision drivers
│   │                                  # (Meta-level: why these standards exist)
│   │
│   ├── frontend/                      # Tier 2: Detailed workflows
│   │   ├── COMPONENT_WORKFLOW.md      # 5-phase component development
│   │   ├── STYLING_CONVENTIONS.md     # Color, spacing, typography rules
│   │   ├── STATE_MANAGEMENT.md        # React hooks patterns
│   │   └── ERROR_HANDLING.md          # How we display errors
│   │
│   ├── backend/                       # Tier 2: Server-side workflows
│   │   ├── ENDPOINT_WORKFLOW.md       # Schema → route → test process
│   │   ├── DATABASE_WORKFLOW.md       # Migrations, seeding, queries
│   │   └── FASTAPI_PATTERNS.md        # Router, dependency injection, typing
│   │
│   ├── devops/                        # Tier 2: Infrastructure workflows
│   │   ├── DOCKER_PATTERNS.md         # Dockerfile, compose standards
│   │   ├── NGINX_PATTERNS.md          # Reverse proxy, static files
│   │   └── DEPLOYMENT_WORKFLOW.md     # Build → test → deploy process
│   │
│   ├── git/                           # Tier 2: Version control
│   │   ├── COMMIT_STANDARDS.md        # Message format, what to commit
│   │   └── BRANCHING_STRATEGY.md      # Branch naming, PR workflow
│   │
│   └── catalog.json                   # Machine-readable index
│                                      # (Used by MemoryGraph later)
│
├── knowledge-graph/                   # ← NEW: MemoryGraph staging (future)
│   ├── entities.json                  # Extracted standards as entities
│   ├── relationships.json             # Links between concepts
│   └── README.md                      # How to ingest this into MemoryGraph
│
└── projects/
    ├── envestero/
    │   └── .openclaw/ENVESTERO_SPECIFIC.md  # Tier 3: Project quirks only
    │
    └── ...
```

---

## Four-Tier Memory Flow

### **Tier 0: Discovery & Raw Learning**
**Location:** `memory/YYYY-MM-DD.md`
**What:** Daily session notes, experiments, "I learned X today"
**Audience:** You + me (working notes)
**Lifespan:** Transient (kept for 30 days, then archived)
**Example:**
```md
# 2026-04-24 - Dashboard Development

Tried hardcoding mock data in TopSignals → hides 404 errors
→ Decision: Never use mock data fallbacks (Tier 1 rule now)

API endpoint design: Should paginate or not?
→ Tested both, pagination better for large datasets
```

---

### **Tier 1: Consensus & Validated Standards**
**Location:** `standards/DEVELOPMENT_STANDARDS.md`
**What:** Principles, decision drivers, "why we do it this way"
**Audience:** Shared with Kira (reference guide)
**Lifespan:** Permanent, versioned
**Example:**
```md
# Core Principles

## No Mock Data Fallbacks
**Why:** Mock data hides broken endpoints
**When:** Always - even "graceful empty state" is better
**Impact:** Requires API endpoints to exist before UI
**Decision Date:** 2026-04-24 (learned through pain)

## Full Type Safety
**Why:** TypeScript catches mismatches at dev time, not runtime
**When:** Every component, every API call
**Impact:** More upfront typing, zero runtime surprises
```

---

### **Tier 2: Detailed Workflows & Processes**
**Location:** `standards/{frontend,backend,devops,git}/...`
**What:** Step-by-step HOW-TO guides, checklists
**Audience:** Shared with Kira (how we work)
**Lifespan:** Updated when process changes
**Example:** `standards/frontend/COMPONENT_WORKFLOW.md` (what we just created)
```md
# Component Development Workflow

Phase 1: Validate API First (5 min)
- [ ] Test endpoint: curl -s http://...
- [ ] Check response structure
- [ ] Document contract

...
```

---

### **Tier 3: Project-Specific Exceptions**
**Location:** `.openclaw/ENVESTERO_SPECIFIC.md` (in project)
**What:** Deviations from standards, quirks, special handling
**Audience:** Team members working on this project
**Lifespan:** Project lifespan
**Example:**
```md
# Envestero Specifics

## Timezone Standard: PST Only
**Standard:** Use user's local timezone
**Envestero:** Always PST (America/Los_Angeles)
**Why:** Crypto markets, international teams, scheduler precision
**Impact:** All times hardcoded as PST, no UTC/ET

## Database Auth Issue
**Standard:** Migrations auto-run on startup
**Envestero:** Manual migration required (signal_events service disabled)
**Why:** Async auth issues, will fix in next session
```

---

### **Tier 4: Machine-Queryable Knowledge Graph (Future)**
**Location:** `knowledge-graph/{entities,relationships,metadata}.json`
**What:** MemoryGraph-ready structured data
**Audience:** MemoryGraph ingestion pipeline
**Lifespan:** Generated/updated when standards change
**Example:**
```json
{
  "entities": [
    {
      "id": "component-workflow",
      "type": "workflow",
      "title": "Component Development Workflow",
      "category": "frontend",
      "tier": 2,
      "file": "standards/frontend/COMPONENT_WORKFLOW.md",
      "created": "2026-04-24",
      "last_updated": "2026-04-24",
      "status": "stable",
      "keywords": ["component", "react", "development", "testing"]
    }
  ],
  "relationships": [
    {
      "source": "component-workflow",
      "target": "error-handling",
      "relationship": "requires",
      "description": "Components must use documented error states"
    }
  ]
}
```

---

## Implementation Strategy

### Right Now (Next 30 minutes)
1. Create `standards/` folder structure
2. Move COMPONENT_DEVELOPMENT_WORKFLOW.md → `standards/frontend/COMPONENT_WORKFLOW.md`
3. Create `standards/DEVELOPMENT_STANDARDS.md` with core principles
4. Create `standards/catalog.json` (hand-written index)
5. Add reference to MEMORY.md pointing to standards/

### Before Next Major Phase (This Week)
1. Fill in Tier 2 files as they're used (ENDPOINT_WORKFLOW, DATABASE_WORKFLOW, etc.)
2. Update catalog.json after each new standard
3. Share with Kira for review + feedback
4. Iterate on what's working/not working

### When MemoryGraph is Ready (Phase TBD)
1. Run extraction pipeline on `standards/` folder
2. Populate `knowledge-graph/entities.json` + `relationships.json`
3. Ingest into MemoryGraph
4. Query it for consistency: "Show all database standards"

---

## Metadata Format (For Now)

Add this to the top of each `standards/` .md file:

```markdown
---
# Metadata (for MemoryGraph later)
tier: 2
category: frontend
tags: [components, react, development, testing]
related_standards: [STYLING_CONVENTIONS, STATE_MANAGEMENT]
status: stable
created: 2026-04-24
last_updated: 2026-04-24
---

# Component Development Workflow
...
```

This way: Zero rework when MemoryGraph is ready. YAML front matter is already structured.

---

## Benefits

✅ **Organized:** Standards live in one place, not scattered across projects
✅ **Shared:** Both you and Kira follow same patterns
✅ **Ready for MemoryGraph:** Already in machine-readable format
✅ **Queryable:** "Show me all frontend standards" works immediately
✅ **Versioned:** Git tracks why standards evolved
✅ **Discoverable:** catalog.json = searchable index

---

## Next Action

Should I:
1. Create the folder structure in workspace now?
2. Move COMPONENT_DEVELOPMENT_WORKFLOW.md to `standards/frontend/`?
3. Create DEVELOPMENT_STANDARDS.md (Tier 1 principles)?
4. Create catalog.json (hand-written for now)?

Then: You + Kira review, iterate, add new standards as we discover them.

Ready to set up? 🎯
