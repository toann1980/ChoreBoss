# OCP Standards Correction (2026-05-02 00:39 PDT)

## What I Misunderstood

❌ **WRONG:** Created `/srv/openclaw_projects/llama.cpp/.openclaw/` folder
✅ **CORRECT:** All project files at root level: `/srv/openclaw_projects/llama.cpp/`

## OCP Standards (Verified from OCP_STANDARDS.md)

**Key Principle:** All documentation files at **root level only**.

```
/srv/openclaw_projects/llama.cpp/
├── START_HERE.md          ← Entry point
├── CURRENT.md             ← Current state (updated end of session)
├── INDEX.md               ← Documentation map
├── README.md              ← Project overview
├── CHANGELOG.md           ← Version history
├── docs/                  ← Subdirectories OK
├── src/
├── tests/
├── memory/                ← Daily work notes
└── [other subdirs]
```

**NO `.openclaw/` wrapper.**

## Why Root-Level Structure

✅ Clean, flat organization  
✅ Fast traversal  
✅ Clear discoverability  
✅ AI-friendly (consistent across all OCP projects)  
✅ Root-level files are the source of truth  

## What Goes Where

### Root Level (Core Documentation)
- `START_HERE.md` — Entry point (update before new work)
- `CURRENT.md` — Current state (update end of session)
- `INDEX.md` — Documentation map
- `README.md` — Project readme
- `CHANGELOG.md` — Version history

### Subdirectories
- `docs/` — Architecture, design, deployment
- `memory/` — Daily session notes (project-local learning)
- `src/` — Code
- `tests/` — Tests

## What I Need To Do

1. ✅ Remove `.openclaw/` folder from llama.cpp project
2. ✅ Move files to root level: `/srv/openclaw_projects/llama.cpp/`
   - `SESSION_2026-05-02.md` → `/srv/openclaw_projects/llama.cpp/SESSION_2026-05-02.md`
   - `COMPREHENSIVE_SESSION_NOTES.md` → `/srv/openclaw_projects/llama.cpp/COMPREHENSIVE_SESSION_NOTES.md`
3. ✅ Create `memory/` folder for daily notes (project-local)
4. ✅ Update or create `CURRENT.md` (end of session snapshot)
5. ✅ Create `START_HERE.md` if missing
6. ✅ Update any AI routines to follow this pattern

## OCP Folder Structure (Standard)

```
/srv/openclaw_projects/
├── START_HERE.md              (Portfolio entry)
├── CURRENT.md                 (Portfolio state)
├── INDEX.md                   (All projects)
├── OCP_STANDARDS.md           (These rules)
├── repos/                     (GitHub projects with repos)
│   ├── Envestero/
│   ├── MemoryGraph/
│   └── [...]
├── llama.cpp/                 (OCP-only projects)
│   ├── START_HERE.md
│   ├── CURRENT.md
│   ├── INDEX.md
│   ├── memory/
│   ├── src/
│   └── [...]
├── BenchModel/
│   ├── START_HERE.md
│   ├── CURRENT.md
│   ├── memory/
│   └── [...]
└── [other OCP projects]
```

## Memory Folder Convention

**For OCP projects:** `[ProjectName]/memory/`
- NOT workspace memory
- NOT `.openclaw/` subfolder
- Daily session notes: `YYYY-MM-DD.md`
- Per OCP standards, keep root clean

Example:
```
/srv/openclaw_projects/llama.cpp/memory/
├── 2026-05-02.md (today's notes)
├── 2026-05-01.md
└── [...]
```

## I Understand

✅ Root-level files only for OCP projects  
✅ No `.openclaw/` folders for OCP  
✅ `memory/` folder for daily notes (project-local)  
✅ All projects follow same structure  
✅ Clean root, discoverability first  

**This is the standard. I'll follow it.**

