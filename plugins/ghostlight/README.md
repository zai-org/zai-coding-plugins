# Ghostlight

Governed, semantic browser control for coding agents. Ghostlight's MCP server drives the
user's real, signed-in Chromium browser through 24 governed tools -- navigate, inspect, find,
click, fill, type, screenshot, record -- with per-action capability classification
(read / action / write / execute) and structured audit. Local by construction: no telemetry
and no update pings; the only network traffic is the checksum-pinned binary download from the
project's GitHub releases.

## MCP server

`npx -y ghostlight` -- the project's npm launcher. It verifies sha256-pinned binaries from
the official GitHub release into `~/.ghostlight/bin/v<version>/`, then hands its inherited
stdio to `ghostlight-mcp-connector`, which demand-starts the sibling local authority.
Requires Node.js 18 or newer.

The first real browser call walks the user through connecting the browser adapter (a
Chrome Web Store reviewed extension) if none is connected yet.

## Skill

`control-browser` teaches agents the observe-then-act handle model (target, view, and
snapshot handles), screenshot-bound coordinates, composition via `browser_sequence` and
`browser_flow`, dialog handling, and the effect-truth rules (never replay a call that is not
repeat-safe).

## Links

- Repository: https://github.com/sylin-org/ghostlight
- License: Apache-2.0 OR MIT
