# Leteo

Persistent memory for coding agents: one Rust binary over one SQLite database,
local-first, no service to sign up to.

Each session opens holding what the project already knows, prompts are kept, and
a compaction is recovered from rather than survived.

## Install

```text
zcode plugins marketplace add zai-org/zai-coding-plugins
zcode plugins install leteo@zai-coding-plugins
```

**The plugin carries configuration, not the binary.** Install `leteo` first, or
the MCP entry and every hook here are commands that are not on `PATH`:

```sh
curl -fsSL https://raw.githubusercontent.com/asanabrial/leteo/main/scripts/install.sh | sh
```

`cargo install leteo` and a Windows script are in the
[project README](https://github.com/asanabrial/leteo#install).

## What it registers

| Event | Command | Effect |
| --- | --- | --- |
| `SessionStart` (`startup`, `clear`) | `leteo hook session-start` | Opens the session and hands back the project's recent work, prompts and most relevant memories |
| `SessionStart` (`compact`) | `leteo hook post-compaction` | Puts back what the compaction took, and clears what had been marked as already shown |
| `UserPromptSubmit` | `leteo hook user-prompt-submit` | Keeps the prompt, and names a memory worth having in front of you — never the same one twice in a session |

Three, not five. This client fires seven lifecycle events — `SessionStart`,
`UserPromptSubmit`, `PreToolUse`, `PermissionRequest`, `PostToolUse`,
`PostToolUseFailure`, `Stop` — and neither `SubagentStop` nor `SessionEnd` is
among them, so the hooks named for those have nowhere to land.

`session-stop` is deliberately **not** moved onto `Stop` to fill the gap. `Stop`
fires when the agent finishes a reply, at the end of every turn rather than at
the end of the conversation; registered there once, it ended the session on every
single prompt, which deleted the save reminder's debounce and made the reminder
appear on every prompt instead of every fifteen minutes. The closing summary
comes from the agent calling `mem_session_summary` itself, which the skill tells
it to do.

Alongside them, [`.mcp.json`](.mcp.json) registers the MCP server with the
`agent` tool profile, so the everyday tools are there from the first message, and
[`skills/memory`](skills/memory/SKILL.md) carries the protocol that tells the
agent when to reach for them. Tools without that protocol is the shape that
measured 0 saves out of 8 tasks.

## Alternative to the plugin

`leteo setup zcode --hooks` writes the same three registrations into
`~/.zcode/cli/config.json` directly. **Pick one, not both** — registered twice,
every lifecycle event runs twice, which stored each prompt twice on the machine
where it was found, 23 identical pairs before anything looked wrong. `leteo
setup` looks for an installed bundle and refuses rather than adding a second
copy.

The plugin is the more robust of the two: configuration-file hooks run only
while `hooks.enabled` is true, and that switch starts off and belongs to the
person, while enabling a plugin is what enables the plugin's hooks.

## Upstream

Canonical source, issues and the full documentation:
<https://github.com/asanabrial/leteo>. MIT licensed. Leteo is a
reimplementation of Engram; that attribution is kept in the project's `NOTICE`.
