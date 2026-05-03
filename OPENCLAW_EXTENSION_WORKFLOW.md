# OpenClaw Extension Workflow

**How to create, build, install, and debug OpenClaw plugins**

---

## Quick Reference

| Step | Command | Purpose |
|------|---------|---------|
| 1. Create | `mkdir my-plugin && cd my-plugin && npm init` | Start a new plugin |
| 2. Write | Create `src/index.ts` with plugin code | Implement tools |
| 3. Build | `npm run build` (tsc) | Compile TypeScript → JavaScript |
| 4. Test | `npm test` | Verify all tests pass |
| 5. Install | `openclaw plugins install -l /path/to/plugin` | Link to OpenClaw |
| 6. Restart | `openclaw gateway restart` | Reload plugin registry |
| 7. Verify | `openclaw gateway status` | Check plugin is loaded |

---

## 1. Create Your Plugin

### Project Structure
```
my-plugin/
├── src/
│   ├── index.ts           ← Plugin entry point
│   ├── feature1.ts        ← Tool implementation
│   ├── feature1.test.ts   ← Test suite
│   └── ...
├── dist/                  ← Compiled JavaScript (auto-generated)
├── package.json
├── tsconfig.json
└── openclaw.plugin.json   ← Plugin manifest
```

### Essential Files

**package.json:**
```json
{
  "name": "@openclaw/my-plugin",
  "version": "0.1.0",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "test": "node --test dist/**/*.test.js"
  },
  "dependencies": {
    "@sinclair/typebox": "^0.x.x"
  }
}
```

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ES2020",
    "moduleResolution": "node",
    "outDir": "./dist",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*.ts"]
}
```

**openclaw.plugin.json:**
```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "description": "What this plugin does",
  "version": "0.1.0",
  "tools": [
    {
      "id": "my_tool",
      "name": "My Tool",
      "description": "Tool description",
      "parameters": {
        "type": "object",
        "properties": {
          "input": { "type": "string" }
        },
        "required": ["input"]
      }
    }
  ]
}
```

---

## 2. Implement Your Plugin

**src/index.ts:**
```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { Type } from "@sinclair/typebox";

export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Does cool things",

  register(api) {
    api.registerTool({
      name: "my_tool",
      label: "My Tool",
      description: "Tool description",
      parameters: Type.Object({
        input: Type.String({ description: "Input text" }),
      }),

      async execute(_id, params: { input: string }) {
        try {
          const result = `Processed: ${params.input}`;
          return {
            content: [{ type: "text", text: result }],
            details: { success: true },
          };
        } catch (error) {
          return {
            content: [{ type: "text", text: `Error: ${error}` }],
            details: { error: "failed" },
          };
        }
      },
    });
  },
});
```

---

## 3. Write Tests

**src/index.test.ts:**
```typescript
import { test } from "node:test";
import { strict as assert } from "node:assert";
import plugin from "./index.js";

test("Plugin registers tools", () => {
  const tools = [];
  const api = {
    registerTool: (config) => tools.push(config.name),
  };

  plugin.register(api);

  assert.equal(tools.includes("my_tool"), true);
});

test("Tool executes successfully", async () => {
  const tools = new Map();
  const api = {
    registerTool: (config) => tools.set(config.name, config),
  };

  plugin.register(api);
  const tool = tools.get("my_tool");
  const result = await tool.execute("test-id", { input: "hello" });

  assert.equal(result.content[0].text.includes("Processed"), true);
});
```

---

## 4. Build Your Plugin

```bash
npm run build
```

This compiles `src/*.ts` → `dist/*.js` + type definitions.

### Verify Build
```bash
ls dist/index.js      # Should exist
npm test              # Should pass
```

---

## 5. Install to OpenClaw

### Link Mode (Development)
```bash
openclaw plugins install -l /path/to/my-plugin
```

**Why `-l` flag?**  
- `-l` = "link mode" — plugin stays in source repo, no copy
- Ideal for development — changes to `src/` are live after rebuild + gateway restart
- Alternative: `plugins install /path/to/my-plugin` (copy mode)

### Handle Security Flags
If your plugin uses shell commands, add:
```bash
openclaw plugins install -l /path/to/my-plugin --dangerously-force-unsafe-install
```

### Verify Installation
```bash
cat ~/.openclaw/openclaw.json | jq '.plugins.entries.my-plugin'
```

Should output your plugin configuration.

---

## 6. Restart the Gateway

```bash
openclaw gateway restart
```

This:
1. Reloads plugin registry
2. Discovers newly installed plugins
3. Registers all tools
4. Makes them available to OpenClaw

### Check Logs
```bash
tail -50 /tmp/openclaw/openclaw-*.log | grep -i "my-plugin\|plugins:"
```

You should see:
```
[plugins] my-plugin registered (1 tool)
ready (... plugins: ... my-plugin ...)
```

---

## 7. Verify Plugin is Loaded

```bash
openclaw gateway status
```

Output should include your plugin in the plugin list.

### Test a Tool
Go to OpenClaw Control UI (http://localhost:18789/) and:
1. Start a chat
2. Mention your tool by name: "Use my_tool with input 'test'"
3. OpenClaw should invoke it

---

## Debugging

### Plugin Not Appearing

**Check 1: Build succeeded**
```bash
npm run build
ls dist/index.js
```

**Check 2: Plugin config is valid**
```bash
cat openclaw.plugin.json | jq .
```

**Check 3: Plugin linked correctly**
```bash
cat ~/.openclaw/openclaw.json | jq '.plugins.entries' | grep my-plugin
```

**Check 4: Gateway loaded it**
```bash
tail /tmp/openclaw/openclaw-*.log | grep -i "my-plugin\|error"
```

**Check 5: Restart is needed**
```bash
openclaw gateway restart
sleep 5
openclaw gateway status
```

### Tool Execution Fails

**Check logs:**
```bash
tail -100 /tmp/openclaw/openclaw-*.log | grep -A5 "my_tool\|error"
```

**Common issues:**
- Missing `async` in tool execute
- Missing `await` on async operations
- Incorrect return format (needs `content` + `details`)
- Type validation error in parameters

---

## Best Practices

### 1. Type Everything
Use TypeBox for runtime validation:
```typescript
parameters: Type.Object({
  name: Type.String({ minLength: 1 }),
  age: Type.Optional(Type.Number()),
})
```

### 2. Return Proper Format
```typescript
return {
  content: [
    { type: "text" as const, text: "..." },  // User sees this
  ],
  details: {
    success: true,
    key: "value",  // For machine consumption
  },
};
```

### 3. Always Handle Errors
```typescript
async execute(_id, params: {}) {
  try {
    // your code
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error instanceof Error ? error.message : String(error)}` }],
      details: { error: "failed" },
    };
  }
}
```

### 4. Test Before Installing
```bash
npm test           # All tests pass?
npm run build      # Compiles clean?
ls dist/index.js   # Output exists?
```

### 5. Version Your Plugin
In `openclaw.plugin.json` and `package.json`:
```json
{
  "version": "0.1.0",
  "description": "What changed in this version"
}
```

---

## Common Patterns

### Reading Files
```typescript
import * as fs from "fs/promises";

const content = await fs.readFile(params.path, "utf-8");
```

### Async Operations
```typescript
const result = await someAsyncFunction();
```

### Parameter Validation
TypeBox validates at runtime; invalid params will reject before reaching `execute()`.

### Multiple Return Values
```typescript
return {
  content: [
    { type: "text", text: "First part" },
    { type: "text", text: "Second part" },
  ],
  details: { count: 2 },
};
```

---

## MemoryGraph as Reference

MemoryGraph is a full example:
- **Location:** `/srv/github/MemoryGraph`
- **7 tools:** Extract, Review, Lint, Promote, Changelog, Compact, Restore
- **42 tests:** Full test suite
- **Real use case:** Knowledge extraction pipeline

Study its `src/index.ts` for patterns.

---

## Next: Distribution

Once your plugin is stable:

1. **Publish to npm:**
   ```bash
   npm publish
   ```

2. **Add to OpenClaw registry:**
   - Submit PR to OpenClaw repository
   - Plugin will be auto-discoverable

3. **Share with others:**
   - GitHub repo link: `git clone ...`
   - Installation: `openclaw plugins install -l <repo-url>`

---

## Reference

- **OpenClaw Plugin SDK:** `openclaw/plugin-sdk/plugin-entry`
- **TypeBox (validation):** https://github.com/sinclairzx81/typebox
- **Node Test Runner:** https://nodejs.org/api/test.html

---

**Happy building!** 🚀
