# ZAI Quota HUD

[中文](README.zh-CN.md)

A Claude Code plugin that displays your ZAI/GLM Coding Plan token quota usage in the statusline.

![ZAI ██░░░ 37%](https://img.shields.io/badge/statusline-quota-brightgreen) ![License](https://img.shields.io/github/license/n1majne3/zai-quota-hud)

## What you see

Below the input bar:

```
ZAI ██░░░ 37%
```

Color changes automatically: green (< 50%), yellow (50-80%), red (> 80%).

At 100% usage, a countdown timer shows time until reset:

```
ZAI █████ 100% ⏳ 1h 23m
```

## Commands

| Command | Description |
|---------|-------------|
| `/zai-quota-hud:setup` | Configure the statusline in Claude Code settings |
| `/zai-quota-hud:quota` | Show detailed quota breakdown (per-model) |

## Requirements

- Claude Code v1.0.80+
- Node.js 18+
- `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` environment variables set (ZAI or Zhipu endpoint)

## License

MIT
