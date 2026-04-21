# ImageForge3D - Project Baseline

**Status:** Active | **Size:** 1.3M | **Files:** 17 Python files

## Overview
AI-powered 3D to image generation. Integrates Blender, FastAPI backend, Vue 3 frontend, and Hugging Face Stable Diffusion for generating AI images from 3D render layers. Uses WebSocket-first architecture for clean Blender ↔ Backend communication.

## Structure
```
ImageForge3D/
├── backend/             # FastAPI backend
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # Vue.js 3 frontend
│   ├── src/
│   ├── public/
│   └── README.md
├── blender/             # Blender addon integration
│   ├── scripts/
│   └── README.md
├── ARCHITECTURE.md
├── IMPLEMENTATION_SUMMARY.md
├── README.md
├── TEST_RESULTS.md
├── .gitignore (3487 bytes)
├── .github/             # CI/CD workflows
├── .prettierrc
└── Notes.md (empty)
```

## Recent Commits (Latest 5)
1. `0c500dc` - Reformat lines, ensure 80 char limit
2. `4a58bd7` - Docstring and typehint all functions
3. `d667146` - Add AO denoise properties and compositor setup for improved rendering quality
4. `f6077e8` - Add quality UI registration for rendering options in the register function
5. `e87e2ee` - Add quality control properties for Cycles rendering: introduce samples, denoise, and quality preset options

## Communication Flow
```
Blender Addon (connects to 8081)
    ↓ WebSocket
Frontend Relay Server (port 8081)
    ↓ WebSocket
FastAPI Backend (port 8000)
    ↓
AI Model Processing (Stable Diffusion)
```

## Tech Stack
- **Backend:** FastAPI + Python
- **Frontend:** Vue.js 3 (SPA)
- **3D Engine:** Blender 4.x addon
- **AI Model:** Hugging Face Stable Diffusion
- **Communication:** WebSocket (async, real-time)
- **GPU Support:** NVIDIA auto-detection
- **Deployment:** Docker (backend + optional frontend)

## Key Features
- **3D Render Layer Processing:** Extracts render passes from Blender
- **AI Image Generation:** Uses Stable Diffusion for AI-driven synthesis
- **WebSocket Relay:** Frontend relay decouples Blender from backend internals
- **Quality Control:** Recent work on Cycles rendering quality (samples, denoise, presets)
- **GPU Acceleration:** Automatic NVIDIA GPU detection

## Documentation
- **ARCHITECTURE.md:** System design & flow
- **IMPLEMENTATION_SUMMARY.md:** Feature breakdown & status
- **TEST_RESULTS.md:** Validation & test coverage
- Each subsystem (backend, frontend, blender) has own README

## Recent Focus (Last 5 commits)
- Code quality: Docstrings, type hints, 80-char line limit
- Rendering quality: AO denoise, compositor setup, quality presets
- Cycles integration: Rendering quality options in UI

## Key Insights
- **Well-documented:** ARCHITECTURE, IMPLEMENTATION_SUMMARY, TEST_RESULTS all present
- **Code discipline:** Recent push for docstrings + type hints (commits 2–5 focused on this)
- **Production-ready:** Full WebSocket architecture, GPU support, Docker
- **Active refinement:** Focus on rendering quality & code standards
- **Modular design:** Clear separation (blender addon, relay, backend, frontend)

## Toan's Role
Core 3D AI generation tool. Aligns with garment/asset creation service (Blender-based).

## Next Steps
- [ ] Review IMPLEMENTATION_SUMMARY for feature completeness
- [ ] Check TEST_RESULTS for coverage gaps
- [ ] Validate WebSocket relay stability under load
- [ ] Review quality control presets (samples, denoise strategy)
