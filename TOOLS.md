# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific
- Project-local conventions and notes that belong in each repo’s `.openclaw/` folder

## Project Notes Convention

- Use a `.openclaw/` subfolder in every project for local docs, decisions, and operating notes.
- Keep project-specific information there instead of scattering it across the repo root.
- Treat `.openclaw/` as the first place to check for repo-local guidance before guessing or searching elsewhere.
- Prefer concise, durable notes over duplicated markdown in multiple locations.
- Never sync `.openclaw/` subfolders to git; keep them local only and add them to `.gitignore` in each project.
- If a project has already tracked `.openclaw/` files, remove them from git so they stay local.

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## NUC Network Configuration (2026-04-26)

**Three Ethernet paths, segmented by purpose:**

| IP | Interface | Purpose | Protocols |
|---|-----------|---------|----------|
| **10.0.0.28** | enp5s0 | SSH + Admin | SSH (terminal, git, deploys) |
| **10.0.0.22** | eno1 | App Traffic | HTTP/HTTPS (Envestero frontend/backend) |
| **10.0.0.81** | wlp6s0 | Backup/Secondary | Fallback if wired NICs down |

**Quick reference:**
```bash
# SSH (always use 10.0.0.28)
ssh leto@10.0.0.28

# Services (Envestero on 10.0.0.22)
http://10.0.0.22:3000  # Frontend (Next.js)
http://10.0.0.22:8000  # Backend (FastAPI)
```

**Why this setup:**
- Wired NICs = stable, low-latency for SSH & app traffic
- Separate planes = SSH control doesn't compete with app data
- Built-in failover = services can shift to enp5s0 if eno1 fails
- Future expansion = reserve enp5s0 secondary for new services (ImageForge3D, MemoryGraph jobs)

**Persistence:** DHCP via systemd-networkd (survives reboots, MAC-based assignment stable)

---

## Telegram Outbound Messaging

**Quick Send Command:**
```bash
openclaw message send --target telegram:8718656405 --message "Your message here"
```

**Details:**
- Telegram User ID: `8718656405` (Toan's primary account)
- Bot name: `@nuc_nova_bot`
- Use format: `telegram:` + user ID
- Returns message ID on success (e.g., "Message ID: 13")
- Works via OpenClaw CLI for one-way outbound messages
- Useful for: alerts, notifications, scheduled reminders, or sending from tools/scripts

**Usage Examples:**
```bash
# Simple message
openclaw message send --target telegram:8718656405 --message "Hello!"

# With JSON output
openclaw message send --target telegram:8718656405 --message "Test" --json
```

**Note:** This is outbound only. For back-and-forth chat, message the bot in Telegram directly.

---

Add whatever helps you do your job. This is your cheat sheet.
