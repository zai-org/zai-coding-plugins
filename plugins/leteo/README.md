# Leteo

Persistent memory for coding agents: one Rust binary over one SQLite database,
local-first, no service to sign up to.

Each session opens holding what the project already knows, prompts are kept,
sub-agent findings are captured before their context is discarded, and a
compaction is recovered from rather than survived.

## Install

```shell
claude plugin marketplace add zai-org/zai-coding-plugins
claude plugin install leteo@zai-coding-plugins
```

**The plugin carries configuration, not the binary.** Install `leteo` first, or
the MCP entry and every hook here are commands that are not on `PATH`:

```shell
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
| `SubagentStop` | `leteo hook subagent-stop` | Captures a sub-agent's Key Learnings, in any of the twelve languages Leteo speaks |
| `SessionEnd` | `leteo hook session-stop` | Closes the session |

Alongside them, [`.mcp.json`](.mcp.json) registers the MCP server with the
`agent` tool profile, so the everyday tools are there from the first message,
and [`skills/memory`](skills/memory/SKILL.md) carries the protocol that tells
the agent when to reach for them. Tools without that protocol is the shape that
measured 0 saves out of 8 tasks.

Every hook is best-effort and bounded: Leteo gives up before Claude Code does,
and a hook that could not do its work says so rather than failing silently.
Memory is an assistant, not a gate.

## Alternative to the plugin

`leteo setup claude-code --hooks` writes the same five registrations into
Claude Code's own settings directly. **Pick one, not both** — registered twice,
every lifecycle event runs twice, which stored each prompt twice on the machine
where it was found, 23 identical pairs before anything looked wrong from the
outside. `leteo setup` looks for an installed bundle and refuses rather than
adding a second copy.

## Design

The bundle is deliberately thin. Project detection, the stable manual session,
`<private>` redaction, deduplication, the save reminder and its debounce, and
the `.leteo/` import all live in the Leteo binary, shared with the CLI, the MCP
server and every other agent's hooks. These files only say which event maps to
which command, so there is one implementation to keep correct instead of two.

Which events belong here is not written out twice either: upstream holds one
list per agent and a guard reads each bundle against it, matchers and deadlines
included. Written out here and nowhere held, they drift.

## Upstream

Canonical source, issues and the full documentation:
<https://github.com/asanabrial/leteo>. MIT licensed. Leteo is a
reimplementation of Engram; that attribution is kept in the project's `NOTICE`.

Leteo also ships a ZCode-targeted bundle upstream, which registers three events
rather than five because that client fires neither `SubagentStop` nor
`SessionEnd`. This entry is the Claude Code one, which is what this marketplace
is for.
