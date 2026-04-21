# OpenClaw — Project Detail

## Installed Instance
- **Config:** `~/.openclaw/openclaw.json` (JSON5 — comments + trailing commas OK)
- **Gateway port:** 18789 (default)
- **Dashboard:** `openclaw dashboard` (auto-embeds token)
- **Platform:** WSL2 (Linux 6.6) on Windows host
- **Security:** `allowInsecureAuth` disabled, Telegram wildcard removed
- **Cron:** Weekly Monday 9am PT security audit active

## Source Repo
- **Location:** `/home/tron/app/openclaw`
- **Remote:** `origin` → `https://github.com/openclaw/openclaw.git`
- **Branch:** `main`
- **Build:** `pnpm build` | **Test:** `pnpm test` | **Check:** `pnpm check`
- ⚠️ Always ask Toan before changing source files

## Architecture
- **Gateway** (`src/gateway/`) — central WS + HTTP server, single port
- **Control UI** (`ui/`) — Vite + Lit SPA; `<title>OpenClaw Control</title>` hardcoded in `ui/index.html` (no config knob)
- **Extensions** (`extensions/`) — 100+ bundled plugins (Discord, Telegram, providers…)
- **Config schema:** `openclaw config schema` prints live JSON Schema
- **Strict validation:** unknown keys / wrong types → gateway refuses to start

## Key Config Paths (authoritative — sourced from live schema + docs)

### UI / Identity
- `ui.seamColor` — hex accent color
- `ui.assistant.name` — display name in Control UI (max 50 chars)
- `ui.assistant.avatar` — emoji, short string, URL, or data URI

### Gateway
- `gateway.port` — TCP port (default 18789)
- `gateway.bind` — auto | loopback | lan | tailnet | custom
- `gateway.mode` — local | remote
- `gateway.auth.mode` — none | token | password | trusted-proxy
- `gateway.auth.token` / `gateway.auth.password`
- `gateway.controlUi.basePath` — URL prefix (e.g. `/openclaw`)
- `gateway.controlUi.allowedOrigins` — required for non-loopback browser clients
- `gateway.controlUi.embedSandbox` — strict | scripts | trusted
- `gateway.controlUi.allowInsecureAuth` — localhost compat toggle only
- `gateway.controlUi.dangerouslyDisableDeviceAuth` — break-glass only
- `gateway.reload.mode` — off | restart | hot | hybrid
- `gateway.tls.enabled` / `.certPath` / `.keyPath` / `.autoGenerate`

### Agents / Models
- `agents.defaults.model` — `"provider/model"` or `{ primary, fallbacks }`
- `agents.defaults.models` — catalog + alias allowlist for `/model`
- `agents.defaults.workspace` — default workspace dir
- `agents.defaults.heartbeat.every` — duration string e.g. `"30m"`; `"0m"` disables
- `agents.defaults.sandbox.mode` — off | non-main | all
- `agents.defaults.embeddedHarness.runtime` — auto | pi | codex | (plugin id)
- `agents.defaults.imageGenerationModel` — string or `{ primary, fallbacks }`
- `agents.list[].id/model/workspace/skills/identity/sandbox/tools` — per-agent overrides

### Channels (auto-start when section exists)
- `channels.<provider>.dmPolicy` — pairing | allowlist | open | disabled
- `channels.<provider>.allowFrom` — sender allowlist
- `channels.<provider>.groups.*` — group config, `requireMention`
- `channels.defaults.groupPolicy` — shared fallback
- Multi-account: `channels.<provider>.accounts.<id>` + `defaultAccount`

### Tools
- `tools.profile` — minimal | coding | messaging | full
- `tools.allow` / `tools.deny` — global allow/deny lists
- `tools.elevated.enabled` + `.allowFrom` — elevated exec control
- `tools.sessions.visibility` — self | tree | agent | all

### Skills
- `agents.defaults.skills` — default skill allowlist (omit = unrestricted)
- `skills.entries.<id>.enabled` — per-skill toggle

### Session
- `session.dmScope` — main | per-peer | per-channel-peer | per-account-channel-peer
- `session.reset.mode` — daily | idle

### Plugins
- `plugins.entries.<id>.config` — plugin config
- ⚠️ Plugin config changes require gateway restart

### Hot Reload
- Most fields apply live
- `gateway.*` and `plugins.*` require restart

## CLI Config Commands
```bash
openclaw config get <path>
openclaw config set <path> <value>
openclaw config unset <path>
openclaw config schema # print full JSON Schema
openclaw config validate
openclaw config file # show config file path