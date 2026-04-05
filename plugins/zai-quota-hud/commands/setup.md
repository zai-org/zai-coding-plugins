---
description: Configure the ZAI Quota HUD statusline in Claude Code settings
allowed-tools: Bash, Read, Write, Edit
---

# Setup ZAI Quota HUD Statusline

Configure the ZAI Quota HUD to display quota information below the Claude Code input bar.

## Steps

### 1. Detect the plugin directory

Find where the zai-quota-hud plugin is installed. Check in order:
1. `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/cache/zai-quota-hud/` (marketplace install)
2. Look for a `--plugin-dir` loaded copy
3. Ask the user for the plugin path

Run: `ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/zai-quota-hud/zai-quota-hud/*/ 2>/dev/null | sort | tail -1`

If that returns a path, use it. If not, ask the user for the absolute path to the `zai-usage-claude-code-plugin` directory.

### 2. Generate the statusline command

For a marketplace-installed plugin:
```
bash -c 'plugin_dir=$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/zai-quota-hud/zai-quota-hud/*/ 2>/dev/null | sort | tail -1); exec node "${plugin_dir}scripts/statusline.mjs"'
```

For a local plugin-dir install:
```
bash -c 'exec node "<PLUGIN_PATH>/scripts/statusline.mjs"'
```

Where `<PLUGIN_PATH>` is the absolute path from step 1.

### 3. Write the statusLine config

Read the current `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json` (create it if it doesn't exist).

Merge in the `statusLine` field while preserving all existing settings:

```json
{
  "statusLine": {
    "type": "command",
    "command": "<generated command from step 2>"
  }
}
```

If a `statusLine` already exists, confirm with the user before overwriting.

### 4. Verify

Run the generated command to confirm it produces output:

```bash
echo '{}' | bash -c '<the generated command>'
```

### 5. Inform the user

Tell the user:
- The statusline has been configured
- They need to **restart Claude Code** for the statusLine config to take effect
- After restart, they should see quota info below the input bar
- If they don't see it, run `/zai-quota-hud:setup` again or check that `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` are set in their environment
