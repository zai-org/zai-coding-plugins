---
description: Query detailed ZAI/GLM Coding Plan quota and usage breakdown
allowed-tools: Bash, Read
---

# Query ZAI Quota Details

Run a detailed quota query and show the full breakdown to the user.

## Execution

### Step 1: Run the query script

Execute the statusline script to get fresh data (bust cache by removing the cache file first):

```bash
rm -f /tmp/zai-quota-cache.json && echo '{}' | node "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/cache/zai-quota-hud/zai-quota-hud/$(ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/zai-quota-hud/zai-quota-hud/ | sort | tail -1)/scripts/statusline.mjs"
```

If the plugin is loaded via `--plugin-dir`, adjust the path accordingly. You can find the plugin root by looking for `scripts/statusline.mjs` relative to the plugin directory.

If that fails, try:
```bash
rm -f /tmp/zai-quota-cache.json && ANTHROPIC_BASE_URL="$ANTHROPIC_BASE_URL" ANTHROPIC_AUTH_TOKEN="$ANTHROPIC_AUTH_TOKEN" node -e "
const https = require('https');
const { URL } = require('url');
const baseUrl = process.env.ANTHROPIC_BASE_URL || '';
const authToken = process.env.ANTHROPIC_AUTH_TOKEN || '';
if (!baseUrl || !authToken) { console.error('Set ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN'); process.exit(1); }
const parsed = new URL(baseUrl);
const base = parsed.protocol + '//' + parsed.host;
const url = new URL(base + '/api/monitor/usage/quota/limit');
const req = https.request({ hostname: url.hostname, port: url.port || 443, path: url.pathname, method: 'GET', headers: { 'Authorization': authToken, 'Accept-Language': 'en-US,en', 'Content-Type': 'application/json' } }, (res) => {
  let d = ''; res.on('data', c => d += c); res.on('end', () => { console.log(JSON.stringify(JSON.parse(d), null, 2)); });
});
req.on('error', e => { console.error(e.message); process.exit(1); });
req.end();
"
```

### Step 2: Format the output

Parse the JSON response and present it clearly:

**If platform is ZHIPU** (ANTHROPIC_BASE_URL contains `open.bigmodel.cn`), present in Chinese:

```
## ZAI 配额使用情况

**账号等级:** {level}

### Token 使用 (5小时窗口)
- 使用率: {percentage}%
- 下次重置: {nextResetTime formatted}

### MCP 使用 (月度)
- 当前用量: {currentValue} / {usage}
- 剩余: {remaining}
- 使用率: {percentage}%
- 下次重置: {nextResetTime formatted}

#### 模型明细:
- {modelCode}: {usage}
```

**If platform is ZAI** (ANTHROPIC_BASE_URL contains `api.z.ai`), present in English:

```
## ZAI Quota Usage

**Account Level:** {level}

### Token Usage (5-hour window)
- Usage: {percentage}%
- Resets at: {nextResetTime formatted}

### MCP Usage (Monthly)
- Current: {currentValue} / {usage}
- Remaining: {remaining}
- Usage: {percentage}%
- Resets at: {nextResetTime formatted}

#### Per-model breakdown:
- {modelCode}: {usage}
```

### Constraint

**Run the query exactly once.** Do not retry on failure. Show the error if it fails.
